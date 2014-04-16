from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from hashlib import md5
import flask.ext.whooshalchemy as whooshalchemy


engine = create_engine("sqlite:///app.db", echo=True)
session = scoped_session(sessionmaker(bind= engine,
                                        autocommit= False,
                                        autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

def create_db():
    Base.metadata.create_all(engine)

#figure out what this does
ROLE_USER = 0
ROLE_ADMIN = 1



followers = Table('user_followers', Base.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True)
    nickname = Column(String(64), unique = True)
    email = Column(String(120), unique = True)
    role = Column(SmallInteger, default = ROLE_USER)
    posts = relationship('Post', backref = 'author', lazy = 'dynamic')
    about_me = Column(String(140))
    last_seen = Column(DateTime)
    followed = relationship('User', 
        secondary = followers, 
        primaryjoin = (followers.c.follower_id == id), 
        secondaryjoin = (followers.c.followed_id == id), 
        backref = backref('followers', lazy = 'dynamic'), 
        lazy = 'dynamic')

    @staticmethod
    def make_unique_nickname(nickname):
        if User.query.filter_by(nickname = nickname).first() == None:
            return nickname
        version = 2
        while True:
            new_nickname = nickname + str(version)
            if User.query.filter_by(nickname = new_nickname).first() == None:
                break
            version += 1
        return new_nickname


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
        
    def __repr__(self):
        return '<User %r>' % (self.nickname)    

    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/' + md5(self.email).hexdigest() + '?d=mm&s=' + str(size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            return self
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            return self
            
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        return Post.query.join(followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id).order_by(Post.timestamp.desc())


class Post(Base):
    __tablename__ = "posts"
    __searchable__ = ['body']

    id = Column(Integer, primary_key = True)
    body = Column(String(140))
    timestamp = Column(DateTime)
    user_id = Column(Integer, ForeignKey('users.id'))

    def __repr__(self):
        return '<Post %r>' % (self.body)


class Basket_Entry(Base):
    __tablename__ = "basket_entries"
    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, ForeignKey('food.id'))
    basket_id = Column(Integer, ForeignKey('baskets.id'))
    baskets = relationship('Baskets', backref="basket_entries")
    food = relationship('Food', backref="basket_entries")
    
class Baskets(Base):
    __tablename__ = "baskets"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    basket_entry = relationship('Basket_Entry')
    name = Column(String(140))

class Food(Base):
    __tablename__ = "food"
    id = Column(Integer, primary_key=True)
    name = Column(String(140))
    brand = Column(String(140))
    store_name= Column(String(140))
    measurement = Column(String(140))
    price = Column(String(10))
    location = Column(Text)
    transit = Column(Text)


def main():
    user = User(nickname = 'beta_tester', email = 'bessiech@usc.edu')


if __name__ == "__main__":
    main()