from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)

app.secret_key = ''
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mysql+pymysql://root:@localhost/miniblog'
)

db = SQLAlchemy(app)
migrate = Migrate(app, db)






@app.route('/')
def index():
    return render_template(
        'index.html'
    )

