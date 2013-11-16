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
				price=food_row[3])
			session.add(new_food_row)
		session.commit()
		session.refresh(new_food_row)

def load_price_entries(session):
	with open ('stores.csv', 'rU') as f:
		filename_stores = csv.reader(f, delimiter=",")
		for storename_row in filename_stores:
			new_storename_row = models.Price_Entry(food_id=storename_row[1], store_id=storename_row[2])
			session.add(new_storename_row)
		session.commit()
		session.refresh(new_storename_row)


def load_stores(session):
	user = 1
	store_names = ["Ralphs", "Fresh and Easy Neighborhood Market", "Superior Super Warehouse", "Smart and Final"]
	for name in store_names:
		name = models.Stores(store_name=name)
		session.add(name)
	session.commit()

def main(session):
	load_food(session)
	load_price_entries(session)
	load_stores(session)

if __name__ == "__main__":
	main(s)