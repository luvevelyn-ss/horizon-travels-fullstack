// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
// Global like toggle for heart icon
window.toggleCardLike = function (button, id) {
  const icon = button.querySelector(".heart-icon");
  icon.classList.toggle("liked");
  const isLiked = icon.classList.contains("liked");
  icon.innerHTML = isLiked ? "&#9829;" : "&#9825;";
  localStorage.setItem(`liked-${id}`, isLiked);
};

function restoreLikedState() {
  document.querySelectorAll(".destination-card").forEach((card) => {
    const id = card.getAttribute("data-id");
    const liked = localStorage.getItem(`liked-${id}`) === "true";
    if (liked) {
      const icon = card.querySelector(".heart-icon");
      icon.classList.add("liked");
      icon.innerHTML = "&#9829;";
    }
  });
}

window.toggleCardLike = function (button, id) {
  const icon = button.querySelector(".heart-icon");
  icon.classList.toggle("liked");
  const isLiked = icon.classList.contains("liked");
  icon.innerHTML = isLiked ? "&#9829;" : "&#9825;";
  localStorage.setItem(`liked-${id}`, isLiked);
};

document.addEventListener("DOMContentLoaded", function () {
  const dropdown = document.querySelector(".dropdown");
  const bookTripLink = document.getElementById("bookTripLink");

  if (dropdown && bookTripLink) {
    bookTripLink.addEventListener("click", (e) => {
      e.preventDefault();
      dropdown.classList.toggle("open");
    });

    window.addEventListener("click", (e) => {
      if (!dropdown.contains(e.target) && e.target !== bookTripLink) {
        dropdown.classList.remove("open");
      }
    });
  }

  // Load heart state from localStorage
  document.querySelectorAll(".destination-card").forEach((card) => {
    const id = card.getAttribute("data-id");
    const liked = localStorage.getItem(`liked-${id}`) === "true";
    if (liked) {
      const icon = card.querySelector(".heart-icon");
      icon.classList.add("liked");
      icon.innerHTML = "&#9829;";
    }
  });

  // Favorites toggle
  window.toggleFavorites = function () {
    const showOnlyFavorites = document.body.classList.toggle("show-favorites");
    document.querySelectorAll(".destination-card").forEach((card) => {
      const id = card.getAttribute("data-id");
      const liked = localStorage.getItem(`liked-${id}`) === "true";
      card.style.display = showOnlyFavorites && !liked ? "none" : "block";
    });
    document.querySelector(".favorites-toggle").textContent = showOnlyFavorites
      ? "Show All"
      : "Show Favorites Only";
  };

  // Hamburger menu
  const menuToggle = document.getElementById("menu-toggle");
  const mobileMenu = document.getElementById("mobileMenu");

  menuToggle.addEventListener("click", () => {
    menuToggle.classList.toggle("open");
    mobileMenu.classList.toggle("active");
  });
});
