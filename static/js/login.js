// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");

  // Toggle password visibility
  document.querySelectorAll(".password-toggle").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.closest(".password-field").querySelector("input");
      const eye = btn.querySelector(".show-icon");
      const eyeSlash = btn.querySelector(".hide-icon");

      const isHidden = input.type === "password";
      input.type = isHidden ? "text" : "password";
      eye.style.display = isHidden ? "none" : "inline";
      eyeSlash.style.display = isHidden ? "inline" : "none";
    });
  });

  // Burger menu toggle for mobile
  const burger = document.querySelector(".burger");
  const mobileMenu = document.querySelector(".mobile-menu");

  if (burger && mobileMenu) {
    burger.addEventListener("click", () => {
      burger.classList.toggle("open");
      mobileMenu.classList.toggle("active");
      document.body.classList.toggle("no-scroll");
    });
  }
});
