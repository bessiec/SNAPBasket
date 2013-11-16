#Database loader to take in initial dummy data 

import csv
import datetime
import models
from models import session
models.create_db()

s = models.session


def load_food(session):
	with open ('food.csv', 'rU') as f:
		filename_food = csv.reader(f, delimiter=",")
		for food_row in filename_food:
			new_food_row = models.Food(name=food_row[0], brand=food_row[1], measurement=food_row[2], 
				price=food_row[3], store_name=food_row[4], location=food_row[5], transit=food_row[6])
			session.add(new_food_row)
		session.commit()
		session.refresh(new_food_row)

def load_basket_entries(session):
	with open ('baskets.csv', 'rU') as f:
		filename_stores = csv.reader(f, delimiter=",")
		for basketname_row in filename_stores:
			new_basketname_row = models.Basket_Entry(food_id=basketname_row[1], basket_id=basketname_row[2])
			session.add(new_basketname_row)
		session.commit()
		session.refresh(new_basketname_row)


def load_baskets(session):
	user = 1
	basket_names = ["Example 1"]
	for name in basket_names:
		name = models.Baskets(name=name)
		session.add(name)
	session.commit()

def main(session):
	load_food(session)
	load_basket_entries(session)
	load_baskets(session)

if __name__ == "__main__":
	main(s)