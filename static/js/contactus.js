// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
const form = document.getElementById("contactForm");
const formMessage = document.getElementById("formMessage");

form.addEventListener("submit", function (event) {
  event.preventDefault();

  // Basic front-end validation
  const name = document.getElementById("name").value.trim();
  const email = document.getElementById("email").value.trim();
  const subject = document.getElementById("subject").value.trim();
  const message = document.getElementById("message").value.trim();

  if (name === "" || email === "" || subject === "" || message === "") {
    formMessage.style.color = "red";
    formMessage.textContent = "Please fill out all fields.";
    return;
  }

  // Simulate successful submission
  formMessage.style.color = "green";
  formMessage.textContent =
    "Thank you for contacting us! We will get back to you soon.";

  // Optionally reset form
  form.reset();
});
