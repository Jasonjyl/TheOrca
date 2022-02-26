from sqlalchemy import Column, Integer, String

from extends import db


class User(db.Model):
    __tablename__ = 'user'

    """
    Integer     int
    String(15)  varchar(15)
    Datetime    datetime
    """

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(15), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # save the password encrypted with the built-in function in werkzeug
    emailaddr = Column(String(40), unique=True, nullable=False)

    # works
    works = db.relationship('Works', backref='user')
    # comments_id
    comments = db.relationship('Comment', backref='user')

    def __str__(self):
        # info = 'This is a user named:....' # we can use this way to make an info string of the user
        return '<class User ---> name: ' + self.username + ' >'


class Censor(db.Model):
    __tablename__ = 'censor'

    id = Column(Integer, primary_key=True, autoincrement=True)
    censor_name = Column(String(15), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    emailaddr = Column(String(40), unique=True, nullable=False)

    works = db.relationship('Works', backref='censor')

    def __str__(self):
        return '<class Censor ---> name: ' + self.censor_name + ' >'
