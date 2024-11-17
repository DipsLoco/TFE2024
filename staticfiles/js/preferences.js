document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM chargé.");

    const form = document.getElementById("cookie-preferences-form");
    const successMessage = document.getElementById("successMessage");
    const modal = document.getElementById("cookieModal");

    if (!form) {
        console.error("Formulaire introuvable.");
        return;
    }

    if (!successMessage) {
        console.error("Conteneur du message de succès introuvable.");
        return;
    }

    console.log("Formulaire détecté :", form);
    console.log("Conteneur du message de succès détecté :", successMessage);

    // Gestion de l'événement du bouton de sauvegarde
    const saveButton = document.getElementById("savePreferences");
    if (!saveButton) {
        console.error("Bouton 'savePreferences' introuvable.");
        return;
    }

    saveButton.addEventListener("click", function (event) {
        event.preventDefault();
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
                    
                    // Affiche le message de succès
                    successMessage.style.display = "block";
                    successMessage.classList.add("visible");

                    // Cache le message après 5 secondes
                    setTimeout(() => {
                        successMessage.style.display = "none";
                        successMessage.classList.remove("visible");
                    }, 5000);

                    // Masque la modale
                    if (modal) {
                        modal.style.display = "none";
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
});
