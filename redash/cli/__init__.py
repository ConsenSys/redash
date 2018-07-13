from __future__ import print_function
import json


import click
from flask.cli import FlaskGroup, run_command
from flask import current_app, url_for

from redash import create_app, settings, __version__
from redash.cli import users, groups, database, data_sources, organization, photic
from redash.monitor import get_status


def create(group):
    app = current_app or create_app()
    group.app = app

    @app.shell_context_processor
    def shell_context():
        from redash import models
        return dict(models=models)

    return app


@click.group(cls=FlaskGroup, create_app=create)
def manager():
    """Management script for Redash"""


manager.add_command(database.manager, "database")
manager.add_command(users.manager, "users")
manager.add_command(groups.manager, "groups")
manager.add_command(data_sources.manager, "ds")
manager.add_command(organization.manager, "org")
manager.add_command(photic.manager, "photic")
manager.add_command(run_command, "runserver")


@manager.command()
def version():
    """Displays Redash version."""
    print(__version__)


@manager.command()
def status():
    print(json.dumps(get_status(), indent=2))


@manager.command()
def check_settings():
    """Show the settings as Redash sees them (useful for debugging)."""
    for name, item in settings.all_settings().iteritems():
        print("{} = {}".format(name, item))


@manager.command()
@click.argument('email', default=settings.MAIL_DEFAULT_SENDER, required=False)
def send_test_mail(email=None):
    """
    Send test message to EMAIL (default: the address you defined in MAIL_DEFAULT_SENDER)
    """
    from redash import mail
    from flask_mail import Message

    if email is None:
        email = settings.MAIL_DEFAULT_SENDER

    mail.send(Message(subject="Test Message from Redash", recipients=[email],
                      body="Test message."))


@manager.command()
def ipython():
    """Starts IPython shell instead of the default Python shell."""
    import sys
    import IPython
    from flask.globals import _app_ctx_stack
    app = _app_ctx_stack.top.app

    banner = 'Python %s on %s\nIPython: %s\nRedash version: %s\n' % (
        sys.version,
        sys.platform,
        IPython.__version__,
        __version__
    )

    ctx = {}
    ctx.update(app.make_shell_context())

    IPython.embed(banner1=banner, user_ns=ctx)


@manager.command()
def list_routes():
    from redash.wsgi import app
    for r in app.url_map.iter_rules():
        print(r)
