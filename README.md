# 🎓 Student Affordability Calculator

A live web application that helps international students plan their finances abroad.

## 🌍 Features
- **326 cities** across 107 countries
- **Live cost of living data** scraped from Numbeo in real time
- **30 currencies** with live exchange rates from the European Central Bank
- **7 scholarship presets** (DAAD, Erasmus+, Commonwealth, CSC, GOI-IES and more)
- **Scholarship confirmation** — verify amounts against your award letter
- **Extras calculator** — travel allowance, research grant, medical coverage
- **Savings goal tracker** — see if your stipend hits your monthly savings target
- **Step-by-step wizard** interface

## 📊 Data Sources
| Data | Source | Method |
|------|--------|--------|
| Cost of living | [Numbeo](https://numbeo.com) | Live web scraping |
| Exchange rates | [European Central Bank](https://ecb.europa.eu) via Frankfurter API | Live API |
| Scholarship amounts | Official scholarship websites | Verified March 2026 |

## 🛠️ Built With
- Python
- Streamlit
- BeautifulSoup4
- Pandas
- Plotly
- Frankfurter API

## 🚀 Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 👤 Author
**Hafsa**
M.S. Data Science, FAST University, Pakistan
