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