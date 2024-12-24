# database_operations #

from models import WBstocks, WBsales, db
from datetime import datetime

def save_WBstocks(data):
    """Сохранение данных в таблицу WBstocks."""
    stock = WBstocks.query.filter_by(date=data['date']).first()
    if not stock:
        stock = WBstocks(
            date=data['date'],
            stocks_available=data['stocks_available'],
            stocks_in_transit=data['stocks_in_transit'],
            stocks_reserved=data['stocks_reserved'],
            stocks_unavailable=data['stocks_unavailable']
        )
        db.session.add(stock)
        db.session.commit()
    return stock

def save_WBsales(data):
    """Сохранение данных в таблицу WBsales."""
    sale = WBsales(
        date=data['date'],
        sales_count=data['sales_count'],
        sales_amount=data['sales_amount']
    )
    db.session.add(sale)
    db.session.commit()
    return sale
