from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, flash


class User(UserMixin,db.Model):
   id = db.Column(db.Integer, primary_key = True)
   username = db.Column(db.String(20))
   first_name = db.Column(db.String(20))
   last_name = db.Column(db.String(20))
   password = db.Column(db.String(200))
   education = db.Column(db.String(20))
   employment = db.Column(db.String(20))
   music = db.Column(db.String(20))
   movie = db.Column(db.String(20))
   nationality = db.Column(db.String(20))
   birthday = db.Column(db.String(20))
   #posts = db.relation('Post', backref = 'user')
  
   def set_password(self, password):
        self.password = generate_password_hash(password)

   def check_password(self, password):
        return check_password_hash(self.password, password)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    u_id = db.Column(db.Integer, db.ForeignKey(User.id))
    content = db.Column(db.String(100))
    image = db.Column(db.String(20))
    creation_time = db.Column(db.DateTime())



#class Friend(db.Model):
 #   u_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key = True)
  #  f_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key = True)

class Friend(db.Model):
    u_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)
    f_id = db.Column(db.Integer, db.ForeignKey(User.id), primary_key=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    p_id = db.Column(db.Integer, db.ForeignKey(Post.id))
    u_id = db.Column(db.Integer, db.ForeignKey(User.id))
    comment = db.Column(db.String(100))
    creation_time = db.Column(db.DateTime())
    

db.create_all()

@login.user_loader
def user_loader(user_id): 
    
    return User.query.get(int(user_id))

@login.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('Unauthorized login')
    return redirect(url_for('index'))