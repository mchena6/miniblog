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

# Inicializar app
app = Flask(__name__)

app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:@localhost/miniblog'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Inicializar base de datos
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importar modelos 
from models import User, Post, Comment, Categorie

# Cargar categorías iniciales (solo si no existen)
with app.app_context():
    # Verificar que no haya categorias cargadas
    if not Categorie.query.first():
        categories = ['Música', 'Política', 'Deportes', 'Historia', 'Entretenimiento', 'Ciencia']
        for category_list in categories:
            category = Categorie(name=category_list)
            db.session.add(category)
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Enviar categorias como variable global
@app.context_processor
def inject_categories():
    categories = Categorie.query.all()
    return dict(categories=categories)

# Registro
@app.route('/register', methods=['GET', 'POST'])
def register():
    # Guardar datos del formulario de registro
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_hash = generate_password_hash(password, method='pbkdf2')
        # Crear usuario
        user = User(username=username, email=email, password_hash=password_hash)

        # Agregarlo a la base de datos
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template(
        'auth/register.html'
    )

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Guardar datos del formulario de login
        username = request.form['username']
        password = request.form['password']
        
        # Buscar usuario en la base de datos
        user = User.query.filter_by(username=username).first()
        # Verificar contraseña del usuario y loguear si coincide
        if user and check_password_hash(pwhash=user.password_hash, password=password):
            login_user(user)
            # Mandar al Inicio
            return redirect(url_for('index'))
        
    return render_template(
        'auth/login.html'
    )

# Logout
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


# Inicio
@app.route('/')
def index():
    # Traer todos los posts en orden descendente por fecha
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('index.html', posts=posts)


# Crear un posteo
@app.route('/post/new' , methods=['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        # Guardar datos del formulario de post
        title = request.form['post_title']
        content = request.form['post_content']
        categorie_id = request.form['post_categorie']
        # Crear Post
        post = Post(title=title, content=content, author=current_user, categorie_id=categorie_id)
        # Agregar a la base de datos
        db.session.add(post)
        db.session.commit()
        # Enviar al Inicio
        return redirect(url_for('index'))
    return render_template('post_form.html')


# Eliminar posteo
@app.route('/post/<int:id>/delete', methods=['POST'])
@login_required
def delete_post(id):
    # Traer post por id
    post = Post.query.get_or_404(id)

    # Verificar que el usuario logueado es el autor del post
    if post.author == current_user:
        # Eliminar post
        db.session.delete(post)
        db.session.commit()
        # Enviar al Inicio
        return(redirect(url_for('index')))



# Ver un post especifico
@app.route('/post/<int:id>')
def post_detail(id):
    # Traer post por id
    post = Post.query.get_or_404(id)
    return render_template(
        'post_detail.html', post=post
    )

# Perfil de un usuario
@app.route('/user/<int:id>')
def user_profile(id):
    # Traer usuario por id
    user = User.query.get_or_404(id)
    return render_template(
        'user_profile.html', user=user
    )

# Todos los posteos de un usuario
@app.route('/user/<int:id>/posts')
def user_posts():
    # Traer usuario por id
    user = User.query.get_or_404(id)
    # Traer posts con el id del usuario
    posts = Post.query.filter_by(id).order_by(Post.created_at.desc()).all()
    return render_template(
        'user_posts.html', user=user, posts=posts
    )

# Crear comentario
@app.route('/post/<int:post_id>/comment', methods=['GET','POST'])
@login_required
def comment_create(post_id):
    if request.method == 'POST':
        # Guardar texto del formulario
        content = request.form['comment_content']
        # Crear comentario
        comment = Comment(text=content, post_id=post_id, author=current_user)
    # Agregar a la base de datos
    db.session.add(comment)
    db.session.commit()
    # Volver a cargar el post 
    return redirect(url_for('post_detail', id=post_id))

# Eliminar comentario
@app.route('/comment/<int:id>', methods=['POST'])
def comment_delete(id):
    # Traer comentario por id
    comment = Comment.query.get_or_404(id)

    # Guardar id del post
    post_id = comment.post.id
    # Verificar si el usuario logueado es el mismo autor del comentario
    if comment.author == current_user:
        # Eliminar de la base de datos
        db.session.delete(comment)
        db.session.commit()
    # Volver a cargar el post
    return redirect(url_for('post_detail', id=post_id))

# Editar comentario
@app.route('/comment/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def comment_edit(id):
    # Traer comentario por id
    comment = Comment.query.get_or_404(id)

    if request.method == 'POST':
        # Guardar texto del formulario
        new_text = request.form['comment_content']
        # Reemplazar texto del comentario con el nuevo texto
        comment.text = new_text
        db.session.commit()
        # Volver a cargar el post
        return redirect(url_for('post_detail', id=comment.post_id))

    return render_template('comment_edit.html', comment=comment)