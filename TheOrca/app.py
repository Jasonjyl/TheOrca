from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from apps import create_app
from extends import db

app = create_app()

manager = Manager(app=app)  # just like a shell

# command tools
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
