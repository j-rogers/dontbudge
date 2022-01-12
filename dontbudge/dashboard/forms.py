"""Dashboard Forms

Contains the form classes for all forms in the dashboard. This includes things like
creating a new account, transaction, or bill. Uses flask_wtf for form creation and
validation.

Author: Josh Rogers (2021)
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, DecimalField
from wtforms.fields.simple import HiddenField
from wtforms.validators import DataRequired, NumberRange, Optional, AnyOf

class AccountForm(FlaskForm):
    """Form for creating a new Account"""
    name = StringField('Account Name', validators=[DataRequired()])
    starting_balance = DecimalField('Starting Balance', validators=[DataRequired()])
    submit = SubmitField('Submit')

class TransactionForm(FlaskForm):
    """Form for creating a new Transaction"""
    description = StringField('Description', validators=[DataRequired()])
    account = SelectField('Account', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', validators=[DataRequired()])
    category = SelectField('Category', validators=[Optional()])
    budget = SelectField('Budget', validators=[Optional()])
    bill = SelectField('Bill', validators=[Optional()])
    type = HiddenField('type', validators=[AnyOf(('deposit', 'withdraw'))])
    submit = SubmitField('Submit')

class BillForm(FlaskForm):
    """Form for creating a new Bill"""
    start = DateField('Date', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    occurence = SelectField(
        'Occurence', 
        choices = [
            ('1W', 'Weekly'),
            ('2W', 'Fortnightly'),
            ('1M', 'Monthly'),
            ('1Q', 'Quartely'),
            ('1Y', 'Annualy')
        ],
        validators = [DataRequired()]
    )
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class SettingsForm(FlaskForm):
    """Form for changing settings"""
    range = SelectField(
        'Occurence', 
        choices = [
            ('1W', 'Weekly'),
            ('2W', 'Fortnightly'),
            ('1M', 'Monthly'),
            ('1Q', 'Quartely'),
            ('1Y', 'Annualy')
        ],
        validators = [Optional()]
    )
    period_start = DateField('Period Start Date', validators=[Optional()])
    submit = SubmitField('Submit')

class CategoryForm(FlaskForm):
    """Form for creating a Category"""
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Submit')

class BudgetForm(FlaskForm):
    """Form for creating a Budget"""
    name = StringField('Name', validators=[DataRequired()])
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Submit')

class DeleteForm(FlaskForm):
    """Form for deleting an Object"""
    submit = SubmitField('Yes')