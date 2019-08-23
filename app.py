"""Blogly application."""

from flask import Flask, render_template, request, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

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
        if first == '' and last == '':
            flash(f'Please enter a first and last name.', 'first-last')
            return redirect('/users/new')
        if first == '':
            flash(f'Please enter a first name.', 'first')
            return redirect('/users/new')
        if last == '':
            flash(f'Please enter a last name.', 'last')
            return redirect('/users/new')

        new_user = User(first_name=first, last_name=last, image_url=image)
        db.session.add(new_user)
        db.session.commit()

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

    posts_from_db = Post.query.filter_by(user_id=user_id)

    return render_template('user-detail.html', first_name=first_name,
                           last_name=last_name, image_url=image_url,
                           user_id=user_id, posts=posts_from_db)


@app.route('/users/<user_id>/edit', methods=['GET', 'POST'])
def edit_user(user_id):
    """User profile editing page"""

    user_from_db = User.query.get_or_404(user_id)

    if request.method == 'POST':
        edit_user_form = request.form
        first = edit_user_form['first']
        last = edit_user_form['last']
        image = edit_user_form['img']
        if image == '':
            image = '/static/images/default-profile.jpg'
        if first == '' and last == '':
            flash(f'Please enter a first and last name.', 'first-last')
            return redirect(f'/users/{user_id}/edit')
        if first == '':
            flash(f'Please enter a first name.', 'first')
            return redirect(f'/users/{user_id}/edit')
        if last == '':
            flash(f'Please enter a last name.', 'last')
            return redirect(f'/users/{user_id}/edit')

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


@app.route('/users/<user_id>/posts/new', methods=['GET', 'POST'])
def new_post(user_id):
    """Add a new post"""

    if request.method == 'POST':
        submitted_post = request.form
        title = submitted_post['post-title']
        content = submitted_post['post-content']
        if title == '' and content == '':
            flash('Please enter a post title and content', 'content-title')
            return redirect(f'/users/{user_id}/posts/new')
        if title == '':
            flash('Please enter a post title.', 'title')
            return redirect(f'/users/{user_id}/posts/new')
        if content == '':
            flash('Please enter your post content.', 'content')
            return redirect(f'/users/{user_id}/posts/new')

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        return redirect(f'/posts/{new_post.id}')
    else:
        user_from_db = User.query.get_or_404(user_id)
        first_name = user_from_db.first_name
        last_name = user_from_db.last_name

        return render_template('new-post.html', first_name=first_name,
                               last_name=last_name, user_id=user_id)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show the selected post"""
    post = Post.query.get_or_404(post_id)
    title = post.title
    content = post.content
    first_name = post.user.first_name
    last_name = post.user.last_name

    return render_template('post-detail.html', title=title, content=content, first_name=first_name, 
                           last_name=last_name,
                           post_id=post_id,
                           user_id=post.user.id)


@app.route('/posts/<int:post_id>/edit', methods=['GET', 'POST'])
def edit_post(post_id):
    """Edit a post"""
    post = Post.query.get_or_404(post_id)

    if request.method == 'POST':
        edits = request.form
        edited_title = edits['post-title']
        edited_content = edits['post-content']
        if edited_title == '' and edited_content == '':
            flash('Please enter a post title and content', 'content-title')
            return redirect(f'/posts/{post_id}/edit')
        if edited_title == '':
            flash('Please enter a post title.', 'title')
            return redirect(f'/posts/{post_id}/edit')
        if edited_content == '':
            flash('Please enter your post content.', 'content')
            return redirect(f'/posts/{post_id}/edit')

        post.title = edited_title
        post.content = edited_content
        db.session.add(post)
        db.session.commit()

        return redirect(f'/users/{post.user.id}')
    else:
        return render_template('edit-post.html', post_id=post_id,
                               title=post.title,
                               content=post.content,
                               user_id=post.user.id)


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    """Delete users post"""

    post_from_db = Post.query.get(post_id)
    user = post_from_db.user.id

    db.session.delete(post_from_db)
    db.session.commit()

    return redirect(f'/users/{user}')

@app.route('/tags')
def list_tags():
    """Show the user a list of all tags."""
    all_tags = Tag.query.all()
    
    return render_template('/tags.html', tags=all_tags)


@app.route('/tag/new')
def show_tag_form():
    """Sends user to add tag form."""
    
    return render_template('create-tag.html')


@app.route('/tag/new', methods=['POST'])
def add_tag():
    """Sends user to add tag form."""
    
    create_tag_form = request.form
    tag_name = create_tag_form["tag-name"]

    if tag_name == '':
        flash('Please enter a tag name.')
        return redirect('/tags/new')

    new_tag = Tag(name=tag_name)
    db.session.add(new_tag)
    db.session.commit()

    return redirect('/tags')


@app.route('/tag/<int:tag_id>')
def tag_detail_page(tag_id):
    """Sends user to tag detail page."""

    tag = Tag.query.get(tag_id)
    name = tag.name
    posts_lists = tag.posts

    return render_template('show-tag.html', name=name, posts=posts_list)


@app.route('/tags/<int:tag_id>/edit')
def show_tag_edit_form(tag_id):
    """Sends user to tag edit page."""

    tag = Tag.query.get(tag_id)

    return render_template('edit-tag.html', tag_id=tag_id, name=tag.name)

@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def edit_tag(tag_id):
    """Edits the tag and sends back to tags page."""

    create_tag_form = request.form
    tag_name = create_tag_form["tag-name"]

    if tag_name == '':
        flash('Please enter a tag name.')
        return redirect(f'/tags/new{tag_id}')
    
    tag = Tag.query.get(tag_id)
    tag.name = tag_name

    db.session.add(tag)
    db.session.commit()

    return redirect(f'/tags/{tag_id}')