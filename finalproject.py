from flask import Flask, render_template, url_for, redirect, flash
from flask import jsonify, request
from flask import session as login_session
from flask_bootstrap import Bootstrap
from forms import CreateCategoryForm, EditCategoryForm, DeleteForm
from forms import AddItemForm, EditItemForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import OAuth2Credentials
from functools import wraps
from database_funcs import is_owner_item, is_owner_category, item_exists
from database_funcs import category_exists, getUserID
from database_funcs import createUser, updateUser, get_name
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


# Decorators to check whether user is logged in,
# is owner of an item or category and whether item or category exists


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            flash('You have to be logged in to use this functionality')
            return redirect(url_for('mainPage'))
        return f(*args, **kwargs)
    return decorated_function


def category_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not category_exists(kwargs['category_id']):
            flash("Category doesn't exist.")
            return redirect(url_for('mainPage'))
        return f(*args, **kwargs)
    return decorated_function


def item_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not item_exists(kwargs['item_id']):
            flash("Item doesn't exist.")
            return redirect(url_for('mainPage'))
        return f(*args, **kwargs)
    return decorated_function


def category_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_owner_category(getUserID(login_session['email']),
                                 kwargs['category_id']):
            flash("You don't have permissions to do that.")
            return redirect(url_for('mainPage'))
        return f(*args, **kwargs)
    return decorated_function


def item_owner_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_owner_item(getUserID(login_session['email']),
                             kwargs['item_id']):
            flash("You don't have permissions to do that.")
            return redirect(url_for('mainPage'))
        return f(*args, **kwargs)
    return decorated_function


# Views

@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    items = session.query(Item).order_by(Item.date_created.desc()).limit(10)
    user_id = get_logged_in_ID()

    if not categories and not items:
        flash('No items to show')

    return render_template('main.html',
                           categories=categories,
                           items=items,
                           user_id=user_id)


@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def newCategory():

    if not is_logged_in():
        flash('You have to be logged in to add a category')
        return redirect(url_for('mainPage'))
    else:
        form = CreateCategoryForm()

        # validate_on_submit checks whether it's a POST request and if data is valid
        if form.validate_on_submit():
            new_category = Category(name=form.name.data,
                                    user_id=getUserID(login_session['email']))
            session.add(new_category)
            session.commit()
            flash('New category created.')
            return redirect(url_for('mainPage'))

        return render_template('newcategory.html',
                               form=form)


@app.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@category_required
@login_required
@category_owner_required
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
                           username=get_logged_in_username())


@app.route('/category/<int:category_id>/delete', methods=['GET', 'POST'])
@category_required
@login_required
@category_owner_required
def deleteCategory(category_id):
    form = DeleteForm()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    if form.validate_on_submit():
        session.delete(category)

        # Deletes items in a deleted category
        for item in items:
            session.delete(item)
        session.commit()
        flash('Category successfully deleted')
        return redirect(url_for('mainPage'))

    return render_template('deletecategory.html',
                           form=form,
                           name=category.name)


@app.route('/category/<int:category_id>')
def showCategory(category_id):
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    items = session.query(Item).filter_by(category_id=category_id)
    items = items.order_by(Item.date_created.desc()).all()

    user_id = get_logged_in_ID()

    if category is None:
        flash("Category doesn't exist.")
        return redirect(url_for('mainPage'))

    return render_template('showcategory.html',
                           category=category,
                           items=items,
                           user_id=user_id)


@app.route('/items/new', methods=['GET', 'POST'])
@login_required
def newItem():

    categories = session.query(Category).all()

    # Add a dynamically assigned list to the form's SelectField
    choices = [(category.id, category.name) for category in categories]
    form = AddItemForm()
    form.category.choices = choices

    if form.validate_on_submit():
        new_item = Item(name=form.name.data,
                        description=form.description.data,
                        category_id=form.category.data,
                        user_id=get_logged_in_ID())
        session.add(new_item)
        session.commit()

        flash('New item created.')
        return redirect(url_for('showCategory', category_id=new_item.category_id))

    return render_template('newitem.html', form=form)


@app.route('/category/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
@item_required
@login_required
@item_owner_required
def editItem(category_id, item_id):

    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    form = EditItemForm(obj=item)  # obj=item populates fields with item's values

    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        session.commit()

        flash('Item successfully edited.')
        return redirect(url_for('showCategory',
                                category_id=category_id))

    return render_template('edititem.html',
                           form=form,
                           category=category,
                           item=item)


@app.route('/category/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
@item_required
@login_required
@item_owner_required
def deleteItem(category_id, item_id):
    form = DeleteForm()
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()

    if form.validate_on_submit():
        session.delete(item)
        session.commit()
        flash('Item successfully deleted.')
        return redirect(url_for('showCategory',
                                category_id=category_id))

    return render_template('deleteitem.html',
                           form=form,
                           category=category,
                           item=item)


@app.route('/category/<int:category_id>/items/<int:item_id>')
def showItem(category_id, item_id):
    item = session.query(Item).filter_by(id=item_id).one_or_none()
    category = session.query(Category).filter_by(id=category_id).one_or_none()
    return render_template('showitem.html',
                           item=item,
                           category=category)


# OAuth2 views and functions


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

            if user_id is None:
                # Create user in a database
                createUser(login_session)
            else:
                # Update user details from google api call

                updateUser(login_session)

            flash("You're logged in as {}.".format(login_session['username']))

        return redirect(url_for('mainPage'))


@app.route('/oauth2callback')
def oauth2callback():

    # As per advice from Google this view doesn't render any html in order not
    # to reveal any query parameters in the url (like state token, or auth code)
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
        return redirect(auth_uri)

    else:
        # Check if the state token returned in the response
        # is the same as one saved in login_session
        if request.args.get('state', '') != login_session['state']:
            return redirect(url_for('auth_error',
                                    error="CSRF tokens don't match!"))

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

        return redirect(url_for('login'))


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

    return redirect(url_for('mainPage'))


@app.route('/auth_error')
def auth_error():
    error = request.args.get('error')
    return render_template('error.html', error=error)


# Access token validation

def validate_access_token(credentials):

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

    if CLIENT_ID != content['aud']:
        return "Token's client ID doesn't match app's."

    # Verify that the access token is used for the intended user

    if credentials.id_token['sub'] != content['sub']:
        return "Token's client ID doesn't match app's."

    return None


# JSON endpoints

@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(categories=[category.serialize for category in categories])


@app.route('/category/<int:category_id>/items/JSON')
def itemsJSON(category_id):
    items = session.query(Item).filter_by(category_id=category_id).all()
    return jsonify(items=[item.serialize for item in items])


# Helper functions


def is_logged_in():
    return 'email' in login_session


def get_logged_in_ID():
    if is_logged_in():
        return getUserID(login_session['email'])
    else:
        return None


def get_logged_in_username():
    if 'username' in login_session:
        return login_session['username']
    else:
        return ''


# Makes functions available in templates

@app.context_processor
def utility_processor():
    return dict(is_logged_in=is_logged_in,
                is_owner_item=is_owner_item,
                is_owner_category=is_owner_category,
                get_logged_in_username=get_logged_in_username,
                get_name=get_name)


# Starts flask server

if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
