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