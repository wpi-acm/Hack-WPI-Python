import hashlib
import json
import os
import random
import string
import smtplib
import time
from datetime import datetime

import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, redirect, url_for, request, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from config_hackWPI import (api_keys, SERVER_LISTEN_ADDR, SERVER_PORT, WAITLIST_LIMIT, HACKATHON_TIME,
                            ALLOWED_EXTENSIONS, REGISTRATION_OPEN)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)


class Hacker(db.Model):
    __tablename__ = 'hackers'

    mlh_id = db.Column(db.Integer, primary_key=True)
    registration_time = db.Column(db.Integer)
    checked_in = db.Column(db.Boolean)
    waitlisted = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    shirt_size = db.Column(db.String(4))
    special_needs = db.Column(db.String(300))


class AutoPromoteKeys(db.Model):
    __tablename__ = 'AutoPromoteKeys'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(4096))
    val = db.Column(db.String(4096))

@app.errorhandler(413)
def filesize_too_big(erro):
    print("Someone tried to send something too big")
    return "That file was too big, please go back and try a smaller resume pdf"

@app.errorhandler(500)
def server_error():
    print("There was a server error... If you're having trouble registering, please email hack@wpi.edu with your details and what you did to break our site :P")

@app.route('/sponsor')
def sponsorindex():
    return render_template('home/sponsor/index.html', registration_open=REGISTRATION_OPEN)

@app.route('/sponsor/<path:path>')
def sponsor(path):
    return send_from_directory('templates/home/sponsor', path)

@app.route('/')
def root():
    return render_template('home/index.html', registration_open=REGISTRATION_OPEN)

@app.route('/assets/<path:path>')
def staticassets(path):

    return send_from_directory('templates/home/assets', path)


@app.route('/resumepost', methods=['POST'])
def resumepost():
    if not REGISTRATION_OPEN:
        return 'Registration is currently closed.', 403

    """A last minute hack to let people post their resume after they've already registered"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "You tried to submit a resume with no file"

        resume = request.files['resume']
        if resume.filename == '':
            return "You tried to submit a resume with no file"

        if resume and not allowed_file(resume.filename):
            return jsonify(
                {'status': 'error', 'action': 'register',
                 'more_info': 'Invalid file type... Accepted types are txt pdf doc docx and rtf...'})

        if resume and allowed_file(resume.filename):
            # Good file!
            filename = session['mymlh']['first_name'].lower() + '_' + session['mymlh']['last_name'].lower() + '_' + str(
                session['mymlh']['id']) + '.' + resume.filename.split('.')[-1].lower()
            filename = secure_filename(filename)
            resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return 'Resume uploaded!  <a href="/dashboard">Return to dashboard</a>'
    return "Something went wrong. If this keeps happening, slack message @bkayastha"


@app.route('/shirtpost', methods=['GET'])
def shirtpost():
    if not REGISTRATION_OPEN:
        return 'Registration is currently closed.', 403
    if not is_logged_in():
        return 'Not signed in'
    
    """MLH removed t-shirt and accommodations fields of profile in V3, this is our hacky substitute"""
    if request.method == 'GET':
        size = request.args.get('size')
        special_needs = request.args.get('special_needs')
        id = session['mymlh']['id']

        upd = {}
        if size:
            upd['shirt_size'] = size
        if special_needs:
            upd['special_needs'] = special_needs
        else:
            upd['special_needs'] = None

        if db.session.query(db.exists().where(Hacker.mlh_id == id)).scalar():
            db.session.query(Hacker).filter(Hacker.mlh_id == id).update(upd)
            db.session.commit()
            return 'Info saved! <a href="../dashboard">Return to dashboard</a>'
    return "Something went wrong. If this keeps happening, email mikel@wpi.edu"


@app.route('/register', methods=['GET', 'POST'])
def register():
    if not REGISTRATION_OPEN:
        return 'Registration is currently closed.', 403

    if request.method == 'GET':
        # Register a hacker...
        if is_logged_in() and db.session.query(
                db.exists().where(Hacker.mlh_id == session['mymlh']['id'])).scalar():
            # Already logged in, take them to dashboard
            return redirect(url_for('dashboard'))

        if request.args.get('code') is None:
            # Get info from MyMLH
            return redirect(
                'https://my.mlh.io/oauth/authorize?client_id=' + api_keys['mlh']['client_id'] + '&redirect_uri=' +
                api_keys['mlh'][
                    'callback'] + '&response_type=code&scope=email+phone_number+demographics+birthday+education')

        if is_logged_in():
            return render_template('register.html', name=session['mymlh']['first_name'])

        code = request.args.get('code')
        oauth_redirect = requests.post(
            'https://my.mlh.io/oauth/token?client_id=' + api_keys['mlh']['client_id'] + '&client_secret=' +
            api_keys['mlh'][
                'secret'] + '&code=' + code + '&redirect_uri=' + api_keys['mlh'][
                'callback'] + '&grant_type=authorization_code')

        if oauth_redirect.status_code == 200:
            access_token = json.loads(oauth_redirect.text)['access_token']
            user_info_request = requests.get('https://my.mlh.io/api/v3/user.json?access_token=' + access_token)
            if user_info_request.status_code == 200:
                print(user_info_request.text)
                user = json.loads(user_info_request.text)['data']
                session['mymlh'] = user
                if db.session.query(db.exists().where(Hacker.mlh_id == user['id'])).scalar():
                    # User already exists in db, log them in
                    return redirect(url_for('dashboard'))

                return render_template('register.html', name=user['first_name'])

        return redirect(url_for('register'))


    if request.method == 'POST':
        if not is_logged_in() or db.session.query(
                db.exists().where(Hacker.mlh_id == session['mymlh']['id'])).scalar():
            # Request flow == messed up somehow, restart them
            return redirect(url_for('register'))

        if 'resume' not in request.files or 'tos' not in request.form:
            # No file or no TOS agreement?
            return redirect(url_for('register'))

        resume = request.files['resume']
        if resume.filename == '':
            resume = False
            # No file selected
            #return redirect(url_for('register'))

        if resume and not allowed_file(resume.filename):
            resume = False
            #return jsonify(
            #    {'status': 'error', 'action': 'register',
            #     'more_info': 'Invalid file type... Accepted types are txt pdf doc docx and rtf...'})

        if resume and allowed_file(resume.filename):
            # Good file!
            filename = session['mymlh']['first_name'].lower() + '_' + session['mymlh']['last_name'].lower() + '_' + str(
                session['mymlh']['id']) + '.' + resume.filename.split('.')[-1].lower()
            filename = secure_filename(filename)
            resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # Determine if hacker should be placed on waitlist
        waitlist = False
        if db.session.query(Hacker).count() + 1 > WAITLIST_LIMIT:
            print(session['mymlh']['first_name'] + " put on waitlist.")
            waitlist = True
        else:
            print(session['mymlh']['first_name'] + " put on registered.")

        first_name = session['mymlh']['first_name']
        last_name = session['mymlh']['last_name']
        email = session['mymlh']['email']

        # Add the user to the database
        print(Hacker(mlh_id=session['mymlh']['id'], registration_time=int(time.time()),
                   checked_in=False, waitlisted=waitlist, admin=False))
        db.session.add(
            Hacker(mlh_id=session['mymlh']['id'], registration_time=int(time.time()),
                   checked_in=False, waitlisted=waitlist, admin=False,
                   first_name=first_name, last_name=last_name, email=email))
        db.session.commit()
        print(session['mymlh']['first_name'] + " put on database successfully.")

        # Send a welcome email
        msg = 'Dear ' + session['mymlh']['first_name'] + '\n\n'
        msg += 'Thanks for applying to Hack@WPI!\n'
        if waitlist:
            msg += 'Sorry! We have hit our registration capacity. You have been placed on the waitlist.\n'
            msg += 'We will let you know if space opens up.\n'
        else:
            msg += 'You are fully registered! You are guarenteed a spot at the hackathon. Be sure to see the schedule at https://hack.wpi.edu. The opening ceremony is at 6:00 PM EST on Zoom at https://wpi.zoom.us/j/97135616505. Other zoom links will be sent through the slack.\n\n'
            msg += 'In the meantime, make sure to join the Slack and DevPost!\n'
            msg += 'http://bit.ly/hack21slack\n'
            msg += 'https://hack-wpi-2021.devpost.com/\n'
        send_email(session['mymlh']['email'], 'Hack@WPI - Thanks for applying', msg)

        # Finally, send them to their dashboard
        return redirect(url_for('dashboard'))


@app.route('/admin', methods=['GET'])
def admin():
    # Displays total registration information...
    # As Firebase could not be used with MyMLH, use PubNub to simulate the realtime database...

    if not is_admin():
        return redirect(url_for('register'))

    waitlist_count = 0
    total_count = 0
    check_in_count = 0
    shirt_count = {'xxs': 0, 'xs': 0, 's': 0, 'm': 0, 'l': 0, 'xl': 0, 'xxl': 0}
    male_count = 0
    female_count = 0
    schools = {}
    majors = {}

    mlh_info = get_mlh_users()

    hackers = []

    result = db.session.query(Hacker)

    for hacker in mlh_info:
        obj = result.filter(Hacker.mlh_id == hacker['id']).one_or_none()

        if obj is None:
            continue

        if obj.waitlisted:
            waitlist_count += 1

        if obj.checked_in:
            check_in_count += 1

        if hacker['gender'] == 'Male':
            male_count += 1
        else:
            female_count += 1

        total_count += 1
        if not 'school' in hacker:
            print("Hacker has no school:")
            print(hacker)
        else:
            if hacker['school']['name'] not in schools:
                schools[hacker['school']['name']] = 1
            else:
                schools[hacker['school']['name']] += 1

        if hacker['major'] not in majors:
            majors[hacker['major']] = 1
        else:
            majors[hacker['major']] += 1

        if obj.shirt_size in shirt_count:
            shirt_count[obj.shirt_size] += 1

        hackers.append({
            'checked_in': obj.checked_in,
            'waitlisted': obj.waitlisted,
            'admin': obj.admin,
            'registration_time': obj.registration_time,
            'id': hacker['id'],
            'email': hacker['email'],
            'first_name': hacker['first_name'],
            'last_name': hacker['last_name'],
            'phone_number': hacker['phone_number'],
            'shirt_size': (obj.shirt_size or '').upper(),
            'special_needs': obj.special_needs,
            'school': hacker['school'] if 'school' in hacker else 'NULL'
        })

    return render_template('admin.html', hackers=hackers, total_count=total_count, waitlist_count=waitlist_count,
                           check_in_count=check_in_count, shirt_count=shirt_count, female_count=female_count,
                           male_count=male_count, schools=schools, majors=majors,
                           mlh_url='https://my.mlh.io/api/v3/users.json?client_id=' + api_keys['mlh'][
                               'client_id'] + '&secret=' + api_keys['mlh'][
                                       'secret'])


@app.route('/change_admin', methods=['GET'])
def change_admin():
    # Promote or drop a given hacker to/from admin status...
    if not is_admin():
        return jsonify({'status': 'error', 'action': 'modify_permissions',
                        'more_info': 'You do not have permissions to perform this action...'})

    if request.args.get('mlh_id') is None or request.args.get('action') is None:
        return jsonify({'status': 'error', 'action': 'change_admin', 'more_info': 'Missing required field...'})

    valid_actions = ['promote', 'demote']
    if request.args.get('action') not in valid_actions:
        return jsonify({'status': 'error', 'action': 'change_admin', 'more_info': 'Invalid action...'})

    if request.args.get('action') == 'promote':
        db.session.query(Hacker).filter(Hacker.mlh_id == request.args.get('mlh_id')).update({'admin': True})
    elif request.args.get('action') == 'demote':
        db.session.query(Hacker).filter(Hacker.mlh_id == request.args.get('mlh_id')).update({'admin': False})
    db.session.commit()


    return jsonify({'status': 'success', 'action': 'change_admin:' + request.args.get('action'), 'more_info': '',
                    'id': request.args.get('mlh_id')})


@app.route('/check_in', methods=['GET'])
def check_in():
    # Check in a hacker...
    if not is_admin():
        return jsonify({'status': 'error', 'action': 'check_in',
                        'more_info': 'You do not have permissions to perform this action...'})

    if request.args.get('mlh_id') is None:
        return jsonify({'status': 'error', 'action': 'check_in', 'more_info': 'Missing required field...'})

    # See if hacker was already checked in...
    checked_in = db.session.query(Hacker.checked_in).filter(
        Hacker.mlh_id == request.args.get('mlh_id')).one_or_none()

    print(db.session.query(Hacker.checked_in).filter(Hacker.mlh_id == request.args.get('mlh_id')))
    print(checked_in)
    if checked_in and checked_in[0]:
        return jsonify({'status': 'error', 'action': 'check_in', 'more_info': 'Hacker already checked in!'})

    # Update db...
    db.session.query(Hacker).filter(Hacker.mlh_id == request.args.get('mlh_id')).update({'checked_in': True})
    db.session.commit()

    mlh_info = get_mlh_user(request.args.get('mlh_id'))

    # Send a welcome email...
    msg = 'Dear ' + mlh_info['first_name'] + ',\n\n'
    msg += 'Thanks for checking in!\n'
    msg += 'We will start shortly, please check your dashboard for updates!\n'
    msg += 'Here are the slides with all the info: https://goo.gl/mGLDem\n'
    send_email(mlh_info['email'], 'HackWPI - Thanks for checking in', msg)

    return jsonify(
        {'status': 'success', 'action': 'check_in', 'more_info': '', 'id': request.args.get('mlh_id')})


@app.route('/drop', methods=['GET'])
def drop():
    mlh_id = request.args.get('mlh_id')
    # Drop a hacker's registration...
    if mlh_id is None:
        return jsonify({'status': 'error', 'action': 'drop', 'more_info': 'Missing required field...'})

    if not is_admin() and not is_self(mlh_id):
        return jsonify({'status': 'error', 'action': 'drop',
                        'more_info': 'You do not have permissions to perform this action...'})

    row = db.session.query(Hacker.checked_in, Hacker.waitlisted, Hacker.first_name, Hacker.last_name, Hacker.email).filter(
        Hacker.mlh_id == mlh_id).one_or_none()

    if row is None:
        return jsonify({'status': 'error', 'action': 'drop',
                        'more_info': 'Could not find hacker...'})

    (checked_in, waitlisted, first_name, last_name, email) = row

    if checked_in:
        return jsonify({'status': 'error', 'action': 'drop', 'more_info': 'Cannot drop, already checked in...'})

    # mlh_info = get_mlh_user(request.args.get('mlh_id'))
    print(first_name + " trying to drop.")


    # Delete from db...
    row = db.session.query(Hacker).filter(Hacker.mlh_id == request.args.get('mlh_id')).first()
    db.session.delete(row)
    db.session.commit()

    # Delete resume...
    for ext in ALLOWED_EXTENSIONS:
        filename = first_name.lower() + '_' + last_name.lower() + '_' + mlh_id + '.' + ext
        try:
            os.remove(app.config['UPLOAD_FOLDER'] + '/' + filename)
        except OSError:
            pass

    # Send a goodbye email...
    msg = 'Dear ' + first_name + ',\n\n'
    msg += 'Your application was dropped, sorry to see you go.\n If this was a mistake, you can re-register by going to hack.wpi.edu/register'
    send_email(email, 'Hack@WPI - Application Dropped', msg)


    print(first_name + " dropped successfully.")
    if is_self(mlh_id):
        session.clear()
        return redirect('https://hack.wpi.edu')

    return jsonify({'status': 'success', 'action': 'drop', 'more_info': '', 'id': mlh_id})


@app.route('/promote_from_waitlist', methods=['GET'])
def promote_from_waitlist():
    print("Time for promotion!")
    # Promote a hacker from the waitlist...
    if request.args.get('mlh_id') is None:
        return jsonify({'status': 'error', 'action': 'promote_from_waitlist', 'more_info': 'Missing required field...'})

    (key, val) = get_auto_promote_keys()

    if request.args.get(key) is None:
        if not is_admin():
            return jsonify({'status': 'error', 'action': 'promote_from_waitlist',
                            'more_info': 'You do not have permissions to perform this action...'})
    else:
        if request.args.get(key) != val:
            return jsonify({'status': 'error', 'action': 'promote_from_waitlist',
                            'more_info': 'Invalid auto promote keys...'})

    (checked_in, waitlisted) = db.session.query(Hacker.checked_in, Hacker.waitlisted).filter(
        Hacker.mlh_id == request.args.get('mlh_id')).one_or_none()

    if checked_in:
        return jsonify(
            {'status': 'error', 'action': 'promote_from_waitlist',
             'more_info': 'Cannot promote, already checked in...'})

    if not waitlisted:
        return jsonify(
            {'status': 'error', 'action': 'promote_from_waitlist',
             'more_info': 'Cannot promote, user is not waitlisted...'})

    # Update db...
    db.session.query(Hacker).filter(Hacker.mlh_id == request.args.get('mlh_id')).update({'waitlisted': False})
    db.session.commit()

    mlh_info = get_mlh_user(request.args.get('mlh_id'))

    # Send a welcome email...
    msg = 'Dear ' + mlh_info['first_name'] + ',\n\n'
    msg += 'You are off the waitlist!\n'
    msg += 'Room has opened up, and you are now welcome to come, we look forward to seeing you!\n'
    msg += 'If you cannot make it, please remove yourself at hack.wpi.edu\dashboard.\n'
    send_email(mlh_info['email'], "Hack@WPI - You're off the Waitlist!", msg)


    print(mlh_info['first_name'] + "is off the waitlist!")

    return jsonify(
        {'status': 'success', 'action': 'promote_from_waitlist', 'more_info': '', 'id': request.args.get('mlh_id')})


@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Display's a hacker's options...
    if not is_logged_in():
        return redirect(url_for('register'))

    hacker = db.session.query(Hacker).filter(Hacker.mlh_id == session['mymlh']['id']).one_or_none()

    # In case application dropped but user not logged out properly
    if not hacker:
        session.clear()
        return redirect(url_for('register'))

    shirt_size = (hacker.shirt_size or 'None').upper()
    return render_template('dashboard.html', name=session['mymlh']['first_name'], id=session['mymlh']['id'],
                           admin=is_admin(), shirt_size=shirt_size, special_needs=hacker.special_needs)

@app.route('/tos', methods=['GET'])
def tos():
    return render_template('tos.html')


def is_logged_in():
    if session is None:
        return False
    if 'mymlh' not in session:
        return False
    return True


def is_admin():
    if not is_logged_in():
        return False
    user_admin = db.session.query(Hacker.admin).filter(Hacker.mlh_id == session['mymlh']['id']).one_or_none()
    if user_admin is None:
        return False
    if not user_admin[0]:
        return False
    return True


def is_self(mlh_id):
    mlh_id = int(mlh_id)
    if not is_logged_in():
        return False
    if session['mymlh']['id'] != mlh_id:
        return False
    return True


def send_email(to, subject, body):
    print("Email sent to: " + to)
    body += '\nPlease let your friends know about the event as well!\n'
    body += 'To update your status, you can go to hack.wpi.edu/dashboard\n'
    body += '\nAll the best!\nThe HackWPI Team\nhttps://twitter.com/hackwpi?lang=en'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    sender = api_keys['smtp_email']['user']
    server.login(sender, api_keys['smtp_email']['pass'])

    msg = _create_MIMEMultipart(subject, sender, to, body)

    server.send_message(msg)
    print("Sucess! (Email to " + to)


def _create_MIMEMultipart(subject, sender, to, body):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    if type(to) == list:
        msg['To'] = ", ".join(to)
    else:
        msg['To'] = to
    msg.attach(MIMEText(body, 'plain'))
    return msg


def get_mlh_user(mlh_id):
    if not isinstance(mlh_id, int):
        mlh_id = int(mlh_id)
    req = requests.get(
        'https://my.mlh.io/api/v3/users.json?client_id=' + api_keys['mlh']['client_id'] + '&secret=' + api_keys['mlh'][
            'secret'])
    if req.status_code == 200:
        hackers = req.json()['data']
        for hacker in hackers:
            if hacker['id'] == mlh_id:
                return hacker


def get_mlh_users():
    page_index = 1
    num_pages = 1
    users = []
    while page_index <= num_pages:
        req = requests.get('https://my.mlh.io/api/v3/users.json?client_id={client_id}&secret={secret}&page={page}'.format(
            client_id=api_keys['mlh']['client_id'],
            secret=api_keys['mlh']['secret'],
            page=page_index
        ))
        if req.status_code == 200:
            users += req.json()['data']
            num_pages = req.json()['pagination']['total_pages']
        page_index += 1

    return users if users else None


def gen_new_auto_promote_keys(n=50):
    key = new_key(n)
    val = new_key(n)
    db.session.add(AutoPromoteKeys(key=key, val=val))
    db.session.commit()
    return (key, val)


def get_auto_promote_keys():
    row = db.session.query(AutoPromoteKeys).one_or_none()
    if row is not None:
        db.session.delete(row)
        db.session.commit()
        return (row.key, row.val)
    else:
        return ('', '')


def new_key(n):
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(n))


def allowed_file(filename):
    return '.' in filename and \
           filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(host=SERVER_LISTEN_ADDR, port=SERVER_PORT, threaded=True)
    
