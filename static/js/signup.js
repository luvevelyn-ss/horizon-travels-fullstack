// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
document.getElementById("signupForm").addEventListener("submit", function (e) {
  const fullName = this.fullName.value.trim();
  const email = this.email.value.trim();
  const password = this.password.value;
  const confirmPassword = this.confirmPassword.value;
  const acceptedTerms = document.getElementById("terms").checked;

  const passwordRegex =
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=[\]{};':"\\|,.<>\/?]).{8,}$/;

  if (!fullName || !email || !password || !confirmPassword) {
    alert("Please fill out all fields.");
    e.preventDefault();
    return;
  }

  if (!acceptedTerms) {
    alert("You must accept the Terms & Conditions and Privacy Policy.");
    e.preventDefault();
    return;
  }

  if (!passwordRegex.test(password)) {
    alert(
      "Password must be at least 8 characters long and include uppercase, lowercase, number, and symbol."
    );
    e.preventDefault();
    return;
  }

  if (password !== confirmPassword) {
    alert("Passwords do not match.");
    e.preventDefault();
    return;
  }
});

// Burger menu toggle for mobile
const burger = document.getElementById("burger-btn");
const mobileMenu = document.getElementById("mobile-menu");

if (burger && mobileMenu) {
  burger.addEventListener("click", () => {
    burger.classList.toggle("open");
    mobileMenu.classList.toggle("active");
  });
}
