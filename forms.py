from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Required

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class CreateCategoryForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    submit = SubmitField('Create')


class EditCategoryForm(CreateCategoryForm):

    submit = SubmitField('Edit')


class DeleteForm(FlaskForm):

    submit = SubmitField('Delete')


class EditItemForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    description = StringField('Description')
    submit = SubmitField('Edit')


class AddItemForm(EditItemForm):

    category = SelectField('Category', coerce=int)
    submit = SubmitField('Add')
