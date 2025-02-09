// script1.js

// Secure Student Page Access
// function checkLogin() {
//     const isLoggedIn = localStorage.getItem("isLoggedIn");
//     if (isLoggedIn === "true") {
//         window.location.href = "students.html";
//     } else {
//         window.location.href = "signin.html";
//     }
// }

// Language Data
const languages = {
    en: { heroText: "Unleash your curiosity and explore a world of endless possibilities with Curiofy - where every click sparks discovery!" },
    hi: { heroText: "अपनी जिज्ञासा को उजागर करें और Curiofy के साथ अंतहीन संभावनाओं की दुनिया का अन्वेषण करें - जहां हर क्लिक खोज को प्रेरित करता है!" },
    mr: { heroText: "आपली जिज्ञासा अनलॉक करा आणि Curiofy सोबत अंतहीन शक्यतांचा शोध घ्या - जिथे प्रत्येक क्लिक शोधला प्रेरणा देते!" }
};

function changeLanguage(lang) {
    localStorage.setItem("selectedLanguage", lang);  // Store selected language
    applyLanguage(lang);
}

function applyLanguage(lang) {
    document.getElementById("hero-text").innerText = languages[lang]?.heroText || languages.en.heroText;
}

document.addEventListener("DOMContentLoaded", function () {
    const savedLang = localStorage.getItem("selectedLanguage") || "en";
    applyLanguage(savedLang);

    document.getElementById("en").addEventListener("click", () => changeLanguage("en"));
    document.getElementById("hi").addEventListener("click", () => changeLanguage("hi"));
    document.getElementById("mr").addEventListener("click", () => changeLanguage("mr"));
});

// Dashboard specific functions
function updateNotifications() {
    // Add real-time notification updates
}

function updateCalendar() {
    // Add calendar updates
}

// Add event listeners when on dashboard page
if (document.querySelector('.teacher-content')) {
    setInterval(updateNotifications, 30000); // Update notifications every 30 seconds
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.textContent === 'Edit Profile') {
                // Handle profile editing
            }
        });
    });
}