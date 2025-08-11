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

app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:@localhost/miniblog'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Post, Comment, Categorie

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

@app.context_processor
def inject_categories():
    categories = Categorie.query.all()
    return dict(categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password, method='pbkdf2')
        user = User(username=username, email=email, password_hash=password_hash)

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template(
        'auth/register.html'
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(pwhash=user.password_hash, password=password):
            login_user(user)
            return redirect(url_for('index'))
        
    return render_template(
        'auth/login.html'
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


# Crear un posteo
@app.route('/post/new' , methods=['GET', 'POST'])
@login_required
def new_post():

    if request.method == 'POST':
        title = request.form['post_title']
        content = request.form['post_content']
        categorie_id = request.form['post_categorie']
        post = Post(title=title, content=content, author=current_user, categorie_id=categorie_id)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('post_form.html')



# Ver un post especifico
@app.route('/post/<int:id>')
def post_detail(id):
    post = Post.query.get_or_404(id)
    return render_template(
        'post_detail.html', post=post
    )

# Perfil de un usuario
@app.route('/user/<int:id>')
def user_profile(id):
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

#Crear comentario
@app.route('/post/<int:post_id>/comment', methods=['GET','POST'])
@login_required
def comment_create(post_id):
    if request.method == 'POST':
        content = request.form['comment_content']
        comment = Comment(text=content, post_id=post_id, author=current_user)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('post_detail', id=post_id))

#Eliminar comentario
@app.route('/comment/<int:id>', methods=['POST'])
def comment_delete(id):
    comment = Comment.query.get_or_404(id)

    post_id = comment.post.id
    if comment.author == current_user:
        db.session.delete(comment)
        db.session.commit()
    return redirect(url_for('post_detail', id=post_id))

#Editar comentario
@app.route('/comment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    comment = Comment.query.get_or_404(id)

    if comment.author != current_user:
        # Opcional: flash("No tienes permiso para editar este comentario")
        return redirect(url_for('post_detail', id=comment.post_id))

    if request.method == 'POST':
        new_text = request.form['comment_content']
        comment.text = new_text
        db.session.commit()
        return redirect(url_for('post_detail', id=comment.post_id))

    return render_template('comment_edit.html', comment=comment)