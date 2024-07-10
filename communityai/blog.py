from datetime import datetime
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Length,ValidationError,Email
from flask import Flask,redirect,url_for,render_template,request,flash,abort
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
db=SQLAlchemy()
app=Flask(__name__)# initiliaze app and configure the secret key
bcrypt=Bcrypt(app)
app.app_context().push()
login_manager=LoginManager()
login_manager.init_app(app)
def create_app():
    app=Flask(__name__)
    app.config['DEBUG'] = True
    app.config["SECRET_KEY"]="9866115a575103d99e14da62c83239d18867f0e3138ba2966c6720e73dce1224"
    app.config['SQLALCHEMY_DATABASE_URI']= os.environ.get("DATAI_DB")#'sqlite:///users.db
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db=SQLAlchemy(app)# initialize database
    db.init_app(app)

    return app
# class reprenting user on database
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
   
    
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)

def log_web_visit():
        url_visited = request.url
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        log_data = f"Date: {timestamp}, URL Visited: {url_visited}, User-Agent: {user_agent}, IP Address: {ip_address}\n"
        with open('web_logs.txt', 'a') as file:
            file.write(log_data)
@app.route("/")
def home():
    log_web_visit()
    return render_template("home.html")
@app.route("/about")
def about():
    log_web_visit()
    return render_template("about.html")

@app.route("/bios")
def bios():
    log_web_visit()
    return render_template("bios.html")
@app.route("/semg")
def semg():
    log_web_visit()
    return render_template("semg.html")
@app.route("/fidele")
def fidele():
    log_web_visit()
    return render_template("fidele.html")
@app.route("/staff")
def staff():
    return render_template("staff.html")
@app.route("/signup",methods=['GET','POST'])
def register():
    log_web_visit()
    form=RegistrationForm()
    if form.validate_on_submit():
        #hash_pass= bcrypt.generate_password_hash(form.password.data)
        new_user=User(username=form.username.data,password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash(f'Your account has been succesfully created!')
        return redirect(url_for('login'))    
    return render_template("signup.html",title='Register',form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    log_web_visit()
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter(User.username==form.username.data).first()
        if user and user.password==form.password.data:
            login_user(user)
            flash('You are in! Create title and blog then post it')
            return redirect(url_for('blogpost'))
        flash("Password does not match!")
    return render_template("login.html",title='Login',form=form)

@app.route("/blogs",methods=['GET','POST'])
def blogs():
    log_web_visit()
    posts=Post.query.all()
    return render_template("blogs.html",posts=posts)

@app.route('/logout')
@login_required
def logout():
    log_web_visit()
    logout_user
    flash("You are logged out")
    return redirect(url_for('login'))

@app.errorhandler(401)
def unauthorized(error):
    flash("You are not currently logged in")
    return redirect(url_for('login'))    

@app.route('/curr')
@login_required
def curr_user():
    return 'current user is '+current_user.username

@app.route("/blogpost",methods=['GET','POST'])
@login_required
def blogpost():
    log_web_visit()
    form = PostForm()
    if form.validate_on_submit():
        post=Post(title=form.title.data,content=form.content.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!")
        return redirect(url_for('home'))
    return render_template("blogpost.html",title="New Post",form=form)

@app.route("/post/<int:post_id>")
def update(post_id):
     log_web_visit()
     post=Post.query.get_or_404(post_id)
     return render_template("singlepost.html",title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
#@login_required
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
        return redirect(url_for("blogs", post_id=post.id))  
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template("blogpost.html", title="Update Post", form=form, legend="Update your blog")

@app.route("/post/<int:post_id>/delete", methods=['GET', 'POST'])
#@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
         abort(403)
    db.session.delete(post)
    db.session.commit() 
    flash(" You blog post has been deleted!")
    return redirect(url_for("blogs"))

@app.route('/contact', methods=['GET', 'POST'])
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
    submit=SubmitField('Login')

class ContactForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()],render_kw={"placeholder":"First Name"})
    lastName = StringField('Last Name', validators=[DataRequired()],render_kw={"placeholder":"Last Name"})
    phone =StringField('Phone', validators=[DataRequired()],render_kw={"placeholder":"phone"})
    email = StringField('Email', validators=[DataRequired(), Email()],render_kw={"placeholder":"Your email"})
    message = TextAreaField('Message', validators=[DataRequired()],render_kw={"placeholder":"Your message"})
    submit = SubmitField('Submit')

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



#delete_users(user_ids=[1,2,3,4,5,6,7,8])
class PostForm(FlaskForm):
    title=StringField("Title",validators=[DataRequired()],render_kw={"placeholder":"Blog Title"})
    content=TextAreaField("Content",validators=[DataRequired()],render_kw={"placeholder":"Type or Paste Blog Content"})
    submit=SubmitField('Post')
#Adding post to database

if __name__ == "__main__":
    app.run(debug=True)


