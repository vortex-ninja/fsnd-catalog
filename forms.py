from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required


class CreateCategoryForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    submit = SubmitField('Create')


class EditCategoryForm(CreateCategoryForm):

    submit = SubmitField('Edit')


class DeleteForm(FlaskForm):

    submit = SubmitField('Delete')


class AddItemForm(FlaskForm):

    name = StringField('Name', validators=[Required()])
    description = StringField('Description')
    submit = SubmitField('Add')


class EditItemForm(AddItemForm):

    submit = SubmitField('Edit')
