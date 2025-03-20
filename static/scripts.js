document.addEventListener("DOMContentLoaded", function() {
    // Navbar Toggle
    let navbarToggler = document.querySelector(".navbar-toggler");
    let navbarMenu = document.querySelector(".navbar-collapse");

    navbarToggler.addEventListener("click", function() {
        navbarMenu.classList.toggle("show");
    });

    // Smooth Scrolling
    let scrollLinks = document.querySelectorAll("a[href^='#']");
    scrollLinks.forEach(link => {
        link.addEventListener("click", function(e) {
            e.preventDefault();
            let target = document.querySelector(this.getAttribute("href"));
            target.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    });

    // Search System
    document.getElementById("searchInput")?.addEventListener("keyup", function() {
        let searchValue = this.value.toLowerCase();
        let bookCards = document.querySelectorAll(".book-card");

        bookCards.forEach(card => {
            let title = card.querySelector("h4").textContent.toLowerCase();
            card.style.display = title.includes(searchValue) ? "block" : "none";
        });
    });

    // AJAX Borrow Book
    document.querySelectorAll(".borrow-btn").forEach(button => {
        button.addEventListener("click", function() {
            let bookId = this.dataset.bookId;
            fetch(`/borrow/${bookId}`, { method: "POST" })
                .then(res => res.json())
                .then(data => alert(data.message))
                .catch(err => console.log("Error:", err));
        });
    });

    // AJAX Return Book
    document.querySelectorAll(".return-btn").forEach(button => {
        button.addEventListener("click", function() {
            let transactionId = this.dataset.transactionId;
            fetch(`/return_book/${transactionId}`, { method: "POST" })
                .then(res => res.json())
                .then(data => alert(data.message))
                .catch(err => console.log("Error:", err));
        });
    });
});
