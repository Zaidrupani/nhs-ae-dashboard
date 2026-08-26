import pandas as pd
import os
import glob

folder_path = r"C:\Users\zaidr\OneDrive\Desktop\Projects\nhs-ae-dashboard\data"
all_files = [f for f in glob.glob(os.path.join(folder_path, "*.csv")) 
             if 'ae_master' not in os.path.basename(f).lower()]
print(f"Found {len(all_files)} source files")

col_names = [
    'period', 'org_code', 'parent_org', 'org_name',
    'att_type1', 'att_type2', 'att_other',
    'att_booked_type1', 'att_booked_type2', 'att_booked_other',
    'over4hr_type1', 'over4hr_type2', 'over4hr_other',
    'over4hr_booked_type1', 'over4hr_booked_type2', 'over4hr_booked_other',
    'wait_4to12hr_dta', 'wait_12plushr_dta',
    'emerg_admit_type1', 'emerg_admit_type2',
    'emerg_admit_other', 'other_emerg_admit'
]

dfs = []
skipped = []

for file in all_files:
    try:
        df = pd.read_csv(file, encoding='latin1', usecols=range(22), header=0)
        df.columns = col_names
        dfs.append(df)
    except Exception as e:
        print(f"Skipped {os.path.basename(file)}: {e}")
        skipped.append(file)

# Combine all
master = pd.concat(dfs, ignore_index=True)

# Parse period column
master['period_clean'] = master['period'].str.replace('MSitAE-', '', regex=False)
master['month_date'] = pd.to_datetime(master['period_clean'], format='%B-%Y', errors='coerce')

# Clean whitespace
master['org_name'] = master['org_name'].str.strip()
master['parent_org'] = master['parent_org'].str.strip()

# Drop unparseable rows
before = len(master)
master = master.dropna(subset=['month_date'])
after = len(master)
print(f"Dropped {before - after} unparseable rows")

# --- Data quality fixes ---

# 1. Drop the TOTAL aggregate row from source files
before = len(master)
master = master[master['org_name'].str.upper() != 'TOTAL']
print(f"Dropped {before - len(master)} TOTAL rows")

# 2. Standardise renamed trusts (old name -> current name)
trust_renames = {
    'MID YORKSHIRE HOSPITALS NHS TRUST': 'MID YORKSHIRE TEACHING NHS TRUST',
    'UNITED LINCOLNSHIRE HOSPITALS NHS TRUST': 'UNITED LINCOLNSHIRE TEACHING HOSPITALS NHS TRUST',
    'EAST AND NORTH HERTFORDSHIRE NHS TRUST': 'EAST AND NORTH HERTFORDSHIRE TEACHING NHS TRUST',
    'ROYAL SURREY COUNTY HOSPITAL NHS FOUNDATION TRUST': 'ROYAL SURREY NHS FOUNDATION TRUST',
    'PORTSMOUTH HOSPITALS UNIVERSITY NATIONAL HEALTH SERVICE TRUST': 'PORTSMOUTH HOSPITALS UNIVERSITY NHS TRUST',
    'SOUTH WARWICKSHIRE NHS FOUNDATION TRUST': 'SOUTH WARWICKSHIRE UNIVERSITY NHS FOUNDATION TRUST',
    'WRIGHTINGTON, WIGAN AND LEIGH NHS FOUNDATION TRUST': 'WRIGHTINGTON, WIGAN AND LEIGH TEACHING HOSPITALS NHS FOUNDATION TRUST',
    'KINGSTON HOSPITAL NHS FOUNDATION TRUST': 'KINGSTON AND RICHMOND NHS FOUNDATION TRUST',
    'PUTNOE MEDICAL CENTRE WALK IN CENTRE': 'PUTNOE WALK IN CENTRE',
    'ROSSENDALE MINOR INJURIES UNIT': 'ROSSENDALE MIU & OOH',
}
master['org_name'] = master['org_name'].replace(trust_renames)

# 3. Null out months with attendances but zero recorded breaches
gap_mask = (master['att_type1'] > 0) & (master['over4hr_type1'] == 0)
print(f"Flagging {gap_mask.sum()} rows as reporting gaps")
master.loc[gap_mask, 'over4hr_type1'] = None

# 4. Flag trusts with insufficient reporting history for ranking
month_counts = master.groupby('org_name')['month_date'].nunique()
master['months_reported'] = master['org_name'].map(month_counts)
print(f"Trusts with <36 months: {(month_counts < 36).sum()}")

master['trust_short'] = (master['org_name']
    .str.replace(r'\s+NHS FOUNDATION TRUST$', '', regex=True)
    .str.replace(r'\s+NHS TRUST$', '', regex=True)
    .str.replace(r'^THE\s+', '', regex=True)
    .str.title()
    .str.replace(r"'S\b", "'s", regex=True)
    .str.replace(r'\bAnd\b', 'and', regex=True)
    .str.replace(r'\bOf\b', 'of', regex=True))

# Save master CSV
output_path = r"C:\Users\zaidr\OneDrive\Desktop\Projects\nhs-ae-dashboard\data\ae_master.csv"
master.to_csv(output_path, index=False)

# Trust-level breach rate for binning
trust_rates = (master[master['att_type1'] > 0]
    .groupby('trust_short')
    .agg(att=('att_type1','sum'), breaches=('over4hr_type1','sum'),
         months=('months_reported','max'))
    .reset_index())

trust_rates['breach_rate'] = trust_rates['breaches'] / trust_rates['att'] * 100
trust_rates = trust_rates[(trust_rates['months'] >= 36) & (trust_rates['att'] > 100000)]

def band(x):
    if x < 25: return 'A. Under 25%'
    elif x < 30: return 'B. 25-30%'
    elif x < 35: return 'C. 30-35%'
    elif x < 40: return 'D. 35-40%'
    elif x < 45: return 'E. 40-45%'
    elif x < 50: return 'F. 45-50%'
    else: return 'G. Over 50%'

trust_rates['band'] = trust_rates['breach_rate'].apply(band)
trust_rates.to_csv(r"C:\Users\zaidr\OneDrive\Desktop\Projects\nhs-ae-dashboard\data\trust_distribution.csv", index=False)
print(trust_rates['band'].value_counts().sort_index())

from statsmodels.tsa.holtwinters import ExponentialSmoothing

# National monthly breach rate
monthly = (master[master['att_type1'] > 0]
    .groupby('month_date')
    .agg(att=('att_type1','sum'), breaches=('over4hr_type1','sum'))
    .reset_index())
monthly['breach_rate'] = monthly['breaches'] / monthly['att'] * 100
monthly = monthly.sort_values('month_date').set_index('month_date')
monthly.index = pd.DatetimeIndex(monthly.index).to_period('M').to_timestamp()

# Fit and forecast 6 months
model = ExponentialSmoothing(monthly['breach_rate'], trend='add',
                             seasonal='add', seasonal_periods=12)
fit = model.fit()
fc = fit.forecast(12)

# Combine actual and forecast into one table for Power BI
actual = pd.DataFrame({'month_date': monthly.index,
                       'breach_rate': monthly['breach_rate'].values,
                       'series': 'Actual'})
forecast = pd.DataFrame({'month_date': fc.index,
                         'breach_rate': fc.values,
                         'series': 'Forecast'})

combined = pd.concat([actual, forecast], ignore_index=True)
combined.to_csv(r"C:\Users\zaidr\OneDrive\Desktop\Projects\nhs-ae-dashboard\data\breach_forecast.csv", index=False)

print(f"Forecast for next 12 months:")
for d, v in zip(fc.index, fc.values):
    print(f"  {d.strftime('%b %Y')}: {v:.2f}%")

# Sense check
print(f"\nTotal rows: {len(master)}")
print(f"Files loaded: {len(all_files)}")
print(f"Files skipped: {len(skipped)}")
print(f"\nDate range: {master['month_date'].min()} to {master['month_date'].max()}")
print(f"Unique trusts: {master['org_name'].nunique()}")
print(f"Unique months: {master['month_date'].nunique()}")
print(f"\nSample dates found:")
print(master['month_date'].value_counts().sort_index().head(10))


import pandas as pd
import mysql.connector

# Load master CSV
master = pd.read_csv(r"C:\Users\zaidr\OneDrive\Desktop\Projects\nhs-ae-dashboard\data\ae_master.csv", encoding='latin1')
# Replace NaN with None for MySQL
master = master.astype(object).where(pd.notnull(master), None)

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='70575611z',  # replace with your password
    database='nhs_ae'
)
cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE ae_performance")

# Insert rows
insert_query = """
INSERT INTO ae_performance VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

data = [tuple(row) for row in master.itertuples(index=False)]
cursor.executemany(insert_query, data)
conn.commit()

print(f"Inserted {cursor.rowcount} rows successfully")
cursor.close()
conn.close()