import os
from flask import Flask, render_template, request, flash, redirect, session, url_for, request, g
from flask.ext.sqlalchemy import SQLAlchemy


import models

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/index')
def index():
	return render_template('index.html')


app.run(debug = True)