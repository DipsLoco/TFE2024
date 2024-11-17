/*!
* Start Bootstrap - Business Frontpage v5.0.9 (https://startbootstrap.com/template/business-frontpage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-business-frontpage/blob/master/LICENSE)
*/
// Ce fichier est intentionnellement vide
// Utilisez ce fichier pour ajouter du JavaScript à votre projet

// Animation de vibration pour les boutons "Ajouter au panier"
document.addEventListener('DOMContentLoaded', function () {
    const dataScript = document.getElementById('data-json');
    if (dataScript) {
        const data = JSON.parse(dataScript.textContent);

        // Variables pour les pourcentages d'inscription et de présence
        var monthlyRegistrationPercentage = parseFloat(data.monthlyRegistrationPercentage);
        var attendancePercentage = parseFloat(data.attendancePercentage);
        var busyHourCountsKeys = data.busyHourCountsKeys;
        var busyHourCountsValues = data.busyHourCountsValues;

        // Cercle d'inscription avec couleur vive
        var registrationCircle = new ProgressBar.Circle('#registrationCircle', {
            color: '#00cc44', // Vert vif
            strokeWidth: 6,
            duration: 1400,
            from: { color: '#eee' },
            to: { color: '#00cc44' }, // Vert plus vif
            step: function (state, circle) {
                circle.path.setAttribute('stroke', state.color);
                circle.setText('');
            }
        });
        registrationCircle.animate(monthlyRegistrationPercentage / 100);

        // Cercle de présence avec couleur vive
        var attendanceCircle = new ProgressBar.Circle('#attendanceCircle', {
            color: '#ff4500', // Orange vif
            strokeWidth: 6,
            duration: 1400,
            from: { color: '#eee' },
            to: { color: '#ff4500' }, // Orange plus vif
            step: function (state, circle) {
                circle.path.setAttribute('stroke', state.color);
                circle.setText('');
            }
        });
        attendanceCircle.animate(attendancePercentage / 100);

        // Graphique des heures les plus fréquentées avec couleurs dynamiques
        var ctx = document.getElementById('busyHoursChart').getContext('2d');
        var busyHoursChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: busyHourCountsKeys,
                datasets: [{
                    label: 'Séances',
                    data: busyHourCountsValues,
                    backgroundColor: busyHourCountsValues.map(function (value) {
                        if (value >= 10) {
                            return '#ff0000'; // Rouge vif
                        } else if (value >= 5) {
                            return '#ffa500'; // Orange vif
                        } else {
                            return '#00ff00'; // Vert vif
                        }
                    }),
                    borderColor: '#000000',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    x: {
                        beginAtZero: true
                    },
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    } else {
        console.error("Aucune donnée JSON trouvée dans le script.");
    }
});

// Fonction pour gérer le changement de langue
function handleLanguageChange() {
    var languageSelect = document.getElementById("languageSelect");
    var selectedLanguageValue = languageSelect.value;

    // Traductions avec drapeaux emoji
    var translations = {
        'fr': '🇫🇷 Votre langue',
        'nl': '🇳🇱 Uw taal',
        'en': '🇬🇧 Your language'
    };

    // Mettre à jour le texte par défaut
    var defaultOption = languageSelect.querySelector('option[disabled]');
    if (translations[selectedLanguageValue] && defaultOption) {
        defaultOption.text = translations[selectedLanguageValue];
    }

    // Persister la langue sélectionnée dans localStorage
    localStorage.setItem('selectedLanguage', selectedLanguageValue);

    // Soumettre le formulaire pour changer la langue
    document.getElementById("languageForm").submit();
}

// Fonction pour maintenir la langue après rechargement
function updateDefaultOptionText() {
    var languageSelect = document.getElementById("languageSelect");
    var selectedLanguageValue = localStorage.getItem('selectedLanguage') || languageSelect.value;

    // Traductions avec emoji drapeaux
    var translations = {
        'fr': '🇫🇷 Votre langue',
        'nl': '🇳🇱 Uw taal',
        'en': '🇬🇧 Your language'
    };

    // Mettre à jour le texte par défaut avec la traduction et l'emoji
    var defaultOption = languageSelect.querySelector('option[disabled]');
    if (translations[selectedLanguageValue] && defaultOption) {
        defaultOption.text = translations[selectedLanguageValue];
    }
}

// Initialisation des événements DOM
document.addEventListener("DOMContentLoaded", function () {
    var languageSelect = document.getElementById("languageSelect");
    updateDefaultOptionText();
    languageSelect.addEventListener("change", handleLanguageChange);
});

// Gestion des formulaires dans les modals
document.addEventListener('DOMContentLoaded', function () {
    const modalForms = document.querySelectorAll('.modal form');

    modalForms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault();  // Empêcher la redirection
            const modal = this.closest('.modal');  // Récupérer le modal

            // Soumettre via POST
            const formData = new FormData(this);
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
                }
            })
            .then(response => {
                if (response.ok) {
                    const modalInstance = bootstrap.Modal.getInstance(modal);
                    modalInstance.hide();  // Fermer le modal
                    window.location.reload();  // Recharger la page
                } else {
                    console.error('Erreur lors de l\'envoi du message');
                }
            })
            .catch(error => {
                console.error('Une erreur s\'est produite :', error);
            });
        });
    });
});

// Fermeture des bandeaux de notification
// document.addEventListener('DOMContentLoaded', function () {
//     const closeAlertButton = document.querySelector('.alert .btn-close');
//     if (closeAlertButton) {
//         closeAlertButton.addEventListener('click', function () {
//             const alertBox = this.parentElement;
//             alertBox.style.display = 'none';  // Masquer le bandeau
//         });
//     }
// });

// Défilement en douceur pour les ancres de page
document.addEventListener('DOMContentLoaded', function () {
    const smoothLinks = document.querySelectorAll('a[href^="#"]');
    smoothLinks.forEach(link => {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
});

// gérer l'envoi de formulaire avec protection contre les soumissions multiples 
document.addEventListener("DOMContentLoaded", function() {
    var forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            var submitButton = e.target.querySelector('button[type="submit"]');
            submitButton.disabled = true;  // Désactiver le bouton d'envoi après la première soumission
        });
    });
});

// Script pour désactiver définitivement la bannière rouge
document.addEventListener('DOMContentLoaded', function() {
    const messageItems = document.querySelectorAll('.list-group-item');

    messageItems.forEach(item => {
        const isReadBadge = item.querySelector('.badge.bg-success');
        if (isReadBadge) {
            // Supprime complètement la classe de bannière "non lu"
            item.classList.remove('list-group-item-warning');
        }
    });
});

// Gestion des filtres de messages et de boutons actifs
document.addEventListener('DOMContentLoaded', function() {
    const filterButtons = document.querySelectorAll('.filters a');

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            filterButtons.forEach(btn => btn.classList.remove('btn-primary'));
            this.classList.add('btn-primary');  // Activer le bouton sélectionné
        });
    });
});








