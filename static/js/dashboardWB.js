// dashboard.js
document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('data-container');
    const metricElements = {
        openCardCount: document.getElementById('openCardCount'),
        addToCartCount: document.getElementById('addToCartCount'),
        ordersCount: document.getElementById('ordersCount'),
        ordersSumRub: document.getElementById('ordersSumRub'),
        buyoutsCount: document.getElementById('buyoutsCount'),
        buyoutsSumRub: document.getElementById('buyoutsSumRub'),
        cancelCount: document.getElementById('cancelCount'),
        cancelSumRub: document.getElementById('cancelSumRub'),
        stocksAvailable: document.getElementById('stocksAvailable'),
        stocksInTransit: document.getElementById('stocksInTransit')
    };

    fetch('/api/data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ begin: '2024-01-01', end: '2024-01-31' }),
    })
        .then(response => response.json())
        .then(data => {
            // Обновляем значения карточек
            Object.keys(metricElements).forEach(key => {
                if (metricElements[key]) {
                    metricElements[key].querySelector('h3').textContent = key.includes('SumRub')
                        ? `₽ ${data[key] || 0}`
                        : data[key] || 0;

                    // Пример: можно добавить тренды или разницы
                    metricElements[key].querySelector('.difference').textContent = `+0`;
                    metricElements[key].querySelector('.trend').textContent = `0%`;
                }
            });

            // Удаляем JSON, если он выводится в контейнер
            if (container) {
                container.textContent = '';
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
            if (container) {
                container.textContent = 'Ошибка загрузки данных.';
            }
        });
});

document.addEventListener("DOMContentLoaded", () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);

    const formattedYesterday = yesterday.toISOString().split("T")[0];
    document.getElementById("begin").value = formattedYesterday;
    document.getElementById("end").value = formattedYesterday;

    fetchData();
});

async function fetchData() {
    const begin = document.getElementById("begin").value; // Дата начала
    const end = document.getElementById("end").value; // Дата конца
    const button = document.querySelector(".filters button");

    // Добавляем анимацию загрузки на кнопку
    button.classList.add("loading");
    button.disabled = true;

    try {
        // Загрузка метрик (основных данных)
        const response = await fetch("/api/data", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ begin, end }),
        });

        if (response.ok) {
            const currentData = await response.json();

            const days = calculateDays(begin, end);
            const previousBegin = shiftDate(begin, -days);
            const previousEnd = shiftDate(end, -days);

            const previousResponse = await fetch("/api/data", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ begin: previousBegin, end: previousEnd }),
            });

            const previousData = previousResponse.ok ? await previousResponse.json() : {};
            updateMetrics(currentData, previousData);
        } else {
            console.error("Ошибка при загрузке данных:", await response.text());
        }

        // Загрузка данных для склада (переходим на GET)
        const stockResponse = await fetch(`/api/stocks?begin=${begin}&end=${end}`, {
            method: "GET",  // Используем GET вместо POST
        });

        if (stockResponse.ok) {
            const stockData = await stockResponse.json();
            updateStockMetrics(stockData);
        } else {
            console.error("Ошибка при загрузке данных склада:", await stockResponse.text());
        }

    } catch (err) {
        console.error("Ошибка:", err);
    } finally {
        // Убираем анимацию загрузки с кнопки
        button.classList.remove("loading");
        button.disabled = false;
    }
}


function calculateDays(begin, end) {
    const beginDate = new Date(begin);
    const endDate = new Date(end);
    return Math.ceil((endDate - beginDate) / (1000 * 60 * 60 * 24)) + 1;
}

function shiftDate(date, shiftDays) {
    const newDate = new Date(date);
    newDate.setDate(newDate.getDate() + shiftDays);
    return newDate.toISOString().split("T")[0];
}

function formatNumber(num, includeCurrency = false) {
    return includeCurrency ? `₽ ${num.toLocaleString("ru-RU")}` : num.toLocaleString("ru-RU");
}

function updateMetrics(current, previous) {
    const keys = [
        "openCardCount",
        "addToCartCount",
        "ordersCount",
        "ordersSumRub",
        "buyoutsCount",
        "buyoutsSumRub",
        "cancelCount",
        "cancelSumRub",
    ];

    const averageChecks = {
        orders: calculateAverageCheck(current.ordersSumRub, current.ordersCount),
        buyouts: calculateAverageCheck(current.buyoutsSumRub, current.buyoutsCount),
        returns: calculateAverageCheck(current.cancelSumRub, current.cancelCount),
    };

    keys.forEach((key) => {
        const card = document.getElementById(key);
        const currentValue = current[key] || 0;
        const previousValue = previous[key] || 0;

        const trend =
            previousValue > 0
                ? (((currentValue - previousValue) / previousValue) * 100).toFixed(2)
                : 0;

        const difference = currentValue - previousValue;

        card.querySelector("h3").textContent = key.includes("SumRub")
            ? formatNumber(currentValue, true)
            : formatNumber(currentValue);

        const isReverse = key === "cancelCount" || key === "cancelSumRub";
        const trendElement = card.querySelector(".trend");
        const differenceElement = card.querySelector(".difference");

        const trendClass = trend > 0 ? (isReverse ? "negative" : "positive") : trend < 0 ? (isReverse ? "positive" : "negative") : "neutral";
        const differenceClass = difference > 0 ? (isReverse ? "negative" : "positive") : difference < 0 ? (isReverse ? "positive" : "negative") : "neutral";

        trendElement.textContent = `${trend > 0 ? "+" : ""}${trend}%`;
        trendElement.className = `trend ${trendClass}`;

        differenceElement.textContent = `${difference > 0 ? "+" : ""}${formatNumber(difference, key.includes("SumRub"))}`;
        differenceElement.className = `difference ${differenceClass}`;
    });

    updateAverageCheckTiles(averageChecks);
}

function calculateAverageCheck(sum, count) {
    if (count === 0) return 0;
    return (sum / count).toFixed(2);
}

function updateAverageCheckTiles(averages) {
    const ordersTile = document.getElementById("averageOrderCheck");
    const buyoutsTile = document.getElementById("averageBuyoutCheck");
    const returnsTile = document.getElementById("averageReturnCheck");

    ordersTile.querySelector("h3").textContent = formatNumber(averages.orders, true);
    buyoutsTile.querySelector("h3").textContent = formatNumber(averages.buyouts, true);
    returnsTile.querySelector("h3").textContent = formatNumber(averages.returns, true);
}

function updateStockMetrics(stockData) {
    const stockKeys = [
        "stocksAvailable",   // Доступные товары
        "stocksInTransit",   // Товары в пути
        "stocksReserved",    // Резервированные товары
        "stocksUnavailable"  // Недоступные товары
    ];

    stockKeys.forEach((key) => {
        const card = document.getElementById(key);
        const value = stockData[key] || 0;

        card.querySelector("h3").textContent = value.toLocaleString("ru-RU");
        card.querySelector(".difference").textContent = `+${value}`;
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll(".metric-card:not(.dragging)")];
    return draggableElements.reduce(
        (closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            if (offset < 0 && offset > closest.offset) {
                return { offset, element: child };
            } else {
                return closest;
            }
        },
        { offset: Number.NEGATIVE_INFINITY }
    ).element;
}
