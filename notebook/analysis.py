import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

# Set style
plt.style.use('dark_background')
sns.set_palette("Blues_r")

# Load master CSV
df = pd.read_csv(r"C:\Users\zaidr\OneDrive\Desktop\ae_master.csv", encoding='latin1')

# Parse date
df['month_date'] = pd.to_datetime(df['month_date'])

# Calculate breach rate
df['breach_rate'] = (df['over4hr_type1'] / df['att_type1'].replace(0, pd.NA)) * 100

# Remove nulls and sort
df = df.dropna(subset=['breach_rate'])
df = df.sort_values('month_date')

print(f"Total rows: {df.shape[0]}")
print(f"Date range: {df['month_date'].min().strftime('%b %Y')} to {df['month_date'].max().strftime('%b %Y')}")
print(f"Unique trusts: {df['org_name'].nunique()}")
print(f"Breach rate range: {df['breach_rate'].min():.1f}% to {df['breach_rate'].max():.1f}%")

df.head()

# National monthly breach rate
monthly = df.groupby('month_date')['breach_rate'].mean().reset_index()
monthly.columns = ['month_date', 'avg_breach_rate']

# Add 3-month rolling average
monthly['rolling_3m'] = monthly['avg_breach_rate'].rolling(window=3).mean()

# Plot
fig, ax = plt.subplots(figsize=(14, 5))

ax.plot(monthly['month_date'], monthly['avg_breach_rate'], 
        color='#00A9CE', linewidth=1.5, alpha=0.5, label='Monthly Breach Rate')
ax.plot(monthly['month_date'], monthly['rolling_3m'], 
        color='#005EB8', linewidth=2.5, label='3-Month Rolling Average')
ax.axhline(y=5, color='#00843D', linewidth=1.5, 
           linestyle='--', label='NHS Target (5%)')
ax.axhline(y=monthly['avg_breach_rate'].mean(), color='#FFB81C', 
           linewidth=1.5, linestyle='--', label=f'4yr Average ({monthly["avg_breach_rate"].mean():.1f}%)')

ax.set_title('National A&E Breach Rate Trend (Apr 2022 – Mar 2026)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Breach Rate %', fontsize=11)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend(loc='upper right')
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig(r"C:\Users\zaidr\OneDrive\Desktop\nhs-ae-dashboard\screenshots\python_trend.png", 
            dpi=150, bbox_inches='tight')
plt.show()

# Add month name and number
df['month_num'] = df['month_date'].dt.month
df['month_name'] = df['month_date'].dt.strftime('%B')

# Average breach rate by month
seasonality = df.groupby(['month_num', 'month_name'])['breach_rate'].mean().reset_index()
seasonality = seasonality.sort_values('month_num')

# Colour - red for high, green for low
colors = ['#00843D' if x == seasonality['breach_rate'].min() 
          else '#DA291C' if x == seasonality['breach_rate'].max() 
          else '#005EB8' for x in seasonality['breach_rate']]

# Plot
fig, ax = plt.subplots(figsize=(14, 5))

bars = ax.bar(seasonality['month_name'], seasonality['breach_rate'], 
              color=colors, edgecolor='none', width=0.6)

# Add value labels on bars
for bar, val in zip(bars, seasonality['breach_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=9, color='white')

ax.axhline(y=seasonality['breach_rate'].mean(), color='#FFB81C',
           linewidth=1.5, linestyle='--', label=f'Annual Average ({seasonality["breach_rate"].mean():.1f}%)')

ax.set_title('Average A&E Breach Rate by Month (Seasonality Analysis)', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Month', fontsize=11)
ax.set_ylabel('Average Breach Rate %', fontsize=11)
ax.yaxis.set_major_formatter(mtick.PercentFormatter())
ax.legend()
ax.grid(True, alpha=0.2, axis='y')

plt.tight_layout()
plt.savefig(r"C:\Users\zaidr\OneDrive\Desktop\nhs-ae-dashboard\screenshots\python_seasonality.png",
            dpi=150, bbox_inches='tight')
plt.show()

# Print key findings
print(f"Worst month: {seasonality.loc[seasonality['breach_rate'].idxmax(), 'month_name']} ({seasonality['breach_rate'].max():.1f}%)")
print(f"Best month: {seasonality.loc[seasonality['breach_rate'].idxmin(), 'month_name']} ({seasonality['breach_rate'].min():.1f}%)")
print(f"Seasonal spread: {seasonality['breach_rate'].max() - seasonality['breach_rate'].min():.1f} percentage points")

# Average breach rate per trust across all months
trust_perf = df.groupby(['org_name', 'parent_org'])['breach_rate'].mean().reset_index()
trust_perf.columns = ['trust', 'region', 'avg_breach_rate']
trust_perf = trust_perf.sort_values('avg_breach_rate', ascending=False)

# Top 10 worst and best
top10_worst = trust_perf.head(10)
top10_best = trust_perf.tail(10).sort_values('avg_breach_rate')

# Plot side by side
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Worst 10
bars1 = ax1.barh(top10_worst['trust'].str[:40], top10_worst['avg_breach_rate'],
                  color='#DA291C', edgecolor='none')
for bar, val in zip(bars1, top10_worst['avg_breach_rate']):
    ax1.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=9, color='white')
ax1.set_title('Top 10 Worst Performing Trusts', fontsize=12, fontweight='bold', pad=10)
ax1.set_xlabel('Average Breach Rate %', fontsize=10)
ax1.xaxis.set_major_formatter(mtick.PercentFormatter())
ax1.grid(True, alpha=0.2, axis='x')

# Best 10
bars2 = ax2.barh(top10_best['trust'].str[:40], top10_best['avg_breach_rate'],
                  color='#00843D', edgecolor='none')
for bar, val in zip(bars2, top10_best['avg_breach_rate']):
    ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=9, color='white')
ax2.set_title('Top 10 Best Performing Trusts', fontsize=12, fontweight='bold', pad=10)
ax2.set_xlabel('Average Breach Rate %', fontsize=10)
ax2.xaxis.set_major_formatter(mtick.PercentFormatter())
ax2.grid(True, alpha=0.2, axis='x')

plt.suptitle('NHS Trust Performance Comparison', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(r"C:\Users\zaidr\OneDrive\Desktop\nhs-ae-dashboard\screenshots\python_trust_comparison.png",
            dpi=150, bbox_inches='tight')
plt.show()

# Print findings
print("TOP 10 WORST TRUSTS:")
print(top10_worst[['trust', 'avg_breach_rate']].to_string(index=False))
print("\nTOP 10 BEST TRUSTS:")
print(top10_best[['trust', 'avg_breach_rate']].to_string(index=False))


# Add year column
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Load data
df = pd.read_csv(r"C:\Users\zaidr\OneDrive\Desktop\ae_master.csv", encoding='latin1')
df['month_date'] = pd.to_datetime(df['month_date'])
df['breach_rate'] = (df['over4hr_type1'] / df['att_type1'].replace(0, pd.NA)) * 100
df = df.dropna(subset=['breach_rate'])
df = df.sort_values('month_date')
df['year'] = df['month_date'].dt.year

# YoY Analysis
yoy = df.groupby(['org_name', 'year'])['breach_rate'].mean().reset_index()
yoy_pivot = yoy.pivot(index='org_name', columns='year', values='breach_rate')
yoy_pivot = yoy_pivot[[2024, 2025]].dropna()
yoy_pivot['change'] = pd.to_numeric(yoy_pivot[2025] - yoy_pivot[2024], errors='coerce')
yoy_pivot = yoy_pivot.reset_index()
yoy_pivot.columns = ['trust', 'rate_2024', 'rate_2025', 'change']
yoy_pivot = yoy_pivot.dropna()

most_deteriorated = yoy_pivot.nlargest(10, 'change')
most_improved = yoy_pivot.nsmallest(10, 'change')

# Plot
plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

bars1 = ax1.barh(most_deteriorated['trust'].str[:40], most_deteriorated['change'],
                  color='#DA291C', edgecolor='none')
for bar, val in zip(bars1, most_deteriorated['change']):
    ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
             f'+{val:.1f}%', va='center', fontsize=9, color='white')
ax1.set_title('Top 10 Most Deteriorated (2024→2025)', fontsize=12, fontweight='bold')
ax1.set_xlabel('Change in Breach Rate %', fontsize=10)
ax1.grid(True, alpha=0.2, axis='x')

bars2 = ax2.barh(most_improved['trust'].str[:40], most_improved['change'],
                  color='#00843D', edgecolor='none')
for bar, val in zip(bars2, most_improved['change']):
    ax2.text(bar.get_width() - 0.1, bar.get_y() + bar.get_height()/2,
             f'{val:.1f}%', va='center', fontsize=9, color='white', ha='right')
ax2.set_title('Top 10 Most Improved (2024→2025)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Change in Breach Rate %', fontsize=10)
ax2.grid(True, alpha=0.2, axis='x')

plt.suptitle('Year on Year Trust Performance Change (2024 vs 2025)',
             fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(r"C:\Users\zaidr\OneDrive\Desktop\nhs-ae-dashboard\screenshots\python_yoy.png",
            dpi=150, bbox_inches='tight')
plt.show()

print("MOST DETERIORATED:")
print(most_deteriorated[['trust', 'rate_2024', 'rate_2025', 'change']].to_string(index=False))
print("\nMOST IMPROVED:")
print(most_improved[['trust', 'rate_2024', 'rate_2025', 'change']].to_string(index=False))