import pandas as pd
import os
import glob

folder_path = r"C:\Users\zaidr\OneDrive\Desktop\aedata"
all_files = glob.glob(os.path.join(folder_path, "*.csv"))

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

# Save master CSV
output_path = r"C:\Users\zaidr\OneDrive\Desktop\ae_master.csv"
master.to_csv(output_path, index=False)

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
master = pd.read_csv(r"C:\Users\zaidr\OneDrive\Desktop\ae_master.csv", encoding='latin1')

# Replace NaN with None for MySQL
master = master.where(pd.notnull(master), None)

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='70575611z',  # replace with your password
    database='nhs_ae'
)
cursor = conn.cursor()

# Insert rows
insert_query = """
INSERT INTO ae_performance VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
)
"""

data = [tuple(row) for row in master.itertuples(index=False)]
cursor.executemany(insert_query, data)
conn.commit()

print(f"Inserted {cursor.rowcount} rows successfully")
cursor.close()
conn.close()