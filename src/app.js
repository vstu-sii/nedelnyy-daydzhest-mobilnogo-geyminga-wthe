
const filters = document.querySelectorAll(".filter");
const cards = document.querySelectorAll(".news-card");

filters.forEach((button) => {
    button.addEventListener("click", () => {
        const selectedCategory = button.dataset.filter;

        filters.forEach((filter) => {
            const active = filter === button;
            filter.classList.toggle("active", active);
            filter.setAttribute("aria-pressed", String(active));
        });

        cards.forEach((card) => {
            card.hidden =
                selectedCategory !== "all" &&
                card.dataset.category !== selectedCategory;
        });
    });
});

const stories = [
    {
        category: "НОВОСТИ",
        title: "Новая эра мобильных игровых миров",
        description:
            "Демонстрационный обзор тенденций мобильного гейминга. Перед публикацией добавьте проверенные факты и ссылки на источники."
    },
    {
        category: "ОБНОВЛЕНИЯ",
        title: "Обновления, ради которых стоит вернуться",
        description:
            "Здесь можно рассказать о новых режимах, заданиях и игровых механиках. Замените пример реальной информацией об обновлении."
    },
    {
        category: "РЕЛИЗЫ",
        title: "Что попробовать на этой неделе",
        description:
            "Подборка мобильных игровых новинок. Добавьте подтверждённые названия игр, даты выхода и поддерживаемые платформы."
    }
];

const dialog = document.querySelector("#story-dialog");

document.querySelectorAll(".read-more").forEach((button) => {
    button.addEventListener("click", () => {
        const story = stories[Number(button.dataset.story)];

        if (!story || !dialog) return;

        document.querySelector("#story-category").textContent =
            story.category;

        document.querySelector("#story-title").textContent =
            story.title;

        document.querySelector("#story-description").textContent =
            story.description;

        dialog.showModal();
    });
});

document.querySelector(".dialog-close").addEventListener("click", () => {
    dialog.close();
});

dialog.addEventListener("click", (event) => {
    if (event.target === dialog) {
        dialog.close();
    }
});
