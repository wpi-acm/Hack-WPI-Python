from datetime import datetime
import click
from flask import current_app, render_template
from flask.cli import AppGroup
from flask_mail import Message
from werkzeug.security import generate_password_hash

from goathacks.registration import bp
from goathacks import db, mail
from goathacks.models import User

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
