/***************************************************************
 JS of the book_detail page exclusively
 ***************************************************************/

/* Add event listeners to three elements of the DOM :
    - The form (asynchronic request)
    - The #reservatio-feedback element
    - The pill availability
*/
document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".reserve-form");
    const feedbackEl = document.getElementById("reservation-feedback");
    const pillEl = document.querySelector(".js-availability-pill");

    // Function showing feedback in the correct element of the DOM
    function showFeedback(level, message) {
        // Check if the element exist
        if (!feedbackEl) return;
        // show the element
        feedbackEl.hidden = false;
        // add a dynamic class
        feedbackEl.className = `reservation-feedback alert-message is-${level}`;
        // insert the text
        feedbackEl.textContent = message;
    }

    // Function updating the availability pill
    function updateAvailabilityUI(availableQuantity) {

        //Check if the element exist
        if (!pillEl) return;

        // if at least one book is available
        if (availableQuantity > 0) {

            // if more than 1, the word become plurial
            const label = availableQuantity > 1 ? "exemplaires" : "exemplaire";
            // remove the class unavailable and the class available
            pillEl.classList.remove("is-unavailable");
            pillEl.classList.add("is-available");
            //insert the test
            pillEl.textContent = `Dispo (${availableQuantity} ${label})`;
        } 
        
        // if the book is unavailable, we do the opposit
        else {
            pillEl.classList.remove("is-available");
            pillEl.classList.add("is-unavailable");
            pillEl.textContent = "Indisponible";
        }
    }

    // Add an ajax behavior to every form of the page
    forms.forEach((form) => {
        const submitBtn = form.querySelector('button[type="submit"]');
        const csrfInput = form.querySelector('input[name="csrfmiddlewaretoken"]');

        form.addEventListener("submit", async (event) => {
            // prevent the default form behavior
            event.preventDefault();

            // get the title of the book
            const title = form.dataset.bookTitle || "ce livre";
            // prepare the confirmation window
            const confirmed = window.confirm(
                `Confirmer la réservation de « ${title} » ?`
            );
            // if the user don't validate his choice, we stop
            if (!confirmed) {
                return;
            }

            // block the button so the user can't send multiple requests at the same time
            if (submitBtn) {
                submitBtn.disabled = true;
            }

            // beginning of the asynchrone post
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

                // check contentType before to avoid django crashing
                const contentType = response.headers.get("content-type") || "";
                const data = contentType.includes("application/json")
                    ? await response.json()
                    : null;

                // if we get data and messages
                if (data && data.message) {
                    // we show the response
                    showFeedback(data.level || (response.ok ? "success" : "error"), data.message);

                    // if we have the quantity in response, we update the availability pill
                    if (typeof data.available_quantity === "number") {
                        updateAvailabilityUI(data.available_quantity);

                        // if the quantity = 0 , we disable the button submit
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
                    // if errors, we just disable the button until further notice or refresh
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