document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".reserve-form");
    const feedbackEl = document.getElementById("reservation-feedback");
    const pillEl = document.querySelector(".js-availability-pill");

    function showFeedback(level, message) {
        if (!feedbackEl) return;
        feedbackEl.hidden = false;
        feedbackEl.className = `reservation-feedback alert-message is-${level}`;
        feedbackEl.textContent = message;
    }

    function updateAvailabilityUI(availableQuantity) {
        if (!pillEl) return;

        if (availableQuantity > 0) {
            const label = availableQuantity > 1 ? "exemplaires" : "exemplaire";
            pillEl.classList.remove("is-unavailable");
            pillEl.classList.add("is-available");
            pillEl.textContent = `Dispo (${availableQuantity} ${label})`;
        } else {
            pillEl.classList.remove("is-available");
            pillEl.classList.add("is-unavailable");
            pillEl.textContent = "Indisponible";
        }
    }

    forms.forEach((form) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');

        form.addEventListener("submit", async (event) => {
            event.preventDefault();

            const title = form.dataset.bookTitle || "ce livre";
            const confirmed = window.confirm(
                `Confirmer la réservation de « ${title} » ?`
            );
            if (!confirmed) {
                return;
            }

            if (submitBtn) {
                submitBtn.disabled = true;
            }

            try {
                const response = await fetch(form.action, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "Accept": "application/json",
                        ...(csrfInput ? { "X-CSRFToken": csrfInput.value } : {}),
                    },
                    body: new FormData(form),
                    credentials: "same-origin",
                });

                const contentType = response.headers.get("content-type") || "";
                const data = contentType.includes("application/json")
                    ? await response.json()
                    : null;

                if (data && data.message) {
                    showFeedback(data.level || (response.ok ? "success" : "error"), data.message);
                    if (typeof data.available_quantity === "number") {
                        updateAvailabilityUI(data.available_quantity);
                        if (submitBtn && data.available_quantity <= 0) {
                            submitBtn.disabled = true;
                        } else if (submitBtn && !data.ok) {
                            submitBtn.disabled = false;
                        }
                    }
                } else {
                    showFeedback(
                        "error",
                        "Réservation impossible : réponse inattendue du serveur."
                    );
                    if (submitBtn) submitBtn.disabled = false;
                }
            } catch (error) {
                showFeedback(
                    "error",
                    "Réservation impossible : erreur réseau lors de la communication avec le serveur."
                );
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    });
});