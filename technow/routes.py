import os
from datetime import datetime,timedelta
from flask import Flask,redirect,url_for,render_template,request,flash,abort
from flask import Blueprint,render_template,request,flash,redirect,url_for,session
from flask_login import login_user, current_user, login_required, logout_user,LoginManager,login_manager
from .extensions import db
from .models import *
from .forms import *
from re import search
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
main= Blueprint("main", __name__)


def log_web_visit():
        url_visited = request.url
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        log_data = f"Date: {timestamp}, URL Visited: {url_visited}, User-Agent: {user_agent}, IP Address: {ip_address}\n"
        with open('web_logs.txt', 'a') as file:
            file.write(log_data)
@main.route("/")
def home():
    log_web_visit()
    return render_template("home.html")

@main.route("/about")
def about():
    log_web_visit()
    return render_template("about.html")

@main.route("/bios")
def bios():
    log_web_visit()
    return render_template("bios.html")
@main.route("/semg")
def semg():
    log_web_visit()
    return render_template("semg.html")
@main.route("/fidele")
def fidele():
    log_web_visit()
    return render_template("fidele.html")
@main.route("/staff")
def staff():
    return render_template("staff.html")
@main.route("/signup",methods=['GET','POST'])
def register():
    log_web_visit()
    form=RegistrationForm()
    if form.validate_on_submit():
        #hash_pass= bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Your account has been succesfully created!')
        return redirect(url_for('main.login'))    
    return render_template("signup.html",title='Register',form=form)

@main.route("/login",methods=['GET','POST'])
def login():
    log_web_visit()
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter(User.username==form.username.data).first()
        if user and user.password==form.password.data:
            remember_me = form.remember_me.data  
            login_user(user, remember=remember_me)
            flash('You are in! Create blog')
            return redirect(url_for('main.blogpost'))
        flash("Password does not match!")
    return render_template("login.html",title='Login',form=form)

@main.route("/blogs",methods=['GET','POST'])
def blogs():
    log_web_visit()
    posts=Post.query.all()
    return render_template("blogs.html",posts=posts)

@main.route('/logout')
@login_required
def logout():
    log_web_visit()
    logout_user
    flash("You are logged out")
    return redirect(url_for('main.login'))

@main.errorhandler(401)
def unauthorized(error):
    flash("You are not currently logged in")
    return redirect(url_for('main.login'))    

@main.route('/curr')
@login_required
def curr_user():
    return 'current user is '+current_user.username

@main.route("/blogpost",methods=['GET','POST'])
@login_required
def blogpost():
    log_web_visit()
    form = PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!")
        return redirect(url_for('main.home'))
    return render_template("blogpost.html",title="New Post",form=form)

@main.route("/post/<int:post_id>")
def update(post_id):
     log_web_visit()
     post=Post.query.get_or_404(post_id)
     return render_template("singlepost.html",title=post.title, post=post)

@main.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update2(post_id):
    log_web_visit()
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    
    form = PostForm()
    if form.validate_on_submit():  
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Blog has been updated!")
        return redirect(url_for("main.blogs", post_id=post.id))  
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("blogpost.html", title="Update Post", form=form, legend="Update your blog")

@main.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
         abort(403)
    db.session.delete(post)
    db.session.commit() 
    flash(" You blog post has been deleted!")
    return redirect(url_for("main.blogs"))

@main.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        def send_email():
    
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()

            server.login(os.environ.get("CONF_EMAIL2"), os.environ.get("CONF_CODE2"))

            # Create the email content
            subject = 'NEW EMAIL FROM A CUSTOMER'
            body = f"First name: {form.firstName.data} \n Last name:  {form.lastName.data} \n Phone: {form.phone.data}\n Email:  {form.email.data}\n Message: {form.message.data}"
            message = MIMEMultipart()
            message['From'] =form.email.data
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Send the email
            server.sendmail(form.email.data, os.environ.get("CONF_EMAIL"), message.as_string())

            # Close the server connection
            server.quit()
        send_email()  
        flash("Thank you for reaching out, we will get back to you as soon as possible")
        form.firstName.data = ''
        form.lastName.data = ''
        form.phone.data = ''
        form.email.data = ''
        form.message.data = ''  
    return render_template("contact.html",form=form)


def delete_users(user_ids=None, usernames=None, emails=None):
    query = User.query
    if user_ids:
        query = query.filter(User.id.in_(user_ids))
    if usernames:
        query = query.filter(User.username.in_(usernames))
    if emails:
        query = query.filter(User.email.in_(emails))
    
    users_to_delete = query.all()
    for user in users_to_delete:
        # Delete posts associated with the user
        for post in user.posts:
            db.session.delete(post)
        db.session.delete(user)
    
    db.session.commit()
    return len(users_to_delete)

