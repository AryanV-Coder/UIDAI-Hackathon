import pandas as pd
import numpy as np
import os
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Set paths
DATA_DIR = r"d:\College_Ml\ML Hackathon Project\api_data_aadhar_enrolment"
OUTPUT_DIR = r"d:\College_Ml\ML Hackathon Project\cleaned_data"

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("AADHAR ENROLLMENT DATA CLEANING PIPELINE")
print("=" * 80)

# Step 1: Load all datasets
print("\n[STEP 1] Loading datasets...")
csv_files = [
    "api_data_aadhar_enrolment_0_500000.csv",
    "api_data_aadhar_enrolment_500000_1000000.csv",
    "api_data_aadhar_enrolment_1000000_1006029.csv"
]

dfs = []
for file in csv_files:
    file_path = os.path.join(DATA_DIR, file)
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        dfs.append(df)
        print(f"  ✓ {file}: {len(df)} rows")
    else:
        print(f"  ✗ {file}: NOT FOUND")

# Combine all datasets
df = pd.concat(dfs, ignore_index=True)
print(f"\nTotal records loaded: {len(df)}")
print(f"Columns: {list(df.columns)}")

# Step 2: Data type conversion
print("\n[STEP 2] Converting data types...")
df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
df['pincode'] = pd.to_numeric(df['pincode'], errors='coerce')
df['age_0_5'] = pd.to_numeric(df['age_0_5'], errors='coerce')
df['age_5_17'] = pd.to_numeric(df['age_5_17'], errors='coerce')
df['age_18_greater'] = pd.to_numeric(df['age_18_greater'], errors='coerce')
print("  ✓ Data types converted")

# Step 3: Handle missing values
print("\n[STEP 3] Handling missing values...")
print(f"  Missing values before cleaning:\n{df.isnull().sum()}")

# Fill numeric missing values with 0 (reasonable for enrollment counts)
df['age_0_5'].fillna(0, inplace=True)
df['age_5_17'].fillna(0, inplace=True)
df['age_18_greater'].fillna(0, inplace=True)
df['pincode'].fillna(0, inplace=True)

# Remove rows with missing date, state, or district
df = df.dropna(subset=['date', 'state', 'district'])
print(f"  ✓ Missing values handled. Rows after: {len(df)}")

# Step 4: Clean geographic data
print("\n[STEP 4] Cleaning geographic data...")

# Strip whitespace
df['state'] = df['state'].str.strip()
df['district'] = df['district'].str.strip()

# Standardize district names
district_mapping = {
    "South 24 Parganas": "South 24 Parganas",
    "South Twenty Four Parganas": "South 24 Parganas",
    "Hazaribag": "Hazaribagh",
    "Hazaribagh": "Hazaribagh",
    "Bagalkot *": "Bagalkot",
}

for old, new in district_mapping.items():
    df['district'] = df['district'].replace(old, new)

# Remove any remaining asterisks or special characters from district names
df['district'] = df['district'].str.replace(r'[*]', '', regex=True).str.strip()

# Standardize state names (capitalize properly)
df['state'] = df['state'].str.title()

print(f"  ✓ Geographic data cleaned")
print(f"  Unique states: {df['state'].nunique()}")
print(f"  Unique districts: {df['district'].nunique()}")

# Step 5: Handle duplicates
print("\n[STEP 5] Handling duplicates...")
duplicates_before = df.duplicated().sum()
df = df.drop_duplicates(subset=['date', 'state', 'district', 'pincode'], keep='first')
duplicates_after = duplicates_before - df.duplicated().sum()
print(f"  ✓ Removed {duplicates_after} duplicate records")

# Step 6: Validate and clean age data
print("\n[STEP 6] Validating age data...")
# Remove rows where all age groups are 0 (no data)
df = df[(df['age_0_5'] + df['age_5_17'] + df['age_18_greater']) > 0]
print(f"  ✓ Removed rows with no enrollment data")

# Check for outliers (using IQR method)
age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
for col in age_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    print(f"  {col}: Q1={Q1}, Q3={Q3}, bounds=[{lower_bound}, {upper_bound}]")

# Step 7: Create additional features for ML
print("\n[STEP 7] Creating ML features...")
df['total_enrollment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
df['pct_age_0_5'] = (df['age_0_5'] / df['total_enrollment'] * 100).round(2)
df['pct_age_5_17'] = (df['age_5_17'] / df['total_enrollment'] * 100).round(2)
df['pct_age_18_greater'] = (df['age_18_greater'] / df['total_enrollment'] * 100).round(2)
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
print("  ✓ Created features: total_enrollment, age percentages, year, month")

# Step 8: Final summary and save
print("\n[STEP 8] Final dataset summary...")
print(f"  Total records: {len(df)}")
print(f"  Date range: {df['date'].min().date()} to {df['date'].max().date()}")
print(f"  Unique states: {df['state'].nunique()}")
print(f"  Unique districts: {df['district'].nunique()}")
print(f"  Unique pincodes: {int(df[df['pincode'] > 0]['pincode'].nunique())}")
print(f"\nData info:")
print(df.info())
print(f"\nStatistical summary:")
print(df[['age_0_5', 'age_5_17', 'age_18_greater', 'total_enrollment']].describe())

# Save cleaned dataset
output_file = os.path.join(OUTPUT_DIR, "aadhar_enrollment_cleaned.csv")
df.to_csv(output_file, index=False)
print(f"\n✓ Cleaned dataset saved: {output_file}")

# Save dataset without sensitive columns (for ML)
ml_df = df[['date', 'state', 'district', 'year', 'month', 
            'age_0_5', 'age_5_17', 'age_18_greater', 'total_enrollment',
            'pct_age_0_5', 'pct_age_5_17', 'pct_age_18_greater']].copy()
ml_output_file = os.path.join(OUTPUT_DIR, "aadhar_enrollment_ml_ready.csv")
ml_df.to_csv(ml_output_file, index=False)
print(f"✓ ML-ready dataset saved: {ml_output_file}")

# Generate data quality report
print("\n" + "=" * 80)
print("DATA QUALITY REPORT")
print("=" * 80)
report = {
    'Total Records': len(df),
    'Date Range': f"{df['date'].min().date()} to {df['date'].max().date()}",
    'States': df['state'].nunique(),
    'Districts': df['district'].nunique(),
    'Missing Values': df.isnull().sum().sum(),
    'Duplicate Rows': df.duplicated().sum(),
    'Min Total Enrollment': df['total_enrollment'].min(),
    'Max Total Enrollment': df['total_enrollment'].max(),
    'Mean Total Enrollment': df['total_enrollment'].mean(),
}
for key, value in report.items():
    print(f"  {key}: {value}")

print("\n" + "=" * 80)
print("CLEANING COMPLETE!")
print("=" * 80)
