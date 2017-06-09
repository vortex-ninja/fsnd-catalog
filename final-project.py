from flask import Flask, render_template, url_for, request, redirect, flash
from flask import jsonify
from flask_bootstrap import Bootstrap
from forms import CreateResForm, EditResForm, DeleteForm
from forms import AddMenuItemForm, EditMenuItemForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem

app = Flask(__name__)
Bootstrap(app)

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/restaurants')
def showRestaurants():
    restaurants = session.query(Restaurant).all()
    if not restaurants:
        flash('The restaurant list is empty.')
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/new', methods=['GET', 'POST'])
def newRestaurant():
    form = CreateResForm()

    # validate_on_submit checks whether it's a POST request and if data is valid
    if form.validate_on_submit():
        new_restaurant = Restaurant(name=form.name.data)
        session.add(new_restaurant)
        session.commit()
        flash('New restaurant created.')
        return redirect(url_for('showRestaurants'))

    return render_template('newrestaurant.html', form=form)


@app.route('/restaurant/<int:restaurant_id>/edit', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):

    form = EditResForm()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if form.validate_on_submit():
        restaurant.name = form.name.data
        session.commit()
        flash('Restaurant successfully edited.')
        return redirect(url_for('showRestaurants'))

    return render_template('editrestaurant.html', form=form, name=restaurant.name)


@app.route('/restaurant/<int:restaurant_id>/delete', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    form = DeleteForm()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    if form.validate_on_submit():
        session.delete(restaurant)
        session.commit()
        flash('Restaurant successfully deleted')
        return redirect(url_for('showRestaurants'))

    return render_template('deleterestaurant.html', form=form, name=restaurant.name)


@app.route('/restaurant/<int:restaurant_id>')
@app.route('/restaurant/<int:restaurant_id>/menu')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    if not items:
        flash('Menu item list is empty.')
    return render_template('menu.html', restaurant=restaurant, items=items)


@app.route('/restaurant/<int:restaurant_id>/menu/new', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    form = AddMenuItemForm()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()

    if form.validate_on_submit():
        item = MenuItem(name=form.name.data,
                        course=form.course.data,
                        description=form.description.data,
                        price=form.price.data,
                        restaurant_id=restaurant_id)
        session.add(item)
        session.commit()
        flash('New menu item created.')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('newmenuitem.html',
                           form=form,
                           restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET', 'POST'])
def editMenuItem(restaurant_id, menu_id):
    form = EditMenuItemForm()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    if form.validate_on_submit(): # How to assign values more consicely
        item.name = form.name.data
        item.course = form.course.data
        item.description = form.description.data
        item.price = form.price.data

        session.commit()
        flash('Menu item successfully edited.')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    form.name.data = item.name
    form.course.data = item.course
    form.description.data = item.description
    form.price.data = item.price

    return render_template('editmenuitem.html',
                           form=form,
                           restaurant=restaurant,
                           item=item)


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    form = DeleteForm()
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()

    if form.validate_on_submit():
        session.delete(item)
        session.commit()
        flash('Menu item successfully deleted.')
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))

    return render_template('deletemenuitem.html',
                           form=form,
                           restaurant=restaurant,
                           item=item)


@app.route('/restaurants/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(Restaurants=[restaurant.serialize for restaurant in restaurants])


@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def menusJSON(restaurant_id):
    menus = session.query(MenuItem).filter_by(restaurant_id=restaurant_id).all()
    return jsonify(MenuItems=[menu.serialize for menu in menus])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    menu = session.query(MenuItem).filter_by(id=menu_id).one_or_none()
    return jsonify(MenuItem=[menu.serialize])


if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
