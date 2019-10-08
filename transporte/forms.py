
import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.fields import BooleanField
from wtforms.fields.html5 import TimeField
from wtforms.validators import *

# DateField from wtforms_components supports min/max depending on DateRange
from wtforms_components import DateField
from wtforms_components import DateRange


VehicleTypes = {
    'car': 'Car',
    'trailer': 'Car with trailer',
    'transporter': 'Transporter',
    '7.5t': '7.5t',
    '12t': '12t',
    '18t': '18t',
    '40t': '40t',
    'truck': 'Truck (unknown size)'
}

Roles = {
    'user': 'User',
    'helpdesk': 'Helpdesk',
    'admin': 'Admin'
}


class LoginForm(FlaskForm):
    login = StringField('Email', validators=[DataRequired(), Email(message='Please enter valid emailaddress')])


class TransportForm(FlaskForm):
    organizer = StringField('Organizer', validators=[DataRequired()])
    needs_organization = BooleanField('Needs organization')
    origin = TextAreaField('Origin', validators=[DataRequired()])
    destination = TextAreaField('Destination', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired(), DateRange(
        min=max(datetime.date.today(), datetime.date(year=2019, month=12, day=14)),
        max=datetime.date(year=2020, month=1, day=7))])
    time = TimeField('ETA', validators=[Optional()])
    vehicle = SelectField('Vehicle', validators=[DataRequired()], choices=[('', '')] + list(VehicleTypes.items()))
    goods = TextAreaField('Goods', validators=[DataRequired()])
    vehicle_owner = StringField('Vehicle Owner')
    orga_contact = TextAreaField('Orga Contact Person / Details', validators=[DataRequired()])
    driver_contact = TextAreaField('Driver Contact Person / Details')
    comment = TextAreaField('Comment')
    file_upload = FileField('Files', render_kw={'multiple': True})
    save = SubmitField('Save')
    saveasnew = SubmitField('Save as new')

class RoleForm(FlaskForm):
    role = SelectField('Role', validators=[DataRequired()], choices=list(Roles.items()))


class TransportFilterForm(FlaskForm):
    day = SelectField('Day', choices=[])
