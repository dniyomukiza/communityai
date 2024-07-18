from flask_wtf import FlaskForm
from flask import flash
from datetime import datetime
from .models import User
from wtforms import StringField, PasswordField, SubmitField,TextAreaField,BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp,ValidationError


class RegistrationForm(FlaskForm):
    username=StringField(validators=[DataRequired()],render_kw={"placeholder":"Username"})
    password=StringField(validators=[DataRequired(),Length(min=2,max=20)],render_kw={"placeholder":"Password"})
    submit=SubmitField('Sign up')
    def validate_username(self,username):
        user_exists=User.query.filter_by(username=username.data).first()
        if user_exists:
            flash("This user already exists, just log in!")
            raise ValidationError   

class LoginForm(FlaskForm):
    username=StringField(validators=[DataRequired()],render_kw={"placeholder":"Username"})
    password=StringField(validators=[DataRequired(),Length(min=2,max=20)],render_kw={"placeholder":"Password"})
    remember_me = BooleanField('Remember Me') 
    submit=SubmitField('Login')

class ContactForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()],render_kw={"placeholder":"First Name"})
    lastName = StringField('Last Name', validators=[DataRequired()],render_kw={"placeholder":"Last Name"})
    phone =StringField('Phone', validators=[DataRequired()],render_kw={"placeholder":"phone"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder":"Your email"})
    message = TextAreaField('Message', validators=[DataRequired()],render_kw={"placeholder":"Your message"})
    submit = SubmitField('Submit')

#delete_users(user_ids=[1,2,3,4,5,6,7,8])
class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()],render_kw={"placeholder":"Blog Title"})
    content=TextAreaField("Content",validators=[DataRequired()],render_kw={"placeholder":"Type or Paste Blog Content"})
    submit=SubmitField('Post')