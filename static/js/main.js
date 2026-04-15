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
// ❤️ LIKE SYSTEM (FIXED)
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
// 🔎 LIVE SEARCH (SAFE)
// =========================
let timeout = null;

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("search-input");
    const resultsBox = document.getElementById("search-results");

    if (!input || !resultsBox) return;

    input.addEventListener("keyup", function () {
        clearTimeout(timeout);

        timeout = setTimeout(() => {
            const query = input.value.trim();

            if (query.length < 2) {
                resultsBox.style.display = "none";
                return;
            }

            fetch(`/live-search/?q=${query}`)
                .then(res => res.json())
                .then(data => {
                    resultsBox.innerHTML = "";

                    if (!data.results || data.results.length === 0) {
                        resultsBox.innerHTML = "<div style='padding:10px;'>No results 😢</div>";
                        resultsBox.style.display = "block";
                        return;
                    }

                    data.results.forEach(item => {
                        const div = document.createElement("div");
                        div.classList.add("search-item");

                        div.innerHTML = `
                            <img src="${item.image}">
                            <span>${item.title}</span>
                        `;

                        div.onclick = () => {
                            window.location.href = `/recipe/${item.id}/`;
                        };

                        resultsBox.appendChild(div);
                    });

                    resultsBox.style.display = "block";
                })
                .catch(err => console.error("Search error:", err));

        }, 300);
    });


    // CLICK OUTSIDE
    document.addEventListener("click", (e) => {
        const wrapper = document.querySelector(".search-wrapper");
        if (wrapper && !wrapper.contains(e.target)) {
            resultsBox.style.display = "none";
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