document.addEventListener("DOMContentLoaded", function () {
    const cookieBanner = document.getElementById("cookieBanner");
    const acceptButton = document.getElementById("acceptCookies");
    const declineButton = document.getElementById("declineCookies");
    const openPreferencesButton = document.getElementById("openPreferences");

    if (!cookieBanner) {
        console.error("Bannière de cookies non trouvée.");
        return;
    }

    console.log("Bannière détectée. Tentative d'affichage...");

    // Fonction pour vérifier le consentement
    const getUserId = () => document.body.dataset.userId || "guest";

    const checkConsentForUser = () => {
        const userId = getUserId();
        const consent = localStorage.getItem(`cookieConsent_${userId}`) || document.cookie.includes(`cookieConsent_${userId}=accepted`);
        if (!consent) {
            cookieBanner.classList.add("show"); // Affiche la bannière
        } else {
            cookieBanner.classList.remove("show"); // Masque la bannière
        }
    };

    // Actions sur clic des boutons
    const acceptCookies = () => {
        const userId = getUserId();
        localStorage.setItem(`cookieConsent_${userId}`, "accepted");
        document.cookie = `cookieConsent_${userId}=accepted; max-age=31536000; path=/`;
        cookieBanner.classList.remove("show");
    };

    const declineCookies = () => {
        const userId = getUserId();
        localStorage.setItem(`cookieConsent_${userId}`, "declined");
        document.cookie = `cookieConsent_${userId}=declined; max-age=31536000; path=/`;
        cookieBanner.classList.remove("show");
    };

    // Ajout des événements sur les boutons
    if (acceptButton) acceptButton.addEventListener("click", acceptCookies);
    if (declineButton) declineButton.addEventListener("click", declineCookies);
    if (openPreferencesButton) openPreferencesButton.addEventListener("click", () => {
        window.location.href = "/preferences";
    });

    // Vérifie et affiche la bannière si nécessaire
    checkConsentForUser();
});
