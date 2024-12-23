// scripts.js

document.addEventListener("DOMContentLoaded", function () {
    const toggleButton = document.getElementById("toggleTableBtn");
    const tableWrapper = document.getElementById("tableWrapper");

    // Проверка существования элементов
    if (!toggleButton || !tableWrapper) {
        console.error("Элементы переключателя или таблицы не найдены!");
        return;
    }

    // Переключение видимости таблицы
    toggleButton.addEventListener("click", () => {
        const isHidden = tableWrapper.style.display === "none";
        tableWrapper.style.display = isHidden ? "block" : "none";
        toggleButton.textContent = isHidden ? "Скрыть" : "Показать";
    });



    // Элементы для управления видимостью блока
    const toggleMethod = document.getElementById("toggle-method");
    const clientApiSettings = document.getElementById("client-api-settings");

    if (toggleMethod && clientApiSettings) {
        // Функция для управления видимостью блока
        const toggleVisibility = () => {
            if (toggleMethod.checked) {
                clientApiSettings.classList.remove("hidden");
            } else {
                clientApiSettings.classList.add("hidden");
            }
        };

        // Инициализация видимости при загрузке страницы
        toggleVisibility();

        // Слушатель событий переключателя
        toggleMethod.addEventListener("change", toggleVisibility);
    }
});

