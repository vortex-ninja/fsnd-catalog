from flask import Flask, render_template, url_for, redirect, flash
from flask import jsonify, request
from flask import session as login_session
from flask_bootstrap import Bootstrap
from forms import CreateCategoryForm, EditCategoryForm, DeleteForm
from forms import AddItemForm, EditItemForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import random
import string
import httplib2
import json

app = Flask(__name__)
Bootstrap(app)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Get client id from json secret file

with open('client_secrets.json', 'r') as f:
    CLIENT_ID = json.loads(f.read())['web']['client_id']



@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=login_session['state'])

@app.route('/gconnect', methods=['POST', 'GET'])
def gconnect():

    # This view returns values to ajax call made from login.html
    # All return values are therefore strings and not Response objects

    # CSRF protection
    if request.args.get('state') != login_session['state']:
        return 'Invalid state parameter'

    # Get code sent by ajax request from login.html signInCallback function
    code = request.data

    try:
        # Create flow object from client_secrets.json

        flow = flow_from_clientsecrets('client_secrets.json',
                                       scope='',
                                       redirect_uri='postmessage')

        # Exchange an authorization code for a Credentials object
        credentials = flow.step2_exchange(code)

    except FlowExchangeError:
        return 'Login error: failed to exchange authorization code'


    # Check that the access token is valid

    h = httplib2.Http()
    access_token = credentials.access_token
    url = credentials.token_info_uri + '?access_token={}'.format(access_token)



    content = h.request(url)[1].decode('utf-8')
    content = json.loads(content)


    error = content.get('error_description')
    if error is not None:
        return error

    # Verify that the access token is used for the intended user

    gplus_id = credentials.id_token['sub']

    if gplus_id != content['sub']:
        return "Token's user ID doesn't match given user ID."

    # Verify that token was issued to the right application

    if content['aud'] != CLIENT_ID:
        return "Token's client ID doesn't match app's."


    # Verify that user is not already logged in

    stored_credentials = login_session.get('credentials')
    stored_gplusid = login_session.get('gplus_id')

    if stored_credentials is not None and stored_gplusid is not None:
        return 'User already logged in.'


    # Store the access token for later use

    login_session['credentials'] = credentials.to_json()
    login_session['gplus_id'] = gplus_id
    login_session['provider'] = 'google'

    # Get user info

    api_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    h = httplib2.Http()
    userinfo_url = api_url + '?access_token={}'.format(access_token)
    data = h.request(userinfo_url)[1].decode('utf-8')
    data = json.loads(data)

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    user_id = getUserID(login_session['email'])

    if user_id is None:
        user_id = createUser(login_session)

    login_session['user_id'] = user_id

    return 'Login Successfull.'

@app.route('/gdisconnect')
def gdisconnect():
    credentials = login_session.get('credentials')
    if credentials is None:
        flash("You're not logged in.")
        return redirect(url_for('mainPage'))


    # revoke_url = credentials['revoke_uri']
    # access_token = credentials['access_token']
    # url = '{}?token={}'.format(revoke_url, access_token)
    # h = httplib2.Http()
    # result = h.request(url)[0]

    del login_session['credentials']
    del login_session['gplus_id']
    del login_session['provider']
    del login_session['username']
    del login_session['email']
    del login_session['user_id']

    flash("You've been logged out.")
    return redirect(url_for('mainPage'))


@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    items = session.query(Item).limit(10)
    if not categories and not items:
        flash('No items to show')
    return render_template('main.html', categories=categories, items=items)


@app.route('/category/new', methods=['GET', 'POST'])
def newCategory():
    form = CreateCategoryForm()

    # validate_on_submit checks whether it's a POST request and if data is valid
    if form.validate_on_submit():
        new_category = Category(name=form.name.data)
        session.add(new_category)
        session.commit()
        flash('New category created.')
        return redirect(url_for('mainPage'))

    return render_template('newcategory.html', form=form)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):

    form = EditCategoryForm()
    category = session.query(Category).filter_by(id=category_id).one()
    if form.validate_on_submit():
        category.name = form.name.data
        session.commit()
        flash('Category successfully edited.')
        return redirect(url_for('mainPage'))

    return render_template('editcategory.html',
                           form=form,
                           name=category.name)


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    form = DeleteForm()
    category = session.query(Category).filter_by(id=category_id).one()
    if form.validate_on_submit():
        session.delete(category)
        session.commit()
        flash('Category successfully deleted')
        return redirect(url_for('mainPage'))

    return render_template('deletecategory.html',
                           form=form,
                           name=category.name)


@app.route('/category/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if not items or not category:
        flash("Category is empty or doesn't exist.")
    return render_template('showcategory.html', category=category, items=items)


@app.route('/category/<int:category_id>/items/new', methods=['GET', 'POST'])
def newItem(category_id):
    form = AddItemForm()
    category = session.query(Category).filter_by(id=category_id).one()

    if form.validate_on_submit():
        item = Item(name=form.name.data,
                    description=form.description.data,
                    category=category)
        session.add(item)
        session.commit()
        flash('New item created.')
        return redirect(url_for('showCategory', category_id=category_id))

    return render_template('newitem.html',
                           form=form,
                           category=category)


@app.route('/category/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    form = EditItemForm()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if form.validate_on_submit():  # How to assign values more consicely (setattr?)
        item.name = form.name.data
        item.description = form.description.data

        session.commit()
        flash('Item successfully edited.')
        return redirect(url_for('showCategory', category_id=category_id))

    form.name.data = item.name
    form.description.data = item.description

    return render_template('edititem.html',
                           form=form,
                           category=category,
                           item=item)


@app.route('/category/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    form = DeleteForm()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if form.validate_on_submit():
        session.delete(item)
        session.commit()
        flash('Item successfully deleted.')
        return redirect(url_for('showCategory', category_id=category_id))

    return render_template('deleteitem.html',
                           form=form,
                           category=category,
                           item=item)

@app.route('/category/<int:category_id>/items/<int:item_id>')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    return render_template('showitem.html', item=item)


# @app.route('/categorys/JSON')
# def categorysJSON():
#     categorys = session.query(Category).all()
#     return jsonify(Categorys=[r.serialize for r in categorys])


# @app.route('/category/<int:category_id>/menu/JSON')
# def menusJSON(category_id):
#     menus = session.query(Item).filter_by(category_id=category_id).all()
#     return jsonify(Items=[menu.serialize for menu in menus])


# @app.route('/category/<int:category_id>/menu/<int:item_id>/JSON')
# def menuItemJSON(category_id, item_id):
#     menu = session.query(Item).filter_by(id=item_id).one_or_none()
#     return jsonify(Item=[menu.serialize])


# User functions

def getUserID(email):
    return session.query(User.id).filter_by(email=email).scalar()

def createUser(login_session):
    new_user = User(name=login_session['username'], email=login_session['email'])
    session.add(new_user)
    session.commit()
    return new_user.id




if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
