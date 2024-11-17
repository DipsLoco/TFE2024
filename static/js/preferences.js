document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM chargé.");

    // Éléments nécessaires
    const form = document.getElementById("cookie-preferences-form");
    const successMessage = document.getElementById("successMessage");
    const modal = document.getElementById("cookieModal");
    const cookieBanner = document.getElementById("cookieBanner");
    const analyticsStatus = document.getElementById("analyticsStatus");
    const reopenPreferences = document.getElementById("reopenPreferences");

    if (!form || !successMessage || !cookieBanner || !analyticsStatus) {
        console.error("Certains éléments nécessaires sont introuvables dans le DOM.");
        return;
    }

    console.log("Formulaire détecté :", form);
    console.log("Conteneur du message de succès détecté :", successMessage);

    // Gestion de l'événement de soumission du formulaire
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Empêche le rechargement automatique du formulaire
        console.log("Tentative d'enregistrement des préférences...");

        const analytics = document.querySelector('input[name="analytics"]').checked;
        const marketing = document.querySelector('input[name="marketing"]').checked;

        console.log("Données à envoyer :", { analytics, marketing });

        fetch("/fr/gym/preferences/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ analytics, marketing })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erreur réseau (${response.status})`);
                }
                return response.json();
            })
            .then(data => {
                console.log("Réponse du serveur :", data);
                if (data.status === "preferences saved") {
                    console.log("Préférences enregistrées avec succès !");
                    
                    // Mettre à jour la bannière avec l'état des cookies
                    analyticsStatus.textContent = analytics ? "Activés" : "Désactivés";

                    // Afficher la bannière
                    cookieBanner.style.display = "block";

                    // Afficher le message de succès
                    successMessage.style.display = "block";
                    successMessage.classList.add("visible");

                    // Cache le message après 5 secondes
                    setTimeout(() => {
                        successMessage.style.display = "none";
                        successMessage.classList.remove("visible");
                    }, 5000);

                    // Masquer la modale
                    if (modal) {
                        console.log("Fermeture du modal détectée.");
                        modal.style.display = "none";

                        setTimeout(() => {
                            if (modal.style.display === "none") {
                                console.log("Le modal a été fermé avec succès.");
                            } else {
                                console.error("Échec de la fermeture du modal.");
                            }
                        }, 100);
                    }
                } else {
                    alert("Erreur : " + data.message);
                }
            })
            .catch(error => {
                console.error("Erreur :", error);
                alert("Une erreur est survenue. Veuillez réessayer.");
            });
    });

    // Gestion des basculeurs
    document.querySelectorAll('.toggle-arrow').forEach(arrow => {
        arrow.addEventListener('click', function () {
            const detail = this.parentElement.nextElementSibling;
            const isHidden = detail.style.display === 'none' || !detail.style.display;
            detail.style.display = isHidden ? 'block' : 'none';
            this.classList.toggle('open', isHidden);
            console.log("Détail basculé :", isHidden ? "Ouvert" : "Fermé");
        });
    });

    // Affichage de la modale uniquement sur la page des préférences
    const currentUrl = window.location.pathname;
    if (currentUrl.includes("preferences") && modal) {
        console.log("Affichage de la modale.");
        modal.style.display = "flex";
    }

    // Rouvrir les préférences depuis la bannière
    if (reopenPreferences) {
        reopenPreferences.addEventListener("click", function (event) {
            event.preventDefault();
            cookieBanner.style.display = "none"; // Cacher la bannière
            if (modal) {
                console.log("Réouverture de la modale...");
                modal.style.display = "flex"; // Rouvrir la modale
            }
        });
    }
});
