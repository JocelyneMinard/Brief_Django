(() => {
    const resultsContainer = document.getElementById("catalog-results");
    const filterForm = document.getElementById("catalog-filter-form");
    const categoryInput = document.getElementById("category-input");
    const authorInput = document.getElementById("author-input");
    const resetBtn = document.getElementById("reset-filters-btn");
    const categoryLinks = document.querySelectorAll("#category-filters .category-pill");

    if (!resultsContainer || !filterForm) return;

    let debounceTimer = null;

    function updateActiveCategoryPill(categoryValue) {
        categoryLinks.forEach((link) => {
            const linkCategory = link.dataset.category || "";
            link.classList.toggle("is-active", linkCategory === String(categoryValue || ""));
        });
    }

    function buildUrlFromState(page = null) {
        const params = new URLSearchParams();
        const category = (categoryInput.value || "").trim();
        const author = (authorInput.value || "").trim();

        if (category) params.set("category", category);
        if (author) params.set("author", author);
        if (page) params.set("page", String(page));

        const queryString = params.toString();
        return queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    }

    async function loadCatalog(url, pushHistory = true) {
        resultsContainer.classList.add("is-loading");

        try {
            const response = await fetch(url, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const html = await response.text();
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, "text/html");
            const nextResults = doc.getElementById("catalog-results");

            if (nextResults) {
                resultsContainer.innerHTML = nextResults.innerHTML;
            }

            if (pushHistory) {
                window.history.pushState({}, "", url);
            }
        } catch (error) {
            console.error("Erreur lors du chargement du catalogue :", error);
            window.location.href = url;
        } finally {
            resultsContainer.classList.remove("is-loading");
        }
    }

    // Clic sur une catégorie (div / lien stylisé)
    categoryLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            const selectedCat = link.dataset.category || "";
            categoryInput.value = selectedCat;
            updateActiveCategoryPill(selectedCat);
            loadCatalog(buildUrlFromState(1));
        });
    });

    // Soumission du formulaire (entrée ou clic sur Rechercher)
    filterForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        loadCatalog(buildUrlFromState(1));
    });

    // Recherche dynamique pendant la saisie (avec léger debounce)
    authorInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            loadCatalog(buildUrlFromState(1));
        }, 250);
    });

    // Bouton réinitialiser
    if (resetBtn) {
        resetBtn.addEventListener("click", (event) => {
            event.preventDefault();
            categoryInput.value = "";
            authorInput.value = "";
            updateActiveCategoryPill("");
            loadCatalog(window.location.pathname);
        });
    }

    // Pagination asynchrone (délégation d'événement car #catalog-results est remplacé)
    resultsContainer.addEventListener("click", (event) => {
        const pageLink = event.target.closest(".pagination a[data-page]");
        if (!pageLink) return;

        event.preventDefault();
        const page = pageLink.dataset.page;
        loadCatalog(buildUrlFromState(page));
    });

    // Support des boutons Précédent / Suivant du navigateur
    window.addEventListener("popstate", () => {
        const params = new URLSearchParams(window.location.search);
        const cat = params.get("category") || "";
        const author = params.get("author") || "";
        categoryInput.value = cat;
        authorInput.value = author;
        updateActiveCategoryPill(cat);
        loadCatalog(window.location.href, false);
    });
})();

const sidebar = document.getElementById("filter-sidebar");
const toggleBtn = document.getElementById("toggle-filters-btn");
const closeBtn = document.getElementById("close-filters-btn");
const backdrop = document.getElementById("sidebar-backdrop");

function setSidebarOpen(isOpen) {
    if (!sidebar) return;
    sidebar.classList.toggle("is-open", isOpen);
    if (toggleBtn) {
        toggleBtn.setAttribute("aria-expanded", String(isOpen));
    }
    if (backdrop) {
        backdrop.hidden = !isOpen;
    }
    document.body.style.overflow = isOpen && window.innerWidth <= 768 ? "hidden" : "";
}

if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        const isCurrentlyOpen = sidebar?.classList.contains("is-open");
        setSidebarOpen(!isCurrentlyOpen);
    });
}

if (closeBtn) {
    closeBtn.addEventListener("click", () => setSidebarOpen(false));
}

if (backdrop) {
    backdrop.addEventListener("click", () => setSidebarOpen(false));
}

document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && sidebar?.classList.contains("is-open")) {
        setSidebarOpen(false);
    }
});

// Ferme automatiquement le tiroir sur mobile après un clic sur une catégorie ou un reset
document.addEventListener("click", (event) => {
    if (window.innerWidth > 768) return;
    if (event.target.closest("#category-filters .category-pill") || event.target.closest("#reset-filters-btn")) {
        setSidebarOpen(false);
    }
});

window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
        setSidebarOpen(false);
    }
});
