# Hack@WPI 2018 Website
Used chronicel's registration system as a base but removed the need of mailchimp.

Rest is from their repo:

## Setup:
- Clone repo
- `pip3 install -r requirements.txt`
- Fill in all config files!
- Database: 
```sh
python3
```
```python
from flask_app import db
db.create_all()
```
- Automatic waitlist management setup: Setup your favorite cron like tool to run `python3 manage_waitlist.py` nightly!
- `python3 flask_app.py`
- 🎉 🔥 🙌 💃 👌 💯
