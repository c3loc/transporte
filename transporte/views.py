
from .transporte import app, db, login_manager
from .models import *
from .forms import *

import datetime
from flask import request, g, render_template, session, url_for, redirect, flash, Markup, escape, \
    send_from_directory, abort
from jinja2 import evalcontextfilter

from validate_email import validate_email

from flask_login import login_user, logout_user, login_required, current_user
from .zammad_integration import update_ticket, close_ticket

import babel
import re
import os

from dateutil import parser
from werkzeug.utils import secure_filename


@app.route('/')
@login_required
def index():
    todo = (
        dict(
            description='Todays transports',
            progress=100,
        ),
        dict(
            description='Overall transports',
            progress=100,
        ),
    )

    query = Transport.query.filter(Transport.cancelled == False)

    try:
        todo[0]['progress'] = 100 / query.filter(Transport.date == datetime.date.today()).count() * query.filter(
            Transport.date == datetime.date.today()).filter(Transport.done == True).count()
    except ZeroDivisionError:
        pass

    try:
        todo[1]['progress'] = 100 / query.count() * query.filter(Transport.done == True).count()
    except ZeroDivisionError:
        pass

    return render_template('layout.html', todo=todo)


@app.route('/login', methods=['GET', 'POST'])
#@limiter.limit('10/hour')
def login():
    loginform = LoginForm()

    if loginform.validate_on_submit():
        email = loginform.login.data
        if app.config['DEBUG'] or validate_email(email, check_mx=True):
            user = User.query.filter(User.login == email).first()

            if user is None:
                # create user
                user = User(login=email)
                db.session.add(user)
                db.session.commit()

            # create token
            user.create_token()

            flash('Check your inbox!')
        else:
            loginform.login.errors.append('Please enter valid email address!')

    return render_template('login.html', loginform=loginform)


@app.route('/login/token/<token>')
def login_with_token(token):
    user = User.verify_login_token(token)

    if user:
        login_user(user)

        return redirect(url_for('index'))
    else:
        flash('Invalid or expired token!')
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()

    flash('You have been logged out.')

    return redirect(url_for('login'))


@app.route('/transports/add', defaults={'id': None}, methods=['GET', 'POST'])
@app.route('/transports/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transport(id=None):
    if id is not None:
        transport = Transport.query.get(id)

        if not (current_user.id == transport.user_id or current_user.role in ['helpdesk', 'admin']):
            transport = None

    else:
        transport = Transport()

    if transport is not None:
        transportform = TransportForm(obj=transport)

        if transportform.validate_on_submit():
            transportform.populate_obj(transport)

            if id is None:
                transport.user_id = current_user.id
            db.session.add(transport)
            db.session.commit()

            ##
            ## if ticket is new, update object with zammad ticket id
            ##
            if transport.ticket_id == None:
                transport.ticket_id = update_ticket(transport)
                db.session.add(transport)
                db.session.commit()
            else:
                update_ticket(transport)

            for file in request.files.getlist('file_upload'):
                file_name = secure_filename(file.filename)
                upload_dir = os.path.join(app.config['UPLOAD_DIR'], str(transport.id))
                file_path = os.path.join(upload_dir, file_name)

                if not os.path.isdir(os.path.join(app.root_path, upload_dir)):
                    os.mkdir(os.path.join(app.root_path, upload_dir))

                file.save(os.path.join(app.root_path, file_path))

                f = File(transport_id=transport.id, name=file_name, path=file_path)
                db.session.add(f)
                db.session.commit()

            flash('Saved')
            if id is None:
                return redirect(url_for('edit_transport', id=transport.id))
    else:
        transportform = TransportForm()
        flash('Not authorized to edit this transport!')

    return render_template('transport_details_edit.html', transportform=transportform, transport=transport)


@app.route('/transports/list')
@login_required
def list_transports():
    transportlist = Transport.query

    if not current_user.role in ['helpdesk', 'admin']:
        transportlist = transportlist.filter(Transport.user_id == current_user.id)

    dates = transportlist.with_entities(Transport.date).distinct().order_by(Transport.date).all()

    filterform = TransportFilterForm(day=request.args.get('day'))
    filterform.day.choices = [('None', 'Filter by date')] + [(date[0], date[0]) for date in dates]

    if filterform.day.data != 'None':
        transportlist = transportlist.filter(Transport.date == parser.parse(filterform.day.data).date())

    return render_template('transport_list.html', transportlist=transportlist, filterform=filterform)


@app.route('/transports/show/<int:id>')
@login_required
def show_transport(id=None):
    transport = Transport.query.get(id)

    if transport is None or not (
            transport.user_id == current_user.id or current_user.role in ['helpdesk', 'admin']):
        transport = None
        flash('Transport is not available')
    else:
        if transport.done:
            flash('Transport is done', 'success')
        elif transport.cancelled:
            flash('Transport was cancelled!', 'danger')

    return render_template('transport_details.html', transport=transport)


@app.route('/transports/mark/<mark>/<int:id>', methods=['GET', 'POST'])
@login_required
def mark_transport(mark, id=None):
    transport = Transport.query.get(id)

    if transport is None or not (
            transport.user_id == current_user.id or current_user.role in ['helpdesk', 'admin']):
        transport = None
        flash('Transport not available')
    elif transport.done:
        flash('Transport already marked as done!')
        transport = None
    elif transport.cancelled:
        flash('Transport cancelled!')
        transport = None

    form = FlaskForm()

    if form.validate_on_submit():
        if mark == 'done' and current_user.role in ['helpdesk', 'admin']:
            transport.done = True
        elif mark == 'cancelled':
            transport.cancelled = True
            
        ##
        ## close ticket
        ##
        if transport.ticket_id:
            close_ticket(transport, mark)

        db.session.add(transport)
        db.session.commit()

        return redirect(url_for('list_transports'))

    return render_template('transport_mark.html', mark=mark, transport=transport, form=form)


@app.route('/users/list')
@login_required
def list_users():
    if not (current_user.role in ['admin']):
        abort(404)

    users = User.query.all()

    return render_template('user_list.html', userlist=users)


@app.route('/users/show/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user(id=None):
    if not (current_user.role in ['admin']):
        abort(404)

    user = User.query.get(id)
    roleform = RoleForm(obj=user)

    if user is None:
        flash('User not available')
    elif roleform.validate_on_submit():
        roleform.populate_obj(user)

        db.session.add(user)
        db.session.commit()

        flash('Saved')

    return render_template('user_details.html', user=user, roleform=roleform)


@app.route('/uploads/<int:transport_id>/<path:filename>')
def uploaded_file(transport_id, filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_DIR'], str(transport_id)),
                               filename)

def format_datetime(value):
    format = "EE, dd.MM.y"
    return babel.dates.format_datetime(value, format)


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'<br />\n'.join(_paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['nl2br'] = nl2br


@app.context_processor
def inject_global_template_vars():
    return dict(app_name=app.config['APP_NAME'], vehicletypes=VehicleTypes, roles=Roles)


@app.context_processor
def inject_today():
    return dict(today=datetime.date.today())

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

