/*!
* Start Bootstrap - Business Frontpage v5.0.9 (https://startbootstrap.com/template/business-frontpage)
* Copyright 2013-2023 Start Bootstrap
* Licensed under MIT (https://github.com/StartBootstrap/startbootstrap-business-frontpage/blob/master/LICENSE)
*/
// This file is intentionally blank
// Use this file to add JavaScript to your project

// JavaScript global pour l'animation de vibration sur les boutons "Ajouter au panier"
document.addEventListener('DOMContentLoaded', function () {
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');

    addToCartButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            // Ajouter la classe d'animation de vibration
            this.classList.add('vibrate');

            // Retirer l'animation après 500ms
            setTimeout(() => {
                this.classList.remove('vibrate');
            }, 500);

            // Simulation de l'ajout au panier
            alert("Produit ajouté au panier !");
        });
    });
});
