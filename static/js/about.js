// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
document.addEventListener("DOMContentLoaded", () => {
  const testimonials = document.querySelectorAll(".testimonial");
  let current = 0;

  function showTestimonial(index) {
    testimonials.forEach((el, i) => {
      el.style.display = i === index ? "block" : "none";
    });
  }

  function rotateTestimonials() {
    current = (current + 1) % testimonials.length;
    showTestimonial(current);
  }

  if (testimonials.length > 1) {
    testimonials.forEach((t) => (t.style.display = "none"));
    showTestimonial(current);
    setInterval(rotateTestimonials, 5000);
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          entry.target.classList.remove("invisible");
        }
      });
    },
    {
      threshold: 0.1,
    }
  );

  document.querySelectorAll(".timeline-event, .testimonial").forEach((el) => {
    el.classList.add("invisible");
    observer.observe(el);
  });
});

document.getElementById("menu-toggle").addEventListener("click", function () {
  const mobileMenu = document.getElementById("mobileMenu");
  mobileMenu.classList.toggle("active");
  this.classList.toggle("open"); // Optional: For animated hamburger icon
});
