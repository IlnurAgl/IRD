from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm, TaskForm, GiveForm
from flask_login import UserMixin
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
    admin = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=True)

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
    delete = db.Column(db.Boolean)
    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


# Создание моделей в базе данных
db.create_all()


# Создание запросов

# Домашняя страница
@app.route('/')
@app.route('/home')
def home():
    if 'username' not in session:
        return redirect('register')
    return render_template('home.html', username=session['username'], tasks=Task.query.filter_by(user_name=session['username']), user=User.query.filter_by(username=session['username']).first())


# Регистрация
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
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, admin=False)
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


# Страница для администратора
@app.route('/users')
def admin():
    if 'username' not in session:
        return redirect('login')
    if not User.query.filter_by(username=session['username']).first().admin:
        return redirect('home')
    return render_template('users.html', users=User.query.all())


@app.route('/status_change/<int:user_id>')
def status_change(user_id):
    if 'username' not in session:
        return redirect('login')
    if not User.query.filter_by(username=session['username']).first().admin:
        return redirect('home')
    user = User.query.filter_by(id=user_id).first()
    if user.status:
        user.status = False
    else:
        user.status = True
    db.session.commit()
    return redirect('/users')

@app.route('/admin_change/<int:user_id>')
def admin_change(user_id):
    if 'username' not in session:
        return redirect('login')    
    if not User.query.filter_by(username=session['username']).first().admin:
        return redirect('home')
    user = User.query.filter_by(id=user_id).first()
    user.admin = True
    db.session.commit()
    return redirect('/users')

# Добавление задачи
@app.route('/add-task', methods=['GET', 'POST'])
def add_task():
    form = TaskForm()
    if 'username' not in session:
        return redirect('login')
    if not User.query.filter_by(username=session['username']).first().status:
        return redirect('home')
    if form.validate_on_submit():
        task = Task(title=form.title.data, content=form.content.data, user_name=session['username'], executor=form.executor.data, priority=form.priority.data, category=form.category.data, stage=form.stage.data, done=form.done.data, date_done=str(form.date_done.data))
        db.session.add(task)
        db.session.commit()
        return redirect('home')
    return render_template('add-task.html', title='Add task', form=form, username=session['username'])


# Редактирование задачи
@app.route('/edit-task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'username' not in session:
        return redirect('login')
    if not User.query.filter_by(username=session['username']).first().status:
        return redirect('home')
    val = Task.query.filter_by(id=task_id).first()
    form = TaskForm()
    if form.validate_on_submit():
        val.title = form.title.data
        val.content = form.content.data
        val.executor = form.executor.data
        val.date_done = form.date_done.data
        val.priority = form.priority.data
        val.category = form.category.data
        val.stage = form.stage.data
        val.done = form.done.data
        db.session.commit()
        return redirect('home')
    return render_template('edit-task.html', form=form, val=val, users=User.query.all())


# Получение полной информации о задаче
@app.route('/task/<int:task_id>')
def task_info(task_id):
    if 'username' not in session:
        return redirect('login')
    if session['username'] not in Task.query.filter_by(id=task_id).first().user_name.split():
        return redirect('home')
    return render_template('task.html', task=Task.query.filter_by(id=task_id).first())


# Отправка задачи
@app.route('/give_task/<int:task_id>')
def give_task(task_id):
    if 'username' not in session:
        return redirect('login')
    if session['username'] not in Task.query.filter_by(id=task_id).first().user_name.split():
        return redirect('home')
    task = Task.query.filter_by(id=task_id).first()
    form = GiveForm()
    if form.validate_on_submit():
        user_id = form.user_id.data
        if not User.query.filter_by(id=user_id).first():
            return redirect('give_task')
        task.user_name += ' ' + User.query.filter_by(id=user_id).first().username
        return redirect('home')
    return render_template('give_task.html', users=User.query.all())


# Удаление записи
@app.route('/del-task/<int:task_id>')
def task_del(task_id):
    if 'username' not in session:
        return redirect('login')
    if session['username'] not in Task.query.filter_by(id=task_id).first().user_name.split():
        return redirect('home')
    task = Task.query.filter_by(id=task_id).first()
    if task.delete:
        task.delete = False
    else:
        task.delete = True
    db.session.commit()
    return redirect('home')


# Выход из аккаунта
@app.route('/logout')
def logout():
    session.pop('username', 0)
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)
