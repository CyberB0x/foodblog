// =========================
// TAILWIND CONFIG
// =========================
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#111111',
                secondary: '#1f1f1f',
                accent: '#f59e0b',
            }
        }
    }
};


// =========================
// ❤️ LIKE SYSTEM
// =========================
function likeRecipe(id) {
    const heart = document.getElementById(`heart-${id}`);
    const likesEl = document.getElementById(`likes-${id}`);

    if (!heart || !likesEl) return;

    fetch(`/like/${id}/`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        likesEl.innerText = data.likes;

        heart.classList.remove("fa-regular");
        heart.classList.add("fa-solid");

        heart.classList.add("like-pop");
        setTimeout(() => heart.classList.remove("like-pop"), 300);

        // сохраняем в localStorage
        let likedRecipes = JSON.parse(localStorage.getItem("likedRecipes")) || {};
        likedRecipes[id] = true;
        localStorage.setItem("likedRecipes", JSON.stringify(likedRecipes));
    });
}


// восстановление лайков после перезагрузки
document.addEventListener("DOMContentLoaded", () => {
    let likedRecipes = JSON.parse(localStorage.getItem("likedRecipes")) || {};

    Object.keys(likedRecipes).forEach(id => {
        const heart = document.getElementById(`heart-${id}`);
        if (heart) {
            heart.classList.remove("fa-regular");
            heart.classList.add("fa-solid");
        }
    });
});


// =========================
// 🔎 LIVE SEARCH (FINAL)
// =========================
let timeout = null;

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const resultsBox = document.getElementById("search-results");
    const wrapper = document.querySelector(".search-wrapper");

    if (!input || !resultsBox) return;

    input.addEventListener("keyup", function () {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            const query = input.value.trim();

            if (query.length < 2) {
                resultsBox.classList.add("hidden");
                return;
            }

            // loader
            resultsBox.innerHTML = "<div class='p-2 text-gray-400'>Searching...</div>";
            resultsBox.classList.remove("hidden");

            fetch(`/live-search/?q=${query}`)
                .then(res => res.json())
                .then(data => {
                    resultsBox.innerHTML = "";

                    if (!data.results || data.results.length === 0) {
                        resultsBox.innerHTML = "<div class='p-2 text-gray-400'>No results 😢</div>";
                        resultsBox.classList.remove("hidden");
                        return;
                    }

                    data.results.forEach(item => {
                        const div = document.createElement("div");
                        div.className = "flex items-center gap-2 p-2 hover:bg-gray-700 cursor-pointer transition";

                        div.innerHTML = `
                            <img src="${item.image}" class="w-10 h-10 object-cover rounded">
                            <span>${item.title}</span>
                        `;

                        div.onclick = () => {
                            window.location.href = `/recipe/${item.id}/`;
                        };

                        resultsBox.appendChild(div);
                    });

                    resultsBox.classList.remove("hidden");
                })
                .catch(err => {
                    console.error("Search error:", err);
                    resultsBox.innerHTML = "<div class='p-2 text-red-400'>Error 😢</div>";
                });

        }, 300); // debounce
    });


    // закрытие при клике вне
    document.addEventListener("click", (e) => {
        if (wrapper && !wrapper.contains(e.target)) {
            resultsBox.classList.add("hidden");
        }
    });
});


// =========================
// ⭐ FAVORITE SYSTEM
// =========================
function toggleFavorite(id) {
    fetch(`/favorite/${id}/`, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        const btn = document.getElementById(`fav-${id}`);
        if (!btn) return;

        if (data.status === "added") {
            btn.classList.add("active");
            btn.innerText = "⭐ Saved";
        } else {
            btn.classList.remove("active");
            btn.innerText = "⭐ Favorite";
        }
    })
    .catch(err => console.error("Favorite error:", err));
}