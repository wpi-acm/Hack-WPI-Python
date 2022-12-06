# GoatHacks Registration Management

This is a rewrite of the original (commit 198f56f2c47831c2f8c192fbb45a47f7b1fb4e5b)
management system for Flask 2.1 and Postgres. The focus was on maintainability
in the future and easy modifications for future years.

## Setting up a development environment
The `Makefile` should have a bunch of useful recipes for you. Once you clone the
repo for the first time, run `make init_env`, which will set up the virtual
environment for development. If the dependencies ever change, you can run `make
upgrade_env` to install the new packages.

To test your code, run `make daemon`, which will start a development server. It
will automatically reload after your changes.

## Setting up for production

You can use your choice of WSGI server. Instructions are provided below for
uWSGI. Please ensure a current (3.x) version of Python and Pip.

1. pip install uwsgi # or the equivalent for your distribution's package manager
2. mkdir -p /etc/uwsgi/apps-available
3. mkdir -p /var/log/uwsgi
4. sudo chown -R nginx:nginx /var/log/uwsgi
5. mkdir -p /var/app
6. git clone https://github.com/WPI-ACM/Hack-WPI-Python /var/app/goathacks
7. cd /var/app/goathacks && make init_env
8. cp /var/app/goathacks/contrib/goathacks.ini /etc/uwsgi/apps-available/goathacks.ini
9. cp /var/app/goathacks/contrib/goathacks.service /etc/systemd/system/goathacks.service
10. cp /var/app/goathacks/goathacks/config.py.example /var/app/goathacks/goathacks/config.py
11. $EDITOR /var/app/goathacks/goathacks/config.py
