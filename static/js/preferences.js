document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM chargé.");

    // Éléments nécessaires
    const form = document.getElementById("cookie-preferences-form");
    const successMessage = document.getElementById("successMessage");
    const modal = document.getElementById("cookieModal");
    const cookieBanner = document.getElementById("cookieBanner");
    const analyticsCheckbox = document.querySelector('input[name="analytics"]');
    const marketingCheckbox = document.querySelector('input[name="marketing"]');
    const analyticsStatus = document.getElementById("analyticsStatus");
    const reopenPreferences = document.getElementById("reopenPreferences");

    if (!form) {
        console.error("Formulaire introuvable.");
        return;
    }

    console.log("Formulaire détecté :", form);

    // Gestion de l'événement de soumission du formulaire
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Empêche le rechargement automatique
        console.log("Tentative d'enregistrement des préférences...");

        const analytics = analyticsCheckbox.checked;
        const marketing = marketingCheckbox.checked;

        console.log("Valeurs envoyées :", { analytics, marketing });

        fetch("/fr/gym/preferences/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ analytics, marketing })
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === "preferences saved") {
                    console.log("Préférences enregistrées avec succès !");

                    // Met à jour l'état de la bannière
                    if (analyticsStatus) {
                        analyticsStatus.textContent = analytics ? "Activés" : "Désactivés";
                    }

                    // Affiche le message de succès
                    if (successMessage) {
                        successMessage.style.display = "block";
                        successMessage.classList.add("visible");
                    }

                    // Transition douce et suppression du fade-in
                    setTimeout(() => {
                        if (successMessage) {
                            successMessage.style.opacity = 0;
                            setTimeout(() => {
                                successMessage.style.display = "none";
                                successMessage.classList.remove("visible");
                            }, 500);
                        }

                        // Ferme doucement le modal
                        if (modal) {
                            modal.style.transition = "transform 0.8s ease, opacity 0.8s ease";
                            modal.style.transform = "scale(0.9)";
                            modal.style.opacity = 0;
                            setTimeout(() => {
                                modal.style.display = "none";
                                console.log("Modal fermé avec transition.");
                            }, 800);
                        }

                        // Affiche immédiatement la bannière avec une transition Slide-In
                        if (cookieBanner) {
                            cookieBanner.style.display = "block"; // Affiche immédiatement
                            cookieBanner.style.transform = "translateY(-50px)";
                            cookieBanner.style.opacity = 0;
                            cookieBanner.style.transition = "transform 0.8s ease, opacity 0.8s ease";
                            setTimeout(() => {
                                cookieBanner.style.transform = "translateY(0)";
                                cookieBanner.style.opacity = 1;
                                console.log("Bannière affichée avec Slide-In.");
                            }, 500);
                        }

                        // Transition vers la page d'accueil avec zoom-in
                        setTimeout(() => {
                            console.log("Redirection vers la page d'accueil avec Zoom-In...");
                            document.body.style.transition = "transform 0.8s ease";
                            document.body.style.transform = "scale(0.9)";
                            setTimeout(() => {
                                window.location.href = "/";
                            }, 800);
                        }, 2000);
                    }, 2000);
                } else {
                    alert("Erreur : " + (data.message || "Impossible d'enregistrer vos préférences."));
                }
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Une erreur est survenue. Veuillez réessayer.");
            });
    });

    // Rouvrir les préférences depuis la bannière
    if (reopenPreferences) {
        reopenPreferences.addEventListener("click", function (event) {
            event.preventDefault();
            if (cookieBanner) cookieBanner.style.display = "none"; // Cacher la bannière
            if (modal) modal.style.display = "flex"; // Rouvrir la modale
        });
    }

    // Gestion des flèches pour afficher/masquer les descriptions
    const toggleArrows = document.querySelectorAll(".toggle-arrow");
    toggleArrows.forEach(arrow => {
        arrow.addEventListener("click", function () {
            const detail = this.parentElement.nextElementSibling;
            const isHidden = detail.style.display === "none" || !detail.style.display;
            detail.style.display = isHidden ? "block" : "none";
            this.classList.toggle("open", isHidden);
            console.log("Détail basculé :", isHidden ? "Ouvert" : "Fermé");
        });
    });

    // Afficher dynamiquement la bannière sur la page d'accueil avec Slide-In
    const currentUrl = window.location.pathname;
    if (currentUrl === "/" && cookieBanner) {
        cookieBanner.style.display = "block";
        cookieBanner.style.transform = "translateY(-50px)";
        cookieBanner.style.opacity = 0;
        cookieBanner.style.transition = "transform 0.8s ease, opacity 0.8s ease";
        setTimeout(() => {
            cookieBanner.style.transform = "translateY(0)";
            cookieBanner.style.opacity = 1;
            console.log("Bannière affichée dynamiquement sur la page d'accueil.");
        }, 500);
    }
});
