from datetime import datetime
import click
from flask import current_app, render_template
from flask.cli import AppGroup
from flask_mail import Message
from werkzeug.security import generate_password_hash

from goathacks.registration import bp
from goathacks import db, mail
from goathacks.models import User

from tabulate import tabulate

gr = AppGroup("user")

@gr.command('create')
@click.option("--email", prompt=True, help="User's Email")
@click.option("--first_name", prompt=True)
@click.option("--last_name", prompt=True)
@click.option("--admin/--no-admin", prompt=True, default=False)
@click.option("--password", prompt=True, hide_input=True,
                confirmation_prompt=True)
@click.option("--school", prompt=True)
@click.option("--phone", prompt=True)
@click.option("--gender", prompt=True)
def create_user(email, first_name, last_name, password, school, phone, gender,
                admin):
    """
    Creates a user
    """

    if gender not in ['F', 'M', 'NB']:
        click.echo("Invalid gender. Must be one of F, M, NB")
        return
    
    num_not_waitlisted = len(User.query.filter_by(waitlisted=False).all())
    waitlisted = False
    if num_not_waitlisted >= current_app.config['MAX_BEFORE_WAITLIST']:
        waitlisted = True

    user = User(
            email=email,
            password=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            last_login=datetime.now(),
            waitlisted=waitlisted,
            school=school,
            phone=phone,
            gender=gender,
            is_admin=admin
            )
    db.session.add(user)
    db.session.commit()

    click.echo("Created user")

@gr.command("promote")
@click.option("--email", prompt=True)
def promote_user(email):
    """
    Promotes a user to administrator
    """
    user = User.query.filter_by(email=email).one()

    user.is_admin = True

    db.session.commit()

    click.echo(f"Promoted {user.first_name} to admin")


@gr.command("demote")
@click.option("--email", prompt=True)
def demote_user(email):
    """
    Demotes a user from administrator
    """
    user = User.query.filter_by(email=email).one()

    user.is_admin = False

    db.session.commit()

    click.echo(f"Demoted {user.first_name} from admin")

@gr.command("waitlist")
@click.option("--email", prompt=True)
def waitlist_user(email):
    """
    Toggles the waitlist status of a user
    """
    user = User.query.filter_by(email=email).one()

    user.waitlisted = not user.waitlisted

    db.session.commit()

    if user.waitlisted:
        click.echo(f"Sent {user.first_name} to the waitlist")
    else:
        msg = Message("Waitlist Promotion")
        msg.add_recipient(user.email)
        msg.body = render_template("emails/waitlist_promotion.txt", user=user)
        mail.send(msg)
        click.echo(f"Promoted {user.first_name} from the waitlist")

@gr.command("drop")
@click.option("--email", prompt=True)
@click.option("--confirm/--noconfirm", prompt=False, default=True)
def drop_user(email, confirm):
    """
    Drops a user's registration
    """
    user = User.query.filter_by(email=email).one()
    if not confirm:
        pass
    else:
        if click.confirm(f"Are you sure you want to drop {user.first_name} {user.last_name}'s registration? **THIS IS IRREVERSIBLE**"):
           pass 
        else:
           return
    db.session.delete(user)
    db.session.commit()
    click.echo(f"Dropped {user.first_name}'s registration")
    
@gr.command("list")
def list_users():
    """
    Gets a list of all users
    """
    users = User.query.all()

    def make_table_content(user):
        return [user.email, f"{user.first_name} {user.last_name}", user.waitlisted, user.is_admin]

    table = map(make_table_content, users)

    print(tabulate(table, headers=["Email", "Name", "Waitlisted", "Admin"]))


@gr.command("autopromote")
def autopromote_users():
    """
    Runs through and automatically promotes users up to the waitlist limit
    """
    WAITLIST_LIMIT = current_app.config['MAX_BEFORE_WAITLIST']
    num_confirmed = db.session.query(User).filter(User.waitlisted == False).count()
    click.echo(f"Got {num_confirmed} confirmed attendees")
    num_waitlisted = db.session.query(User).filter(User.waitlisted == True).count()
    click.echo(f"Got {num_waitlisted} waitlisted attendees")

    num_to_promote = WAITLIST_LIMIT - num_confirmed

    if num_to_promote > num_waitlisted:
        num_to_promote = num_waitlisted

    click.echo(f"About to promote {str(num_to_promote)} attendees from waitlist")

    users = db.session.query(User).filter(User.waitlisted == True).all()

    num_promoted = 0
    num_to_promote_orig = num_to_promote

    for u in users:
        if num_to_promote > 0:
            click.echo(f"Attempting to promote {u.email} ({u.id})")
            u.waitlisted = False
            db.session.commit()
            msg = Message("Waitlist Promotion")
            msg.add_recipient(u.email)
            msg.sender = ("GoatHacks Team", "hack@wpi.edu")
            msg.body = render_template("emails/waitlist_promotion.txt", user=u)
            mail.send(msg)
            num_promoted += 1
            num_to_promote -= 1

    click.echo(f"Promoted {num_promoted}/{num_to_promote_orig} attendees off the waitlist!")
            
