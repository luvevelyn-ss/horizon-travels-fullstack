# Full-Stack Travel Booking Website (Flask)

A **solo full-stack travel booking web application** built using **Flask**.  
The website allows users to register, log in, browse travel destinations, and make bookings, with an **admin dashboard** for managing destinations and viewing bookings.

This project demonstrates **end-to-end web development**, covering frontend UI, backend logic, authentication, and database integration.

---

## 🎥 Demo

📹 A full walkthrough of the website is included in this repository.

The demo video demonstrates:

- User registration and login
- Browsing travel destinations
- Booking flow
- Admin dashboard for managing destinations and bookings

---

## 🚀 Features

### 👤 User Features

- User registration and login system
- Secure authentication using Flask sessions
- Browse available travel destinations
- View detailed destination information
- Make travel bookings through a form
- Input validation and error handling
- Logout functionality

### 🛠️ Admin Features

- Admin login
- Add, edit, and delete travel destinations
- View all user bookings
- Manage website content from the backend

---

## 🧭 Website Flow (As Shown in Demo Video)

1. User lands on the homepage
2. User registers or logs in
3. Logged-in users browse available destinations
4. User selects a destination and submits a booking
5. Booking details are stored in the database
6. Admin logs in to manage destinations and view bookings

---

## 🧠 What I Learned

- Building a full-stack web application independently
- Designing user authentication systems with Flask
- Connecting frontend templates to backend routes
- Using databases to store user and booking data
- Handling user input securely
- Structuring Flask projects for scalability
- Debugging and testing complete application flows

---

## 🛠️ Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask

### Database

- SQLite

### Tools

- Git & GitHub
- VS Code

---

## 📂 Project Structure

```
.
├── app.py
├── config.py
├── database.py
├── requirements.txt
├── horizontravels.sql
├── Horizon Travels.mwb
├── templates/
│   ├── index.html
│   ├── about.html
│   ├── login.html
│   ├── signup.html
│   ├── booking.html
│   ├── payment.html
│   ├── ticket.html
│   ├── manage_booking.html
│   ├── admin_login.html
│   └── admin_dashboard.html
├── static/
│   ├── css/
│   │   ├── index.css
│   │   ├── about.css
│   │   ├── login.css
│   │   ├── signup.css
│   │   ├── booking.css
│   │   ├── payment.css
│   │   ├── admin.css
│   │   └── manage_booking.css
│   ├── js/
│   │   ├── index.js
│   │   ├── about.js
│   │   ├── login.js
│   │   ├── signup.js
│   │   ├── booking.js
│   │   ├── payment.js
│   │   ├── contactus.js
│   │   └── manage_booking.js
│   └── images/
│       ├── logo.png
│       ├── hero.jpg
│       ├── about.jpg
│       ├── aberdeen.jpg
│       ├── birmingham.jpg
│       ├── bristol.jpg
│       ├── cardiff.jpg
│       ├── dundee.jpg
│       ├── edinburgh.jpg
│       ├── glasgow.jpg
│       ├── london.jpg
│       ├── manchester.jpg
│       ├── newcastle.jpg
│       ├── portsmouth.jpg
│       ├── southampton.jpg
│       └── customers.jpg
└── README.md
```

## ▶️ How to Run Locally

1. Clone the repository
   git clone https://github.com/luvevelyn-ss/horizon-travels-fullstack.git
   cd horizon-travels-fullstack
3. Install dependencies
   pip install flask
4. Run the application
   python app.py
5. Open in browser
   http://127.0.0.1:5000

## 🔐 Admin Access

Admin credentials are predefined for demonstration purposes.
You can update the admin credentials directly in the code or database if required.

## 🎯 Future Improvements

Online payment integration
Booking history for users
Role-based access control
Improved UI/UX styling
Deployment to a cloud platform
