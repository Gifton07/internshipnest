import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Generate sample data
n_samples = 1338

# Age: 18-64 years
age = np.random.randint(18, 65, n_samples)

# Sex: male/female
sex = np.random.choice(['male', 'female'], n_samples)

# BMI: 15-50 (realistic range)
bmi = np.random.uniform(15, 50, n_samples)

# Children: 0-5
children = np.random.randint(0, 6, n_samples)

# Smoker: yes/no (with realistic distribution)
smoker = np.random.choice(['yes', 'no'], n_samples, p=[0.2, 0.8])

# Region: four regions
region = np.random.choice(['southwest', 'southeast', 'northwest', 'northeast'], n_samples)

# Create DataFrame
df = pd.DataFrame({
    'age': age,
    'sex': sex,
    'bmi': bmi,
    'children': children,
    'smoker': smoker,
    'region': region
})

# Calculate charges based on realistic factors
charges = []

for i in range(n_samples):
    base_charge = 250
    
    # Age factor
    age_factor = 1 + (df.iloc[i]['age'] - 18) * 0.02
    
    # BMI factor
    bmi_factor = 1 + (df.iloc[i]['bmi'] - 25) * 0.01
    
    # Children factor
    children_factor = 1 + df.iloc[i]['children'] * 0.1
    
    # Smoker factor (major impact)
    smoker_factor = 3.0 if df.iloc[i]['smoker'] == 'yes' else 1.0
    
    # Region factor
    region_factors = {
        'southwest': 1.0,
        'southeast': 1.1,
        'northwest': 1.05,
        'northeast': 1.15
    }
    region_factor = region_factors[df.iloc[i]['region']]
    
    # Sex factor (minor impact)
    sex_factor = 1.1 if df.iloc[i]['sex'] == 'male' else 1.0
    
    # Calculate final charge
    charge = base_charge * age_factor * bmi_factor * children_factor * smoker_factor * region_factor * sex_factor
    
    # Add some randomness
    charge *= np.random.uniform(0.8, 1.2)
    
    charges.append(round(charge, 2))

df['charges'] = charges

# Save to CSV
df.to_csv('insurance.csv', index=False)

print("Insurance dataset created successfully!")
print(f"Dataset shape: {df.shape}")
print("\nFirst few rows:")
print(df.head())
print("\nDataset statistics:")
print(df.describe())
print("\nCategorical variables:")
print(df[['sex', 'smoker', 'region']].value_counts()) 