document.querySelectorAll("[data-confirm]").forEach((button) => {
    button.addEventListener("click", (event) => {
        const message = button.getAttribute("data-confirm");

        if (!window.confirm(message)) {
            event.preventDefault();
        }
    });
});

document.querySelectorAll("details").forEach((details) => {
    details.addEventListener("toggle", () => {
        if (!details.open) {
            return;
        }

        document.querySelectorAll("details[open]").forEach((otherDetails) => {
            if (otherDetails !== details) {
                otherDetails.open = false;
            }
        });
    });
});
