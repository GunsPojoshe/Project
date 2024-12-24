# wildberries_api/api_wildberries.py
from flask import jsonify, request
from flask_socketio import emit
import requests
import time
from datetime import datetime, timedelta
from models import WBstocks


API_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQxMTE4djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTc0Nzk0OTkwMCwiaWQiOiIwMTkzNGUxNi0zZTM1LTcwN2QtOTkzYi04YTQ4NjgyMzdkYzciLCJpaWQiOjI1Mzk4OTI2LCJvaWQiOjM5MjU4MDksInMiOjEwNzM3NDk3NTgsInNpZCI6IjhjYmQ5NWM1LTcxYTItNGZkMS1iNGEzLWFmN2EyYjA1OTBhOSIsInQiOmZhbHNlLCJ1aWQiOjI1Mzk4OTI2fQ.wKbTKUOXoIWLvoqChuyCCXNb2OzYwzup1U3E2qhSFI9wpsy7IBtE9CeTwWX7RmjJeH29PE7S3-OeW5lY3B3duA"
API_URL = "https://seller-analytics-api.wildberries.ru/api/v2/nm-report/grouped"
API_STOCKS_URL = "https://statistics-api.wildberries.ru/api/v1/supplier/stocks"



def register_wildberries_routes(app, socketio):
    @app.route("/api/data", methods=["POST"])
    def get_data():
        try:
            data = request.json
            if not data or "begin" not in data or "end" not in data:
                return jsonify({"error": "Неверные входные данные."}), 400

            begin_date = datetime.strptime(data["begin"], "%Y-%m-%d")
            end_date = datetime.strptime(data["end"], "%Y-%m-%d") + timedelta(days=1)

            if begin_date > end_date:
                return jsonify({"error": "Начальная дата не может быть больше конечной."}), 400

            total_days = (end_date - begin_date).days
            processed_days = 0
            headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
            total_metrics = {
                "openCardCount": 0,
                "addToCartCount": 0,
                "ordersCount": 0,
                "ordersSumRub": 0,
                "buyoutsCount": 0,
                "buyoutsSumRub": 0,
                "cancelCount": 0,
                "cancelSumRub": 0
            }

            max_days_per_request = 30
            current_date = begin_date

            while current_date < end_date:
                next_date = min(current_date + timedelta(days=max_days_per_request), end_date)
                payload = {
                    "period": {
                        "begin": current_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "end": next_date.strftime("%Y-%m-%d %H:%M:%S")
                    },
                    "groupBy": "brandNames",
                    "fields": ["openCardCount", "addToCartCount", "ordersCount", "ordersSumRub",
                               "buyoutsCount", "buyoutsSumRub", "cancelCount", "cancelSumRub"],
                    "page": 1
                }

                while True:
                    response = requests.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 429:
                        emit_progress(socketio, processed_days, total_days, "Ожидание из-за лимита запросов...")
                        time.sleep(60)
                        continue
                    elif response.status_code == 200:
                        break
                    else:
                        return jsonify({"error": f"Ошибка API: {response.status_code} - {response.text}"}), 500

                api_data = response.json()
                if "data" not in api_data or "groups" not in api_data["data"]:
                    return jsonify({"error": "Неверная структура ответа API."}), 500

                for group in api_data["data"]["groups"]:
                    stats = group.get("statistics", {}).get("selectedPeriod", {})
                    total_metrics["openCardCount"] += stats.get("openCardCount", 0)
                    total_metrics["addToCartCount"] += stats.get("addToCartCount", 0)
                    total_metrics["ordersCount"] += stats.get("ordersCount", 0)
                    total_metrics["ordersSumRub"] += stats.get("ordersSumRub", 0)
                    total_metrics["buyoutsCount"] += stats.get("buyoutsCount", 0)
                    total_metrics["buyoutsSumRub"] += stats.get("buyoutsSumRub", 0)
                    total_metrics["cancelCount"] += stats.get("cancelCount", 0)
                    total_metrics["cancelSumRub"] += stats.get("cancelSumRub", 0)

                processed_days += (next_date - current_date).days
                emit_progress(socketio, processed_days, total_days, "Загрузка данных...")
                current_date = next_date

            stocks_response = requests.get(f"{request.url_root}api/stocks", verify=False)
            if stocks_response.status_code == 200:
                stocks_data = stocks_response.json()
                total_metrics.update({
                    "stocksAvailable": stocks_data.get("stocksAvailable", 0),
                    "stocksInTransit": stocks_data.get("stocksInTransit", 0)
                })

            emit_progress(socketio, total_days, total_days, "Загрузка завершена!")
            return jsonify(total_metrics)
        except Exception as e:
            return jsonify({"error": f"Произошла ошибка: {str(e)}"}), 500

    @app.route("/api/stocks", methods=["GET"])
    def get_stocks_data():
        try:
            today = datetime.today().strftime("%Y-%m-%d")
            headers = {"Authorization": f"Bearer {API_TOKEN}", "Content-Type": "application/json"}
            params = {"dateFrom": today, "dateTo": today}

            response = requests.get(API_STOCKS_URL, headers=headers, params=params)

            if response.status_code != 200:
                return jsonify({"error": f"Ошибка API: {response.status_code} - {response.text}"}), 500

            stock_data = response.json()
            stocks_metrics = {
                "date": today,
                "stocks_available": sum(item.get("quantity", 0) for item in stock_data),
                "stocks_in_transit": sum(item.get("inWayToClient", 0) for item in stock_data),
                "stocks_reserved": sum(item.get("stocksReserved", 0) for item in stock_data),
                "stocks_unavailable": sum(item.get("stocksUnavailable", 0) for item in stock_data),
            }

            # Проверяем, есть ли данные для этой даты в новой базе
            existing_stock = WBstocks.query.filter_by(date=today).first()
            if not existing_stock:
                # Сохраняем новые данные в новую базу
                new_stock = Stock(
                    date=stocks_metrics["date"],
                    stocks_available=stocks_metrics["stocks_available"],
                    stocks_in_transit=stocks_metrics["stocks_in_transit"],
                    stocks_reserved=stocks_metrics["stocks_reserved"],
                    stocks_unavailable=stocks_metrics["stocks_unavailable"]
                )
                db.session.add(new_stock)
                db.session.commit()

            return jsonify(stocks_metrics)
        except Exception as e:
            return jsonify({"error": f"Произошла ошибка: {str(e)}"}), 500

    def emit_progress(socketio, processed, total, message):
        progress = (processed / total) * 100
        socketio.emit("progress", {"progress": progress, "message": message}, to=None)

#Запоминай и жди следующий файл