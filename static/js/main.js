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
// CSRF HELPER
// =========================
function getCSRFToken() {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let cookie of cookies) {
            cookie = cookie.trim();

            if (cookie.startsWith("csrftoken=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring("csrftoken=".length)
                );
                break;
            }
        }
    }

    return cookieValue;
}


// =========================
// LIKE SYSTEM (FIXED)
// =========================
console.log("Cookies:", document.cookie);
console.log("CSRF:", getCSRFToken());
fetch(`/like/${id}/`, {
    method: "POST",
    credentials: "same-origin",
    headers: {
        "X-CSRFToken": getCSRFToken(),
        "X-Requested-With": "XMLHttpRequest"
    }
})

function likeRecipe(id) {
    const heart = document.getElementById(`heart-${id}`);
    const likesEl = document.getElementById(`likes-${id}`);

    if (!heart || !likesEl) return;

    let likedRecipes = JSON.parse(localStorage.getItem("likedRecipes")) || {};

    //уже лайкнул — стоп
    if (likedRecipes[id]) return;

    fetch(`/like/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => {
        if (!res.ok) throw new Error("Server error");
        return res.json();
    })
    .then(data => {
        likesEl.innerText = data.likes;

        heart.classList.remove("fa-regular");
        heart.classList.add("fa-solid");

        heart.classList.add("like-pop");
        setTimeout(() => heart.classList.remove("like-pop"), 300);

        likedRecipes[id] = true;
        localStorage.setItem("likedRecipes", JSON.stringify(likedRecipes));
    })
    .catch(err => {
        console.error("Like error:", err);
    });
}


// =========================
// RESTORE LIKES
// =========================
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
// LIVE SEARCH (IMPROVED)
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

            resultsBox.innerHTML = "<div class='p-2 text-gray-400'>Searching...</div>";
            resultsBox.classList.remove("hidden");

            fetch(`/live-search/?q=${encodeURIComponent(query)}`)
                .then(res => {
                    if (!res.ok) throw new Error("Search error");
                    return res.json();
                })
                .then(data => {
                    resultsBox.innerHTML = "";

                    if (!data.results?.length) {
                        resultsBox.innerHTML = "<div class='p-2 text-gray-400'>No results 😢</div>";
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
                })
                .catch(err => {
                    console.error(err);
                    resultsBox.innerHTML = "<div class='p-2 text-red-400'>Error 😢</div>";
                });

        }, 300);
    });

    // закрытие
    document.addEventListener("click", (e) => {
        if (wrapper && !wrapper.contains(e.target)) {
            resultsBox.classList.add("hidden");
        }
    });
});


// =========================
// FAVORITE SYSTEM (FIXED)
// =========================
function toggleFavorite(id) {
    const btn = document.getElementById(`fav-${id}`);
    const text = btn.querySelector(".text");

    fetch(`/favorite/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {
        console.log(data);

        if (data.status === "added") {
            btn.classList.remove("bg-red-500");
            btn.classList.add("bg-green-500");
            text.innerText = "Favorited ✓";
        } else {
            btn.classList.remove("bg-green-500");
            btn.classList.add("bg-red-500");
            text.innerText = "Favorite";
        }
    })
    .catch(err => console.log(err));
}

function togglePassword(id, el) {
    const input = document.getElementById(id);

    if (!input) {
        console.log("NOT FOUND:", id);
        return;
    }

    if (input.type === "password") {
        input.type = "text";
        el.textContent = "👁️";
    } else {
        input.type = "password";
        el.textContent = "🙈";
    }
}

//Save btn
function saveRecipe(id) {
    const btn = document.getElementById(`save-${id}`);

    fetch(`/save/${id}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "X-Requested-With": "XMLHttpRequest"
        }
    })
    .then(res => res.json())
    .then(data => {

        if (data.saved) {
            btn.innerText = "Saved ✓";
            btn.classList.add("bg-green-500");
        } else {
            btn.innerText = "Save";
            btn.classList.remove("bg-green-500");
        }

    })
    .catch(err => console.log(err));
}

// Profile menu
const profileBtn = document.getElementById("profileBtn");
const profileMenu = document.getElementById("profileMenu");

if (profileBtn) {
  profileBtn.addEventListener("click", () => {
    profileMenu.classList.toggle("hidden");
  });

  // Закрытие при клике вне
  document.addEventListener("click", (e) => {
    if (!profileBtn.contains(e.target) && !profileMenu.contains(e.target)) {
      profileMenu.classList.add("hidden");
    }
  });
}


function showRatingToast() {

    const toast = document.getElementById("rating-toast");

    toast.classList.remove("opacity-0", "pointer-events-none");
    toast.classList.add("opacity-100");

    setTimeout(() => {

        toast.classList.remove("opacity-100");
        toast.classList.add("opacity-0", "pointer-events-none");

    }, 2500);

}

function toggleMenu(){

    const menu = document.getElementById("mobileMenu");

    menu.classList.toggle("hidden");

}

console.log("MAIN JS LOADED 🔥");
