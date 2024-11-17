
    // Gestion de l'affichage du popup de souscription
const showSubscriptionPopup = "{{ show_subscription_popup|yesno:'true,false' }}" === "true";

if (showSubscriptionPopup) {
    setTimeout(() => {
        document.getElementById("subscriptionPopup").style.display = "flex";
    }, 2000);
}

// Code pour fermer le popup
document.getElementById("closePopup").onclick = function() {
    document.getElementById("subscriptionPopup").style.display = "none";
};

// Fermer le popup en cliquant en dehors de celui-ci
window.onclick = function(event) {
    const popup = document.getElementById("subscriptionPopup");
    if (event.target === popup) {
        popup.style.display = "none";
    }
};

    // Filtrage des achats entre les plans et les services
    document.getElementById('purchaseFilter').addEventListener('change', function() {
        let filterValue = this.value;
        let planSection = document.getElementById('planPurchases');
        let serviceSection = document.getElementById('servicePurchases');

        if (filterValue === 'plans') {
            planSection.style.display = 'block';
            serviceSection.style.display = 'none';
        } else if (filterValue === 'services') {
            planSection.style.display = 'none';
            serviceSection.style.display = 'block';
        } else {
            planSection.style.display = 'block';
            serviceSection.style.display = 'block';
        }
    });