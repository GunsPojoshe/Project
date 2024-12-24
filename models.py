# models.py #
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'  # Указываем имя таблицы явно
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Модель для таблицы WBstocks
class WBstocks(db.Model):
    __tablename__ = 'wbstocks'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, unique=True)
    stocks_available = db.Column(db.Integer, nullable=False, default=0)
    stocks_in_transit = db.Column(db.Integer, nullable=False, default=0)
    stocks_reserved = db.Column(db.Integer, nullable=False, default=0)
    stocks_unavailable = db.Column(db.Integer, nullable=False, default=0)

# Модель для таблицы WBsales
class WBsales(db.Model):
    __tablename__ = 'wbsales'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    sales_count = db.Column(db.Integer, nullable=False, default=0)
    sales_amount = db.Column(db.Float, nullable=False, default=0.0)
