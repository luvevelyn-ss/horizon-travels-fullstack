// StudentName=Shune Pyae Pyae Aung
// StudentID=24028257

// seat layout config
const renderPattern = ["A", "B", "", "C", "D", "", "E", "F"];
const totalSeats = 130;
const businessSeats = Math.round(totalSeats * 0.2);
const economySeats = totalSeats - businessSeats;

// wire up on load
window.onload = () => {
  toggleReturnDate();
  renderSeats();
  renderSeatLegend();
  setMinDepartureDate();
  setupDepartureDateListener();

  // run calculateFare on Search click
  document.getElementById("searchBtn").addEventListener("click", calculateFare);
};

function toggleReturnDate() {
  const isReturn =
    document.querySelector("input[name='tripType']:checked").value === "return";
  document.getElementById("returnDateGroup").style.display = isReturn
    ? "block"
    : "none";
}

function renderSeats() {
  const container = document.getElementById("seats-container");
  container.innerHTML = "";
  container.style.gridTemplateColumns = `repeat(${renderPattern.length}, 1fr)`;

  const businessRows = 4;
  const totalRows = 26;

  for (let row = 1; row <= totalRows; row++) {
    renderPattern.forEach((letter) => {
      const seat = document.createElement("div");
      if (!letter) {
        seat.className = "aisle";
      } else {
        const seatId = `${row}${letter}`;
        const isBiz = row <= businessRows;
        seat.textContent = seatId;
        seat.className = `seat ${isBiz ? "business" : "economy"}`;
        seat.onclick = () => {
          if (!seat.classList.contains("disabled")) {
            seat.classList.toggle("selected");
            updateSeatSelection();
          }
        };
      }
      container.appendChild(seat);
    });
  }

  document.getElementById(
    "seat-availability"
  ).textContent = `Available Seats — Business: ${businessSeats}, Economy: ${economySeats}`;
}

function renderSeatLegend() {
  const legend = document.getElementById("seat-legend");
  if (!legend) return;
  legend.innerHTML = `
    <div class="legend-item"><div class="seat business"></div> Business</div>
    <div class="legend-item"><div class="seat economy"></div> Economy</div>
    <div class="legend-item"><div class="seat selected"></div> Selected</div>
  `;
}

function updateSeatSelection() {
  const count = document.querySelectorAll(".seat.selected").length;
  document.getElementById("seats").value = count;
}

function calculateFare() {
  const from = document.getElementById("fromCity").value;
  const to = document.getElementById("toCity").value;
  const seats = parseInt(document.getElementById("seats").value, 10);
  const classType = document.getElementById("classType").value;
  const travelDate = new Date(document.getElementById("travelDate").value);
  const returnField = document.getElementById("returnDate");
  const returnDate = returnField.offsetParent
    ? new Date(returnField.value)
    : null;
  const today = new Date();

  const flightTimes = document.getElementById("flightTimes");
  const fareResult = document.getElementById("fareResult");
  const bookingSummary = document.getElementById("bookingSummary");

  // clear previous
  flightTimes.innerHTML = "";
  fareResult.textContent = "";
  bookingSummary.innerHTML = "";

  // basic checks
  if (!from || !to || !seats || from === to || isNaN(travelDate)) {
    fareResult.textContent = "Please fill all fields correctly.";
    return;
  }
  if (seats < 1 || seats > 130) {
    fareResult.textContent = "Seats must be between 1 and 130.";
    return;
  }
  if ([0, 6].includes(travelDate.getDay())) {
    fareResult.textContent = "Flights only operate Monday to Friday.";
    return;
  }
  const daysAdvance = Math.floor((travelDate - today) / (1000 * 60 * 60 * 24));
  if (daysAdvance < 0 || daysAdvance > 90) {
    fareResult.textContent =
      "Bookings can only be made up to 3 months in advance.";
    return;
  }

  // seat selection
  const selectedSeats = [...document.querySelectorAll(".seat.selected")].map(
    (s) => s.textContent
  );
  if (selectedSeats.length !== seats) {
    fareResult.textContent = `Please select exactly ${seats} seat(s).`;
    return;
  }

  // fetch flight times & base fare from your API
  fetch(
    `/api/flights?from=${encodeURIComponent(from)}&to=${encodeURIComponent(to)}`
  )
    .then((r) => r.json())
    .then((data) => {
      const flights = data.flights;
      if (!flights.length) {
        flightTimes.innerHTML = `<h4><i class="fas fa-plane-departure"></i> Flight Times</h4>
                                 <p>No matching flights found.</p>`;
        return;
      }

      // outbound only / plus return
      let timesHTML = `Out: ${flights[0].depart} → ${flights[0].arrive}<br/>`;
      if (returnDate) {
        if (returnDate < travelDate || [0, 6].includes(returnDate.getDay())) {
          flightTimes.innerHTML = `<h4><i class="fas fa-plane-departure"></i> Flight Times</h4>
                                   <p>No matching flights found.</p>`;
          fareResult.textContent =
            "Return date must be Mon–Fri and after departure.";
          return;
        }
        if (flights[1]) {
          timesHTML += `Return: ${flights[1].depart} → ${flights[1].arrive}`;
        }
      }

      flightTimes.innerHTML = `<h4><i class="fas fa-plane-departure"></i> Flight Times</h4>
                               <p>${timesHTML}</p>`;

      // calculate discount
      let discount = 0;
      if (daysAdvance >= 80) discount = 0.25;
      else if (daysAdvance >= 60) discount = 0.15;
      else if (daysAdvance >= 45) discount = 0.1;

      const base = data.baseFare || 100;
      let total =
        base * seats * (classType === "business" ? 2 : 1) * (1 - discount);

      // return leg
      if (returnDate && flights[1]) {
        const rDays = Math.floor((returnDate - today) / (1000 * 60 * 60 * 24));
        let rDisc = 0;
        if (rDays >= 80) rDisc = 0.25;
        else if (rDays >= 60) rDisc = 0.15;
        else if (rDays >= 45) rDisc = 0.1;
        total +=
          base * seats * (classType === "business" ? 2 : 1) * (1 - rDisc);
      }

      fareResult.textContent = `Total Price: £${total.toFixed(2)}${
        discount ? ` (includes ${discount * 100}% discount)` : ""
      }`;
      bookingSummary.innerHTML = `
        <strong>Booking Summary</strong><br>
        Route: ${from} → ${to}<br>
        Class: ${classType}, Passengers: ${seats}<br>
        Seats: ${selectedSeats.join(", ")}<br>
        Depart: ${travelDate.toDateString()}${
        returnDate ? `<br>Return: ${returnDate.toDateString()}` : ""
      }<br>
        Total Fare: £${total.toFixed(2)}
        <button class="confirm-button" onclick="confirmBooking()">Confirm Booking</button>
      `;
    })
    .catch(() => {
      fareResult.textContent = "Error fetching flights—please try again.";
    });
}

function confirmBooking() {
  const from = document.getElementById("fromCity").value;
  const to = document.getElementById("toCity").value;
  const seats = parseInt(document.getElementById("seats").value, 10);
  const classType = document.getElementById("classType").value;
  const travelDate = new Date(document.getElementById("travelDate").value);
  const returnField = document.getElementById("returnDate");
  const returnDate = returnField.offsetParent
    ? new Date(returnField.value)
    : null;
  const selectedSeats = [...document.querySelectorAll(".seat.selected")].map(
    (s) => s.textContent
  );

  // 💾 Store booking summary + selected seats in localStorage
  localStorage.setItem(
    "bookingSummary",
    JSON.stringify({
      fromCity: from,
      toCity: to,
      travelDate: travelDate.toISOString().split("T")[0],
      returnDate: returnDate ? returnDate.toISOString().split("T")[0] : null,
      seats: seats,
      classType: classType,
    })
  );

  localStorage.setItem("selectedSeats", JSON.stringify(selectedSeats));

  // build payload for backend
  const payload = {
    route: `${from} → ${to}`,
    departureDate: travelDate.toDateString(),
    returnDate: returnDate ? returnDate.toDateString() : null,
    passengers: seats,
    selectedSeats,
    classType,
    totalAmount: document
      .getElementById("fareResult")
      .textContent.match(/£([\d.]+)/)[1],
  };

  fetch("/api/book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
    .then((res) => res.json())
    .then((result) => {
      if (result.status === "ok") {
        localStorage.setItem("lastBookingId", result.bookingId);
        window.location.href = "/payment";
      } else {
        alert("Booking failed.");
      }
    });
}

function setMinDepartureDate() {
  const today = new Date();
  const formattedToday = today.toISOString().split("T")[0];
  document.getElementById("travelDate").setAttribute("min", formattedToday);
}

function setupDepartureDateListener() {
  const travelDateInput = document.getElementById("travelDate");
  const returnDateInput = document.getElementById("returnDate");
  travelDateInput.addEventListener("change", () => {
    const dep = new Date(travelDateInput.value);
    if (!isNaN(dep)) {
      const nextDay = new Date(dep);
      nextDay.setDate(dep.getDate() + 1);
      returnDateInput.setAttribute("min", nextDay.toISOString().split("T")[0]);
    }
  });
}

document.getElementById("searchBtn").addEventListener("click", () => {
  const bookingSummary = {
    fromCity: document.getElementById("fromCity").value,
    toCity: document.getElementById("toCity").value,
    travelDate: document.getElementById("travelDate").value,
    returnDate: document.getElementById("returnDate").value,
    seats: document.getElementById("seats").value,
    classType: document.getElementById("classType").value,
  };

  localStorage.setItem("bookingSummary", JSON.stringify(bookingSummary));
});

// Hamburger menu toggle
document.addEventListener("DOMContentLoaded", () => {
  const menuToggle = document.getElementById("menu-toggle");
  const mobileMenu = document.getElementById("mobileMenu");
  menuToggle?.addEventListener("click", () => {
    menuToggle.classList.toggle("open");
    mobileMenu.classList.toggle("active");
  });
});
