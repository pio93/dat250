from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.models import User, Post, Comment, Friend
from app.forms import IndexForm, PostForm, FriendsForm, ProfileForm, CommentsForm, RegisterForm, LoginForm
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
import flask_sqlalchemy
import os

# this file contains all the different routes, and the logic for communicating with the database

# home page/login/registration
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        redirect(url_for('stream', username=current_user.username))
    form = IndexForm()
    form.register = RegisterForm()

    if form.login.is_submitted() and form.login.submit.data:
        user = User.query.filter_by(username = form.login.username.data).first()
        if user == None or form.login.username.data == '':
            flash('Invalid username or password!')
        elif user.check_password(form.login.password.data):
            login_user(user, remember=form.login.remember_me.data)
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Invalid username or password!')

    elif form.register.is_submitted() and form.register.submit.data and form.register.validate():

        user = User(username=form.register.username.data, first_name=form.register.first_name.data, 
        last_name=form.register.last_name.data)
        user.set_password(form.register.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('index.html', title='Welcome', form=form)


# content stream page
@app.route('/stream/<username>', methods=['GET', 'POST'])
@login_required
def stream(username):
    if username != current_user.username:
        return redirect(current_user.username)
    
    form = PostForm()
  
    user = User.query.filter_by(username = username).first()
    if form.is_submitted():
        validInput = True
        if form.image.data:
            extension = os.path.splitext(form.image.data.filename) #Gets the uploaded file's extension
            extension = extension[1].lower()
            if extension in app.config['ALLOWED_EXTENSIONS']: #Checks if the file extension is in the whitelist, returns true if it is
                path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
                form.image.data.save(path)
            else:
                validInput = False
                flash("Invalid file extension")
        
        if validInput:
            post = Post(u_id = user.id, content=form.content.data, image=form.image.data.filename, creation_time=datetime.now())
            db.session.add(post)
            db.session.commit()
        
        return redirect(url_for('stream', username=username))

    friends = db.session.query(Friend).filter(user.id == Friend.u_id).all()
    posts_f = db.session.query(User, Post).join(Post).filter(Post.u_id == user.id).all()
    posts = []
    for friend in friends:
        friend_posts = db.session.query(User,Post).join(Post).filter(Post.u_id == friend.f_id).all()
        for friend_post in friend_posts:
            posts_f.append(friend_post)
    for post_f in posts_f:
        if post_f != None:
            post = post_f + (db.session.query(Comment).filter(post_f[1].id == Comment.p_id).count(),)
            posts.append(post)
    posts.sort(key=sortPosts, reverse=True)
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    if username != current_user.username:
        return redirect(current_user.username)

    user = User.query.filter_by(username = username).first()
    form = CommentsForm()
    if form.is_submitted():
       

        comment = Comment(p_id=p_id, u_id=user.id, comment = form.comment.data, creation_time = datetime.now())
        db.session.add(comment)
        db.session.commit()

    post = Post.query.filter_by(id = p_id).first()
    if not post:
        return error()
    all_comments = db.session.query(Comment, User, Post).join(User, User.id == Comment.u_id).join(Post, Post.id == Comment.p_id).filter(Comment.p_id == post.id).all()
    all_comments.sort(key=sortComments, reverse=True)
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if username != current_user.username:
        return redirect(current_user.username)

    form = FriendsForm()
    
    user = User.query.filter_by(username = username).first()
    if username == current_user.username and form.is_submitted():
    
        friend = User.query.filter_by(username = form.username.data).first()
        if friend is None:
            flash('User does not exist')
        else:
            friend = Friend(u_id = user.id, f_id = friend.id)
            db.session.add(friend)
            db.session.commit()
    
   
    friends = db.session.query(User, Friend).join(Friend, User.id == Friend.u_id).filter(user.id == Friend.u_id).filter(user.id != Friend.f_id).all()
    all_friends = []
    for friend in friends: 
        all_friends.append(User.query.filter(User.id == friend[1].f_id).first())
    return render_template('friends.html', title='Friends', username=username,form=form, friends=all_friends)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    owner = True
    if username != current_user.username:
       owner = False

    user = User.query.filter_by(username = username).first()
    if not user:
        return error()
    if username == current_user.username and form.is_submitted():
        user.education = form.education.data
        user.employment = form.employment.data
        user.music = form.music.data
        user.movie = form.movie.data
        user.nationality = form.nationality.data 
        user.birthday = form.birthday.data

        db.session.add(user)      
        db.session.commit()
        return redirect(url_for('profile', username=username))
    
 
    
    return render_template('profile.html', title='profile', username=username, user=user, form=form, owner=owner)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return error()


def error(error_message="Page not found", error_type=404):
    return render_template('error.html', error_message=error_message, error_type=error_type)

def sortPosts(obj):
    return obj[1].creation_time

def sortComments(obj):
    return obj[0].creation_time