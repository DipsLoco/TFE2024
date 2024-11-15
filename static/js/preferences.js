function toggleDetails(element) {
    const detail = element.nextElementSibling;
    const arrow = element.querySelector(".toggle-arrow");
    
    if (detail.style.display === "block") {
        detail.style.display = "none";
        arrow.innerHTML = "&#9656;"; // Flèche droite
    } else {
        detail.style.display = "block";
        arrow.innerHTML = "&#9662;"; // Flèche vers le bas
    }
}

function accepterCookies() {
    fetch("{% url 'cookie_consent' %}?action=accept", {
        method: 'POST',
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'
        }
    }).then(response => {
        if (response.ok) {
            localStorage.setItem("cookieConsent", "accepted");
            document.getElementById("cookieBanner").style.display = "none";
            document.getElementById("cookieModal").style.display = "none";
        }
    });
}

function enregistrerPreferences() {
    localStorage.setItem("cookiePreferencesSaved", "true");
    fermerPreferences();
}

function fermerPreferences() {
    document.getElementById("cookieModal").style.display = "none";
}

document.addEventListener("DOMContentLoaded", function() {
    if (!localStorage.getItem("cookieConsent")) {
        document.getElementById("cookieBanner").style.display = "block";
    }
});