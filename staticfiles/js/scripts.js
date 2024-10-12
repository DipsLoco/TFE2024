/*!
* Start Bootstrap - Business Frontpage v5.0.9 (https://startbootstrap.com/template/business-frontpage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-business-frontpage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

// JavaScript global pour l'animation de vibration sur les boutons "Ajouter au panier"
document.addEventListener('DOMContentLoaded', function () {
    const dataScript = document.getElementById('data-json');
    if (dataScript) {
        const data = JSON.parse(dataScript.textContent);

        // Utilisation des variables
        var monthlyRegistrationPercentage = parseFloat(data.monthlyRegistrationPercentage);
        var attendancePercentage = parseFloat(data.attendancePercentage);
        var busyHourCountsKeys = data.busyHourCountsKeys;
        var busyHourCountsValues = data.busyHourCountsValues;

        // Couleur plus vive pour le cercle de l'inscription
        var registrationCircle = new ProgressBar.Circle('#registrationCircle', {
            color: '#00cc44', // Vert vif
            strokeWidth: 6,
            duration: 1400,
            from: { color: '#eee' },
            to: { color: '#00cc44' }, // Plus vif
            step: function (state, circle) {
                circle.path.setAttribute('stroke', state.color);
                circle.setText('');
            }
        });
        registrationCircle.animate(monthlyRegistrationPercentage / 100);

        // Couleur plus vive pour le cercle de présence
        var attendanceCircle = new ProgressBar.Circle('#attendanceCircle', {
            color: '#ff4500', // Orange vif
            strokeWidth: 6,
            duration: 1400,
            from: { color: '#eee' },
            to: { color: '#ff4500' }, // Plus vif
            step: function (state, circle) {
                circle.path.setAttribute('stroke', state.color);
                circle.setText('');
            }
        });
        attendanceCircle.animate(attendancePercentage / 100);

        // Graphique des heures les plus fréquentées avec des couleurs vives
        var ctx = document.getElementById('busyHoursChart').getContext('2d');
        var busyHoursChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: busyHourCountsKeys,
                datasets: [{
                    label: 'Séances',
                    data: busyHourCountsValues,
                    backgroundColor: busyHourCountsValues.map(function(value) {
                        if (value >= 10) {
                            return '#ff0000'; // Rouge vif pour les heures très fréquentées
                        } else if (value >= 5) {
                            return '#ffa500'; // Orange vif pour les heures moyennement fréquentées
                        } else {
                            return '#00ff00'; // Vert vif pour les heures peu fréquentées
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

