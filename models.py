from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy import ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from hashlib import md5
import flask.ext.whooshalchemy as whooshalchemy

engine = create_engine("sqlite:///app.db", echo=True)
session = scoped_session(sessionmaker(bind=engine,
										autocommit = False,
										autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

def create_db():
	Base.metadata.create_all(engine)

#Association class to tie food and prices to stores and other metadata
class Price_Entry(Base):
	__tablename__ = "price_entries"
	id = Column(Integer, primary_key = True)
	food_id = Column(integer, ForeignKey('food.id'))

class Food(Base):
	__tablename__ = "food"
	id = Column(Integer, primary_key = True)
	measurement = Column(String(140))
	measurement_amount = Column(Integer)
	name = Column(String(140))
	price = Column(Text)

class Stores(Base):
	__tablename__ = "stores"
	id = Column(Integer, primary_key = True)
	food_id = Column(Integer, ForeignKey('food.id'))
	price_entries = relationship('Price_Entry')
	store_name = Column(String(140))
	address = Column(Text)
	map_link = Column(Text)
	metro_stops = Column(Text)

class Prices(Base):
	__tablename__ = "prices"
	id = Column(Integer, primary_key = True)
	food_id = Column(Integer, ForeignKey('food.id'))
	store_id = Column(Integer, ForeignKey('stores.id'))
	price = Column(String(140))

#Seeding an initial user 
def main():
	user = User(nickname = 'bessie_tester', email = 'bessiechu@ymail.com')


if __name__ == "__main__":
	main()