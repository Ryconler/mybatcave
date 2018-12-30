#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from app import create_app,db
from app.models import User
from flask_script import Manager,Shell
from flask_migrate import Migrate,MigrateCommand

app=create_app(os.getenv('FLASK_CONFIG')or 'default')
manager=Manager(app)
migrate=Migrate(app,db)

def make_shell_context():
    return dict(app=app, db=db, User=User)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)



@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade,init,migrate
    from app.models import UrlResource, User
    # migrate database to latest revision


@manager.command
def clearAlembic():
    from flask_migrate import upgrade
    from app.models import Alembic
    Alembic.clear_A()



if __name__=='__main__':
    manager.run()