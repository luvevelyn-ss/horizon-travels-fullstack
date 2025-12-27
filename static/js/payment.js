// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257
document.addEventListener("DOMContentLoaded", () => {
  const summary = JSON.parse(localStorage.getItem("bookingSummary"));
  const container = document.getElementById("paymentSummary");

  if (summary) {
    container.innerHTML = `
            <h2>Booking Summary</h2>
            <p><i class="fas fa-plane-departure"></i> <strong>From:</strong> ${
              summary.fromCity
            }</p>
            <p><i class="fas fa-plane-arrival"></i> <strong>To:</strong> ${
              summary.toCity
            }</p>
            <p><i class="fas fa-calendar-alt"></i> <strong>Departure:</strong> ${
              summary.travelDate
            }</p>
            <p><i class="fas fa-calendar-day"></i> <strong>Return:</strong> ${
              summary.returnDate || "N/A"
            }</p>
            <p><i class="fas fa-users"></i> <strong>Seats:</strong> ${
              summary.seats
            }</p>
            <p><i class="fas fa-chair"></i> <strong>Class:</strong> ${
              summary.classType
            }</p>
        `;
  } else {
    container.innerHTML = "<p>No booking summary found.</p>";
  }

  // Format card number
  new Cleave("#cardNumber", {
    creditCard: true,
  });

  // Format expiry MM/YY
  new Cleave("#expiry", {
    date: true,
    datePattern: ["m", "y"],
  });

  // Limit CVV to 4 digits max
  document.getElementById("cvv").addEventListener("input", function () {
    this.value = this.value.replace(/[^0-9]/g, "").slice(0, 4);
  });

  document
    .getElementById("paymentForm")
    .addEventListener("submit", function (e) {
      e.preventDefault(); // prevent actual form submit

      const summary = JSON.parse(localStorage.getItem("bookingSummary"));
      const selectedSeats =
        JSON.parse(localStorage.getItem("selectedSeats")) || [];

      if (!summary || selectedSeats.length === 0) {
        alert("Booking summary or seat selection is missing.");
        return;
      }

      const classType = summary.classType;
      const farePerSeat = classType === "Business" ? 200 : 120; // Example fares
      const totalFare = farePerSeat * selectedSeats.length;
      const discount = 0.1; // Example 10% discount
      const finalFare = totalFare - totalFare * discount;
      const durationMin = 150; // Example duration (2h30m)

      const booking = {
        name: document.getElementById("cardName").value || "Anonymous",
        from: summary.fromCity,
        to: summary.toCity,
        travelDate: summary.travelDate,
        mode: "Flight",
        type: classType,
        seatNumbers: selectedSeats,
        fare: totalFare,
        discount: discount,
        final: finalFare,
        durationMin: durationMin,
      };

      fetch("/process_payment", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(booking),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Payment failed.");
          }
          return response.json();
        })
        .then((data) => {
          alert("Payment successful! Redirecting to your ticket...");
          window.location.href = `/ticket/${data.bookingId}`;
        })
        .catch((error) => {
          console.error("Error:", error);
          alert(
            "There was a problem processing your payment. Please try again."
          );
        });
    });
});

// Hamburger menu
const menuToggle = document.getElementById("menu-toggle");
const mobileMenu = document.getElementById("mobileMenu");

menuToggle.addEventListener("click", () => {
  menuToggle.classList.toggle("open");
  mobileMenu.classList.toggle("active");
});
