const filters = document.querySelectorAll(".filter");
const newsContainer = document.querySelector(".news-grid");
const eventsContainer = document.querySelector(".event-list");
const dialog = document.querySelector("#story-dialog");

let news = [];
let selectedCategory = "all";

// Состояние загрузки новостей
function showLoading() {
    newsContainer.textContent = "Загружаем новости...";
}

// Ошибка загрузки новостей
function showError(message) {
    newsContainer.replaceChildren();

    const error = document.createElement("p");
    error.className = "error-state";
    error.textContent = message;

    const retry = document.createElement("button");
    retry.textContent = "Повторить";
    retry.addEventListener("click", loadNews);

    error.append(" ", retry);
    newsContainer.append(error);
}

// Отображение новостей
function renderNews() {
    const filteredNews = selectedCategory === "all"
        ? news
        : news.filter(item => item.category === selectedCategory);

    newsContainer.replaceChildren();

    if (filteredNews.length === 0) {
        const empty = document.createElement("p");
        empty.className = "empty-state";
        empty.textContent = "Новостей пока нет.";
        newsContainer.append(empty);
        return;
    }

    filteredNews.forEach(item => {
        const card = document.createElement("article");
        card.className = "news-card";
        card.dataset.category = item.category;

        const category = document.createElement("span");
        category.className = "news-category";
        category.textContent = item.category.toUpperCase();

        const title = document.createElement("h3");
        title.textContent = item.title;

        const summary = document.createElement("p");
        summary.textContent = item.summary;

        const button = document.createElement("button");
        button.className = "read-more";
        button.textContent = "Читать далее";
        button.dataset.id = item.id;

        button.addEventListener("click", () => {
            openStory(item.id);
        });

        card.append(category, title, summary, button);
        newsContainer.append(card);
    });
}

// Загрузка новостей
async function loadNews() {
    showLoading();

    try {
        const response = await fetch("/api/news");

        if (!response.ok) {
            throw new Error("Ошибка сервера: " + response.status);
        }

        news = await response.json();
        renderNews();
    } catch (error) {
        console.error("Ошибка загрузки новостей:", error);
        showError("Не удалось загрузить новости.");
    }
}

// Открытие отдельной новости
async function openStory(id) {
    try {
        const response = await fetch(`/api/news/${id}`);

        if (!response.ok) {
            throw new Error("Новость не найдена");
        }

        const story = await response.json();

        document.querySelector("#story-category").textContent =
            story.category.toUpperCase();

        document.querySelector("#story-title").textContent =
            story.title;

        document.querySelector("#story-description").textContent =
            story.summary;

        dialog.showModal();
    } catch (error) {
        console.error("Ошибка открытия новости:", error);
        alert("Не удалось открыть новость.");
    }
}

// Фильтры новостей
filters.forEach(button => {
    button.addEventListener("click", () => {
        selectedCategory = button.dataset.filter;

        filters.forEach(filter => {
            const active = filter === button;
            filter.classList.toggle("active", active);
            filter.setAttribute("aria-pressed", String(active));
        });

        renderNews();
    });
});

// Закрытие модального окна
document.querySelector(".dialog-close").addEventListener("click", () => {
    dialog.close();
});

dialog.addEventListener("click", event => {
    if (event.target === dialog) {
        dialog.close();
    }
});

// Состояние загрузки событий
function showEventsLoading() {
    eventsContainer.textContent = "Загружаем события...";
}

// Загрузка событий из базы данных
async function loadEvents() {
    showEventsLoading();

    try {
        const response = await fetch("/api/events");

        if (!response.ok) {
            throw new Error("Ошибка сервера: " + response.status);
        }

        const events = await response.json();

        eventsContainer.replaceChildren();

        if (events.length === 0) {
            eventsContainer.textContent = "Событий пока нет.";
            return;
        }

        events.forEach(event => {
            const date = new Date(event.starts_at);

            const card = document.createElement("article");
            card.className = "event";

            const dateBlock = document.createElement("div");
            dateBlock.className = "event-date";

            const day = document.createElement("strong");
            day.textContent = date.toLocaleDateString("ru-RU", {
                day: "2-digit",
                timeZone: "UTC"
            });

            const month = document.createElement("span");
            month.textContent = date.toLocaleDateString("ru-RU", {
                month: "short",
                timeZone: "UTC"
            }).toUpperCase();

            dateBlock.append(day, month);

            const info = document.createElement("div");
            info.className = "event-info";

            const title = document.createElement("h3");
            title.textContent = event.title;

            const description = document.createElement("p");
            description.textContent =
                event.description || "Описание отсутствует.";

            info.append(title, description);

            const type = document.createElement("span");
            type.className = "event-type";
            type.textContent = "СОБЫТИЕ";

            card.append(dateBlock, info, type);
            eventsContainer.append(card);
        });

    } catch (error) {
        console.error("Ошибка загрузки событий:", error);

        eventsContainer.replaceChildren();

        const message = document.createElement("p");
        message.className = "error-state";
        message.textContent = "Не удалось загрузить события.";

        const retry = document.createElement("button");
        retry.textContent = "Повторить";
        retry.addEventListener("click", loadEvents);

        eventsContainer.append(message, retry);
    }
}

// Запуск приложения
loadNews();
loadEvents();
