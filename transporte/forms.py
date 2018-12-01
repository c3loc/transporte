
import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, DateField, SelectField, TextAreaField, HiddenField, TimeField
from wtforms.fields import BooleanField
from wtforms.validators import *
from wtforms.widgets import html5 as widgets_html5
from wtforms_components import DateRange


VehicleTypes = {
    'car': 'Car',
    'trailer': 'Car with trailer',
    'transporter': 'Transporter',
    '7.5t': '7.5t',
    '18t': '18t',
    '40t': '40t',
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
    location_from = TextAreaField('Origin', validators=[DataRequired()])
    location_to = TextAreaField('Destination', validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired(), DateRange(
        min=max(datetime.date.today(), datetime.date(year=2018, month=12, day=15)),
        max=datetime.date(year=2019, month=1, day=6))], widget=widgets_html5.DateInput())
    time = TimeField('Time', validators=[Optional()], widget=widgets_html5.TimeInput())
    vehicle = SelectField('Vehicle', validators=[DataRequired()], choices=[('', '')] + list(VehicleTypes.items()))
    goods = TextAreaField('Goods', validators=[DataRequired()])
    vehicle_owner = StringField('Vehicle Owner')
    orga_contact = TextAreaField('Orga Contact Person / Details', validators=[DataRequired()])
    driver_contact = TextAreaField('Driver Contact Person / Details')
    comment = TextAreaField('Comment')
    file_upload = FileField('Files', render_kw={'multiple': True})


class RoleForm(FlaskForm):
    role = SelectField('Role', validators=[DataRequired()], choices=list(Roles.items()))


class TransportFilterForm(FlaskForm):
    day = SelectField('Day', choices=[])
