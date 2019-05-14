from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, TaskForm
from flask_login import UserMixin
from datetime import datetime
from flask_bcrypt import Bcrypt

session = {}

# Создание приложения
app = Flask(__name__)

# Конфигурации приложения
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# Создание приложения для хеширования пароля
bcrypt = Bcrypt(app)

# Создание базы данных
db = SQLAlchemy(app)


# Создание модели пользователя
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


# Создание модели отправки
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_done = db.Column(db.Text, nullable=False)
    user_name = db.Column(db.Text, nullable=False)
    executor = db.Column(db.Text)
    priority = db.Column(db.Text)
    category = db.Column(db.Text)
    stage = db.Column(db.Text)
    done = db.Column(db.Text)
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Создание моделей в базе данных
db.create_all()


# Создание запросов

@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('register')
    return render_template('home.html', username=session['username'], tasks=Task.query.filter_by(user_name=session['username']))

@app.route('/')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect('home', username=session['username'])
    # Форма регистрации
    form = RegistrationForm()
    if form.validate_on_submit():
        # Создание хеша пароля
        if User.query.filter_by(username=form.username.data).first():
            flash('Пользователь с таким именем уже зарегистрирован в системе')
            return render_template('register.html', title='Регистрация', form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash('Пользователь с такой почтой уже зарегистрирован в системе')
            return render_template('register.html', title='Регистрация', form=form)        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)


# Запрос на вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if 'username' in session:
        return redirect('home')
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash('Такого пользователя нет')
            return render_template('login.html', form=form)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['username'] = form.username.data
            return redirect('home')
        else:
            flash('Неправильный пароль', 'danger')
            render_template('login.html', form=form)
    return render_template('login.html', title='Login', form=form)


@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if 'username' not in session:
        return redirect('login')
    if form.validate_on_submit():
        task = Task(title=form.title.data, content=form.content.data, user_name=session['username'], executor=form.executor.data, priority=form.priority.data, category=form.category.data, stage=form.stage.data, done=form.done.data, date_done=str(form.date_done.data))
        db.session.add(task)
        db.session.commit()
        return redirect('home')
    return render_template('add-task.html', title='Add task', form=form, username=session['username'])


# Выход из аккаунта
@app.route('/logout')
def logout():
    session.pop('username', 0)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
