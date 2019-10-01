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
    form = IndexForm()
    form.register = RegisterForm()

    if form.login.is_submitted() and form.login.submit.data:
        #user = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.login.username.data), one=True)
        user = User.query.filter_by(username = form.login.username.data).first()
        if user == None or form.login.username.data == '':
            flash('Invalid username or password!')
        elif user.check_password(form.login.password.data):
            login_user(user, remember=form.login.remember_me.data)
            return redirect(url_for('stream', username=form.login.username.data))
        else:
            flash('Invalid username or password!')

    elif form.register.is_submitted() and form.register.submit.data and form.register.validate():
        #query_db('INSERT INTO Users (username, first_name, last_name, password) VALUES("{}", "{}", "{}", "{}");'.format(form.register.username.data, form.register.first_name.data,
         #form.register.last_name.data, form.register.password.data))

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
        flash('Unauthorized login')
        return redirect(current_user.username)
    
    form = PostForm()
     #user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    user = User.query.filter_by(username = username).first()
    if form.is_submitted():
        if form.image.data:
            path = os.path.join(app.config['UPLOAD_PATH'], form.image.data.filename)
            form.image.data.save(path)


        #query_db('INSERT INTO Posts (u_id, content, image, creation_time) VALUES({}, "{}", "{}", \'{}\');'.format(user['id'], form.content.data, form.image.data.filename, datetime.now()))
        post = Post(u_id = user.id, content=form.content.data, image=form.image.data.filename, creation_time=datetime.now())
        db.session.add(post)
        db.session.commit()
        
        return redirect(url_for('stream', username=username))

    uid = user.id
    #posts = query_db('SELECT p.*, u.*, (SELECT COUNT(*) FROM Comments WHERE p_id=p.id) AS cc FROM Posts AS p JOIN Users AS u ON u.id=p.u_id WHERE p.u_id IN (SELECT u_id FROM Friends WHERE f_id={0}) OR p.u_id IN (SELECT f_id FROM Friends WHERE u_id={0}) OR p.u_id={0} ORDER BY p.creation_time DESC;'.format(user['id']))
    #posts = user.posts
    #posts = User.query.outerjoin(Post).filter(user.id == Post.u_id).all()
    posts = db.session.query(User, Post).join(Post,Post.u_id == user.id).all()
    return render_template('stream.html', title='Stream', username=username, form=form, posts=posts)

# comment page for a given post and user.
@app.route('/comments/<username>/<int:p_id>', methods=['GET', 'POST'])
@login_required
def comments(username, p_id):
    if username != current_user.username:
        flash('Unauthorized login')
        return redirect(current_user.username)

    user = User.query.filter_by(username = username).first()
    form = CommentsForm()
    if form.is_submitted():
        #user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
        
        #query_db('INSERT INTO Comments (p_id, u_id, comment, creation_time) VALUES({}, {}, "{}", \'{}\');'.format(p_id, user['id'], form.comment.data, datetime.now()))

        comment = Comment(p_id=p_id, u_id=user.id, comment = form.comment.data, creation_time = datetime.now())
        db.session.add(comment)
        db.session.commit()
    #post = query_db('SELECT * FROM Posts WHERE id={};'.format(p_id), one=True)
    post = Post.query.filter_by(id = p_id).first()
    #all_comments = query_db('SELECT DISTINCT * FROM Comments AS c JOIN Users AS u ON c.u_id=u.id WHERE c.p_id={} ORDER BY c.creation_time DESC;'.format(p_id))
    #all_comments = Post.query.join(Comment, post.id == Comment.p_id)
    #all_comments = db.session.query(Post, Comment).join(Comment,Comment.p_id == post.id, Comment.u_id == user.id)
    all_comments = db.session.query(Comment, User, Post).join(User).join(Post).filter(Comment.u_id == user.id, Comment.p_id == post.id).all()
    return render_template('comments.html', title='Comments', username=username, form=form, post=post, comments=all_comments)

# page for seeing and adding friends
@app.route('/friends/<username>', methods=['GET', 'POST'])
@login_required
def friends(username):
    if username != current_user.username:
        flash('Unauthorized login')
        return redirect(current_user.username)

    form = FriendsForm()
    #user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    user = User.query.filter_by(username = username).first()
    if form.is_submitted():
        #friend = query_db('SELECT * FROM Users WHERE username="{}";'.format(form.username.data), one=True)
        friend = User.query.filter_by(username = form.username.data).first()
        if friend is None:
            flash('User does not exist')
        else:
            #query_db('INSERT INTO Friends (u_id, f_id) VALUES({}, {});'.format(user['id'], friend['id']))
            friend = Friend(u_id = user.id, f_id = friend.id)
            db.session.add(friend)
            db.session.commit
    
    #all_friends = query_db('SELECT * FROM Friends AS f JOIN Users as u ON f.f_id=u.id WHERE f.u_id={} AND f.f_id!={} ;'.format(user['id'], user['id']))
    #all_friends = user.friends
    #all_friends = Friend.query.join(User, (user.id == Friend.u_id) & (user.id != Friend.f_id))
    all_friends = db.session.query(User, Friend).join(Friend,User.id == Friend.u_id, user.id != Friend.f_id).all()
    return render_template('friends.html', title='Friends', username=username,form=form, friends=all_friends)

# see and edit detailed profile information of a user
@app.route('/profile/<username>', methods=['GET', 'POST'])
@login_required
def profile(username):
    form = ProfileForm()
    if form.is_submitted():
       # query_db('UPDATE Users SET education="{}", employment="{}", music="{}", movie="{}", nationality="{}", birthday=\'{}\' WHERE username="{}" ;'.format(
        #    form.education.data, form.employment.data, form.music.data, form.movie.data, form.nationality.data, form.birthday.data, username))
        db.session.query(User).filter_by(username=username).update({"education":form.education.data})
        db.session.query(User).filter_by(username=username).update({"employment":form.employment.data})
        db.session.query(User).filter_by(username=username).update({"music":form.music.data})
        db.session.query(User).filter_by(username=username).update({"movie":form.movie.data})
        db.session.query(User).filter_by(username=username).update({"nationality":form.nationality.data})
        db.session.query(User).filter_by(username=username).update({"birthday":form.birthday.data})
        db.session.commit
        return redirect(url_for('profile', username=username))
    
    #user = query_db('SELECT * FROM Users WHERE username="{}";'.format(username), one=True)
    user = User.query.filter_by(username = username).first()
    return render_template('profile.html', title='profile', username=username, user=user, form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))