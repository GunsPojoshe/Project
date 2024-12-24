# app.py #

from flask import Flask, render_template, redirect, url_for, request, flash, session, get_flashed_messages, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Подключение Flask-Migrate
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_socketio import SocketIO
from wildberries_api.api_wildberries import register_wildberries_routes
from models import db, WBstocks, WBsales, User
from sqlalchemy import text

# Инициализация приложения
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Инициализация SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Конфигурация базы данных Main.db
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'Main.db')

# Инициализация базы данных и миграций
db.init_app(app)
migrate = Migrate(app, db)

# Регистрация маршрутов Wildberries
register_wildberries_routes(app, socketio)
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

    user = db.session.get(User, session['user_id'])
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
    return render_template("sales.html")

# Остатки
@app.route("/stock")
def stock():
    return render_template("stock.html")

@app.route("/debug/stocks", methods=["GET"])
def debug_stocks():
    try:
        stocks = Stock.query.all()
        stock_list = [
            {
                "id": stock.id,
                "date": stock.date.strftime("%Y-%m-%d"),
                "stocks_available": stock.stocks_available,
                "stocks_in_transit": stock.stocks_in_transit,
                "stocks_reserved": stock.stocks_reserved,
                "stocks_unavailable": stock.stocks_unavailable,
            }
            for stock in stocks
        ]
        return jsonify(stock_list)
    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)

