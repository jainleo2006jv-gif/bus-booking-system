# 🚌 BusGo — Bus Booking System
### ITI Mini Project Report

---

## 1. PROJECT TITLE
**BusGo — Online Bus Booking System**

---

## 2. OBJECTIVE
To design and develop a fully functional, web-based Bus Booking System using Python and
Streamlit that allows users to search buses, select seats, fill passenger details, confirm bookings,
download e-tickets as PDF, view booking history, and cancel bookings — all through a clean,
modern dashboard UI.

---

## 3. PROJECT STRUCTURE

```
bus_booking/
├── app.py            ← Main Streamlit application (all code here)
├── requirements.txt  ← Python dependencies
└── README.md         ← This file
```

---

## 4. SOFTWARE REQUIREMENTS

| Component        | Version / Details          |
|------------------|---------------------------|
| Operating System | Windows 10/11 or Ubuntu   |
| Python           | 3.9 or higher             |
| Streamlit        | 1.32.0 or higher          |
| ReportLab        | 4.1.0 or higher           |
| Pandas           | 2.0.0 or higher           |
| Browser          | Chrome / Firefox / Edge   |

---

## 5. HARDWARE REQUIREMENTS

| Component | Minimum Specification  |
|-----------|------------------------|
| Processor | Intel Core i3 or above |
| RAM       | 4 GB or above          |
| Storage   | 500 MB free space      |
| Network   | Not required (runs locally) |

---

## 6. HOW TO INSTALL AND RUN

### Step 1 — Install Python
Download and install Python 3.9+ from https://www.python.org

### Step 2 — Install Dependencies
Open Command Prompt / Terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

OR install individually:

```bash
pip install streamlit reportlab pandas
```

### Step 3 — Run the App

```bash
streamlit run app.py
```

The app will open automatically in your browser at:
```
http://localhost:8501
```

---

## 7. FEATURES EXPLAINED

### 7.1 Search Buses
- Select **From City**, **To City**, and **Journey Date** using dropdowns and a date picker.
- Laid out in **3 columns** for a clean dashboard look.
- Validates that both cities are selected and are different.

### 7.2 Available Buses Display
- Shows **5 sample buses** with details: Operator, Bus Type, Departure, Arrival, Duration,
  Price, Seats Available, Rating.
- Uses **5 columns per bus card** for a professional card layout.
- Seats available shown in colour (green / orange / red).

### 7.3 Seat Selection (Grid Layout)
- Displays up to 44 seats in a **4-column grid**.
- **Green button** = Available seat.
- **Red label**   = Booked seat (cannot be clicked).
- **Blue button**  = Currently selected seat (click again to deselect).
- Prevents selecting already-booked seats.

### 7.4 Passenger Details Form
- **4 columns**: Full Name, Age, Gender, Mobile Number.
- All fields are validated before allowing booking.

### 7.5 Booking Summary
- **2-column layout**: Journey Details (left) + Ticket Details (right).
- Shows a real-time preview of all booking info before confirmation.

### 7.6 Booking Confirmation + E-Ticket
- Generates a **unique Booking ID** (e.g., `BKG1A2B3C4D`).
- Displays a beautiful dark-blue **ticket card** with all details.
- Shows **balloons** animation on successful booking.

### 7.7 PDF Ticket Download
- Generates a professional **A4 PDF ticket** using ReportLab.
- Includes journey table, passenger table, booking ID banner, and footer.
- One-click download using Streamlit's `download_button`.

### 7.8 Booking History
- Shows all bookings (confirmed + cancelled) in a **pandas DataFrame table**.
- Displayed in the **Booking History** tab.

### 7.9 Cancel Booking
- Enter a **Booking ID** and click Cancel.
- The seat is freed and becomes available again for new bookings.
- Active bookings are listed for reference.

### 7.10 Dashboard Metrics
- Top row shows **4 metric cards**: Total Bookings, Cancellations, Revenue, Buses Available.
- Updates in real-time as bookings are made.

---

## 8. VIVA QUESTIONS AND ANSWERS

**Q1. What is Streamlit?**
A: Streamlit is an open-source Python framework that allows developers to create interactive
web applications quickly without needing HTML, CSS, or JavaScript knowledge. It converts
Python scripts into shareable web apps.

**Q2. What is st.session_state?**
A: `st.session_state` is a Streamlit feature that allows storing variables across reruns of the
app (since Streamlit reruns the script on every interaction). We use it to store the selected bus,
selected seat, booking history, and booked seats.

**Q3. What is ReportLab used for?**
A: ReportLab is a Python library for generating PDF documents programmatically. In this project,
we use it to create a formatted A4 PDF e-ticket with tables, colours, and styled text.

**Q4. What is st.columns() used for?**
A: `st.columns(n)` splits the Streamlit page into `n` side-by-side columns, allowing us to
create dashboard-style layouts with multiple elements displayed horizontally.

**Q5. How do you prevent duplicate seat booking?**
A: We store booked seats in `st.session_state["booked_seats"]` as a dictionary `{bus_id: [seats]}`.
Before confirming a booking, we check if the seat is already in this list. Booked seats show
as red labels without a clickable button.

**Q6. What is uuid used for?**
A: The `uuid` (Universally Unique Identifier) module generates unique random IDs. We use
`uuid.uuid4()` to generate a unique Booking ID for every confirmed ticket.

**Q7. What is st.download_button?**
A: `st.download_button` creates a button that allows users to download a file directly from the
browser. We pass the PDF bytes from ReportLab to this button so users can download their ticket.

**Q8. What validation is done in the project?**
A: (a) From City and To City must be selected and different, (b) passenger name cannot be empty,
(c) age must be a number between 1 and 120, (d) gender must be selected, (e) mobile number must
be exactly 10 digits, (f) journey date cannot be in the past.

**Q9. What is pandas used for here?**
A: Pandas is used to create a `DataFrame` from the booking history list and display it as a
formatted table using `st.dataframe()`.

**Q10. What is the difference between st.success, st.error, st.warning, and st.info?**
A: These are Streamlit alert functions that display colored message boxes:
- `st.success` → green (success message)
- `st.error`   → red (error message)
- `st.warning` → yellow (warning message)
- `st.info`    → blue (informational message)

---

## 9. CONCLUSION
The BusGo Bus Booking System successfully demonstrates the use of Python and Streamlit to build
a modern, interactive web application. The project covers key concepts like state management,
form validation, dynamic UI rendering, PDF generation, and modular code design — making it an
excellent mini project for ITI students to understand full-stack Python web development.

---

## 10. FUTURE SCOPE

1. **Database Integration** — Replace in-memory session storage with SQLite or MySQL for
   persistent data storage across sessions.
2. **User Authentication** — Add login/signup functionality with password hashing.
3. **Payment Gateway** — Integrate a payment API (Razorpay/PayU) for real ticket payments.
4. **Admin Dashboard** — Add an admin panel to manage buses, routes, and view all bookings.
5. **Email Confirmation** — Send the PDF ticket to the passenger's email using smtplib.
6. **OTP Verification** — Add mobile OTP verification using Twilio API.
7. **Dynamic Routes** — Allow admins to add/edit bus routes and schedules dynamically.
8. **Multi-language Support** — Support regional languages for a wider user base.

---

*Submitted as ITI Mini Project | Department of Computer Science | Academic Year 2024–25*
