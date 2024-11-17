document.addEventListener("DOMContentLoaded", function() {
    const searchInput = document.getElementById("searchInput");
    searchInput.value = "";  // Réinitialise le champ au chargement de la page

    document.getElementById("searchForm").addEventListener("submit", function() {
        setTimeout(function() {
            searchInput.value = ""; // Réinitialise le champ après la soumission
        }, 100);
    });
});

// Script pour défilement en douceur
document.addEventListener("DOMContentLoaded", function() {
    var links = document.querySelectorAll('a[href*="#contact"]');
    links.forEach(function(link) {
        link.addEventListener("click", function(e) {
            var url = new URL(this.href);
            if (url.pathname === window.location.pathname) {
                e.preventDefault();
                var targetElement = document.getElementById('contact');
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop,
                        behavior: 'smooth'
                    });
                }
            } else {
                window.location.href = this.href;
            }
        });
    });
});