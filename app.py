# ============================================================
#  🚌 BUS BOOKING SYSTEM — ITI Mini Project
#  Author  : ITI Student
#  Tech    : Python · Streamlit · ReportLab
#  Run     : streamlit run app.py
# ============================================================

import streamlit as st
import uuid
from datetime import date, datetime
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT


# ──────────────────────────────────────────────────────────
#  PAGE CONFIG
# ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🚌 BusGo — Bus Booking System",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ──────────────────────────────────────────────────────────
#  GLOBAL CSS
# ──────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }

/* ── App background ── */
.stApp { background: #f0f4ff; }

/* ── Top hero banner ── */
.hero {
    background: linear-gradient(135deg, #1a1a6e 0%, #3b5bdb 60%, #74c0fc 100%);
    border-radius: 18px;
    padding: 2rem 2.5rem;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(59,91,219,.35);
}
.hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0; }
.hero p  { font-size: 1.05rem; margin: 0.3rem 0 0; opacity: .85; }

/* ── Section card ── */
.section-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.4rem;
    box-shadow: 0 2px 16px rgba(0,0,0,.07);
    border-left: 5px solid #3b5bdb;
}
.section-title {
    font-size: 1.15rem;
    font-weight: 800;
    color: #1a1a6e;
    margin-bottom: 1rem;
}

/* ── Bus result card ── */
.bus-card {
    background: linear-gradient(135deg, #f8f9ff 0%, #eef2ff 100%);
    border: 1.5px solid #d0d8ff;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    cursor: pointer;
    transition: box-shadow .2s;
}
.bus-card:hover { box-shadow: 0 4px 18px rgba(59,91,219,.2); }
.bus-card.selected {
    border: 2.5px solid #3b5bdb;
    background: #eef2ff;
    box-shadow: 0 4px 18px rgba(59,91,219,.25);
}
.bus-name   { font-size: 1.1rem; font-weight: 800; color: #1a1a6e; }
.bus-type   { font-size: .82rem; background:#dbe4ff; color:#3b5bdb;
              border-radius:20px; padding:2px 10px; margin-left:6px; font-weight:700; }
.bus-price  { font-size: 1.35rem; font-weight: 800; color: #2f9e44; }
.bus-time   { font-size: 1.05rem; font-weight: 700; color: #1a1a6e; }
.bus-label  { font-size: .78rem; color: #888; margin-bottom: 1px; }

/* ── Seat grid ── */
.seat-available { background:#d3f9d8; border:1.5px solid #2f9e44;
                  color:#2f9e44; border-radius:6px; padding:6px 10px;
                  font-weight:700; font-size:.85rem; text-align:center;
                  cursor:pointer; margin:3px; }
.seat-booked    { background:#ffe3e3; border:1.5px solid #e03131;
                  color:#e03131; border-radius:6px; padding:6px 10px;
                  font-weight:700; font-size:.85rem; text-align:center;
                  cursor:not-allowed; margin:3px; }
.seat-selected  { background:#74c0fc; border:1.5px solid #1971c2;
                  color:#1971c2; border-radius:6px; padding:6px 10px;
                  font-weight:700; font-size:.85rem; text-align:center;
                  cursor:pointer; margin:3px; }

/* ── Ticket confirmation ── */
.ticket-box {
    background: linear-gradient(135deg, #1a1a6e 0%, #3b5bdb 100%);
    color: white;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(59,91,219,.35);
}
.ticket-id   { font-size: 1.5rem; font-weight: 800; letter-spacing: 2px; }
.ticket-row  { display:flex; justify-content:space-between;
               border-bottom: 1px solid rgba(255,255,255,.15);
               padding: .45rem 0; font-size:.95rem; }
.ticket-key  { opacity:.75; }
.ticket-val  { font-weight:700; }

/* ── History table ── */
.history-tag {
    background:#d3f9d8; color:#2f9e44; border-radius:20px;
    padding:2px 10px; font-weight:700; font-size:.82rem;
}
.cancelled-tag {
    background:#ffe3e3; color:#e03131; border-radius:20px;
    padding:2px 10px; font-weight:700; font-size:.82rem;
}

/* ── Legend chips ── */
.legend { display:flex; gap:14px; align-items:center; margin-bottom:.8rem; }
.chip   { border-radius:6px; padding:4px 14px; font-size:.82rem; font-weight:700; }
.chip-a { background:#d3f9d8; color:#2f9e44; border:1.5px solid #2f9e44; }
.chip-b { background:#ffe3e3; color:#e03131; border:1.5px solid #e03131; }
.chip-s { background:#74c0fc; color:#1971c2; border:1.5px solid #1971c2; }

/* ── Buttons ── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
}

/* ── Metrics ── */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.4rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,.07);
}
.metric-num  { font-size:1.8rem; font-weight:800; color:#3b5bdb; }
.metric-lbl  { font-size:.85rem; color:#888; font-weight:600; }

</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
#  SAMPLE DATA
# ──────────────────────────────────────────────────────────
CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Nagpur", "Surat", "Bhopal", "Indore", "Kochi"
]

BUS_DATA = [
    {
        "bus_id": "BUS001",
        "operator": "RedBus Express",
        "bus_type": "AC Sleeper",
        "departure": "06:00",
        "arrival": "12:30",
        "duration": "6h 30m",
        "price": 850,
        "total_seats": 32,
        "rating": "4.5 ⭐",
    },
    {
        "bus_id": "BUS002",
        "operator": "VRL Travels",
        "bus_type": "Non-AC Seater",
        "departure": "08:15",
        "arrival": "15:45",
        "duration": "7h 30m",
        "price": 420,
        "total_seats": 40,
        "rating": "4.1 ⭐",
    },
    {
        "bus_id": "BUS003",
        "operator": "SRS Travels",
        "bus_type": "AC Semi-Sleeper",
        "departure": "21:30",
        "arrival": "05:00",
        "duration": "7h 30m",
        "price": 680,
        "total_seats": 36,
        "rating": "4.3 ⭐",
    },
    {
        "bus_id": "BUS004",
        "operator": "Orange Tours",
        "bus_type": "Luxury Volvo",
        "departure": "23:00",
        "arrival": "07:30",
        "duration": "8h 30m",
        "price": 1200,
        "total_seats": 28,
        "rating": "4.8 ⭐",
    },
    {
        "bus_id": "BUS005",
        "operator": "KSRTC",
        "bus_type": "AC Seater",
        "departure": "07:00",
        "arrival": "13:30",
        "duration": "6h 30m",
        "price": 550,
        "total_seats": 44,
        "rating": "3.9 ⭐",
    },
]


# ──────────────────────────────────────────────────────────
#  SESSION STATE INIT
# ──────────────────────────────────────────────────────────
def init_session():
    """Initialise all session-state keys on first load."""
    defaults = {
        "search_done": False,
        "search_params": {},
        "selected_bus": None,
        "selected_seat": None,
        "booking_history": [],           # list of booking dicts
        "booked_seats": {},              # {bus_id: [seat_no, ...]}
        "latest_ticket": None,
        "show_ticket": False,
        "step": "search",               # search | select_bus | select_seat | passenger | confirm
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session()


# ──────────────────────────────────────────────────────────
#  HELPER FUNCTIONS
# ──────────────────────────────────────────────────────────
def generate_booking_id():
    return "BKG" + str(uuid.uuid4()).upper()[:8]

def get_booked_seats(bus_id):
    """Return list of seat numbers already booked for a bus."""
    return st.session_state["booked_seats"].get(bus_id, [])

def book_seat(bus_id, seat_no):
    """Mark a seat as booked."""
    if bus_id not in st.session_state["booked_seats"]:
        st.session_state["booked_seats"][bus_id] = []
    st.session_state["booked_seats"][bus_id].append(seat_no)

def cancel_seat(bus_id, seat_no):
    """Free a previously booked seat."""
    if bus_id in st.session_state["booked_seats"]:
        seats = st.session_state["booked_seats"][bus_id]
        if seat_no in seats:
            seats.remove(seat_no)

def available_seats_count(bus):
    booked = len(get_booked_seats(bus["bus_id"]))
    return bus["total_seats"] - booked

def validate_passenger(name, age_str, gender, mobile):
    """Return (True, '') or (False, error_message)."""
    if not name.strip():
        return False, "Full name is required."
    if not age_str.strip() or not age_str.strip().isdigit():
        return False, "Age must be a valid number."
    age = int(age_str.strip())
    if age < 1 or age > 120:
        return False, "Age must be between 1 and 120."
    if gender == "-- Select --":
        return False, "Please select a gender."
    if not mobile.strip() or not mobile.strip().isdigit() or len(mobile.strip()) != 10:
        return False, "Mobile number must be exactly 10 digits."
    return True, ""


# ──────────────────────────────────────────────────────────
#  PDF GENERATION
# ──────────────────────────────────────────────────────────
def generate_ticket_pdf(ticket: dict) -> bytes:
    """Build a PDF ticket using ReportLab and return raw bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#1a1a6e"),
        alignment=TA_CENTER,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    )
    sub_style = ParagraphStyle(
        "sub",
        parent=styles["Normal"],
        fontSize=11,
        textColor=colors.HexColor("#3b5bdb"),
        alignment=TA_CENTER,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "section",
        parent=styles["Normal"],
        fontSize=12,
        textColor=colors.HexColor("#1a1a6e"),
        fontName="Helvetica-Bold",
        spaceAfter=6,
        spaceBefore=12,
    )

    story = []

    # ── Header ──
    story.append(Paragraph("🚌 BusGo — E-Ticket", title_style))
    story.append(Paragraph("Your journey awaits. Bon Voyage!", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#3b5bdb")))
    story.append(Spacer(1, 0.4 * cm))

    # ── Booking ID banner ──
    bid_data = [[f"Booking ID:  {ticket['booking_id']}"]]
    bid_table = Table(bid_data, colWidths=["100%"])
    bid_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#3b5bdb")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("FONTNAME",  (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE",  (0, 0), (-1, -1), 14),
        ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(bid_table)
    story.append(Spacer(1, 0.4 * cm))

    # ── Journey Details ──
    story.append(Paragraph("🗺️  Journey Details", section_style))
    journey_data = [
        ["Field", "Details"],
        ["From City", ticket["from_city"]],
        ["To City", ticket["to_city"]],
        ["Journey Date", ticket["journey_date"]],
        ["Bus Operator", ticket["bus_operator"]],
        ["Bus Type", ticket["bus_type"]],
        ["Departure", ticket["departure"]],
        ["Arrival", ticket["arrival"]],
        ["Seat Number", str(ticket["seat_no"])],
        ["Ticket Price", f"₹ {ticket['price']}"],
    ]
    journey_table = Table(journey_data, colWidths=[6 * cm, 10 * cm])
    journey_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#1a1a6e")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f8f9ff"), colors.HexColor("#eef2ff")]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#d0d8ff")),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(journey_table)

    # ── Passenger Details ──
    story.append(Paragraph("👤  Passenger Details", section_style))
    passenger_data = [
        ["Field", "Details"],
        ["Full Name",      ticket["passenger_name"]],
        ["Age",            str(ticket["age"])],
        ["Gender",         ticket["gender"]],
        ["Mobile Number",  ticket["mobile"]],
    ]
    p_table = Table(passenger_data, colWidths=[6 * cm, 10 * cm])
    p_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), colors.HexColor("#2f9e44")),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 11),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f4fdf6"), colors.HexColor("#ebfbee")]),
        ("GRID",         (0, 0), (-1, -1), 0.5, colors.HexColor("#b2f2bb")),
        ("TOPPADDING",   (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 7),
        ("LEFTPADDING",  (0, 0), (-1, -1), 10),
    ]))
    story.append(p_table)

    # ── Footer ──
    story.append(Spacer(1, 0.6 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#3b5bdb")))
    story.append(Spacer(1, 0.2 * cm))
    footer_style = ParagraphStyle(
        "footer",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#888888"),
        alignment=TA_CENTER,
    )
    story.append(Paragraph(
        f"Generated on {datetime.now().strftime('%d %b %Y %I:%M %p')}  |  "
        "BusGo Bus Booking System  |  ITI Mini Project",
        footer_style
    ))

    doc.build(story)
    return buffer.getvalue()


# ──────────────────────────────────────────────────────────
#  UI SECTIONS
# ──────────────────────────────────────────────────────────

# ─── HERO BANNER ────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🚌 BusGo — Bus Booking System</h1>
  <p>Search · Book · Travel  |  Fast · Safe · Reliable</p>
</div>
""", unsafe_allow_html=True)


# ─── TOP METRICS ────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
total_bookings   = len([b for b in st.session_state["booking_history"] if b["status"] == "Confirmed"])
cancelled        = len([b for b in st.session_state["booking_history"] if b["status"] == "Cancelled"])
total_revenue    = sum(b["price"] for b in st.session_state["booking_history"] if b["status"] == "Confirmed")
buses_available  = len(BUS_DATA)

with m1:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-num">{total_bookings}</div>
      <div class="metric-lbl">✅ Total Bookings</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-num">{cancelled}</div>
      <div class="metric-lbl">❌ Cancellations</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-num">₹{total_revenue:,}</div>
      <div class="metric-lbl">💰 Revenue</div>
    </div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-num">{buses_available}</div>
      <div class="metric-lbl">🚌 Buses Available</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────
#  TABS
# ──────────────────────────────────────────────────────────
tab_book, tab_history, tab_cancel = st.tabs([
    "🎟️  Book Ticket",
    "📋  Booking History",
    "❌  Cancel Booking",
])


# ╔══════════════════════════════════════════════════════╗
#  TAB 1 — BOOK TICKET
# ╚══════════════════════════════════════════════════════╝
with tab_book:

    # ── STEP 1: SEARCH ────────────────────────────────
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔍 Step 1 — Search Buses</div>', unsafe_allow_html=True)

    col_from, col_to, col_date = st.columns(3)
    with col_from:
        from_city = st.selectbox("🏙️ From City", ["-- Select --"] + CITIES, key="from_city")
    with col_to:
        to_city = st.selectbox("🏙️ To City", ["-- Select --"] + CITIES, key="to_city")
    with col_date:
        journey_date = st.date_input(
            "📅 Journey Date",
            min_value=date.today(),
            value=date.today(),
            key="journey_date",
        )

    _, btn_col, _ = st.columns([3, 2, 3])
    with btn_col:
        search_btn = st.button("🔍  Search Buses", use_container_width=True, type="primary")

    if search_btn:
        if from_city == "-- Select --" or to_city == "-- Select --":
            st.error("⚠️  Please select both From City and To City.")
        elif from_city == to_city:
            st.error("⚠️  From City and To City cannot be the same.")
        else:
            st.session_state["search_done"] = True
            st.session_state["search_params"] = {
                "from_city": from_city,
                "to_city": to_city,
                "journey_date": str(journey_date),
            }
            st.session_state["selected_bus"]  = None
            st.session_state["selected_seat"] = None
            st.session_state["step"]          = "select_bus"

    st.markdown('</div>', unsafe_allow_html=True)


    # ── STEP 2: SELECT BUS ────────────────────────────
    if st.session_state.get("search_done"):
        sp = st.session_state["search_params"]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-title">🚌 Step 2 — Available Buses &nbsp;'
            f'<span style="font-size:.85rem;color:#666;font-weight:600;">'
            f'{sp["from_city"]} → {sp["to_city"]}  |  {sp["journey_date"]}</span></div>',
            unsafe_allow_html=True
        )

        for bus in BUS_DATA:
            avail = available_seats_count(bus)
            is_sel = (
                st.session_state["selected_bus"] is not None and
                st.session_state["selected_bus"]["bus_id"] == bus["bus_id"]
            )
            card_cls = "bus-card selected" if is_sel else "bus-card"

            c1, c2, c3, c4, c5 = st.columns([3, 2, 2, 2, 2])
            with c1:
                st.markdown(
                    f'<span class="bus-name">{bus["operator"]}</span>'
                    f'<span class="bus-type">{bus["bus_type"]}</span>',
                    unsafe_allow_html=True
                )
                st.caption(f"🆔 {bus['bus_id']}  |  {bus['rating']}")
            with c2:
                st.markdown('<div class="bus-label">🕐 Departure</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bus-time">{bus["departure"]}</div>', unsafe_allow_html=True)
            with c3:
                st.markdown('<div class="bus-label">🕓 Arrival</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bus-time">{bus["arrival"]}</div>', unsafe_allow_html=True)
            with c4:
                st.markdown('<div class="bus-label">⏱ Duration</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="bus-time">{bus["duration"]}</div>', unsafe_allow_html=True)
                avail_color = "#2f9e44" if avail > 5 else ("#f08c00" if avail > 0 else "#e03131")
                st.markdown(
                    f'<span style="color:{avail_color};font-size:.85rem;font-weight:700;">'
                    f'{"✅" if avail > 0 else "❌"} {avail} seats left</span>',
                    unsafe_allow_html=True
                )
            with c5:
                st.markdown(f'<div class="bus-price">₹ {bus["price"]}</div>', unsafe_allow_html=True)
                if avail > 0:
                    if st.button(
                        f"{'✔ Selected' if is_sel else 'Select'}",
                        key=f"sel_{bus['bus_id']}",
                        type="primary" if is_sel else "secondary",
                        use_container_width=True,
                    ):
                        st.session_state["selected_bus"]  = bus
                        st.session_state["selected_seat"] = None
                        st.session_state["step"]          = "select_seat"
                        st.rerun()
                else:
                    st.button("Sold Out", key=f"sold_{bus['bus_id']}", disabled=True, use_container_width=True)

            st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)


    # ── STEP 3: SELECT SEAT ───────────────────────────
    if st.session_state["selected_bus"] is not None:
        bus = st.session_state["selected_bus"]
        booked = get_booked_seats(bus["bus_id"])
        total  = bus["total_seats"]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-title">💺 Step 3 — Select Seat &nbsp;'
            f'<span style="font-size:.85rem;color:#666;font-weight:600;">{bus["operator"]}</span></div>',
            unsafe_allow_html=True
        )

        # Legend
        st.markdown("""
        <div class="legend">
          <span class="chip chip-a">✅ Available</span>
          <span class="chip chip-b">❌ Booked</span>
          <span class="chip chip-s">🔵 Selected</span>
        </div>
        """, unsafe_allow_html=True)

        # Seat grid — 4 seats per row
        seats_per_row = 4
        num_rows = (total + seats_per_row - 1) // seats_per_row

        for row_idx in range(num_rows):
            cols = st.columns(seats_per_row)
            for col_idx in range(seats_per_row):
                seat_no = row_idx * seats_per_row + col_idx + 1
                if seat_no > total:
                    break
                with cols[col_idx]:
                    is_booked   = seat_no in booked
                    is_selected = st.session_state["selected_seat"] == seat_no

                    if is_booked:
                        st.markdown(
                            f'<div class="seat-booked">❌ {seat_no}</div>',
                            unsafe_allow_html=True
                        )
                    elif is_selected:
                        if st.button(f"🔵 {seat_no}", key=f"seat_{seat_no}", use_container_width=True):
                            st.session_state["selected_seat"] = None
                            st.rerun()
                    else:
                        if st.button(f"✅ {seat_no}", key=f"seat_{seat_no}", use_container_width=True):
                            st.session_state["selected_seat"] = seat_no
                            st.rerun()

        if st.session_state["selected_seat"]:
            st.success(f"✅ Seat **{st.session_state['selected_seat']}** selected!")

        st.markdown('</div>', unsafe_allow_html=True)


    # ── STEP 4: PASSENGER DETAILS ─────────────────────
    if st.session_state["selected_seat"] is not None:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Step 4 — Passenger Details</div>', unsafe_allow_html=True)

        pc1, pc2, pc3, pc4 = st.columns(4)
        with pc1:
            p_name   = st.text_input("👤 Full Name", placeholder="e.g. Rahul Sharma", key="p_name")
        with pc2:
            p_age    = st.text_input("🎂 Age", placeholder="e.g. 25", key="p_age")
        with pc3:
            p_gender = st.selectbox("⚧ Gender", ["-- Select --", "Male", "Female", "Other"], key="p_gender")
        with pc4:
            p_mobile = st.text_input("📱 Mobile Number (10 digits)", placeholder="e.g. 9876543210", key="p_mobile")

        st.markdown('</div>', unsafe_allow_html=True)


        # ── STEP 5: BOOKING SUMMARY + CONFIRM ─────────
        bus  = st.session_state["selected_bus"]
        seat = st.session_state["selected_seat"]
        sp   = st.session_state["search_params"]

        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Step 5 — Booking Summary</div>', unsafe_allow_html=True)

        sum_l, sum_r = st.columns(2)
        with sum_l:
            st.markdown("**🗺️ Journey Details**")
            st.markdown(f"- **From:** {sp['from_city']}")
            st.markdown(f"- **To:** {sp['to_city']}")
            st.markdown(f"- **Date:** {sp['journey_date']}")
            st.markdown(f"- **Bus:** {bus['operator']} ({bus['bus_type']})")
            st.markdown(f"- **Departure:** {bus['departure']}  →  **Arrival:** {bus['arrival']}")
            st.markdown(f"- **Duration:** {bus['duration']}")
        with sum_r:
            st.markdown("**💺 Ticket Details**")
            st.markdown(f"- **Seat No.:** {seat}")
            st.markdown(f"- **Price:** ₹ {bus['price']}")
            if p_name.strip():
                st.markdown(f"- **Passenger:** {p_name.strip()}")
            if p_age.strip():
                st.markdown(f"- **Age:** {p_age.strip()}")
            if p_gender != "-- Select --":
                st.markdown(f"- **Gender:** {p_gender}")
            if p_mobile.strip():
                st.markdown(f"- **Mobile:** {p_mobile.strip()}")

        _, btn_col2, _ = st.columns([3, 2, 3])
        with btn_col2:
            confirm_btn = st.button("🎟️  Confirm Booking", use_container_width=True, type="primary")

        if confirm_btn:
            valid, err = validate_passenger(p_name, p_age, p_gender, p_mobile)
            if not valid:
                st.error(f"⚠️  {err}")
            else:
                # Create ticket
                booking_id = generate_booking_id()
                ticket = {
                    "booking_id":     booking_id,
                    "from_city":      sp["from_city"],
                    "to_city":        sp["to_city"],
                    "journey_date":   sp["journey_date"],
                    "bus_id":         bus["bus_id"],
                    "bus_operator":   bus["operator"],
                    "bus_type":       bus["bus_type"],
                    "departure":      bus["departure"],
                    "arrival":        bus["arrival"],
                    "duration":       bus["duration"],
                    "seat_no":        seat,
                    "price":          bus["price"],
                    "passenger_name": p_name.strip(),
                    "age":            int(p_age.strip()),
                    "gender":         p_gender,
                    "mobile":         p_mobile.strip(),
                    "booked_at":      datetime.now().strftime("%d %b %Y %I:%M %p"),
                    "status":         "Confirmed",
                }
                book_seat(bus["bus_id"], seat)
                st.session_state["booking_history"].append(ticket)
                st.session_state["latest_ticket"]  = ticket
                st.session_state["show_ticket"]    = True
                st.session_state["selected_bus"]   = None
                st.session_state["selected_seat"]  = None
                st.session_state["search_done"]    = False
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


    # ── TICKET CONFIRMED ──────────────────────────────
    if st.session_state.get("show_ticket") and st.session_state["latest_ticket"]:
        t = st.session_state["latest_ticket"]
        st.balloons()
        st.success("🎉 Booking Confirmed! Your ticket is ready.")

        st.markdown(f"""
        <div class="ticket-box">
          <div style="text-align:center;margin-bottom:1rem;">
            <div style="font-size:2rem;">🎟️</div>
            <div class="ticket-id">{t['booking_id']}</div>
            <div style="opacity:.7;font-size:.9rem;margin-top:2px;">Booking Confirmed ✅</div>
          </div>
          <div class="ticket-row"><span class="ticket-key">🗺️ Route</span>
            <span class="ticket-val">{t['from_city']} → {t['to_city']}</span></div>
          <div class="ticket-row"><span class="ticket-key">📅 Date</span>
            <span class="ticket-val">{t['journey_date']}</span></div>
          <div class="ticket-row"><span class="ticket-key">🚌 Bus</span>
            <span class="ticket-val">{t['bus_operator']} ({t['bus_type']})</span></div>
          <div class="ticket-row"><span class="ticket-key">🕐 Departure</span>
            <span class="ticket-val">{t['departure']}</span></div>
          <div class="ticket-row"><span class="ticket-key">🕓 Arrival</span>
            <span class="ticket-val">{t['arrival']}</span></div>
          <div class="ticket-row"><span class="ticket-key">💺 Seat</span>
            <span class="ticket-val">{t['seat_no']}</span></div>
          <div class="ticket-row"><span class="ticket-key">👤 Passenger</span>
            <span class="ticket-val">{t['passenger_name']}  |  Age {t['age']}  |  {t['gender']}</span></div>
          <div class="ticket-row"><span class="ticket-key">📱 Mobile</span>
            <span class="ticket-val">{t['mobile']}</span></div>
          <div class="ticket-row"><span class="ticket-key">💰 Price</span>
            <span class="ticket-val">₹ {t['price']}</span></div>
          <div class="ticket-row"><span class="ticket-key">🕑 Booked At</span>
            <span class="ticket-val">{t['booked_at']}</span></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── PDF Download Button ────────────────────────
        pdf_bytes = generate_ticket_pdf(t)
        dl_col1, dl_col2, dl_col3 = st.columns([2, 2, 2])
        with dl_col2:
            st.download_button(
                label="📄  Download Ticket PDF",
                data=pdf_bytes,
                file_name=f"BusGo_Ticket_{t['booking_id']}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary",
            )
        with dl_col3:
            if st.button("🔄  Book Another Ticket", use_container_width=True):
                st.session_state["show_ticket"] = False
                st.session_state["latest_ticket"] = None
                st.rerun()


# ╔══════════════════════════════════════════════════════╗
#  TAB 2 — BOOKING HISTORY
# ╚══════════════════════════════════════════════════════╝
with tab_history:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 All Bookings</div>', unsafe_allow_html=True)

    history = st.session_state["booking_history"]
    if not history:
        st.info("📭 No bookings yet. Book a ticket first!")
    else:
        # Build display rows
        rows = []
        for b in reversed(history):
            status_html = (
                '<span class="history-tag">✅ Confirmed</span>'
                if b["status"] == "Confirmed"
                else '<span class="cancelled-tag">❌ Cancelled</span>'
            )
            rows.append({
                "Booking ID":    b["booking_id"],
                "Passenger":     b["passenger_name"],
                "Route":         f"{b['from_city']} → {b['to_city']}",
                "Date":          b["journey_date"],
                "Bus":           b["bus_operator"],
                "Seat":          b["seat_no"],
                "Price (₹)":     b["price"],
                "Status":        b["status"],
                "Booked At":     b["booked_at"],
            })

        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown('</div>', unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════╗
#  TAB 3 — CANCEL BOOKING
# ╚══════════════════════════════════════════════════════╝
with tab_cancel:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">❌ Cancel Booking</div>', unsafe_allow_html=True)

    cancel_id = st.text_input(
        "Enter Booking ID to Cancel",
        placeholder="e.g. BKG1A2B3C4D",
        key="cancel_id_input"
    )

    _, cbtn_col, _ = st.columns([3, 2, 3])
    with cbtn_col:
        cancel_btn = st.button("❌  Cancel Booking", use_container_width=True, type="primary")

    if cancel_btn:
        if not cancel_id.strip():
            st.error("⚠️  Please enter a Booking ID.")
        else:
            found = False
            for b in st.session_state["booking_history"]:
                if b["booking_id"].upper() == cancel_id.strip().upper():
                    found = True
                    if b["status"] == "Cancelled":
                        st.warning("⚠️  This booking is already cancelled.")
                    else:
                        b["status"] = "Cancelled"
                        cancel_seat(b["bus_id"], b["seat_no"])
                        st.success(
                            f"✅ Booking **{b['booking_id']}** cancelled successfully! "
                            f"Seat **{b['seat_no']}** is now available."
                        )
                        st.balloons()
                    break
            if not found:
                st.error("❌  Booking ID not found. Please check and try again.")

    # ── Show active bookings for reference ─────────────
    active = [b for b in st.session_state["booking_history"] if b["status"] == "Confirmed"]
    if active:
        st.markdown("---")
        st.markdown("**Your Active Bookings:**")
        for b in active:
            st.markdown(
                f"🟢 `{b['booking_id']}` — {b['from_city']} → {b['to_city']} "
                f"| Seat {b['seat_no']} | {b['journey_date']}"
            )

    st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────
#  FOOTER
# ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#aaa;font-size:.85rem;padding:1rem 0;">
  🚌 <b>BusGo Bus Booking System</b> · ITI Mini Project ·
  Built with ❤️ using Python · Streamlit · ReportLab
</div>
""", unsafe_allow_html=True)
