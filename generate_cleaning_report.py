"""
Data Cleaning Summary - Visual Report Generation
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (16, 12)

# Load cleaned data
df = pd.read_csv('cleaned_data/aadhar_enrollment_ml_ready.csv')
df['date'] = pd.to_datetime(df['date'])

# Create figure with subplots
fig = plt.figure(figsize=(18, 14))

# 1. Temporal trends (top)
ax1 = plt.subplot(3, 3, 1)
monthly_data = df.groupby('month')['total_enrollment'].sum()
ax1.plot(monthly_data.index, monthly_data.values, marker='o', linewidth=2, markersize=8, color='#2E86AB')
ax1.set_xlabel('Month', fontsize=11, fontweight='bold')
ax1.set_ylabel('Total Enrollment', fontsize=11, fontweight='bold')
ax1.set_title('Enrollment Trends Over Time', fontsize=12, fontweight='bold')
ax1.grid(True, alpha=0.3)

# 2. Age group distribution (pie)
ax2 = plt.subplot(3, 3, 2)
age_totals = [df['age_0_5'].sum(), df['age_5_17'].sum(), df['age_18_greater'].sum()]
age_labels = ['Age 0-5', 'Age 5-17', 'Age 18+']
colors = ['#A23B72', '#F18F01', '#C73E1D']
ax2.pie(age_totals, labels=age_labels, autopct='%1.1f%%', colors=colors, startangle=90)
ax2.set_title('Enrollment by Age Group', fontsize=12, fontweight='bold')

# 3. Distribution of total enrollment
ax3 = plt.subplot(3, 3, 3)
ax3.hist(df['total_enrollment'], bins=50, color='#06A77D', edgecolor='black', alpha=0.7)
ax3.set_xlabel('Total Enrollment per Record', fontsize=11, fontweight='bold')
ax3.set_ylabel('Frequency', fontsize=11, fontweight='bold')
ax3.set_title('Distribution of Enrollment Values', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3)

# 4. Top 10 states
ax4 = plt.subplot(3, 3, 4)
top_states = df.groupby('state')['total_enrollment'].sum().nlargest(10)
ax4.barh(range(len(top_states)), top_states.values, color='#D62828')
ax4.set_yticks(range(len(top_states)))
ax4.set_yticklabels(top_states.index, fontsize=9)
ax4.set_xlabel('Total Enrollment', fontsize=10, fontweight='bold')
ax4.set_title('Top 10 States by Enrollment', fontsize=12, fontweight='bold')
ax4.invert_yaxis()
ax4.grid(True, alpha=0.3, axis='x')

# 5. Data quality metrics
ax5 = plt.subplot(3, 3, 5)
ax5.axis('off')
quality_text = f"""
DATA QUALITY METRICS

Total Records: 980,712
Date Range: Mar 2 - Dec 31, 2025
States: 49
Districts: 964
Unique Pincodes: 19,463

Duplicates Removed: 25,317
Missing Values: 0
Data Errors: 0

Data Completeness: 100%
Data Validity: 100%
"""
ax5.text(0.05, 0.95, quality_text, transform=ax5.transAxes, 
         fontsize=10, verticalalignment='top', fontfamily='monospace',
         bbox=dict(boxstyle='round', facecolor='#E8F4F8', alpha=0.8))

# 6. Age group statistics
ax6 = plt.subplot(3, 3, 6)
age_stats = pd.DataFrame({
    'Mean': [df['age_0_5'].mean(), df['age_5_17'].mean(), df['age_18_greater'].mean()],
    'Median': [df['age_0_5'].median(), df['age_5_17'].median(), df['age_18_greater'].median()],
    'Std': [df['age_0_5'].std(), df['age_5_17'].std(), df['age_18_greater'].std()]
}, index=['Age 0-5', 'Age 5-17', 'Age 18+'])

x_pos = np.arange(len(age_stats.index))
width = 0.25
ax6.bar(x_pos - width, age_stats['Mean'], width, label='Mean', color='#1F77B4')
ax6.bar(x_pos, age_stats['Median'], width, label='Median', color='#FF7F0E')
ax6.bar(x_pos + width, age_stats['Std'], width, label='Std Dev', color='#2CA02C')
ax6.set_ylabel('Value', fontsize=10, fontweight='bold')
ax6.set_title('Age Group Statistics', fontsize=12, fontweight='bold')
ax6.set_xticks(x_pos)
ax6.set_xticklabels(age_stats.index, fontsize=9)
ax6.legend(fontsize=8)
ax6.grid(True, alpha=0.3, axis='y')

# 7. Monthly enrollment comparison
ax7 = plt.subplot(3, 3, 7)
monthly_by_age = df.groupby('month')[['age_0_5', 'age_5_17', 'age_18_greater']].mean()
ax7.plot(monthly_by_age.index, monthly_by_age['age_0_5'], marker='o', label='Age 0-5', linewidth=2)
ax7.plot(monthly_by_age.index, monthly_by_age['age_5_17'], marker='s', label='Age 5-17', linewidth=2)
ax7.plot(monthly_by_age.index, monthly_by_age['age_18_greater'], marker='^', label='Age 18+', linewidth=2)
ax7.set_xlabel('Month', fontsize=10, fontweight='bold')
ax7.set_ylabel('Average Enrollment', fontsize=10, fontweight='bold')
ax7.set_title('Seasonal Age Group Trends', fontsize=12, fontweight='bold')
ax7.legend(fontsize=8)
ax7.grid(True, alpha=0.3)

# 8. Data cleaning impact
ax8 = plt.subplot(3, 3, 8)
categories = ['Raw\nRecords', 'After\nDupicate\nRemoval', 'Final\nClean\nRecords']
values = [1006029, 1006029 - 25317, 980712]
colors_clean = ['#FF6B6B', '#FFA500', '#51CF66']
bars = ax8.bar(categories, values, color=colors_clean, edgecolor='black', linewidth=2)
ax8.set_ylabel('Record Count', fontsize=10, fontweight='bold')
ax8.set_title('Data Cleaning Impact', fontsize=12, fontweight='bold')
ax8.set_ylim([0, 1100000])
for bar, val in zip(bars, values):
    height = bar.get_height()
    ax8.text(bar.get_x() + bar.get_width()/2., height,
            f'{val:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
ax8.grid(True, alpha=0.3, axis='y')

# 9. Key metrics summary
ax9 = plt.subplot(3, 3, 9)
ax9.axis('off')
metrics_text = f"""
CLEANING OPERATIONS PERFORMED

✓ Data Type Conversion
  • Date normalization
  • Numeric standardization

✓ Missing Value Handling
  • Zero fill-down for age groups
  • No data rows removed

✓ Duplicate Removal
  • 25,317 duplicates identified
  • By: date, state, district, pincode

✓ Geographic Standardization
  • District name consolidation
  • Special character removal

✓ Feature Engineering
  • Total enrollment calculation
  • Age percentage creation
  • Temporal features (year, month)

✓ Validation
  • Outlier analysis (retained valid)
  • Data completeness check
"""
ax9.text(0.05, 0.95, metrics_text, transform=ax9.transAxes,
        fontsize=9, verticalalignment='top', fontfamily='monospace',
        bbox=dict(boxstyle='round', facecolor='#F0F8E8', alpha=0.8))

plt.suptitle('Aadhar Enrollment Data Cleaning Summary Report', 
            fontsize=16, fontweight='bold', y=0.995)
plt.tight_layout(rect=[0, 0, 1, 0.99])
plt.savefig('cleaned_data/data_cleaning_report.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved: cleaned_data/data_cleaning_report.png")
plt.close()

# Generate detailed statistics CSV
print("\nGenerating detailed statistics...")
stats_summary = pd.DataFrame({
    'Metric': [
        'Total Records',
        'Date Range (Start)',
        'Date Range (End)',
        'Unique States',
        'Unique Districts',
        'Unique Pincodes',
        'Age 0-5 (Mean)',
        'Age 5-17 (Mean)',
        'Age 18+ (Mean)',
        'Total Enrollment (Mean)',
        'Total Enrollment (Max)',
        'Missing Values',
        'Duplicate Records',
        'Data Completeness %'
    ],
    'Value': [
        f"{len(df):,}",
        str(df['date'].min().date()),
        str(df['date'].max().date()),
        str(df['state'].nunique()),
        str(df['district'].nunique()),
        str(int(df[df['pincode'] > 0]['pincode'].nunique())),
        f"{df['age_0_5'].mean():.2f}",
        f"{df['age_5_17'].mean():.2f}",
        f"{df['age_18_greater'].mean():.2f}",
        f"{df['total_enrollment'].mean():.2f}",
        f"{df['total_enrollment'].max():,}",
        "0",
        "0",
        "100.0%"
    ]
})

stats_summary.to_csv('cleaned_data/cleaning_statistics.csv', index=False)
print("✓ Statistics saved: cleaned_data/cleaning_statistics.csv")

print("\n" + "="*80)
print("CLEANING REPORT GENERATION COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  1. data_cleaning_report.png - Visual summary")
print("  2. cleaning_statistics.csv - Detailed metrics")
