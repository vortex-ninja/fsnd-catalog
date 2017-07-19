from flask import Flask, render_template, url_for, redirect, flash
from flask import jsonify
from flask_bootstrap import Bootstrap
from forms import CreateCategoryForm, EditCategoryForm, DeleteForm
from forms import AddItemForm, EditItemForm
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item

app = Flask(__name__)
Bootstrap(app)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
@app.route('/catalog')
def mainPage():
    categories = session.query(Category).all()
    items = session.query(Item).limit(5)
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


if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
