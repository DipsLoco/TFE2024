// Filtrage des achats entre les plans et les services
document.getElementById('purchaseFilter').addEventListener('change', function() {
    let filterValue = this.value;
    let planSection = document.getElementById('planPurchases');
    let serviceSection = document.getElementById('servicePurchases');

    if (filterValue == 'plans') {
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
console.log("Page chargée !");