document.addEventListener("DOMContentLoaded", function () {
    const toggleCheckbox = document.getElementById("toggleTableCheckbox");
    const tableWrapper = document.getElementById("tableWrapper");
    const columnToggles = document.querySelectorAll(".column-toggle");
    const table = document.querySelector(".sales-table");

    // Изначально показываем таблицу
    tableWrapper.style.display = "block";

    // === Переключение видимости всей таблицы ===
    toggleCheckbox.addEventListener("change", () => {
        tableWrapper.style.display = toggleCheckbox.checked ? "block" : "none";
    });

    // === Загрузка названий колонок с сервера ===
    fetch("/api/columns")
        .then((response) => response.json())
        .then((data) => {
            for (const [key, value] of Object.entries(data)) {
                const titleElement = document.querySelector(`.column-title[data-column="${key}"]`);
                if (titleElement) {
                    titleElement.textContent = value;
                }
            }
        })
        .catch(() => alert("Ошибка загрузки данных с сервера"));

    // === Редактирование названий колонок ===
    document.querySelectorAll('.edit-column-btn').forEach((button) => {
        button.addEventListener('click', () => {
            const columnKey = button.dataset.column;
            const titleElement = document.querySelector(`.column-title[data-column="${columnKey}"]`);
            const currentTitle = titleElement ? titleElement.textContent : '';

            const newTitle = prompt('Введите новое название для колонки:', currentTitle);
            if (newTitle && newTitle.trim() !== '') {
                if (titleElement) titleElement.textContent = newTitle;

                // Отправка на сервер
                fetch("/api/columns", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ column_key: columnKey, column_name: newTitle }),
                }).then((response) => {
                    if (!response.ok) {
                        alert("Ошибка при сохранении данных на сервере");
                    }
                }).catch(() => {
                    alert("Ошибка при отправке данных на сервер");
                });
            }
        });
    });

    // === Управление видимостью колонок через выпадающее меню ===
    columnToggles.forEach((toggle) => {
        toggle.addEventListener("change", () => {
            const columnIndex = toggle.dataset.column;
            const cells = table.querySelectorAll(
                `td:nth-child(${parseInt(columnIndex) + 1}), th:nth-child(${parseInt(columnIndex) + 1})`
            );

            cells.forEach((cell) => {
                cell.style.display = toggle.checked ? "" : "none";
            });
        });
    });
});
