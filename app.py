# app.py #

from flask import Flask, render_template, redirect, url_for, request, flash, session, get_flashed_messages, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Подключение Flask-Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'


# Конфигурация для двух баз данных
basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_BINDS'] = {
    'users': 'sqlite:///' + os.path.join(basedir, 'instance', 'users.db'),
    'sales_funnel': 'sqlite:///' + os.path.join(basedir, 'instance', 'sales_funnel.db')
}

# Инициализация базы данных и миграций
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Настройка миграций

# Модель пользователя
class User(db.Model):
    __bind_key__ = 'users'  # Привязка к базе данных users.db
    __tablename__ = 'users'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


# Создание таблиц в базах данных
with app.app_context():
    # Создаём таблицы для базы данных users.db
    db.metadata.create_all(bind=db.engines['users'])

    # Создаём таблицы для базы данных sales_funnel.db
    db.metadata.create_all(bind=db.engines['sales_funnel'])

    print(app.url_map)

    # Модель для хранения пользовательских названий колонок sales_funnel
class ColumnName(db.Model):
    __bind_key__ = 'sales_funnel'
    __tablename__ = 'column_names'
    id = db.Column(db.Integer, primary_key=True)
    column_key = db.Column(db.String(150), unique=True, nullable=False)
    column_name = db.Column(db.String(150), nullable=False)



# Форма регистрации
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=25, message="Имя пользователя должно быть от 3 до 25 символов")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message="Пароль должен быть не менее 6 символов")
    ])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# Главная страница / Вход
@app.route("/", methods=["GET", "POST"])
def home():
    if 'user_id' not in session:
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash("Вы успешно вошли!", "success")
                return redirect(url_for('home'))
            else:
                flash("Неправильное имя пользователя или пароль.", "danger")
        return render_template("login.html", form=form)

    user = User.query.get(session['user_id'])
    return render_template("home.html", user=user)

# Логин
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Вы успешно вошли!", "success")
            return redirect(url_for('home'))
        else:
            flash("Неправильное имя пользователя или пароль.", "danger")
    return render_template("login.html", form=form)

# Регистрация
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(username=username).first():
            flash("Имя пользователя уже занято.", "danger")
            return render_template("register.html", form=form)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна!", "success")
        return redirect(url_for('home'))
    return render_template("register.html", form=form)

# Профиль
@app.route("/profile")
def profile():
    if 'user_id' not in session:
        flash("Сначала войдите в систему.", "danger")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template("profile.html", user=user)

# Настройки профиля
@app.route("/profilesettings", methods=["GET", "POST"])
def profilesettings():
    if 'user_id' not in session:
        flash("Сначала войдите в систему.", "danger")
        return redirect(url_for('home'))

    user = User.query.get(session['user_id'])
    return render_template("profilesettings.html", user=user)

# Выход
@app.route("/logout")
def logout():
    session.pop('user_id', None)
    get_flashed_messages()
    flash("Вы вышли из системы.", "success")
    return redirect(url_for('login'))

# Продажи
@app.route("/sales", methods=["GET", "POST"])
def sales():
    import sqlite3
    import pandas as pd

    db_path = "instance/sales_funnel.db"
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')

    # Строим запрос с фильтрацией по датам
    query = "SELECT * FROM sales_funnel"
    conditions = []

    # Добавляем условия для фильтрации по дате
    if start_date:
        conditions.append(f"start_date >= '{start_date}'")
    if end_date:
        conditions.append(f"end_date <= '{end_date}'")

    # Если есть условия, добавляем их в запрос
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    # Отладка: выводим сформированный запрос
    print("Сформированный запрос:", query)

    # Выполняем запрос
    conn = sqlite3.connect(db_path)
    sales_data = pd.read_sql(query, conn)
    conn.close()

    # Преобразуем данные в список словарей
    sales_data = sales_data.to_dict(orient="records")
    columns = sales_data[0].keys() if sales_data else []

    return render_template("sales.html", sales_data=sales_data, columns=columns)

# API для работы с названиями колонок sales_funnel
@app.route("/api/columns", methods=["POST", "GET"])
def manage_columns():
    if request.method == "POST":
        data = request.json
        column_key = data.get("column_key")
        column_name = data.get("column_name")

        if not column_key or not column_name:
            print("Invalid data received:", data)
            return jsonify({"error": "Invalid data"}), 400

        column = ColumnName.query.filter_by(column_key=column_key).first()
        if column:
            column.column_name = column_name
        else:
            column = ColumnName(column_key=column_key, column_name=column_name)
            db.session.add(column)
        db.session.commit()
        return jsonify({"success": True})

    elif request.method == "GET":
        columns = ColumnName.query.all()
        print("Отладка: данные из базы column_names:")
        for col in columns:
            print(f"ID: {col.id}, Key: {col.column_key}, Name: {col.column_name}")
        return jsonify({col.column_key: col.column_name for col in columns})

# Остатки
@app.route("/stock")
def stock():
    return render_template("stock.html")

if __name__ == "__main__":
    
    app.run(debug=True)



