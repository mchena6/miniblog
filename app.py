from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    current_user,
    LoginManager,
    login_required,
    login_user,
    logout_user,
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


app = Flask(__name__)

app.secret_key = ''
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:@localhost/miniblog'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Post, Comment

# Relaciones de la base de datos:
# user.posts -> post de un usuario
# user.comments -> comentarios de un usuario
# post.comments -> comentarios de un post
# post.author -> usuario que posteo
# comment.author -> usuario que escribio un comentario
# comment.post -> post al que pertenece un comentario

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login')
def login():
    return render_template(
        'auth/login.html'
    )

@app.route('/register')
def register():
    return render_template(
        'auth/register.html'
    )

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Ruta principal
@app.route('/')
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template(
       'index.html', posts=posts
    )

# Ver un post especifico
@app.route('/post/<int:id>')
def post_detail():
    post = Post.query.get_or_404(id)
    return render_template(
        'post_detail.html', post=post
    )

# Perfil de un usuario
@app.route('/user/<int:id>')
def user_profile():
    user = User.query.get_or_404(id)
    return render_template(
        'user_profile.html', user=user
    )

# Todos los posteos de un usuario
@app.route('/user/<int:id>/posts')
def user_posts():
    user = User.query.get_or_404(id)
    posts = Post.query.filter_by(id).order_by(Post.created_at.desc()).all()
    return render_template(
        'user_posts.html', user=user, posts=posts
    )

