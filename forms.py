from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import Required


class CreateResForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    submit = SubmitField('Create')


class EditResForm(CreateResForm):

    submit = SubmitField('Edit')


class DeleteForm(FlaskForm):

    submit = SubmitField('Delete')


class AddMenuItemForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    course = RadioField('Course', choices=[('Appetizer', 'Appetizer'),
                                           ('Entree', 'Entree'),
                                           ('Dessert', 'Dessert'),
                                           ('Beverage', 'Beverage')])
    description = StringField('Description')
    price = StringField('Price')
    submit = SubmitField('Add')


class EditMenuItemForm(AddMenuItemForm):

    submit = SubmitField('Edit')
