
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import plotly.graph_objects as go
import re
from io import StringIO

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Affordability Calculator",
    page_icon="🎓",
    layout="centered"
)

# ── Styling ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header  { visibility: hidden; }
.stApp { background: #F7F5F0; }
.hero {
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 60%, #40916C 100%);
    padding: 44px 40px; border-radius: 24px; margin-bottom: 32px;
    position: relative; overflow: hidden;
}
.hero::after {
    content:''; position:absolute; width:300px; height:300px;
    border-radius:50%; background:rgba(255,255,255,0.04);
    top:-80px; right:-80px;
}
.hero h1 {
    font-family:'DM Serif Display',serif;
    color:white; font-size:2.4rem; margin:0 0 10px; line-height:1.2;
}
.hero p { color:rgba(255,255,255,0.78); font-size:0.95rem; margin:0; }
.progress-bar-wrap {
    background:#E8E4DC; border-radius:100px;
    height:6px; margin:0 0 6px; overflow:hidden;
}
.progress-bar-fill {
    height:6px; border-radius:100px;
    background:linear-gradient(90deg,#1B4332,#40916C);
    transition:width 0.4s ease;
}
.progress-label {
    font-size:0.75rem; color:#9C9589;
    text-transform:uppercase; letter-spacing:0.07em; margin-bottom:24px;
}
.card {
    background:white; border-radius:18px; padding:28px 32px;
    border:1px solid #E8E4DC; margin-bottom:18px;
    box-shadow:0 2px 16px rgba(0,0,0,0.04);
}
.step-label {
    font-size:0.7rem; text-transform:uppercase;
    letter-spacing:0.1em; color:#9C9589;
    font-weight:600; margin-bottom:14px;
}
.step-title {
    font-family:'DM Serif Display',serif;
    font-size:1.35rem; color:#1A1A1A; margin-bottom:18px;
}
.currency-detected {
    background:#F0FFF4; border:1px solid #9AE6B4;
    border-radius:12px; padding:16px 20px; margin:12px 0;
    display:flex; align-items:center; gap:12px;
}
.currency-big { font-family:'DM Serif Display',serif; font-size:2rem; color:#1B4332; }
.schol-box {
    background:#F0FFF4; border:1px solid #9AE6B4;
    border-radius:12px; padding:16px 20px; margin:12px 0;
}
.schol-amount {
    font-family:'DM Serif Display',serif;
    font-size:2rem; color:#1B4332; line-height:1;
}
.schol-source { font-size:0.73rem; color:#718096; margin-top:4px; }
.badge {
    display:inline-block; border-radius:100px;
    padding:3px 12px; font-size:0.73rem; font-weight:600; margin:3px 4px 3px 0;
}
.badge-green { background:#F0FFF4; color:#276749; border:1px solid #9AE6B4; }
.badge-blue  { background:#EBF8FF; color:#2B6CB0; border:1px solid #90CDF4; }
.info-note {
    background:#EBF8FF; border:1px solid #90CDF4;
    border-radius:10px; padding:12px 16px;
    font-size:0.82rem; color:#2C5282; margin:10px 0;
}
.verdict-box {
    border-radius:16px; padding:24px 28px; font-size:1.05rem;
    font-weight:600; margin:20px 0; text-align:center;
    box-shadow:0 4px 20px rgba(0,0,0,0.06);
}
.verdict-amount {
    font-family:'DM Serif Display',serif;
    font-size:2.4rem; display:block; margin-top:6px;
}
.row-item {
    display:flex; justify-content:space-between; align-items:center;
    padding:11px 0; border-bottom:1px solid #F0EDE7; font-size:0.88rem;
}
.row-item:last-child { border-bottom:none; }
.savings-wrap {
    background:white; border-radius:18px; padding:24px 28px;
    border:1px solid #E8E4DC; margin-top:18px;
}
.savings-bar-bg {
    background:#E8E4DC; border-radius:100px;
    height:10px; margin:10px 0 6px; overflow:hidden;
}
.savings-bar-fill { height:10px; border-radius:100px; transition:width 0.5s ease; }
.grocery-note {
    background:#FFFBEB; border:1px solid #F6E05E;
    border-radius:10px; padding:11px 15px;
    font-size:0.79rem; color:#744210; margin-top:10px;
}
</style>
""", unsafe_allow_html=True)

# ── Complete world flags (107 countries) ──────────────────────────────────────
CITY_FLAGS = {
    "Afghanistan":"🇦🇫","Albania":"🇦🇱","Algeria":"🇩🇿","Argentina":"🇦🇷",
    "Armenia":"🇦🇲","Australia":"🇦🇺","Austria":"🇦🇹","Azerbaijan":"🇦🇿",
    "Bahrain":"🇧🇭","Bangladesh":"🇧🇩","Belarus":"🇧🇾","Belgium":"🇧🇪",
    "Bosnia And Herzegovina":"🇧🇦","Brazil":"🇧🇷","Bulgaria":"🇧🇬",
    "Cambodia":"🇰🇭","Canada":"🇨🇦","Chile":"🇨🇱","China":"🇨🇳",
    "Colombia":"🇨🇴","Costa Rica":"🇨🇷","Croatia":"🇭🇷","Cyprus":"🇨🇾",
    "Czech Republic":"🇨🇿","Denmark":"🇩🇰","Ecuador":"🇪🇨","Egypt":"🇪🇬",
    "Estonia":"🇪🇪","Finland":"🇫🇮","France":"🇫🇷","Georgia":"🇬🇪",
    "Germany":"🇩🇪","Ghana":"🇬🇭","Greece":"🇬🇷","Guatemala":"🇬🇹",
    "Hong Kong (China)":"🇭🇰","Hungary":"🇭🇺","Iceland":"🇮🇸","India":"🇮🇳",
    "Indonesia":"🇮🇩","Iran":"🇮🇷","Iraq":"🇮🇶","Ireland":"🇮🇪",
    "Israel":"🇮🇱","Italy":"🇮🇹","Japan":"🇯🇵","Jordan":"🇯🇴",
    "Kazakhstan":"🇰🇿","Kenya":"🇰🇪","Kosovo (Disputed Territory)":"🇽🇰",
    "Kuwait":"🇰🇼","Kyrgyzstan":"🇰🇬","Latvia":"🇱🇻","Lebanon":"🇱🇧",
    "Libya":"🇱🇾","Lithuania":"🇱🇹","Luxembourg":"🇱🇺","Malaysia":"🇲🇾",
    "Malta":"🇲🇹","Mexico":"🇲🇽","Moldova":"🇲🇩","Mongolia":"🇲🇳",
    "Montenegro":"🇲🇪","Morocco":"🇲🇦","Nepal":"🇳🇵","Netherlands":"🇳🇱",
    "New Zealand":"🇳🇿","Nigeria":"🇳🇬","North Macedonia":"🇲🇰","Norway":"🇳🇴",
    "Oman":"🇴🇲","Pakistan":"🇵🇰","Panama":"🇵🇦","Paraguay":"🇵🇾",
    "Peru":"🇵🇪","Philippines":"🇵🇭","Poland":"🇵🇱","Portugal":"🇵🇹",
    "Qatar":"🇶🇦","Romania":"🇷🇴","Russia":"🇷🇺","Saudi Arabia":"🇸🇦",
    "Serbia":"🇷🇸","Singapore":"🇸🇬","Slovakia":"🇸🇰","Slovenia":"🇸🇮",
    "South Africa":"🇿🇦","South Korea":"🇰🇷","Spain":"🇪🇸","Sri Lanka":"🇱🇰",
    "Sweden":"🇸🇪","Switzerland":"🇨🇭","Taiwan":"🇹🇼","Thailand":"🇹🇭",
    "Trinidad And Tobago":"🇹🇹","Tunisia":"🇹🇳","Turkey":"🇹🇷","Uganda":"🇺🇬",
    "Ukraine":"🇺🇦","United Arab Emirates":"🇦🇪","United Kingdom":"🇬🇧",
    "United States":"🇺🇸","Uruguay":"🇺🇾","Uzbekistan":"🇺🇿",
    "Venezuela":"🇻🇪","Vietnam":"🇻🇳","Zimbabwe":"🇿🇼","Ajara":"🇬🇪",
}

# ── Complete world currencies ──────────────────────────────────────────────────
COUNTRY_CURRENCY = {
    # Europe — Euro
    "Austria":("EUR","€"),"Belgium":("EUR","€"),"Croatia":("EUR","€"),
    "Cyprus":("EUR","€"),"Estonia":("EUR","€"),"Finland":("EUR","€"),
    "France":("EUR","€"),"Germany":("EUR","€"),"Greece":("EUR","€"),
    "Ireland":("EUR","€"),"Italy":("EUR","€"),"Latvia":("EUR","€"),
    "Lithuania":("EUR","€"),"Luxembourg":("EUR","€"),"Malta":("EUR","€"),
    "Netherlands":("EUR","€"),"Portugal":("EUR","€"),"Slovakia":("EUR","€"),
    "Slovenia":("EUR","€"),"Spain":("EUR","€"),"Montenegro":("EUR","€"),
    "Kosovo (Disputed Territory)":("EUR","€"),
    # Europe — Non-Euro
    "United Kingdom":("GBP","£"),"Switzerland":("CHF","Fr"),
    "Norway":("NOK","kr"),"Sweden":("SEK","kr"),"Denmark":("DKK","kr"),
    "Czech Republic":("CZK","Kč"),"Poland":("PLN","zł"),
    "Hungary":("HUF","Ft"),"Romania":("RON","lei"),"Bulgaria":("BGN","лв"),
    "Iceland":("ISK","kr"),"Serbia":("RSD","din"),"Albania":("ALL","L"),
    "North Macedonia":("MKD","ден"),"Bosnia And Herzegovina":("BAM","KM"),
    "Moldova":("MDL","L"),"Ukraine":("UAH","₴"),"Belarus":("BYN","Br"),
    "Russia":("RUB","₽"),"Turkey":("TRY","₺"),"Georgia":("GEL","₾"),
    "Armenia":("AMD","֏"),"Azerbaijan":("AZN","₼"),
    "Kazakhstan":("KZT","₸"),"Kyrgyzstan":("KGS","с"),
    "Uzbekistan":("UZS","so'm"),
    # Asia
    "China":("CNY","¥"),"Japan":("JPY","¥"),"South Korea":("KRW","₩"),
    "India":("INR","₹"),"Pakistan":("PKR","₨"),"Bangladesh":("BDT","৳"),
    "Singapore":("SGD","S$"),"Hong Kong (China)":("HKD","HK$"),
    "Taiwan":("TWD","NT$"),"Thailand":("THB","฿"),"Vietnam":("VND","₫"),
    "Malaysia":("MYR","RM"),"Indonesia":("IDR","Rp"),
    "Philippines":("PHP","₱"),"Cambodia":("KHR","៛"),
    "Sri Lanka":("LKR","Rs"),"Nepal":("NPR","Rs"),
    "Mongolia":("MNT","₮"),"Israel":("ILS","₪"),
    "Jordan":("JOD","JD"),"Lebanon":("LBP","L£"),
    "Iraq":("IQD","IQD"),"Iran":("IRR","﷼"),
    "Saudi Arabia":("SAR","﷼"),"UAE":("AED","د.إ"),
    "United Arab Emirates":("AED","د.إ"),"Kuwait":("KWD","KD"),
    "Qatar":("QAR","﷼"),"Bahrain":("BHD","BD"),"Oman":("OMR","OMR"),
    # Americas
    "United States":("USD","$"),"Canada":("CAD","CA$"),
    "Mexico":("MXN","MX$"),"Brazil":("BRL","R$"),
    "Argentina":("ARS","AR$"),"Colombia":("COP","COP$"),
    "Chile":("CLP","CLP$"),"Peru":("PEN","S/"),
    "Ecuador":("USD","$"),"Uruguay":("UYU","$U"),
    "Paraguay":("PYG","₲"),"Panama":("USD","$"),
    "Costa Rica":("CRC","₡"),"Guatemala":("GTQ","Q"),
    "Venezuela":("VES","Bs"),
    "Trinidad And Tobago":("TTD","TT$"),
    # Africa / Middle East
    "South Africa":("ZAR","R"),"Nigeria":("NGN","₦"),
    "Kenya":("KES","KSh"),"Ghana":("GHS","GH₵"),
    "Egypt":("EGP","E£"),"Morocco":("MAD","MAD"),
    "Tunisia":("TND","TND"),"Algeria":("DZD","DZD"),
    "Libya":("LYD","LD"),"Uganda":("UGX","USh"),
    "Zimbabwe":("ZWL","Z$"),
    # Oceania
    "Australia":("AUD","A$"),"New Zealand":("NZD","NZ$"),
    "Ajara":("GEL","₾"),
}

# ── All supported currencies for student selection ────────────────────────────
ALL_CURRENCIES = {
    "EUR — Euro (€)"                    :("EUR","€"),
    "GBP — British Pound (£)"           :("GBP","£"),
    "USD — US Dollar ($)"               :("USD","$"),
    "CHF — Swiss Franc (Fr)"            :("CHF","Fr"),
    "NOK — Norwegian Krone (kr)"        :("NOK","kr"),
    "SEK — Swedish Krona (kr)"          :("SEK","kr"),
    "DKK — Danish Krone (kr)"           :("DKK","kr"),
    "PLN — Polish Zloty (zł)"           :("PLN","zł"),
    "CZK — Czech Koruna (Kč)"           :("CZK","Kč"),
    "HUF — Hungarian Forint (Ft)"       :("HUF","Ft"),
    "RON — Romanian Leu (lei)"          :("RON","lei"),
    "CNY — Chinese Yuan (¥)"           :("CNY","¥"),
    "JPY — Japanese Yen (¥)"           :("JPY","¥"),
    "KRW — South Korean Won (₩)"       :("KRW","₩"),
    "INR — Indian Rupee (₹)"           :("INR","₹"),
    "PKR — Pakistani Rupee (₨)"        :("PKR","₨"),
    "BDT — Bangladeshi Taka (৳)"       :("BDT","৳"),
    "SGD — Singapore Dollar (S$)"       :("SGD","S$"),
    "AED — UAE Dirham (د.إ)"           :("AED","د.إ"),
    "SAR — Saudi Riyal (﷼)"           :("SAR","﷼"),
    "CAD — Canadian Dollar (CA$)"       :("CAD","CA$"),
    "AUD — Australian Dollar (A$)"      :("AUD","A$"),
    "TRY — Turkish Lira (₺)"          :("TRY","₺"),
    "BRL — Brazilian Real (R$)"         :("BRL","R$"),
    "MYR — Malaysian Ringgit (RM)"      :("MYR","RM"),
    "THB — Thai Baht (฿)"             :("THB","฿"),
    "IDR — Indonesian Rupiah (Rp)"      :("IDR","Rp"),
    "VND — Vietnamese Dong (₫)"        :("VND","₫"),
    "PHP — Philippine Peso (₱)"        :("PHP","₱"),
    "ZAR — South African Rand (R)"      :("ZAR","R"),
}

# ── US States mapping ─────────────────────────────────────────────────────────
US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
    "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN",
    "TX","UT","VT","VA","WA","WV","WI","WY","DC"
}

# ── Scholarships ──────────────────────────────────────────────────────────────
SCHOLARSHIPS = {
    "I'll enter my own amount":{
        "masters":None,"phd":None,"insurance_covered":False,
        "tuition_covered":False,"covers":[],"source":"","note":"",
    },
    "DAAD — Germany":{
        "masters":992,"phd":1400,"insurance_covered":True,"tuition_covered":False,
        "covers":["Health Insurance","Travel Allowance"],
        "source":"daad.de — verified March 2026",
        "note":"German public universities charge no tuition fees. PhD also receives €460/yr research grant.",
    },
    "Erasmus+ Mundus":{
        "masters":1400,"phd":None,"insurance_covered":True,"tuition_covered":True,
        "covers":["Full Tuition","Health Insurance","Travel Costs"],
        "source":"European Commission — verified March 2026",
        "note":"€1,400/month for up to 24 months.",
    },
    "Swedish Institute":{
        "masters":1050,"phd":None,"insurance_covered":True,"tuition_covered":True,
        "covers":["Full Tuition","Health Insurance","Travel Grant SEK 15,000"],
        "source":"si.se — verified March 2026",
        "note":"SEK 12,000/month (~€1,050). Tuition paid directly to university.",
    },
    "Commonwealth — UK":{
        "masters":1611,"phd":1699,"insurance_covered":True,"tuition_covered":True,
        "covers":["Full Tuition","Health Insurance","Arrival Allowance"],
        "source":"cscuk.fcdo.gov.uk — verified March 2026",
        "note":"£1,378/month Masters | £1,452/month PhD. Original amounts in GBP.",
    },
    "CSC — China":{
        "masters":390,"phd":455,"insurance_covered":True,"tuition_covered":True,
        "covers":["Full Tuition","Health Insurance","Free Accommodation"],
        "source":"csc.edu.cn — verified March 2026",
        "note":"CNY 3,000/month Masters | CNY 3,500/month PhD. Free on-campus accommodation provided.",
    },
    "Government of Ireland (GOI-IES)":{
        "masters":833,"phd":833,"insurance_covered":False,"tuition_covered":True,
        "covers":["Full Tuition Waiver"],
        "source":"hea.ie — verified March 2026",
        "note":"€10,000/year = €833/month. One year award only.",
    },
}

# ── Functions ──────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def get_world_cities():
    """Fetch all world cities from Numbeo — single request, deduplicated"""
    url     = "https://www.numbeo.com/cost-of-living/rankings.jsp?title=2025"
    headers = {"User-Agent":"Mozilla/5.0"}
    resp    = requests.get(url, headers=headers)
    tables  = pd.read_html(StringIO(resp.text))
    df      = None
    for t in tables:
        if "City" in t.columns:
            df = t[["City"]].dropna().copy()
            break
    if df is None:
        return [], {}, {}
    df["City_Clean"]     = df["City"].str.split(",").str[0].str.strip()
    df["Country_Raw"]    = df["City"].str.split(",").str[1].str.strip()
    df["Country_Clean"]  = df["Country_Raw"]
    df.loc[df["Country_Clean"].isin(US_STATES), "Country_Clean"] = "United States"
    df = df.drop_duplicates(subset="City_Clean").reset_index(drop=True)
    df["Flag"]    = df["Country_Clean"].map(CITY_FLAGS).fillna("🌍")
    df["Display"] = df["Flag"] + " " + df["City_Clean"]
    city_map    = dict(zip(df["Display"],    df["City_Clean"]))
    country_map = dict(zip(df["City_Clean"], df["Country_Clean"]))
    return sorted(df["Display"].tolist()), city_map, country_map

@st.cache_data(show_spinner=False)
def get_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency: return 1.0
    try:
        url  = f"https://api.frankfurter.dev/v1/latest?base={from_currency}&symbols={to_currency}"
        resp = requests.get(url, timeout=5)
        return resp.json()["rates"][to_currency]
    except:
        return 1.0

@st.cache_data(show_spinner=False)
def get_city_costs(city_name):
    url     = f"https://www.numbeo.com/cost-of-living/in/{city_name.replace(' ','-')}"
    headers = {"User-Agent":"Mozilla/5.0"}
    resp    = requests.get(url, headers=headers)
    if resp.status_code != 200: return None
    soup  = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", {"class":"data_wide_table"})
    if not table: return None
    rows  = table.find_all("tr")
    costs = {
        "city":city_name,"eating_out":None,"transport":None,
        "phone":None,"internet":None,"entertainment":None,
        "rent_city":None,"rent_outside":None,
        "avg_salary":None,"groceries":None,"utilities":None,
    }
    def extract(row):
        m = re.findall(r'[\d,]+\.\d+', row.get_text())
        return float(m[0].replace(",","")) if m else None
    grocery_items = {
        "Milk (Regular, 1 Liter)":8,"Fresh White Bread (1 lb Loaf)":4,
        "Eggs (12, Large Size)":2,"Chicken Fillets (1 lb)":4,
        "Apples (1 lb)":4,"Tomatoes (1 lb)":4,"Potatoes (1 lb)":4,
        "Onions (1 lb)":2,"Bottled Water (50 oz)":8,
    }
    grocery_total = 0
    for row in rows:
        t = row.get_text()
        if   "Meal at an Inexpensive Restaurant"          in t:
            p = extract(row)
            if p: costs["eating_out"] = round(p*8,2)
        elif "Monthly Public Transport Pass"              in t: costs["transport"]     = extract(row)
        elif "Mobile Phone Plan"                          in t: costs["phone"]         = extract(row)
        elif "Broadband Internet"                         in t: costs["internet"]      = extract(row)
        elif "Monthly Fitness Club"                       in t: costs["entertainment"] = extract(row)
        elif "1 Bedroom Apartment in City Centre"         in t: costs["rent_city"]     = extract(row)
        elif "1 Bedroom Apartment Outside of City Centre" in t: costs["rent_outside"]  = extract(row)
        elif "Average Monthly Net Salary"                 in t: costs["avg_salary"]    = extract(row)
        elif "Basic Utilities"                            in t: costs["utilities"]     = extract(row)
        for item, qty in grocery_items.items():
            if item in t:
                p = extract(row)
                if p: grocery_total += p*qty
    if grocery_total > 0:
        costs["groceries"] = round(grocery_total*3, 2)
    return costs

def calculate(city_costs, stipend_chosen, extras_chosen,
              housing_provided, insurance_covered,
              chosen_currency, numbeo_currency):
    conversion      = get_exchange_rate(numbeo_currency, chosen_currency)
    expenses_chosen = {}
    if not housing_provided:
        v = city_costs["rent_outside"]
        if v: expenses_chosen["🏠 Rent (outside city centre)"] = round(v*conversion,2)
    for key, label in [
        ("groceries","🛒 Groceries"),("transport","🚌 Transport"),
        ("eating_out","🍕 Eating Out"),("entertainment","🎬 Entertainment"),
    ]:
        v = city_costs[key]
        if v: expenses_chosen[label] = round(v*conversion,2)
    phone   = city_costs["phone"]    or 0
    internet= city_costs["internet"] or 0
    if phone or internet:
        expenses_chosen["📱 Phone & Internet"] = round((phone+internet)*conversion,2)
    if not insurance_covered:
        v = city_costs["utilities"]
        if v: expenses_chosen["🏥 Utilities & Insurance"] = round(v*conversion,2)
    total     = round(sum(expenses_chosen.values()),2)
    income    = round(stipend_chosen + extras_chosen, 2)
    remaining = round(income - total, 2)
    eur_rate  = get_exchange_rate("EUR", chosen_currency)
    if remaining > 400*eur_rate:
        verdict=("✅ Comfortable","You can save money each month","#F0FFF4","#276749")
    elif remaining > 0:
        verdict=("⚠️ Tight","You can cover expenses but no savings","#FFFBEB","#B7791F")
    else:
        verdict=("❌ Not enough","Stipend does not cover basic expenses","#FFF5F5","#C53030")
    return {"expenses":expenses_chosen,"total":total,
            "income":income,"remaining":remaining,
            "verdict":verdict,"rate":conversion}

# ── Session state ──────────────────────────────────────────────────────────────
if "step" not in st.session_state: st.session_state.step = 1
def go_next(): st.session_state.step += 1
def go_back(): st.session_state.step -= 1
TOTAL_STEPS = 7

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🎓 Student Affordability<br>Calculator</h1>
    <p>Plan your life abroad — enter your scholarship and city.<br>
    We fetch live costs and show your budget in any currency you choose.</p>
</div>
""", unsafe_allow_html=True)

pct = int((st.session_state.step/TOTAL_STEPS)*100)
st.markdown(f"""
<div class="progress-bar-wrap">
    <div class="progress-bar-fill" style="width:{pct}%;"></div>
</div>
<div class="progress-label">Step {st.session_state.step} of {TOTAL_STEPS}</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Study level
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.step == 1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 1 — About You</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">What level are you studying?</div>', unsafe_allow_html=True)
    level = st.radio("",[
        "🎓 PhD / Doctoral","📚 Masters (MSc / MA / MBA)",
        "🔄 Exchange Student","💼 Self-funded / Other"
    ], label_visibility="collapsed")
    st.session_state.level = level
    st.markdown('</div>', unsafe_allow_html=True)
    st.button("Continue →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — City + currency
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 2 — Destination & Currency</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Which city are you moving to?</div>', unsafe_allow_html=True)

    with st.spinner("Loading world cities from Numbeo..."):
        cities_display, city_map, country_map = get_world_cities()

    selected_display = st.selectbox("", cities_display,
        index=cities_display.index("🇩🇪 Berlin") if "🇩🇪 Berlin" in cities_display else 0,
        label_visibility="collapsed"
    )
    city    = city_map[selected_display]
    country = country_map.get(city,"")
    auto_code, auto_symbol = COUNTRY_CURRENCY.get(country,("EUR","€"))

    st.markdown(f"""
    <div class="currency-detected">
        <div class="currency-big">{auto_symbol}</div>
        <div>
            <div style="font-weight:600;color:#1B4332;">
                Auto-detected: {auto_code} for {country}
            </div>
            <div style="font-size:0.8rem;color:#718096;">
                You can change this below
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    currency_options = list(ALL_CURRENCIES.keys())
    auto_label = next((k for k,v in ALL_CURRENCIES.items() if v[0]==auto_code),
                       currency_options[0])
    selected_currency_label = st.selectbox(
        "Show my budget in:", options=currency_options,
        index=currency_options.index(auto_label)
    )
    chosen_code, chosen_symbol = ALL_CURRENCIES[selected_currency_label]

    with st.spinner("Fetching live exchange rate..."):
        rate_eur_to_chosen = get_exchange_rate("EUR", chosen_code)

    if chosen_code != "EUR":
        st.markdown(f"""
        <div class="info-note">
            🔄 Live rate: 1 EUR = {rate_eur_to_chosen:.4f} {chosen_code}<br>
            <span style="font-size:0.76rem;">Source: European Central Bank via Frankfurter API</span>
        </div>""", unsafe_allow_html=True)

    st.session_state.city               = city
    st.session_state.city_display       = selected_display
    st.session_state.country            = country
    st.session_state.numbeo_currency    = auto_code
    st.session_state.chosen_code        = chosen_code
    st.session_state.chosen_symbol      = chosen_symbol
    st.session_state.rate_eur_to_chosen = rate_eur_to_chosen
    st.markdown('</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1: st.button("← Back", on_click=go_back, use_container_width=True)
    with col2: st.button("Continue →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Stipend in chosen currency
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 3:
    sym  = st.session_state.get("chosen_symbol","€")
    code = st.session_state.get("chosen_code","EUR")
    rate = st.session_state.get("rate_eur_to_chosen",1.0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 3 — Your Monthly Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-title">What is your monthly stipend in {sym} ({code})?</div>',
                unsafe_allow_html=True)

    default_val = int(round(1200*rate))
    max_val     = int(round(20000*rate))
    step_val    = max(1, int(round(50*rate)))

    stipend_chosen = st.number_input(
        f"Monthly stipend ({sym})",
        min_value=0, max_value=max_val,
        value=default_val, step=step_val
    )
    if code != "EUR":
        equiv = round(stipend_chosen/rate, 2)
        st.markdown(f'<div class="info-note">≈ €{equiv:,.2f} EUR equivalent</div>',
                    unsafe_allow_html=True)

    st.session_state.stipend_chosen = stipend_chosen
    st.markdown('</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1: st.button("← Back", on_click=go_back, use_container_width=True)
    with col2: st.button("Continue →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Scholarship
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 4:
    sym  = st.session_state.get("chosen_symbol","€")
    code = st.session_state.get("chosen_code","EUR")
    rate = st.session_state.get("rate_eur_to_chosen",1.0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 4 — Your Scholarship</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Which scholarship do you have?</div>', unsafe_allow_html=True)

    scholarship_name = st.selectbox("", list(SCHOLARSHIPS.keys()),
                                    label_visibility="collapsed")
    s      = SCHOLARSHIPS[scholarship_name]
    is_phd = "PhD" in st.session_state.get("level","")
    preset_eur = s["phd"] if is_phd else s["masters"]

    if scholarship_name != "I'll enter my own amount" and preset_eur:
        preset_chosen = round(preset_eur*rate, 2)
        st.markdown(f"""
        <div class="schol-box">
            <div style="font-size:0.73rem;color:#276749;font-weight:600;
                text-transform:uppercase;letter-spacing:0.06em;margin-bottom:6px;">
                Our records — {scholarship_name}
            </div>
            <div class="schol-amount">{sym}{preset_chosen:,.2f}
                <span style="font-size:1rem;color:#718096;">/month</span>
            </div>
            <div style="font-size:0.78rem;color:#718096;margin-top:2px;">
                ≈ €{preset_eur:,} EUR · converted at 1 EUR = {rate:.4f} {code}
            </div>
            <div class="schol-source">📌 {s['source']}</div>
        </div>""", unsafe_allow_html=True)

        if s["covers"]:
            badges="".join([f'<span class="badge badge-green">✅ {c}</span>'
                            for c in s["covers"]])
            st.markdown(f"**Also covered:** {badges}", unsafe_allow_html=True)
        if s["note"]:
            st.markdown(f'<div class="info-note">ℹ️ {s["note"]}</div>',
                        unsafe_allow_html=True)

        confirm = st.radio(
            "⚠️ Does this match your award letter?",
            [f"✅ Yes — my award letter shows {sym}{preset_chosen:,.2f}/month",
             "✏️ No — my actual amount is different"]
        )
        if confirm.startswith("✅"):
            stipend_chosen = preset_chosen
            st.success(f"Using {sym}{stipend_chosen:,.2f}/month")
        else:
            stipend_chosen = st.number_input(
                f"Enter exact monthly amount ({sym})",
                min_value=0, max_value=int(round(20000*rate)),
                value=int(preset_chosen), step=max(1,int(round(50*rate)))
            )
        st.session_state.stipend_chosen = stipend_chosen
    else:
        st.info("Using the amount you entered in Step 3.")

    st.session_state.schol_data = s
    st.markdown('</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1: st.button("← Back", on_click=go_back, use_container_width=True)
    with col2: st.button("Continue →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Extras
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 5:
    sym  = st.session_state.get("chosen_symbol","€")
    code = st.session_state.get("chosen_code","EUR")
    rate = st.session_state.get("rate_eur_to_chosen",1.0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 5 — Scholarship Extras</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">What else does your scholarship provide?</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="info-note">ℹ️ Annual amounts divided by 12 and added monthly. All in {sym} ({code}).</div>',
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    extras_chosen = 0

    has_travel = st.checkbox("✈️ Travel Allowance")
    if has_travel:
        travel_yr = st.number_input(f"Travel allowance per year ({sym})",
            min_value=0, max_value=int(round(20000*rate)),
            value=int(round(500*rate)), step=max(1,int(round(50*rate))))
        travel_mo = round(travel_yr/12, 2)
        extras_chosen += travel_mo
        st.markdown(f'<span class="badge badge-blue">+{sym}{travel_mo:.0f}/month</span>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    has_research = st.checkbox("🔬 Research Grant / Annual Allowance")
    if has_research:
        research_yr = st.number_input(f"Research grant per year ({sym})",
            min_value=0, max_value=int(round(20000*rate)),
            value=int(round(460*rate)), step=max(1,int(round(50*rate))))
        research_mo = round(research_yr/12, 2)
        extras_chosen += research_mo
        st.markdown(f'<span class="badge badge-blue">+{sym}{research_mo:.0f}/month</span>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    has_medical = st.checkbox("🏥 Medical / Health Insurance Covered")
    if has_medical:
        st.markdown('<span class="badge badge-green">✅ Health costs excluded</span>',
                    unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    has_tuition = st.checkbox("🎟️ Tuition Waiver / Fees Covered")
    if has_tuition:
        st.markdown('<span class="badge badge-green">✅ Noted</span>',
                    unsafe_allow_html=True)

    if extras_chosen > 0:
        st.markdown(f"""
        <div class="schol-box" style="margin-top:16px;">
            <div style="font-size:0.73rem;color:#276749;font-weight:600;
                text-transform:uppercase;letter-spacing:0.06em;margin-bottom:4px;">
                Total extras added monthly
            </div>
            <div class="schol-amount">+{sym}{extras_chosen:.0f}
                <span style="font-size:1rem;color:#718096;">/month</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.session_state.extras_chosen     = extras_chosen
    st.session_state.insurance_covered = has_medical
    st.markdown('</div>', unsafe_allow_html=True)
    col1,col2 = st.columns(2)
    with col1: st.button("← Back", on_click=go_back, use_container_width=True)
    with col2: st.button("Continue →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Housing + savings
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 6:
    sym  = st.session_state.get("chosen_symbol","€")
    code = st.session_state.get("chosen_code","EUR")
    rate = st.session_state.get("rate_eur_to_chosen",1.0)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 6 — Accommodation</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Is accommodation provided?</div>', unsafe_allow_html=True)

    covers = st.session_state.get("schol_data",{}).get("covers",[])
    if "Free Accommodation" in covers:
        st.markdown('<div class="info-note">💡 Your scholarship includes free accommodation.</div>',
                    unsafe_allow_html=True)

    housing_answer = st.radio("",[
        "🏠 No — I need to find and pay for my own housing",
        "🏫 Yes — accommodation is provided or covered"
    ], label_visibility="collapsed")
    st.session_state.housing_provided = housing_answer.startswith("🏫")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 6b — Savings Goal</div>', unsafe_allow_html=True)
    st.markdown('<div class="step-title">How much do you want to save per month?</div>',
                unsafe_allow_html=True)

    max_goal     = int(round(600*rate))
    default_goal = int(round(150*rate))
    step_goal    = max(1, int(round(25*rate)))
    savings_goal = st.slider(f"Monthly savings target ({sym})",
                              0, max_goal, default_goal, step_goal)
    st.session_state.savings_goal = savings_goal
    st.markdown('</div>', unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1: st.button("← Back", on_click=go_back, use_container_width=True)
    with col2: st.button("Calculate My Budget →", on_click=go_next, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Results
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.step == 7:
    city             = st.session_state.get("city","Berlin")
    city_display     = st.session_state.get("city_display",city)
    stipend_chosen   = st.session_state.get("stipend_chosen",1200)
    extras_chosen    = st.session_state.get("extras_chosen",0)
    housing_provided = st.session_state.get("housing_provided",False)
    insurance_covered= st.session_state.get("insurance_covered",False)
    savings_goal     = st.session_state.get("savings_goal",150)
    chosen_code      = st.session_state.get("chosen_code","EUR")
    chosen_symbol    = st.session_state.get("chosen_symbol","€")
    numbeo_currency  = st.session_state.get("numbeo_currency","EUR")
    rate             = st.session_state.get("rate_eur_to_chosen",1.0)
    sym              = chosen_symbol

    with st.spinner(f"Fetching live cost data for {city_display} from Numbeo..."):
        city_costs = get_city_costs(city)

    if not city_costs:
        st.error("Could not fetch data. Please go back and try another city.")
        st.button("← Back", on_click=go_back)
    else:
        result = calculate(city_costs, stipend_chosen, extras_chosen,
                           housing_provided, insurance_covered,
                           chosen_code, numbeo_currency)
        label,sublabel,bg,fg = result["verdict"]

        st.markdown(f"""
        <div class="verdict-box" style="background:{bg};color:{fg};border:1px solid {fg}33;">
            {label}<br>
            <span style="font-size:1rem;font-weight:400;opacity:0.85;">{sublabel}</span>
            <span class="verdict-amount">{sym}{result['remaining']:,.2f} / month</span>
            <div style="font-size:0.78rem;opacity:0.7;margin-top:6px;">
                All amounts in {chosen_code} ·
                Rate: 1 EUR = {rate:.4f} {chosen_code} (ECB, live)
            </div>
        </div>""", unsafe_allow_html=True)

        if extras_chosen > 0:
            st.markdown(f"""
            <div class="info-note">
                💰 Total monthly income:
                <b>{sym}{stipend_chosen:,.2f}</b> stipend +
                <b>{sym}{extras_chosen:,.2f}</b> extras =
                <b>{sym}{result['income']:,.2f}</b>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Monthly Breakdown")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="row-item">
            <span>💰 <b>Monthly Stipend</b></span>
            <span style="color:#276749;font-weight:700;">+{sym}{stipend_chosen:,.2f}</span>
        </div>""", unsafe_allow_html=True)
        if extras_chosen > 0:
            st.markdown(f"""
            <div class="row-item">
                <span>🎁 <b>Scholarship Extras</b></span>
                <span style="color:#276749;font-weight:700;">+{sym}{extras_chosen:,.2f}</span>
            </div>""", unsafe_allow_html=True)
        for item,cost in result["expenses"].items():
            st.markdown(f"""
            <div class="row-item">
                <span>{item}</span>
                <span style="color:#C53030;">-{sym}{cost:,.2f}</span>
            </div>""", unsafe_allow_html=True)
        rc   = "#276749" if result["remaining"]>=0 else "#C53030"
        sign = "+" if result["remaining"]>=0 else ""
        st.markdown(f"""
        <hr style="border:1px solid #E8E4DC;margin:10px 0;">
        <div class="row-item">
            <span><b>💵 Left at end of month</b></span>
            <span style="color:{rc};font-weight:700;font-size:1.15rem;">
                {sign}{sym}{result['remaining']:,.2f}
            </span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="grocery-note">
            🛒 <b>Grocery estimate:</b> Based on 9 core items (milk, bread, eggs,
            chicken, apples, tomatoes, potatoes, onions, water) with realistic monthly
            quantities, scaled ×3 for a full monthly shop. Prices fetched live from
            Numbeo in local city currency, converted to {chosen_code} at live ECB rate.
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="savings-wrap">', unsafe_allow_html=True)
        st.markdown("### 🎯 Savings Goal Tracker")
        actual_savings = max(result["remaining"],0)
        if savings_goal > 0:
            pct_s     = min(int((actual_savings/savings_goal)*100),100)
            bar_color = "#40916C" if pct_s>=100 else "#F6AD55" if pct_s>=50 else "#FC8181"
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;
                        font-size:0.85rem;margin-bottom:6px;">
                <span>Goal: <b>{sym}{savings_goal:,}/month</b></span>
                <span>Actual: <b>{sym}{actual_savings:,.0f}/month</b></span>
            </div>
            <div class="savings-bar-bg">
                <div class="savings-bar-fill"
                     style="width:{pct_s}%;background:{bar_color};"></div>
            </div>
            <div style="font-size:0.8rem;color:#718096;margin-top:6px;">
                {pct_s}% of savings goal reached
            </div>""", unsafe_allow_html=True)
            if   pct_s>=100: st.success("🎉 You are hitting your savings goal!")
            elif pct_s>=50 : st.warning(f"⚠️ {sym}{savings_goal-actual_savings:.0f} short of goal.")
            else            : st.error(f"❌ {sym}{savings_goal-actual_savings:.0f} short — consider a cheaper city.")
        else:
            st.info("No savings goal set.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("### 📊 Where Does Your Money Go?")
        fig = go.Figure(go.Pie(
            labels=list(result["expenses"].keys()),
            values=list(result["expenses"].values()),
            hole=0.52,
            marker=dict(colors=["#1B4332","#2D6A4F","#40916C",
                                 "#52B788","#74C69D","#95D5B2","#B7E4C7"]),
            textinfo="percent",
            hovertemplate=f"%{{label}}<br>{sym}%{{value:,.2f}}<extra></extra>"
        ))
        fig.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                x=1.05, y=0.5,
                font=dict(size=12, family="DM Sans"),
                bgcolor="rgba(0,0,0,0)",
            ),
            paper_bgcolor="#F7F5F0", plot_bgcolor="#F7F5F0",
            margin=dict(l=0, r=120, t=20, b=0),
            height=420,
            font=dict(family="DM Sans")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            f"📍 Cost data: Numbeo ({city_display}, live) · "
            f"Exchange rates: ECB via Frankfurter API (live) · "
            f"Scholarship data: official sources, verified March 2026"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Start Over — Try Another City", use_container_width=True):
            st.session_state.step = 1
            st.rerun()

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border:1px solid #E8E4DC;margin:32px 0 16px">
<div style="text-align:center;color:#B5AFA5;font-size:0.78rem;padding-bottom:16px;">
    Built by <strong style="color:#1B4332">mhb</strong> ·
    M.S. Data Science, FAST University, Pakistan ·
    Costs: Numbeo (live) · Rates: ECB via Frankfurter API (live) ·
    Scholarships: official sources (2025-2026)
</div>
""", unsafe_allow_html=True)
