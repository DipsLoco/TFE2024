
document.addEventListener("DOMContentLoaded", function () {
    const cookieBanner = document.getElementById("cookieBanner");
    const acceptButton = document.getElementById("acceptCookies");
    const declineButton = document.getElementById("declineCookies");
    const openPreferencesButton = document.getElementById("openPreferences");

    const getUserId = () => document.body.dataset.userId || "guest";

    const checkConsentForUser = () => {
        const userId = getUserId();
        const consent = localStorage.getItem(`cookieConsent_${userId}`) || document.cookie.includes(`cookieConsent_${userId}=accepted`);
        if (!consent) {
            cookieBanner.style.display = "block";
        } else {
            cookieBanner.style.display = "none";
        }
    };

    const acceptCookies = () => {
        const userId = getUserId();
        localStorage.setItem(`cookieConsent_${userId}`, "accepted");
        document.cookie = `cookieConsent_${userId}=accepted; max-age=31536000; path=/`;
        cookieBanner.style.display = "none";
    };

    const declineCookies = () => {
        const userId = getUserId();
        localStorage.setItem(`cookieConsent_${userId}`, "declined");
        document.cookie = `cookieConsent_${userId}=declined; max-age=31536000; path=/`;
        cookieBanner.style.display = "none";
    };

    if (acceptButton) acceptButton.addEventListener("click", acceptCookies);
    if (declineButton) declineButton.addEventListener("click", declineCookies);
    if (openPreferencesButton) openPreferencesButton.addEventListener("click", () => (location.href = "/preferences"));
    checkConsentForUser();
});
