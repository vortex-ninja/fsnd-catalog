from flask import Flask, render_template, url_for, redirect, flash
from flask import jsonify, request
from flask import session as login_session
from flask_bootstrap import Bootstrap
from forms import CreateCategoryForm, EditCategoryForm, DeleteForm
from forms import AddItemForm, EditItemForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2Credentials
import httplib2
import json
import os
import hashlib

app = Flask(__name__)
Bootstrap(app)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Get client id from json secret file

with open('client_secrets.json', 'r') as f:
    CLIENT_ID = json.loads(f.read())['web']['client_id']


@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    items = session.query(Item).limit(10)
    if not categories and not items:
        flash('No items to show')
    return render_template('main.html',
                           categories=categories,
                           items=items,
                           username=logged_in_name())


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

    return render_template('newcategory.html',
                           form=form,
                           username=logged_in_name())


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
                           name=category.name,
                           username=logged_in_name())


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
                           name=category.name,
                           username=logged_in_name())


@app.route('/category/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id).all()
    if not items or not category:
        flash("Category is empty or doesn't exist.")
    return render_template('showcategory.html',
                           category=category,
                           items=items,
                           username=logged_in_name())


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
        return redirect(url_for('showCategory',
                                category_id=category_id,
                                username=logged_in_name()))

    return render_template('newitem.html',
                           form=form,
                           category=category,
                           username=logged_in_name())


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
        return redirect(url_for('showCategory',
                                category_id=category_id,
                                username=logged_in_name()))

    form.name.data = item.name
    form.description.data = item.description

    return render_template('edititem.html',
                           form=form,
                           category=category,
                           item=item,
                           username=logged_in_name())


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
        return redirect(url_for('showCategory',
                                category_id=category_id,
                                username=logged_in_name()))

    return render_template('deleteitem.html',
                           form=form,
                           category=category,
                           item=item,
                           username=logged_in_name())


@app.route('/category/<int:category_id>/items/<int:item_id>')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    return render_template('showitem.html',
                           item=item,
                           username=logged_in_name())


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

@app.route('/login')
def login():
    if 'credentials' not in login_session:
        return redirect(url_for('oauth2callback'))
    credentials = OAuth2Credentials.from_json(login_session['credentials'])

    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))
    else:

        # Check if the user is already logged in

        if 'gplus_id' in login_session:
            flash("You're already logged in.")
        else:
            login_session['gplus_id'] = credentials.id_token['sub']

            # Make an API call to user_info endpoint to get more data about the user

            h = httplib2.Http()
            api_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
            url = '{}?access_token={}'.format(api_url, credentials.access_token)

            response, content = h.request(url)
            content = json.loads(content.decode('utf-8'))



            # Save user data to login session

            login_session['email'] = content['email']
            login_session['username'] = content['name']

            # Check whether user is registered in a database

            user_id = getUserID(login_session['email'])
            print('EMAIL : ' + login_session['email'])
            print('USER_ID: ' + str(user_id))

            if user_id is None:
                # Create user in a database
                createUser(login_session)
            else:
                # Update user details from google api call

                updateUser(login_session)

            flash("You're logged in as {}.".format(login_session['username']))

        return redirect(url_for('mainPage', username=logged_in_name()))


@app.route('/oauth2callback')
def oauth2callback():

    # As per advice from Google this view doesn't render any html in order not to
    # reveal any query parameters in the url (like state token, or auth code)
    # It only redirects to other views

    flow = flow_from_clientsecrets('client_secrets.json',
                                   scope='openid email',
                                   redirect_uri=url_for('oauth2callback',
                                                        _external=True))

    if 'code' not in request.args:

        # CSRF protection
        state = hashlib.sha256(os.urandom(1024)).hexdigest()
        login_session['state'] = state
        flow.params['state'] = state

        auth_uri = flow.step1_get_authorize_url()

        print('AUTH URI: ')
        print(auth_uri)

        return redirect(auth_uri)
    else:
        # Check if the state token returned in the response
        # is the same as one saved in login_session
        if request.args.get('state', '') != login_session['state']:
            return redirect(url_for('auth_error',
                                    error="CSRF tokens don't match!",
                                    username=logged_in_name()))

        # Get the auth code from request's arguments

        auth_code = request.args.get('code')

        # Exchange auth code for a credentials object
        credentials = flow.step2_exchange(auth_code)

        # Token validation
        error = validate_access_token(credentials)

        # if there are errors in validation redirect to an error page
        if error is not None:
            return redirect(url_for('auth_error', error=error))

        # Save credentials object
        login_session['credentials'] = credentials.to_json()

        return redirect(url_for('login', username=logged_in_name()))


@app.route('/logout')
def logout():
    if 'credentials' in login_session and 'gplus_id' in login_session:
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['email']
        del login_session['username']
        flash("You've been logged out")
    else:
        flash("You're not logged in")

    return redirect(url_for('mainPage', username=logged_in_name()))


@app.route('/auth_error')
def auth_error():
    return request.args.get('error')

# Access token validation


def validate_access_token(credentials):

    # credentials = OAuth2Credentials.from_json(login_session['credentials'])
    http_auth = httplib2.Http()
    token_info_uri = credentials.token_info_uri
    access_token = credentials.access_token
    url = '{}?access_token={}'.format(token_info_uri, access_token)

    response, content = http_auth.request(url)
    content = json.loads(content.decode('utf-8'))

    # Check for errors in a call to token info uri

    if 'error' in response:
        return response.get('error')

    # Verify that token was issued to the right application

    print('CLIENT ID: ' + CLIENT_ID)
    print("content['aud']: " + content['aud'])



    if CLIENT_ID != content['aud']:
        return "Token's client ID doesn't match app's."

    # Verify that the access token is used for the intended user

    if credentials.id_token['sub'] != content['sub']:
        return "Token's client ID doesn't match app's."

    return None



# User functions

# Returns the name of a logged in user, otherwise returns an empty string
def logged_in_name():
    if 'username' in login_session:
        return login_session['username']
    else:
        return ''

def getUserID(email):
    return session.query(User.id).filter_by(email=email).scalar()

def createUser(login_session):
    new_user = User(name=login_session['username'], email=login_session['email'])
    session.add(new_user)
    session.commit()
    return new_user.id

def updateUser(login_session):
    email = login_session['email']
    username = login_session['username']

    user = session.query(User).filter_by(email=email).one_or_none()

    if user is not None:
        user.email = login_session['email']
        user.name = login_session['username']

    session.commit()




if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
