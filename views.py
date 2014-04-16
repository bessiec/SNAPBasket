
import os
from flask import Flask, render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from forms import LoginForm, EditForm, PostForm
from models import User, ROLE_USER, ROLE_ADMIN, Post
from datetime import datetime
import models
import logging

app = Flask(__name__)

lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

basedir = os.path.abspath(os.path.dirname(__file__))
oid = OpenID(app, os.path.join(basedir, 'tmp'))


app.csrf_enabled = True
app.secret_key = "rainbowssunshineunicorns2512351"


#CSRF_ENABLED setting activates the cross-site request forgery prevention.
#Secret key is used to create a cryptographic token that is used to validate a form.

OPENID_PROVIDERS = [
    { 'name': 'Google', 'url': 'https://www.google.com/accounts/o8/id' },
    { 'name': 'Yahoo', 'url': 'http://me.yahoo.com' },
    { 'name': 'AOL', 'url': 'http://openid.aol.com/<username>' },
    { 'name': 'Flickr', 'url': 'http://www.flickr.com/<username>' },
    { 'name': 'MyOpenID', 'url': 'http://www.myopenid.com' }]



SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

#The SQLALCHEMY_DATABASE_URI is the path of our database file.
#The SQLALCHEMY_MIGRATE_REPO is the folder in which we will store the SQLAlchemy-migrate data files



@app.errorhandler(404)
def internal_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    models.session.rollback()
    return render_template('500.html'), 500


@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user
    if g.user.is_authenticated():
        g.user.last_seen = datetime.utcnow()
        models.session.add(g.user)
        models.session.commit()

"""The following handlers have to do with the content 
on the company page"""

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

#Handlers for snap info

@app.route('/snap')
def snap():
    return render_template('whatissnap.html')

@app.route('/snap_statistics')
def snap_statistics():
    return render_template('snap_statistics.html')

#Handlers for the About Us Section

@app.route('/story')
def story():
    return render_template('our_story.html')

@app.route('/team')
def team():
    return render_template('about_us.html')


@app.route('/contact')
def contact():
    return render_template('contact_us.html')


#The following handlers below all have to do with the prototype 

@app.route('/demo', methods = ['GET', 'POST'])
@app.route('/demo/<int:page>', methods = ['GET', 'POST'])
@login_required
def demo(page = 1):
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body = form.post.data, timestamp = datetime.utcnow(), author = g.user)
        models.session.add(post)
        models.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('demo'))
    posts = g.user.posts
    return render_template('demo.html',
        title = 'Demo',
        form = form,
        posts = posts)


# @app.route('/demo_faq')
# def index():
#     return render_template('demo_faq.html')

@app.route('/login', methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('demo'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', 
        title = 'Sign In',
        form = form,
        providers = OPENID_PROVIDERS)

@app.route('/edit', methods = ['GET', 'POST'])
@login_required
def edit():
    form = EditForm(g.user.nickname)
    if form.validate_on_submit():
        g.user.nickname = form.nickname.data
        g.user.about_me = form.about_me.data
        models.session.add(g.user)
        models.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit'))
    else:
        form.nickname.data = g.user.nickname
        form.about_me.data = g.user.about_me
    return render_template('edit.html',
        form = form)

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        nickname = User.make_unique_nickname(nickname)
        user = User(nickname = nickname, email = resp.email, role = ROLE_USER)
        models.session.add(user)
        models.session.commit()
        models.session.add(user.follow(user))
        models.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('demo'))
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember = remember_me)
    return redirect(request.args.get('next') or url_for('demo'))

@app.route('/user/<nickname>')
@login_required
def user(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('app'))
    posts = user.posts
    baskets = models.session.query(models.Baskets).filter_by(user_id = g.user.id).all()
    return render_template('user.html',
        user = user,
        posts = posts,
        baskets = baskets)



@app.route('/smart_final')
def smart_final():
    smart_final_foods = models.session.query(models.Food).all()
    return render_template("smart_final.html")


@app.route('/follow/<nickname>')
def follow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t follow yourself!')
        return redirect(url_for('user', nickname = nickname))
    follow_user = g.user.follow(user)
    if follow_user is None:
        flash('Cannot follow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    session.add(follow_user)
    session.commit()
    flash('You are now following ' + nickname + '!')
    return redirect(url_for('user', nickname = nickname))

@app.route('/unfollow/<nickname>')
def unfollow(nickname):
    user = User.query.filter_by(nickname = nickname).first()
    if user == None:
        flash('User ' + nickname + ' not found.')
        return redirect(url_for('index'))
    if user == g.user:
        flash('You can\'t unfollow yourself!')
        return redirect(url_for('user', nickname = nickname))
    u = g.user.unfollow(user)
    if u is None:
        flash('Cannot unfollow ' + nickname + '.')
        return redirect(url_for('user', nickname = nickname))
    session.add(u)
    session.commit()
    flash('You have stopped following ' + nickname + '.')
    return redirect(url_for('user', nickname = nickname))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/shopping_lists')
def show_shoppinglists():
    baskets = models.session.query(models.Baskets).all()
    return render_template('shoppinglists.html', baskets = baskets) 

@app.route('/food_items')
def show_foods():
    all_items = models.session.query(models.Food).all()
    return render_template("food_items.html",all_items=all_items)

@app.route('/create_shoppinglist')
def create_shoppinglist():
    select_item = models.session.query(models.Food).all()
    return render_template("create_shoppinglist.html", select_item=select_item)

@app.route('/make_shoppinglist')
def make_shoppinglist():
    new_shoppinglist_name = request.args.get("shoppinglist_name")
    added_item = request.args.get("added_item")
    added_shoppinglist = models.Baskets(name=new_shoppinglist_name, user_id=g.user.id)
    models.session.add(added_shoppinglist) 
    models.session.commit()
    models.session.refresh(added_shoppinglist)

    counter = 0
    for argument in request.args:
        if argument[0:10] == "added_item":
            request.args[argument]
            new_basket_row = models.Basket_Entry(basket_id=added_shoppinglist.id,
                food_id=request.args[argument])
            counter += 1
            models.session.add(new_basket_row)
    models.session.commit()

    return render_template("shoppinglist_created.html")


#Handlers for Individual Stores in USC Area for MVP Example
#code not completed 

@app.route('/ralphs')
def ralphs():
    ralphs_foods = models.session.query(models.Food).all()
    return render_template("ralphs.html")


@app.route('/superior')
def superior():
    superior_foods = models.session.query(models.Food).all()
    return render_template("superior.html")

@app.route('/food4less')
def food_4_less():
    food_4_less = models.session.query(models.Food).all()
    return render_template("food4less.html")

@app.route('/fresh_easy')
def fresh_easy():
    fresh_easy_foods = models.session.query(models.Food).all()
    return render_template("fresh_easy.html")

@app.route('/smart_final')
def smart_final():
    smart_final_foods = models.session.query(models.Food).all()
    return render_template("smart_final.html")

@app.teardown_appcontext
def shutdown_session(exception=None):
    models.session.remove()
    


app.run(debug = True)