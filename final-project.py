from flask import Flask, render_template, url_for, request, redirect
from flask_bootstrap import Bootstrap
from forms import CreateResForm, EditResForm, DeleteForm
from forms import AddMenuItemForm, EditMenuItemForm

app = Flask(__name__)
Bootstrap(app)


#Fake Restaurants
restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]


#Fake Menu Items
items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    form = CreateResForm()
    if form.validate_on_submit():  # checks whether it's a POST request and if data is valid
        pass

    return render_template('newrestaurant.html', form=form)


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    form = EditResForm()
    if form.validate_on_submit():
        pass

    print(restaurant_id)
    for r in restaurants:
        if r['id'] == str(restaurant_id):
            name = r['name']
    return render_template('editrestaurant.html', form=form, name=name)


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    form = DeleteForm()
    if form.validate_on_submit():
        pass

    for r in restaurants:
        if r['id'] == str(restaurant_id):
            name = r['name']
    return render_template('deleterestaurant.html', form=form, name=name)


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    return render_template('menu.html', restaurant_id=restaurant_id, items=items)


@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    form = AddMenuItemForm()
    if form.validate_on_submit():
        pass

    for r in restaurants:
        if r['id'] == str(restaurant_id):
            name = r['name']
    return render_template('newmenuitem.html',
                           form=form,
                           name=name,
                           restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    form = EditMenuItemForm()
    form.course.data = 'Beverage'
    if form.validate_on_submit():
        pass

    for r in restaurants:
        if r['id'] == str(restaurant_id):
            name = r['name']
    return render_template('editmenuitem.html',
                           form=form,
                           restaurant=name,
                           menu_item='gryzka',
                           restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    form = DeleteForm()
    if form.validate_on_submit():
        pass

    for r in restaurants:
        if r['id'] == str(restaurant_id):
            name = r['name']
    return render_template('deletemenuitem.html',
                           form=form,
                           menu_item='gryzka',
                           restaurant_id=restaurant_id)


if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5001)
