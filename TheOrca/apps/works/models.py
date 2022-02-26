from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Text

from extends import db


class Works(db.Model):
    __tablename__ = 'works'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(20), nullable=False)
    description = Column(String(100))
    upload_time = Column(DateTime, default=datetime.now)
    post_time = Column(DateTime)
    text = Column(String(100))  # 图片上的简短文字，可为空
    # 下面两项酌情考虑吧
    # recommend = Column(Integer, default=0)  # just as like_num
    # read = Column(Integer, default=0)
    photos = Column(JSON, nullable=False)
    editor_id = Column(Integer, ForeignKey('user.id'))
    censor_id = Column(Integer, ForeignKey('censor.id'))
    checked = Column(Integer, default=0)

    comments = db.relationship('Comment', backref='works')
    works_tag = db.relationship('Works_tag', backref='works')

    def __str__(self):
        return '<class Works ---> title: ' + self.title + ' >'


class Tag(db.Model):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(4), nullable=False)

    works_tag = db.relationship('Works_tag', backref='tag')

    def __str__(self):
        return '<class Tag ---> name: ' + self.tag_name + ' >'


class Works_tag(db.Model):
    """
    about the relationship between works and tags(many to many)
    """
    __tablename__ = 'works_tag'

    id = Column(Integer, primary_key=True, autoincrement=True)

    works_id = Column(Integer, ForeignKey('works.id'))
    tag_id = Column(Integer, ForeignKey('tag.id'))

    def __str__(self):
        return '<class Works_tag ---> serial number: ' + self.id + ' >'


class Comment(db.Model):
    __tablename__ = 'comment'

    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    works_id = Column(Integer, ForeignKey('works.id'))

    def __str__(self):
        return '<class Comment ---> name: ' + self.content + ' >'
