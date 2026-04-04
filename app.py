import streamlit as st
import sqlite3
import hashlib
import random
import string
import re
from datetime import datetime, date, timedelta
import io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, HRFlowable
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

DB_PATH = "bus_booking.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

COUPONS = {
    "SAVE10":  ("percent", 10),
    "FLAT50":  ("flat",    50),
    "FIRST20": ("percent", 20),
    "BLAZE25": ("percent", 25),
}

st.set_page_config(
    page_title="BusGo — Smart Bus Booking",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');
:root{--bg:#0b0e1a;--surface:#131728;--card:#1a1f35;--border:#252d4a;--accent:#f97316;--accent2:#fb923c;--blue:#3b82f6;--green:#22c55e;--red:#ef4444;--text:#e8eaf0;--muted:#7c8ab0;--radius:14px;}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text);font-family:'DM Sans',sans-serif;}
[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3,h4,h5{font-family:'Syne',sans-serif!important;color:var(--text)!important;}
[data-testid="metric-container"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;padding:1rem!important;}
[data-baseweb="input"] input,[data-baseweb="select"] div,[data-testid="stDateInput"] input,textarea{background:var(--card)!important;border:1px solid var(--border)!important;color:var(--text)!important;border-radius:8px!important;}
.stButton>button{background:linear-gradient(135deg,var(--accent),var(--accent2))!important;color:#fff!important;border:none!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:700!important;letter-spacing:.04em!important;transition:transform .15s,box-shadow .15s!important;}
.stButton>button:hover{transform:translateY(-2px)!important;box-shadow:0 8px 24px rgba(249,115,22,.35)!important;}
[data-baseweb="tab-list"]{background:var(--surface)!important;border-radius:var(--radius)!important;gap:4px!important;padding:4px!important;}
[data-baseweb="tab"]{background:transparent!important;color:var(--muted)!important;border-radius:10px!important;font-family:'Syne',sans-serif!important;font-weight:600!important;}
[aria-selected="true"][data-baseweb="tab"]{background:var(--accent)!important;color:#fff!important;}
[data-testid="stAlert"]{border-radius:var(--radius)!important;}
hr{border-color:var(--border)!important;}
[data-testid="stSelectbox"]>div>div{background:var(--card)!important;border-color:var(--border)!important;color:var(--text)!important;}
[data-testid="stNumberInput"] input{background:var(--card)!important;color:var(--text)!important;border-color:var(--border)!important;}
[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius)!important;}
.bus-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:1.4rem 1.6rem;margin-bottom:1rem;}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:.75rem;font-weight:700;font-family:'Syne',sans-serif;letter-spacing:.06em;}
.badge-green{background:rgba(34,197,94,.15);color:#22c55e;}
.badge-red{background:rgba(239,68,68,.15);color:#ef4444;}
.badge-orange{background:rgba(249,115,22,.15);color:#f97316;}
.badge-blue{background:rgba(59,130,246,.15);color:#3b82f6;}
.hero-banner{background:linear-gradient(135deg,#1a1f35 0%,#0f1628 60%,#1a1220 100%);border:1px solid var(--border);border-radius:20px;padding:2rem 2.5rem;margin-bottom:2rem;position:relative;overflow:hidden;}
.hero-banner::before{content:'';position:absolute;top:-40px;right:-40px;width:200px;height:200px;background:radial-gradient(circle,rgba(249,115,22,.18) 0%,transparent 70%);border-radius:50%;}
.hero-title{font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;background:linear-gradient(135deg,#f97316,#fb923c,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;}
.hero-sub{color:var(--muted);margin-top:.4rem;font-size:1rem;}
.auth-logo{text-align:center;font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,#f97316,#fbbf24);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:.25rem;}
.demo-creds{background:rgba(59,130,246,.1);border:1px solid rgba(59,130,246,.25);border-radius:10px;padding:.7rem 1rem;font-size:.85rem;color:#93c5fd;margin-top:1rem;}
</style>
""", unsafe_allow_html=True)

# ─── DB ──────────────────────────────────────────────────────────────────────
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    conn = get_conn(); c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT DEFAULT '',username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,role TEXT DEFAULT 'User',
        mobile TEXT DEFAULT '',email TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now','localtime')))""")
    for col,defn in [("full_name","TEXT DEFAULT ''"),("mobile","TEXT DEFAULT ''"),
                     ("email","TEXT DEFAULT ''"),("created_at","TEXT DEFAULT (datetime('now','localtime'))")]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} {defn}")
        except: pass
    c.execute("""CREATE TABLE IF NOT EXISTS buses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,bus_name TEXT NOT NULL,
        bus_number TEXT NOT NULL,from_city TEXT NOT NULL,to_city TEXT NOT NULL,
        departure TEXT NOT NULL,arrival TEXT NOT NULL,total_seats INTEGER DEFAULT 40,
        price REAL NOT NULL,bus_type TEXT DEFAULT 'AC Sleeper',
        amenities TEXT DEFAULT '',is_active INTEGER DEFAULT 1)""")
    for col,defn in [("bus_name","TEXT NOT NULL DEFAULT ''"),("bus_number","TEXT NOT NULL DEFAULT ''"),
                     ("from_city","TEXT NOT NULL DEFAULT ''"),("to_city","TEXT NOT NULL DEFAULT ''"),
                     ("departure","TEXT NOT NULL DEFAULT ''"),("arrival","TEXT NOT NULL DEFAULT ''"),
                     ("total_seats","INTEGER DEFAULT 40"),("price","REAL DEFAULT 0"),
                     ("bus_type","TEXT DEFAULT 'AC Sleeper'"),("amenities","TEXT DEFAULT ''"),
                     ("is_active","INTEGER DEFAULT 1")]:
        try: c.execute(f"ALTER TABLE buses ADD COLUMN {col} {defn}")
        except: pass
    c.execute("""CREATE TABLE IF NOT EXISTS bookings(
        id INTEGER PRIMARY KEY AUTOINCREMENT,pnr TEXT UNIQUE NOT NULL,
        username TEXT NOT NULL,bus_id INTEGER NOT NULL,passenger_name TEXT NOT NULL,
        passenger_age INTEGER DEFAULT 0,passenger_gender TEXT DEFAULT '',
        seat_number TEXT NOT NULL,journey_date TEXT NOT NULL,
        booking_date TEXT DEFAULT (datetime('now','localtime')),
        fare REAL NOT NULL,discount REAL DEFAULT 0,total_paid REAL NOT NULL,
        coupon_used TEXT DEFAULT '',payment_method TEXT DEFAULT 'UPI',
        status TEXT DEFAULT 'Confirmed',refund_amount REAL DEFAULT 0)""")
    for col,defn in [("pnr","TEXT DEFAULT ''"),("username","TEXT DEFAULT ''"),
                     ("bus_id","INTEGER DEFAULT 0"),("passenger_name","TEXT DEFAULT ''"),
                     ("seat_number","TEXT DEFAULT ''"),("journey_date","TEXT DEFAULT ''"),
                     ("fare","REAL DEFAULT 0"),("total_paid","REAL DEFAULT 0"),
                     ("status","TEXT DEFAULT 'Confirmed'"),
                     ("booking_date","TEXT DEFAULT (datetime('now','localtime'))"),
                     ("passenger_age","INTEGER DEFAULT 0"),("passenger_gender","TEXT DEFAULT ''"),
                     ("discount","REAL DEFAULT 0"),("coupon_used","TEXT DEFAULT ''"),
                     ("payment_method","TEXT DEFAULT 'UPI'"),("refund_amount","REAL DEFAULT 0")]:
        try: c.execute(f"ALTER TABLE bookings ADD COLUMN {col} {defn}")
        except: pass
    conn.commit(); _seed_admin(conn); _seed_buses(conn); conn.close()

def _seed_admin(conn):
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?",(ADMIN_USERNAME,))
    if not c.fetchone():
        c.execute("INSERT INTO users(full_name,username,password,role) VALUES(?,?,?,?)",
                  ("Administrator",ADMIN_USERNAME,hash_pw(ADMIN_PASSWORD),"Admin"))
        conn.commit()

def _seed_buses(conn):
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM buses")
    if c.fetchone()[0]==0:
        buses=[
            ("Blaze Express","TN01AB1234","Chennai","Bangalore","06:00","11:30",40,450,"AC Sleeper","WiFi,Water,Blanket"),
            ("Star Liner","TN02CD5678","Chennai","Coimbatore","21:00","05:00",36,380,"AC Semi-Sleeper","WiFi,Charging"),
            ("Raj Travels","KA03EF9012","Bangalore","Mumbai","18:00","08:00",44,950,"Volvo AC","WiFi,USB,Snacks"),
            ("City Shuttle","MH04GH3456","Mumbai","Pune","08:00","11:00",32,250,"Non-AC Seater","Water"),
            ("Royal Cruiser","TN05IJ7890","Chennai","Hyderabad","19:30","06:30",40,750,"AC Sleeper","WiFi,Blanket,Snacks"),
            ("Speed Link","AP06KL2345","Hyderabad","Bangalore","22:00","05:30",36,600,"AC Semi-Sleeper","WiFi,Charging"),
            ("Golden Travels","TN07MN6789","Coimbatore","Chennai","07:00","13:00",40,420,"AC Sleeper","WiFi,Water"),
            ("Night Rider","KA08OP0123","Bangalore","Chennai","22:30","05:00",44,480,"Volvo AC","WiFi,Blanket,USB"),
        ]
        c.executemany("INSERT INTO buses(bus_name,bus_number,from_city,to_city,departure,arrival,total_seats,price,bus_type,amenities) VALUES(?,?,?,?,?,?,?,?,?,?)",buses)
        conn.commit()

# ─── AUTH ─────────────────────────────────────────────────────────────────────
def authenticate(username,password):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT username,role FROM users WHERE username=? AND password=?",(username,hash_pw(password)))
    row=c.fetchone(); conn.close(); return row

def register_user(full_name,username,password,mobile,email):
    conn=get_conn(); c=conn.cursor()
    try:
        c.execute("INSERT INTO users(full_name,username,password,role,mobile,email) VALUES(?,?,?,?,?,?)",
                  (full_name,username,hash_pw(password),"User",mobile,email))
        conn.commit(); return True,"Account created! You can now log in."
    except sqlite3.IntegrityError: return False,"Username already taken."
    finally: conn.close()

def username_exists(u):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT id FROM users WHERE username=?",(u,))
    e=c.fetchone() is not None; conn.close(); return e

def logout():
    for k in ["logged_in","username","role","page","selected_bus","selected_seats","search_results"]:
        st.session_state.pop(k,None)

# ─── BUS / BOOKING ───────────────────────────────────────────────────────────
def get_cities():
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT DISTINCT from_city FROM buses WHERE is_active=1 UNION SELECT DISTINCT to_city FROM buses WHERE is_active=1 ORDER BY 1")
    cities=[r[0] for r in c.fetchall()]; conn.close(); return cities

def search_buses(fc,tc):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT id,bus_name,bus_number,from_city,to_city,departure,arrival,total_seats,price,bus_type,amenities FROM buses WHERE from_city=? AND to_city=? AND is_active=1",(fc,tc))
    rows=c.fetchall(); conn.close(); return rows

def get_bus(bid):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT * FROM buses WHERE id=?",(bid,))
    row=c.fetchone(); conn.close(); return row

def get_booked_seats(bus_id,jdate):
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT seat_number FROM bookings WHERE bus_id=? AND journey_date=? AND status='Confirmed'",(bus_id,jdate))
    seats=[r[0] for r in c.fetchall()]; conn.close(); return seats

def gen_pnr():
    return "BG"+"".join(random.choices(string.digits,k=8))

def create_booking(username,bus_id,pname,page,pgender,seat,jdate,fare,discount,total_paid,coupon,payment):
    pnr=gen_pnr(); conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO bookings(pnr,username,bus_id,passenger_name,passenger_age,passenger_gender,seat_number,journey_date,fare,discount,total_paid,coupon_used,payment_method,status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,'Confirmed')",
              (pnr,username,bus_id,pname,page,pgender,seat,jdate,fare,discount,total_paid,coupon,payment))
    conn.commit(); conn.close(); return pnr

def get_user_bookings(username):
    conn=get_conn(); c=conn.cursor()
    c.execute("""SELECT b.pnr,bu.bus_name,bu.from_city,bu.to_city,b.passenger_name,b.seat_number,
        b.journey_date,b.total_paid,b.status,b.booking_date,b.coupon_used,b.payment_method,
        b.refund_amount,b.id,bu.departure,bu.arrival,bu.bus_type,bu.bus_number,b.discount,b.fare,b.passenger_age,b.passenger_gender
        FROM bookings b JOIN buses bu ON b.bus_id=bu.id WHERE b.username=? ORDER BY b.booking_date DESC""",(username,))
    rows=c.fetchall(); conn.close(); return rows

def get_all_bookings():
    conn=get_conn(); c=conn.cursor()
    c.execute("""SELECT b.pnr,b.username,bu.bus_name,bu.from_city,bu.to_city,b.passenger_name,
        b.seat_number,b.journey_date,b.total_paid,b.status,b.booking_date,b.payment_method,b.refund_amount
        FROM bookings b JOIN buses bu ON b.bus_id=bu.id ORDER BY b.booking_date DESC""")
    rows=c.fetchall(); conn.close(); return rows

def search_pnr(pnr):
    conn=get_conn(); c=conn.cursor()
    c.execute("""SELECT b.pnr,b.username,bu.bus_name,bu.bus_number,bu.from_city,bu.to_city,
        bu.departure,bu.arrival,b.passenger_name,b.passenger_age,b.passenger_gender,b.seat_number,
        b.journey_date,b.total_paid,b.status,b.booking_date,b.coupon_used,b.payment_method,
        b.discount,b.refund_amount,bu.bus_type
        FROM bookings b JOIN buses bu ON b.bus_id=bu.id WHERE b.pnr=?""",(pnr,))
    row=c.fetchone(); conn.close(); return row

def cancel_booking(pnr,username,is_admin=False):
    conn=get_conn(); c=conn.cursor()
    if is_admin: c.execute("SELECT total_paid,status FROM bookings WHERE pnr=?",(pnr,))
    else: c.execute("SELECT total_paid,status FROM bookings WHERE pnr=? AND username=?",(pnr,username))
    row=c.fetchone()
    if not row: conn.close(); return False,"Booking not found."
    if row[1]=="Cancelled": conn.close(); return False,"Already cancelled."
    refund=round(row[0]*0.85,2)
    c.execute("UPDATE bookings SET status='Cancelled',refund_amount=? WHERE pnr=?",(refund,pnr))
    conn.commit(); conn.close(); return True,refund

def get_all_users():
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT id,full_name,username,role,mobile,email,created_at FROM users ORDER BY created_at DESC")
    rows=c.fetchall(); conn.close(); return rows

def get_all_buses():
    conn=get_conn(); c=conn.cursor()
    c.execute("SELECT id,bus_name,bus_number,from_city,to_city,departure,arrival,total_seats,price,bus_type,amenities,is_active FROM buses ORDER BY id")
    rows=c.fetchall(); conn.close(); return rows

def add_bus(bname,bnum,fc,tc,dep,arr,seats,price,btype,amenities):
    conn=get_conn(); c=conn.cursor()
    c.execute("INSERT INTO buses(bus_name,bus_number,from_city,to_city,departure,arrival,total_seats,price,bus_type,amenities) VALUES(?,?,?,?,?,?,?,?,?,?)",
              (bname,bnum,fc,tc,dep,arr,seats,price,btype,amenities))
    conn.commit(); conn.close()

def toggle_bus(bid,active):
    conn=get_conn(); c=conn.cursor()
    c.execute("UPDATE buses SET is_active=? WHERE id=?",(1 if active else 0,bid))
    conn.commit(); conn.close()

def delete_user(uid):
    conn=get_conn(); c=conn.cursor()
    c.execute("DELETE FROM users WHERE id=? AND role!='Admin'",(uid,))
    conn.commit(); conn.close()

# ─── PDF ─────────────────────────────────────────────────────────────────────
def generate_pdf(info:dict)->bytes:
    if not REPORTLAB_AVAILABLE: return b""
    buf=io.BytesIO()
    doc=SimpleDocTemplate(buf,pagesize=A4,leftMargin=20*mm,rightMargin=20*mm,topMargin=15*mm,bottomMargin=15*mm)
    orange=colors.HexColor("#f97316"); dark=colors.HexColor("#0b0e1a")
    card=colors.HexColor("#1a1f35"); muted=colors.HexColor("#7c8ab0"); white=colors.white
    ts=ParagraphStyle; styles=getSampleStyleSheet()
    T=lambda n,**kw: ParagraphStyle(n,**kw)
    title_s=T("t",fontName="Helvetica-Bold",fontSize=22,textColor=orange,alignment=TA_CENTER,spaceAfter=4)
    sub_s=T("s",fontName="Helvetica",fontSize=10,textColor=muted,alignment=TA_CENTER,spaceAfter=2)
    lbl_s=T("l",fontName="Helvetica-Bold",fontSize=9,textColor=muted)
    val_s=T("v",fontName="Helvetica",fontSize=10,textColor=white)
    pnr_s=T("p",fontName="Helvetica-Bold",fontSize=18,textColor=orange,alignment=TA_CENTER)
    elems=[]
    elems.append(Paragraph("🚌 BusGo",title_s))
    elems.append(Paragraph("Smart Bus Booking — E-Ticket",sub_s))
    elems.append(Spacer(1,6*mm))
    elems.append(HRFlowable(width="100%",thickness=1,color=orange))
    elems.append(Spacer(1,4*mm))
    elems.append(Paragraph(f"PNR: {info['pnr']}",pnr_s))
    elems.append(Spacer(1,4*mm))
    tbl_style=TableStyle([("BACKGROUND",(0,0),(-1,-1),card),("ROWBACKGROUNDS",(0,0),(-1,-1),[card,colors.HexColor("#1f2540")]),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#252d4a")),("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),8)])
    data=[[Paragraph("Bus",lbl_s),Paragraph(info['bus_name'],val_s),Paragraph("Bus No.",lbl_s),Paragraph(info['bus_number'],val_s)],
          [Paragraph("From",lbl_s),Paragraph(info['from_city'],val_s),Paragraph("To",lbl_s),Paragraph(info['to_city'],val_s)],
          [Paragraph("Departure",lbl_s),Paragraph(info['departure'],val_s),Paragraph("Arrival",lbl_s),Paragraph(info['arrival'],val_s)],
          [Paragraph("Journey Date",lbl_s),Paragraph(info['journey_date'],val_s),Paragraph("Seat",lbl_s),Paragraph(info['seat_number'],val_s)],
          [Paragraph("Bus Type",lbl_s),Paragraph(info['bus_type'],val_s),Paragraph("Status",lbl_s),Paragraph(info['status'],val_s)]]
    tbl=Table(data,colWidths=[35*mm,65*mm,35*mm,35*mm]); tbl.setStyle(tbl_style); elems.append(tbl)
    elems.append(Spacer(1,3*mm))
    p_data=[[Paragraph("Passenger",lbl_s),Paragraph(info['passenger_name'],val_s),Paragraph("Age/Gender",lbl_s),Paragraph(f"{info.get('passenger_age','')} / {info.get('passenger_gender','')}",val_s)],
            [Paragraph("Booked By",lbl_s),Paragraph(info['username'],val_s),Paragraph("Payment",lbl_s),Paragraph(info.get('payment_method',''),val_s)]]
    p_tbl=Table(p_data,colWidths=[35*mm,65*mm,35*mm,35*mm]); p_tbl.setStyle(tbl_style); elems.append(p_tbl)
    elems.append(Spacer(1,3*mm))
    fare_data=[[Paragraph("Base Fare",lbl_s),Paragraph(f"Rs. {info['fare']:.2f}",val_s)],
               [Paragraph("Discount",lbl_s),Paragraph(f"- Rs. {info.get('discount',0):.2f} {info.get('coupon_used','') or ''}",val_s)],
               [Paragraph("Total Paid",lbl_s),Paragraph(f"Rs. {info['total_paid']:.2f}",val_s)]]
    f_tbl=Table(fare_data,colWidths=[60*mm,110*mm])
    f_tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),card),("BACKGROUND",(0,2),(-1,2),colors.HexColor("#1a2a1a")),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#252d4a")),("TOPPADDING",(0,0),(-1,-1),7),
        ("BOTTOMPADDING",(0,0),(-1,-1),7),("LEFTPADDING",(0,0),(-1,-1),8)]))
    elems.append(f_tbl); elems.append(Spacer(1,5*mm))
    elems.append(HRFlowable(width="100%",thickness=1,color=orange)); elems.append(Spacer(1,3*mm))
    elems.append(Paragraph("Thank you for choosing BusGo! Have a safe journey.",sub_s))
    elems.append(Paragraph(f"Booked: {info.get('booking_date','')}",sub_s))
    doc.build(elems); return buf.getvalue()

# ─── AUTH PAGE ────────────────────────────────────────────────────────────────
def render_auth():
    _,col2,_ = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div style='text-align:center;margin-bottom:2rem;'>
            <div style='font-size:3rem;'>🚌</div>
            <div class='auth-logo'>BusGo</div>
            <div style='color:#7c8ab0;font-size:.95rem;'>Smart Bus Booking Platform</div>
        </div>""",unsafe_allow_html=True)
        tab_l,tab_r=st.tabs(["🔐  Login","✍️  Register"])
        with tab_l:
            st.markdown("<br>",unsafe_allow_html=True)
            uname=st.text_input("Username",key="lu",placeholder="Enter username")
            passwd=st.text_input("Password",type="password",key="lp",placeholder="Enter password")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Login  →",use_container_width=True,key="btn_login"):
                if not uname or not passwd: st.error("Please fill all fields.")
                else:
                    res=authenticate(uname,passwd)
                    if res:
                        st.session_state.logged_in=True; st.session_state.username=res[0]
                        st.session_state.role=res[1]; st.session_state.page="book"; st.rerun()
                    else: st.error("Invalid username or password.")
            st.markdown("""<div class='demo-creds'>🔑 <b>Demo Credentials</b><br>
                Admin &nbsp;→ <code>admin</code> / <code>admin123</code><br>
                Register to create a User account</div>""",unsafe_allow_html=True)
        with tab_r:
            st.markdown("<br>",unsafe_allow_html=True)
            r_full=st.text_input("Full Name",key="rf",placeholder="Your full name (optional)")
            r_user=st.text_input("Username *",key="ru",placeholder="Choose a username")
            r_email=st.text_input("Email",key="re",placeholder="your@email.com (optional)")
            r_mob=st.text_input("Mobile",key="rm",placeholder="10-digit (optional)")
            r_pass=st.text_input("Password *",type="password",key="rp",placeholder="Min 6 characters")
            r_conf=st.text_input("Confirm Password *",type="password",key="rc",placeholder="Repeat password")
            st.markdown("<br>",unsafe_allow_html=True)
            if st.button("Create Account  →",use_container_width=True,key="btn_reg"):
                errors=[]
                if not r_user.strip(): errors.append("Username is required.")
                elif username_exists(r_user.strip()): errors.append("Username already taken.")
                if not r_pass: errors.append("Password is required.")
                elif len(r_pass)<6: errors.append("Password must be ≥ 6 characters.")
                if r_pass!=r_conf: errors.append("Passwords do not match.")
                if r_mob and not re.fullmatch(r"\d{10}",r_mob.strip()): errors.append("Mobile must be 10 digits.")
                if r_email and not re.fullmatch(r"[^@]+@[^@]+\.[^@]+",r_email.strip()): errors.append("Invalid email format.")
                if errors:
                    for e in errors: st.error(e)
                else:
                    ok,msg=register_user(r_full.strip(),r_user.strip(),r_pass,r_mob.strip(),r_email.strip())
                    if ok: st.success(f"✅ {msg}"); st.info("Switch to Login tab to sign in.")
                    else: st.error(msg)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""<div style='padding:1rem 0 .5rem;text-align:center;'>
            <div style='font-size:2rem;'>🚌</div>
            <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;
                background:linear-gradient(135deg,#f97316,#fbbf24);
                -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>BusGo</div>
        </div>""",unsafe_allow_html=True)
        st.divider()
        role=st.session_state.get("role","User"); user=st.session_state.get("username","")
        bc="badge-orange" if role=="Admin" else "badge-blue"
        st.markdown(f"""<div style='padding:.5rem;text-align:center;'>
            <div style='font-weight:600;font-size:.95rem;'>👤 {user}</div>
            <span class='badge {bc}'>{role}</span></div>""",unsafe_allow_html=True)
        st.divider()
        pages={"book":"🚌 Book Ticket",
               "mybookings":"📋 Booking History" if role=="Admin" else "📋 My Bookings",
               "pnr":"🔍 PNR Search","cancel":"❌ Cancel Booking"}
        if role=="Admin": pages["admin"]="⚙️ Admin Panel"
        for key,label in pages.items():
            active=st.session_state.get("page")==key
            if st.button(label,use_container_width=True,key=f"nav_{key}",
                         type="primary" if active else "secondary"):
                st.session_state.page=key; st.rerun()
        st.divider()
        if st.button("🚪 Logout",use_container_width=True,key="btn_logout"):
            logout(); st.rerun()

# ─── PAGE: BOOK ───────────────────────────────────────────────────────────────
def page_book():
    st.markdown("""<div class='hero-banner'>
        <div class='hero-title'>🚌 Book Your Ticket</div>
        <div class='hero-sub'>Search buses · Choose seats · Travel smart</div>
    </div>""",unsafe_allow_html=True)
    cities=get_cities()
    if not cities: st.warning("No buses available."); return
    c1,c2,c3=st.columns([2,2,1.5])
    with c1: from_c=st.selectbox("From",cities,key="sf")
    with c2: to_c=st.selectbox("To",[x for x in cities if x!=from_c],key="st")
    with c3: j_date=st.date_input("Journey Date",min_value=date.today(),key="sd")
    if st.button("🔍 Search Buses",use_container_width=True,key="btn_search"):
        st.session_state.search_results=search_buses(from_c,to_c)
        st.session_state.sdate=str(j_date)
        st.session_state.selected_bus=None; st.session_state.selected_seats=[]
    results=st.session_state.get("search_results")
    if results is None: return
    if not results: st.info(f"No buses from **{from_c}** to **{to_c}**."); return
    st.markdown(f"### Found {len(results)} bus(es)")
    for bus in results:
        bid,bname,bnum,fc,tc,dep,arr,total_s,price,btype,amenities=bus
        booked=get_booked_seats(bid,st.session_state.get("sdate",str(j_date)))
        avail=total_s-len(booked)
        with st.container():
            st.markdown(f"""<div class='bus-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div><div style='font-family:Syne,sans-serif;font-size:1.15rem;font-weight:700;'>{bname}</div>
                    <div style='color:#7c8ab0;font-size:.85rem;'>{bnum} &nbsp;·&nbsp; <span class='badge badge-blue'>{btype}</span></div></div>
                    <div style='text-align:right;'><div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#f97316;'>₹{price:.0f}</div>
                    <div style='color:#7c8ab0;font-size:.8rem;'>per seat</div></div>
                </div>
                <div style='display:flex;gap:2rem;margin-top:.8rem;'>
                    <div><div style='font-size:1.1rem;font-weight:700;'>{dep}</div><div style='color:#7c8ab0;font-size:.8rem;'>{fc}</div></div>
                    <div style='color:#7c8ab0;font-size:1.2rem;padding-top:4px;'>→</div>
                    <div><div style='font-size:1.1rem;font-weight:700;'>{arr}</div><div style='color:#7c8ab0;font-size:.8rem;'>{tc}</div></div>
                </div>
                <div style='margin-top:.6rem;font-size:.82rem;color:#7c8ab0;'>
                    🪑 {avail} seats available &nbsp;·&nbsp; {amenities.replace(","," · ")}
                </div></div>""",unsafe_allow_html=True)
            if st.button(f"Select →",key=f"sb_{bid}"):
                st.session_state.selected_bus=bid; st.session_state.selected_seats=[]; st.rerun()
    if st.session_state.get("selected_bus"):
        st.divider(); _booking_flow(st.session_state.get("sdate",str(j_date)))

def _booking_flow(jdate:str):
    bus_id=st.session_state.selected_bus
    bus=get_bus(bus_id)
    if not bus: return
    bid,bname,bnum,fc,tc,dep,arr,total_s,price,btype,amenities,_=bus
    booked=get_booked_seats(bus_id,jdate)
    st.markdown(f"### 🪑 Select Seat — {bname}")
    all_seats=[f"{r}{c}" for r in "ABCDE" for c in range(1,9)][:total_s]
    selected=st.session_state.get("selected_seats",[])
    seat_html="<div style='display:flex;flex-wrap:wrap;gap:8px;margin-bottom:1rem;'>"
    for s in all_seats:
        if s in booked:
            seat_html+=f"<div style='width:42px;height:42px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;background:rgba(239,68,68,.1);border:2px solid #2a1a1a;color:#444;font-family:Syne,sans-serif;'>{s}</div>"
        elif s in selected:
            seat_html+=f"<div style='width:42px;height:42px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;background:#f97316;border:2px solid #f97316;color:#fff;font-family:Syne,sans-serif;'>{s}</div>"
        else:
            seat_html+=f"<div style='width:42px;height:42px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700;background:rgba(34,197,94,.15);border:2px solid #22c55e;color:#22c55e;font-family:Syne,sans-serif;'>{s}</div>"
    seat_html+="</div>"
    st.markdown(seat_html,unsafe_allow_html=True)
    st.markdown("""<div style='display:flex;gap:1rem;margin-bottom:1rem;font-size:.8rem;'>
        <span class='badge badge-green'>■ Available</span>
        <span class='badge badge-orange'>■ Selected</span>
        <span class='badge badge-red'>■ Booked</span></div>""",unsafe_allow_html=True)
    avail_seats=[s for s in all_seats if s not in booked]
    seat_choice=st.multiselect("Choose Seat(s)",avail_seats,default=selected,key="seat_ms")
    st.session_state.selected_seats=seat_choice
    if not seat_choice: return
    st.markdown("### 👤 Passenger Details")
    with st.form("bform"):
        c1,c2=st.columns(2)
        with c1:
            pname=st.text_input("Passenger Name *",placeholder="Full name on ticket")
            page=st.number_input("Age *",min_value=1,max_value=120,value=25)
        with c2:
            pgender=st.selectbox("Gender *",["Male","Female","Other"])
            payment=st.selectbox("Payment Method",["UPI","Credit Card","Debit Card","Net Banking","Cash"])
        coupon_code=st.text_input("Coupon Code (optional)",placeholder="SAVE10 · FLAT50 · FIRST20 · BLAZE25")
        qty=len(seat_choice); subtotal=price*qty
        discount=0.0; coupon_v=""
        cu=coupon_code.strip().upper()
        if cu in COUPONS:
            ctype,cval=COUPONS[cu]
            if ctype=="percent": discount=round(subtotal*cval/100,2)
            else: discount=min(float(cval),subtotal)
            coupon_v=cu
        total_paid=max(0,subtotal-discount)
        st.markdown(f"""<div class='bus-card' style='margin-top:.5rem;'>
            <div style='display:flex;justify-content:space-between;'><span>Seats</span><span>{', '.join(seat_choice)}</span></div>
            <div style='display:flex;justify-content:space-between;'><span>Base Fare</span><span>₹{subtotal:.2f}</span></div>
            <div style='display:flex;justify-content:space-between;color:#22c55e;'><span>Discount</span><span>- ₹{discount:.2f}</span></div>
            <hr style='border-color:#252d4a;margin:.4rem 0;'>
            <div style='display:flex;justify-content:space-between;font-weight:700;font-size:1.1rem;'>
                <span>Total</span><span style='color:#f97316;'>₹{total_paid:.2f}</span></div>
        </div>""",unsafe_allow_html=True)
        if st.form_submit_button("✅ Confirm Booking",use_container_width=True):
            if not pname.strip(): st.error("Passenger name is required.")
            else:
                pnrs=[]
                for seat in seat_choice:
                    pnr=create_booking(st.session_state.username,bus_id,pname.strip(),page,pgender,
                                       seat,jdate,price,discount/qty if qty else 0,
                                       total_paid/qty if qty else 0,coupon_v,payment)
                    pnrs.append(pnr)
                st.success(f"🎉 Booking Confirmed! PNR(s): **{', '.join(pnrs)}**")
                st.balloons()
                st.session_state.selected_bus=None; st.session_state.selected_seats=[]
                st.session_state.last_pnrs=pnrs

# ─── PAGE: MY BOOKINGS ────────────────────────────────────────────────────────
def page_my_bookings():
    role=st.session_state.get("role","User"); is_admin=role=="Admin"
    st.markdown(f"""<div class='hero-banner'>
        <div class='hero-title'>{'📋 All Booking History' if is_admin else '📋 My Bookings'}</div>
        <div class='hero-sub'>{'Manage all passenger bookings' if is_admin else 'Your travel history'}</div>
    </div>""",unsafe_allow_html=True)
    if is_admin:
        rows=get_all_bookings()
        if not rows: st.info("No bookings yet."); return
        import csv; buf=io.StringIO(); w=csv.writer(buf)
        w.writerow(["PNR","User","Bus","From","To","Passenger","Seat","Date","Paid","Status","Booked On","Payment","Refund"])
        for r in rows: w.writerow(r)
        st.download_button("⬇️ Export CSV",buf.getvalue().encode(),"bookings.csv","text/csv")
        st.markdown("---")
        c1,c2,c3,c4=st.columns(4)
        conf=sum(1 for r in rows if r[9]=="Confirmed"); canc=sum(1 for r in rows if r[9]=="Cancelled")
        rev=sum(r[8] for r in rows if r[9]=="Confirmed")
        c1.metric("Total",len(rows)); c2.metric("Confirmed",conf); c3.metric("Cancelled",canc); c4.metric("Revenue",f"₹{rev:,.0f}")
        st.markdown("---")
        for r in rows:
            pnr,user,bname,fc,tc,pname,seat,jdate,paid,status,bdate,pay,refund=r
            badge="badge-green" if status=="Confirmed" else "badge-red"
            with st.expander(f"🎫 {pnr}  ·  {fc} → {tc}  ·  {jdate}  ·  {user}"):
                st.markdown(f"""<div style='display:flex;gap:2rem;flex-wrap:wrap;'>
                    <div><b>Bus</b><br>{bname}</div><div><b>Passenger</b><br>{pname}</div>
                    <div><b>Seat</b><br>{seat}</div><div><b>Paid</b><br>₹{paid:.2f}</div>
                    <div><b>Payment</b><br>{pay}</div>
                    <div><b>Status</b><br><span class='badge {badge}'>{status}</span></div>
                    {f"<div><b>Refund</b><br>₹{refund:.2f}</div>" if refund else ""}
                </div>""",unsafe_allow_html=True)
                if status=="Confirmed":
                    if st.button("Cancel (Admin)",key=f"ac_{pnr}"):
                        ok,val=cancel_booking(pnr,"",is_admin=True)
                        if ok: st.success(f"Cancelled. Refund ₹{val}"); st.rerun()
    else:
        rows=get_user_bookings(st.session_state.username)
        if not rows: st.info("No bookings yet. Book your first ticket!"); return
        for r in rows:
            pnr,bname,fc,tc,pname,seat,jdate,paid,status,bdate,coupon,pay,refund,bid,dep,arr,btype,bnum,disc,fare,page2,pgender=r
            badge="badge-green" if status=="Confirmed" else "badge-red"
            with st.expander(f"🎫 {pnr}  ·  {fc} → {tc}  ·  {jdate}"):
                st.markdown(f"""<div class='bus-card'>
                    <div style='display:flex;justify-content:space-between;'>
                        <div><div style='font-family:Syne,sans-serif;font-weight:700;font-size:1.05rem;'>{bname}</div>
                        <div style='color:#7c8ab0;font-size:.85rem;'>{dep} → {arr} &nbsp;·&nbsp; {btype}</div></div>
                        <span class='badge {badge}'>{status}</span>
                    </div>
                    <div style='display:flex;gap:2rem;flex-wrap:wrap;margin-top:.8rem;'>
                        <div><b>Passenger</b><br>{pname}</div><div><b>Seat</b><br>{seat}</div>
                        <div><b>Date</b><br>{jdate}</div><div><b>Paid</b><br>₹{paid:.2f}</div>
                        <div><b>Payment</b><br>{pay}</div>
                        {f"<div><b>Coupon</b><br>{coupon}</div>" if coupon else ""}
                        {f"<div><b>Refund</b><br>₹{refund:.2f}</div>" if refund else ""}
                    </div></div>""",unsafe_allow_html=True)
                if REPORTLAB_AVAILABLE and status=="Confirmed":
                    info={"pnr":pnr,"bus_name":bname,"bus_number":bnum,"from_city":fc,"to_city":tc,
                          "departure":dep,"arrival":arr,"passenger_name":pname,"passenger_age":page2,
                          "passenger_gender":pgender,"seat_number":seat,"journey_date":jdate,
                          "total_paid":paid,"fare":fare,"discount":disc,"coupon_used":coupon,
                          "payment_method":pay,"status":status,"booking_date":bdate,
                          "username":st.session_state.username,"bus_type":btype}
                    pdf=generate_pdf(info)
                    if pdf: st.download_button("⬇️ Download Ticket PDF",pdf,f"ticket_{pnr}.pdf","application/pdf",key=f"pdf_{pnr}")

# ─── PAGE: PNR ────────────────────────────────────────────────────────────────
def page_pnr():
    st.markdown("""<div class='hero-banner'>
        <div class='hero-title'>🔍 PNR Search</div>
        <div class='hero-sub'>Enter your PNR to check booking status</div>
    </div>""",unsafe_allow_html=True)
    pnr_in=st.text_input("PNR Number",placeholder="e.g. BG12345678",key="pnr_in")
    if st.button("Search",use_container_width=True,key="btn_pnr"):
        if not pnr_in.strip(): st.error("Enter a PNR number."); return
        row=search_pnr(pnr_in.strip().upper())
        if not row: st.error("No booking found for this PNR."); return
        pnr,user,bname,bnum,fc,tc,dep,arr,pname,page2,pgender,seat,jdate,paid,status,bdate,coupon,pay,disc,refund,btype=row
        role=st.session_state.get("role","User")
        if role!="Admin" and user!=st.session_state.username:
            st.error("You can only view your own bookings."); return
        badge="badge-green" if status=="Confirmed" else "badge-red"
        st.markdown(f"""<div class='bus-card' style='margin-top:1rem;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:800;'>{pnr}</div>
                <span class='badge {badge}'>{status}</span>
            </div><hr style='border-color:#252d4a;margin:.8rem 0;'>
            <div style='display:grid;grid-template-columns:1fr 1fr;gap:.8rem;'>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>BUS</div><div>{bname} ({bnum})</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>TYPE</div><div>{btype}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>FROM → TO</div><div>{fc} → {tc}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>DEPARTURE / ARRIVAL</div><div>{dep} / {arr}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>JOURNEY DATE</div><div>{jdate}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>SEAT</div><div>{seat}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>PASSENGER</div><div>{pname}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>AGE / GENDER</div><div>{page2} / {pgender}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>BASE FARE</div><div>₹{paid+disc:.2f}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>DISCOUNT</div><div style='color:#22c55e;'>- ₹{disc:.2f} {coupon or ''}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>TOTAL PAID</div><div style='color:#f97316;font-weight:700;'>₹{paid:.2f}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>PAYMENT</div><div>{pay}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>BOOKED BY</div><div>{user}</div></div>
                <div><div style='color:#7c8ab0;font-size:.8rem;'>BOOKED ON</div><div>{bdate}</div></div>
                {f"<div><div style='color:#7c8ab0;font-size:.8rem;'>REFUND</div><div style='color:#22c55e;'>₹{refund:.2f}</div></div>" if refund else ""}
            </div></div>""",unsafe_allow_html=True)
        if REPORTLAB_AVAILABLE and status=="Confirmed":
            info={"pnr":pnr,"bus_name":bname,"bus_number":bnum,"from_city":fc,"to_city":tc,
                  "departure":dep,"arrival":arr,"passenger_name":pname,"passenger_age":page2,
                  "passenger_gender":pgender,"seat_number":seat,"journey_date":jdate,
                  "total_paid":paid,"fare":paid+disc,"discount":disc,"coupon_used":coupon,
                  "payment_method":pay,"status":status,"booking_date":bdate,"username":user,"bus_type":btype}
            pdf=generate_pdf(info)
            if pdf: st.download_button("⬇️ Download Ticket PDF",pdf,f"ticket_{pnr}.pdf","application/pdf",key="pnr_dl")

# ─── PAGE: CANCEL ─────────────────────────────────────────────────────────────
def page_cancel():
    st.markdown("""<div class='hero-banner'>
        <div class='hero-title'>❌ Cancel Booking</div>
        <div class='hero-sub'>85% refund processed on cancellation</div>
    </div>""",unsafe_allow_html=True)
    role=st.session_state.get("role","User")
    pnr_c=st.text_input("PNR to Cancel",placeholder="BG12345678",key="cpnr")
    st.info("ℹ️ Cancellation Policy: 85% of total paid amount will be refunded.")
    if st.button("Proceed to Cancel",use_container_width=True,key="btn_cancel"):
        if not pnr_c.strip(): st.error("Enter a PNR."); return
        row=search_pnr(pnr_c.strip().upper())
        if not row: st.error("PNR not found."); return
        pnr,user=row[0],row[1]
        if role!="Admin" and user!=st.session_state.username:
            st.error("You can only cancel your own bookings."); return
        ok,val=cancel_booking(pnr,st.session_state.username,is_admin=(role=="Admin"))
        if ok: st.success(f"✅ Booking **{pnr}** cancelled. Refund of **₹{val:.2f}** will be processed."); st.balloons()
        else: st.error(val)

# ─── PAGE: ADMIN ──────────────────────────────────────────────────────────────
def page_admin():
    if st.session_state.get("role")!="Admin": st.error("Access denied."); return
    st.markdown("""<div class='hero-banner'>
        <div class='hero-title'>⚙️ Admin Panel</div>
        <div class='hero-sub'>Manage buses, users & system</div>
    </div>""",unsafe_allow_html=True)
    t_users,t_buses,t_add,t_stats=st.tabs(["👥 Users","🚌 Buses","➕ Add Bus","📊 Stats"])

    with t_users:
        st.subheader("All Registered Users")
        users=get_all_users()
        if not users: st.info("No users."); 
        else:
            for u in users:
                uid,fname,uname,urole,mobile,email,created=u
                bc="badge-orange" if urole=="Admin" else "badge-blue"
                icon="👑" if urole=="Admin" else "👤"
                with st.expander(f"{icon} {uname}  ·  {urole}"):
                    c1,c2=st.columns([3,1])
                    with c1:
                        st.markdown(f"""<div style='font-size:.9rem;'>
                            <div><b>Full Name:</b> {fname or '—'}</div>
                            <div><b>Mobile:</b> {mobile or '—'}</div>
                            <div><b>Email:</b> {email or '—'}</div>
                            <div><b>Created:</b> {created}</div>
                        </div>""",unsafe_allow_html=True)
                    with c2:
                        if urole!="Admin":
                            if st.button("🗑️ Delete",key=f"du_{uid}"):
                                delete_user(uid); st.success("Deleted."); st.rerun()

    with t_buses:
        st.subheader("All Buses")
        for b in get_all_buses():
            bid,bname,bnum,fc,tc,dep,arr,seats,price,btype,amenities,active=b
            with st.expander(f"{'✅' if active else '🔴'} {bname}  ·  {fc} → {tc}"):
                c1,c2=st.columns([3,1])
                with c1:
                    st.markdown(f"""<div style='font-size:.9rem;display:grid;grid-template-columns:1fr 1fr;gap:.5rem;'>
                        <div><b>Bus No:</b> {bnum}</div><div><b>Type:</b> {btype}</div>
                        <div><b>Departure:</b> {dep}</div><div><b>Arrival:</b> {arr}</div>
                        <div><b>Seats:</b> {seats}</div><div><b>Price:</b> ₹{price:.0f}</div>
                        <div><b>Amenities:</b> {amenities}</div>
                    </div>""",unsafe_allow_html=True)
                with c2:
                    if st.button("Deactivate" if active else "Activate",key=f"tb_{bid}"):
                        toggle_bus(bid,not active); st.rerun()

    with t_add:
        st.subheader("Add New Bus")
        with st.form("abf"):
            c1,c2=st.columns(2)
            with c1:
                ab_name=st.text_input("Bus Name *"); ab_num=st.text_input("Bus Number *")
                ab_from=st.text_input("From City *"); ab_to=st.text_input("To City *")
                ab_dep=st.text_input("Departure *",placeholder="HH:MM")
            with c2:
                ab_arr=st.text_input("Arrival *",placeholder="HH:MM")
                ab_seats=st.number_input("Seats",10,60,40)
                ab_price=st.number_input("Price ₹",50,10000,400)
                ab_type=st.selectbox("Bus Type",["AC Sleeper","AC Semi-Sleeper","Non-AC Sleeper","Non-AC Seater","Volvo AC"])
                ab_am=st.text_input("Amenities",placeholder="WiFi,Water,Blanket")
            if st.form_submit_button("Add Bus",use_container_width=True):
                if not all([ab_name,ab_num,ab_from,ab_to,ab_dep,ab_arr]):
                    st.error("Fill all required fields.")
                else:
                    add_bus(ab_name,ab_num,ab_from,ab_to,ab_dep,ab_arr,int(ab_seats),float(ab_price),ab_type,ab_am)
                    st.success(f"Bus '{ab_name}' added!"); st.rerun()

    with t_stats:
        st.subheader("System Overview")
        conn=get_conn(); c=conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role='User'"); tu=c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM buses WHERE is_active=1"); ab=c.fetchone()[0]
        c.execute("SELECT COUNT(*),SUM(total_paid) FROM bookings WHERE status='Confirmed'"); br=c.fetchone()
        c.execute("SELECT COUNT(*) FROM bookings WHERE status='Cancelled'"); canc=c.fetchone()[0]
        c.execute("""SELECT bu.from_city||' → '||bu.to_city,COUNT(*) as cnt FROM bookings b
            JOIN buses bu ON b.bus_id=bu.id WHERE b.status='Confirmed'
            GROUP BY bu.id ORDER BY cnt DESC LIMIT 5"""); top=c.fetchall()
        conn.close()
        col1,col2,col3,col4=st.columns(4)
        col1.metric("Registered Users",tu); col2.metric("Active Buses",ab)
        col3.metric("Confirmed Bookings",br[0] or 0); col4.metric("Revenue",f"₹{br[1] or 0:,.0f}")
        if top:
            st.markdown("---"); st.markdown("**Top Routes**")
            for route,cnt in top: st.markdown(f"- **{route}** → {cnt} bookings")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    init_db()
    if "logged_in" not in st.session_state: st.session_state.logged_in=False
    if "page" not in st.session_state: st.session_state.page="book"
    if not st.session_state.logged_in: render_auth(); return
    render_sidebar()
    p=st.session_state.get("page","book")
    if p=="book": page_book()
    elif p=="mybookings": page_my_bookings()
    elif p=="pnr": page_pnr()
    elif p=="cancel": page_cancel()
    elif p=="admin": page_admin()
    else: page_book()

main()
