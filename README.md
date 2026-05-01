# nhs-ae-dashboard
NHS A&E Performance Analysis Dashboard — SQL, Python, Power BI | 4 Years of NHS England Data

# 🏥 NHS A&E Performance Dashboard

An end-to-end data analytics project analysing 4 years of NHS England A&E performance data (April 2022 – March 2026) to identify key drivers of 4 hour target breaches and highlight operational inefficiencies across hospital trusts.

## 📊 Project Overview

This dashboard analyses A&E attendance and 4-hour breach rate data across 232 NHS trusts in England, identifying underperforming trusts, seasonal demand patterns, and year-on-year performance trends.

**Business Question:**
> Which NHS trusts are underperforming against A&E wait time targets, and what operational patterns (seasonality, regional variation, demand pressure) explain these breaches?

---

## 🔍 Key Findings

- **40.07% national breach rate** — ~4 in 10 patients waited over 4 hours  
- **United Lincolnshire Hospitals NHS Trust** — worst performing trust (~59% breach rate)  
- **Clear seasonal pattern** — breach rates peak in December (~43.9%) and are lowest in May (~37.6%)  
- **Significant variation across trusts** — most operate between 52%–58% breach rate  
- **National improvement in 2025** — breach rate decreased by ~1.6 percentage points vs 2024  
- **NHS North West** — highest regional pressure (~44% breach rate)  

---

## 📈 Business Impact

This analysis highlights operational inefficiencies across NHS trusts and supports data driven decision-making to improve A&E performance, reduce waiting times, and optimise resource allocation during peak demand periods.

## 🏥 Real-World Application

This dashboard can be used by NHS managers and healthcare analysts to:
- Monitor A&E performance in real time  
- Identify underperforming trusts  
- Allocate staffing and resources more effectively  
- Plan for seasonal demand surges  

## 🛠️ Tools Used

| Tool | Purpose |
|---|---|
| Python (pandas) | Data cleaning, transformation, and combining 48 monthly datasets |
| MySQL | Data storage, querying, and KPI calculations |
| Power BI | Interactive dashboard design and visualisation |

## 📁 Repository Structure

```
nhs-ae-dashboard/
│
├── sql/
│   ├── 01_create_table.sql
│   ├── 02_breach_rate_by_trust.sql
│   ├── 03_national_trend.sql
│   ├── 04_seasonal_analysis.sql
│   ├── 05_yoy_deterioration.sql
│   └── 06_critical_12hr_waits.sql
│
├── screenshots/
│   ├── page1_national_overview.png
│   ├── page2_trust_comparison.png
│   └── page3_seasonal_patterns.png
│
├── NHS_AE_Performance_Dashboard.pbix
└── README.md
```
## 📸 Dashboard Preview

### Page 1 — National Overview
![National Overview](screenshots/page1_national_overview.png)

### Page 2 — Trust Comparison
![Trust Comparison](screenshots/page2_trust_comparison.png)

### Page 3 — Seasonal Patterns
![Seasonal Patterns](screenshots/page3_seasonal_patterns.png)

---

## 💡 Recommendations

## 💡 Recommendations

1. **Increase winter staffing capacity** — breach rates in Dec–Jan are ~6% higher than summer months  
2. **Target high-performing outliers** — United Lincolnshire and Shrewsbury consistently exceed 55% breach rates  
3. **Address regional imbalance** — NHS North West shows highest sustained pressure  
4. **Sustain improvement strategies** — replicate 2025 interventions that reduced national breach rate by ~1.6%  

---

## 📂 Data Source

Official NHS England A&E Attendances and Emergency Admissions statistics:
🔗 https://www.england.nhs.uk/statistics/statistical-work-areas/ae-waiting-times-and-activity/

---

## 👤 Author

## 👤 Author

**Zaid Rupani**  
MSc Data Science & Analytics — University of Leeds  
📧 zaidrupani.work@gmail.com  
🔗 LinkedIn: [(add your link here)](https://www.linkedin.com/in/zaid-rupani-b027b420b/)
🔗 Portfolio: https://www.datascienceportfol.io/zaidrupani
