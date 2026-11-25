(() => {
    document.querySelectorAll(".toggle-password-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const wrapper = btn.closest(".password-field");
            const input = wrapper?.querySelector("input");
            if (!input) return;

            const showPassword = input.type === "password";
            input.type = showPassword ? "text" : "password";

            btn.setAttribute("aria-pressed", String(showPassword));
            btn.setAttribute(
                "aria-label",
                showPassword ? "Masquer le mot de passe" : "Afficher le mot de passe"
            );

            btn.querySelector(".icon-eye")?.classList.toggle("hidden", showPassword);
            btn.querySelector(".icon-eye-off")?.classList.toggle("hidden", !showPassword);
        });
    });
})();