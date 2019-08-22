"""Blogly application."""

from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config["SECRET_KEY"] = "terces"
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
debug = DebugToolbarExtension(app)
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)


@app.route('/')
def index():
    """Serve the home page."""

    return redirect('/users')


@app.route('/users')
def users():
    """Serve the users page with a list of all users."""

    # Do a GET request to SQLAlchemy for all Users
    user_list = User.query.all()

    return render_template('/users.html', users=user_list)


@app.route('/users/new', methods=['GET', 'POST'])
def new_user():
    """Add a new user."""

    if request.method == 'POST':
        create_user_form = request.form
        first = create_user_form["first"]
        last = create_user_form["last"]
        image = create_user_form["img"]
        if image == '':
            image = None
        # Process the user into the database
        new_user = User(first_name=first, last_name=last, image_url=image)
        db.session.add(new_user)
        db.session.commit()
        print('THE NEW USER ID IS', new_user.id)

        # Render the Users User ID page
        return redirect(f'/users/{new_user.id}')
    else:
        return render_template('create-user.html')


@app.route('/users/<user_id>')
def show_profile(user_id):
    """Show the users profile page"""

    profile = User.query.get(user_id)
    first_name = profile.first_name
    last_name = profile.last_name
    image_url = profile.image_url

    return render_template('user-detail.html', first_name=first_name,
                           last_name=last_name, image_url=image_url,
                           user_id=user_id)


@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """User profile editing page"""

    user_from_db = User.query.get_or_404(user_id)

    if request.method == 'POST':
        edit_user_form = request.form
        first = edit_user_form['first']
        last = edit_user_form['last']
        image = edit_user_form['img']


        print("USER INFO ------->>>>>>", user_from_db)
        user_from_db.first_name = first
        user_from_db.last_name = last
        user_from_db.image_url = image
        db.session.commit()

        return redirect(f'/users/{user_id}')

    else:
        first_name = user_from_db.first_name
        last_name = user_from_db.last_name
        image_url = user_from_db.image_url

        return render_template('edit-user.html', first_name=first_name, last_name=last_name, image_url=image_url, user_id=user_id)

@app.route('/users/<user_id>/delete')
def delete_user(user_id):
    """Delete User profile"""
    user_from_db = User.query.get(user_id)

    db.session.delete(user_from_db)
    db.session.commit()

    return redirect('/users')