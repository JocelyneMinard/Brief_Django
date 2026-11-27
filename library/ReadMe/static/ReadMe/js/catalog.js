/***************************************************************
 JS of the catalog page exclusively
 ***************************************************************/

(() => {
    const resultsContainer = document.getElementById("catalog-results");
    const filterForm = document.getElementById("catalog-filter-form");
    const categoryInput = document.getElementById("category-input");
    const searchInput = document.getElementById("search-input");
    const resetBtn = document.getElementById("reset-filters-btn");
    const categoryLinks = document.querySelectorAll("#category-filters .category-pill");

    // Exit early if the core catalog elements are not present on the current page
    if (!resultsContainer || !filterForm) return;

    let debounceTimer = null;

    /**
     * Highlight the category pill matching the active category value
     * @param {string} categoryValue - Currently selected category identifier or empty string.
     */
    function updateActiveCategoryPill(categoryValue) {
        categoryLinks.forEach((link) => {
            const linkCategory = link.dataset.category || "";
            link.classList.toggle("is-active", linkCategory === String(categoryValue || ""));
        });
    }

    /**
     * Build a catalog URL with active category, search query, and optional page parameters
     * @param {number|string|null} [page=null] - Target page number to include in query params
     * @returns {string} Constructed relative URL
     */
    function buildUrlFromState(page = null) {
        const params = new URLSearchParams();
        const category = (categoryInput?.value || "").trim();
        const query = (searchInput?.value || "").trim();

        if (category) params.set("category", category);
        if (query) params.set("q", query);
        if (page) params.set("page", String(page));

        const queryString = params.toString();
        return queryString ? `${window.location.pathname}?${queryString}` : window.location.pathname;
    }

    /**
     * Fetch updated catalog HTML asynchronously and replace the results container.
     * Falls back to a full page navigation on fetch or parsing errors.
     * @param {string} url - Target catalog URL to fetch.
     * @param {boolean} [pushHistory=true] - Whether to push a new entry into browser history.
     */
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

    // Filter by category pill click and reset pagination to page 1
    categoryLinks.forEach((link) => {
        link.addEventListener("click", (event) => {
            event.preventDefault();
            const selectedCat = link.dataset.category || "";
            if (categoryInput) categoryInput.value = selectedCat;
            updateActiveCategoryPill(selectedCat);
            loadCatalog(buildUrlFromState(1));
        });
    });

    // Handle explicit form submission (Enter key or search button)
    filterForm.addEventListener("submit", (event) => {
        event.preventDefault();
        clearTimeout(debounceTimer);
        loadCatalog(buildUrlFromState(1));
    });

    // Debounce live search requests while typing in the search input
    if (searchInput) {
        searchInput.addEventListener("input", () => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                loadCatalog(buildUrlFromState(1));
            }, 250);
        });
    }

    // Clear active filters and reload the unfiltered catalog base URL
    if (resetBtn) {
        resetBtn.addEventListener("click", (event) => {
            event.preventDefault();
            if (categoryInput) categoryInput.value = "";
            if (searchInput) searchInput.value = "";
            updateActiveCategoryPill("");
            loadCatalog(window.location.pathname);
        });
    }

    // Delegate pagination clicks because #catalog-results inner HTML is replaced dynamically
    resultsContainer.addEventListener("click", (event) => {
        const pageLink = event.target.closest(".pagination a[data-page]");
        if (!pageLink) return;

        event.preventDefault();
        const page = pageLink.dataset.page;
        loadCatalog(buildUrlFromState(page));
    });

    // Sync filter inputs, active pill, and results when using browser Back/Forward buttons
    window.addEventListener("popstate", () => {
        const params = new URLSearchParams(window.location.search);
        const cat = params.get("category") || "";
        const query = params.get("q") || "";
        if (categoryInput) categoryInput.value = cat;
        if (searchInput) searchInput.value = query;
        updateActiveCategoryPill(cat);
        loadCatalog(window.location.href, false);
    });
})();

const sidebar = document.getElementById("filter-sidebar");
const toggleBtn = document.getElementById("toggle-filters-btn");
const closeBtn = document.getElementById("close-filters-btn");
const backdrop = document.getElementById("sidebar-backdrop");

/**
 * Open or close the mobile filter sidebar and sync ARIA/backdrop/scroll state.
 * @param {boolean} isOpen - Desired open state for the sidebar.
 */
function setSidebarOpen(isOpen) {
    if (!sidebar) return;
    sidebar.classList.toggle("is-open", isOpen);
    if (toggleBtn) {
        toggleBtn.setAttribute("aria-expanded", String(isOpen));
    }
    if (backdrop) {
        backdrop.hidden = !isOpen;
    }
    // Lock background scrolling only when the mobile drawer is open on small viewports.
    document.body.style.overflow = isOpen && window.innerWidth <= 768 ? "hidden" : "";
}

// Toggle drawer visibility from the filter button.
if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
        const isCurrentlyOpen = sidebar?.classList.contains("is-open");
        setSidebarOpen(!isCurrentlyOpen);
    });
}

// Close drawer via the explicit close button.
if (closeBtn) {
    closeBtn.addEventListener("click", () => setSidebarOpen(false));
}

// Close drawer when clicking the dimmed backdrop overlay.
if (backdrop) {
    backdrop.addEventListener("click", () => setSidebarOpen(false));
}

// Close drawer when pressing Escape while open.
document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && sidebar?.classList.contains("is-open")) {
        setSidebarOpen(false);
    }
});

// Automatically close the mobile drawer after selecting a category or resetting filters.
document.addEventListener("click", (event) => {
    if (window.innerWidth > 768) return;
    if (event.target.closest("#category-filters .category-pill") || event.target.closest("#reset-filters-btn")) {
        setSidebarOpen(false);
    }
});

// Reset drawer state when resizing from mobile to desktop layout.
window.addEventListener("resize", () => {
    if (window.innerWidth > 768) {
        setSidebarOpen(false);
    }
});