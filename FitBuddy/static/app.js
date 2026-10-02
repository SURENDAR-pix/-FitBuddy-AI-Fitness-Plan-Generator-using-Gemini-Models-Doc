document
    .querySelectorAll("[data-loading-form]")
    .forEach((form) => {

        form.addEventListener(
            "submit",
            () => {

                const button =
                    form.querySelector(
                        'button[type="submit"]'
                    );

                if (button) {

                    button.disabled = true;

                    button.style.opacity = "0.65";
                }

                form.classList.add(
                    "is-loading"
                );
            }
        );
    });