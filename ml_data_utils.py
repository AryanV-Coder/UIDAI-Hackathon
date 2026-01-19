"""
Quick Start Guide for Using Cleaned Aadhar Enrollment Data
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

# ============================================================================
# 1. LOADING THE CLEANED DATA
# ============================================================================

def load_data():
    """Load the ML-ready dataset"""
    df = pd.read_csv('cleaned_data/aadhar_enrollment_ml_ready.csv')
    df['date'] = pd.to_datetime(df['date'])
    return df

# ============================================================================
# 2. EXPLORATORY DATA ANALYSIS
# ============================================================================

def explore_data(df):
    """Basic EDA of the dataset"""
    print("Dataset Shape:", df.shape)
    print("\nData Types:\n", df.dtypes)
    print("\nBasic Statistics:\n", df.describe())
    print("\nMissing Values:\n", df.isnull().sum())
    print("\nUnique Values:")
    print(f"  States: {df['state'].nunique()}")
    print(f"  Districts: {df['district'].nunique()}")
    print(f"  Months: {df['month'].nunique()}")

# ============================================================================
# 3. DATA PREPROCESSING FOR ML
# ============================================================================

def prepare_data_for_ml(df, target_column=None, test_size=0.2, random_state=42):
    """
    Prepare data for ML modeling
    
    Args:
        df: DataFrame with cleaned data
        target_column: Column to predict (if any)
        test_size: Proportion of test set
        random_state: For reproducibility
    
    Returns:
        X_train, X_test, y_train, y_test (if target specified)
        or X, y_mappings (if no target specified)
    """
    
    # Create a copy to avoid modifying original
    df_processed = df.copy()
    
    # Drop date column (use year/month instead)
    df_processed = df_processed.drop('date', axis=1)
    
    # Separate features and categorical variables
    categorical_cols = ['state', 'district']
    numerical_cols = [col for col in df_processed.columns 
                     if col not in categorical_cols and col != target_column]
    
    # One-hot encode categorical variables
    df_encoded = pd.get_dummies(df_processed, columns=categorical_cols, drop_first=True)
    
    # Separate features and target
    if target_column:
        y = df_encoded[target_column]
        X = df_encoded.drop(target_column, axis=1)
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        return X_train, X_test, y_train, y_test
    else:
        return df_encoded, {'categorical': categorical_cols, 'numerical': numerical_cols}

# ============================================================================
# 4. FEATURE SCALING
# ============================================================================

def scale_features(X_train, X_test):
    """Scale numerical features using StandardScaler"""
    scaler = StandardScaler()
    
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_test_scaled, scaler

# ============================================================================
# 5. ANALYSIS BY GEOGRAPHIC REGIONS
# ============================================================================

def analyze_by_state(df):
    """Analyze enrollment by state"""
    state_stats = df.groupby('state').agg({
        'age_0_5': ['sum', 'mean'],
        'age_5_17': ['sum', 'mean'],
        'age_18_greater': ['sum', 'mean'],
        'total_enrollment': ['sum', 'mean']
    }).round(2)
    
    return state_stats.sort_values(('total_enrollment', 'sum'), ascending=False)

def analyze_by_district(df, state=None):
    """Analyze enrollment by district (optionally filtered by state)"""
    if state:
        df_filtered = df[df['state'] == state]
    else:
        df_filtered = df
    
    district_stats = df_filtered.groupby('district').agg({
        'total_enrollment': ['sum', 'mean'],
        'age_0_5': 'mean',
        'age_5_17': 'mean',
        'age_18_greater': 'mean'
    }).round(2)
    
    return district_stats.sort_values(('total_enrollment', 'sum'), ascending=False)

# ============================================================================
# 6. TEMPORAL ANALYSIS
# ============================================================================

def analyze_temporal_trends(df):
    """Analyze enrollment trends over time"""
    monthly_stats = df.groupby('month').agg({
        'total_enrollment': ['sum', 'mean', 'std'],
        'age_0_5': 'mean',
        'age_5_17': 'mean',
        'age_18_greater': 'mean'
    }).round(2)
    
    return monthly_stats

# ============================================================================
# 7. AGE GROUP DISTRIBUTION
# ============================================================================

def analyze_age_distribution(df):
    """Analyze distribution of enrollment across age groups"""
    age_stats = {
        'age_0_5': {
            'total': df['age_0_5'].sum(),
            'mean': df['age_0_5'].mean(),
            'median': df['age_0_5'].median(),
            'std': df['age_0_5'].std()
        },
        'age_5_17': {
            'total': df['age_5_17'].sum(),
            'mean': df['age_5_17'].mean(),
            'median': df['age_5_17'].median(),
            'std': df['age_5_17'].std()
        },
        'age_18_greater': {
            'total': df['age_18_greater'].sum(),
            'mean': df['age_18_greater'].mean(),
            'median': df['age_18_greater'].median(),
            'std': df['age_18_greater'].std()
        }
    }
    
    return pd.DataFrame(age_stats).T.round(2)

# ============================================================================
# 8. EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Load data
    print("Loading data...")
    df = load_data()
    
    # Exploratory analysis
    print("\n" + "="*80)
    print("EXPLORATORY DATA ANALYSIS")
    print("="*80)
    explore_data(df)
    
    # State-level analysis
    print("\n" + "="*80)
    print("TOP 10 STATES BY TOTAL ENROLLMENT")
    print("="*80)
    print(analyze_by_state(df).head(10))
    
    # Temporal trends
    print("\n" + "="*80)
    print("MONTHLY ENROLLMENT TRENDS")
    print("="*80)
    print(analyze_temporal_trends(df))
    
    # Age distribution
    print("\n" + "="*80)
    print("AGE GROUP DISTRIBUTION ANALYSIS")
    print("="*80)
    print(analyze_age_distribution(df))
    
    # Prepare data for ML (without target variable)
    print("\n" + "="*80)
    print("PREPARING DATA FOR ML")
    print("="*80)
    X, col_info = prepare_data_for_ml(df)
    print(f"Feature matrix shape: {X.shape}")
    print(f"Feature columns: {X.shape[1]}")
    print(f"Categorical features encoded: {len(col_info['categorical'])}")
    print(f"Numerical features: {len(col_info['numerical'])}")
    
    # Scale features
    X_train, X_test = X.iloc[:int(0.8*len(X))], X.iloc[int(0.8*len(X)):]
    X_train_scaled, X_test_scaled, scaler = scale_features(X_train, X_test)
    print(f"\nScaled training data shape: {X_train_scaled.shape}")
    print(f"Scaled test data shape: {X_test_scaled.shape}")
    
    print("\n✓ Data is ready for ML model training!")
