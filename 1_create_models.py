# 1_create_models.py (Updated to include Tobacco)

import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier

print("Starting model creation process with an expanded and larger dataset...")

# --- Part 1: Weather Prediction Model (No changes needed here) ---
print("Step 1: Generating detailed weather data and training models...")
# This part is unchanged.
date_range = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
data = pd.DataFrame(date_range, columns=['date'])
data['day_of_year'] = data['date'].dt.dayofyear
base_temp = 25 + 10 * np.sin(2 * np.pi * (data['day_of_year'] - 80) / 365)
data['temp_avg'] = base_temp + np.random.normal(0, 1.5, len(data))
data['temp_high'] = data['temp_avg'] + np.random.uniform(4, 8, len(data))
data['temp_low'] = data['temp_avg'] - np.random.uniform(4, 8, len(data))
data['month'] = data['date'].dt.month
data['rainfall'] = np.random.uniform(0, 5, len(data))
monsoon_months = [6, 7, 8, 9]
is_monsoon = data['month'].isin(monsoon_months)
data.loc[is_monsoon, 'rainfall'] += np.random.uniform(5, 25, size=is_monsoon.sum())
data['rainfall'] = data['rainfall'].clip(lower=0)
data['humidity'] = 60 - 20 * np.cos(2 * np.pi * data['day_of_year'] / 365) + np.random.normal(0, 5, len(data))
data['humidity'] = data['humidity'].clip(lower=20, upper=95)
X_weather = data[['day_of_year']]
weather_models = {}
for var in ['temp_high', 'temp_low', 'temp_avg', 'rainfall', 'humidity']:
    print(f"Training model for {var}...")
    y = data[var]
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_weather, y)
    weather_models[var] = model
with open('weather_models.pkl', 'wb') as f:
    pickle.dump(weather_models, f)
print("Weather models saved successfully.")


# --- Part 2: Crop Recommendation Model (Expanded and Enlarged) ---
print("\nStep 2: Generating a larger, more diverse dataset with new crops...")

num_samples_per_case = 2500
all_crop_data = []

# --- Data Generation Logic (with new crops) ---
print("Generating data for soil-dominant crops...")

# Black Soil -> Cotton
df_cotton = pd.DataFrame()
df_cotton['soil_type'] = ['Black'] * num_samples_per_case
df_cotton['rainfall'] = np.random.uniform(60, 110, num_samples_per_case)
df_cotton['temp_avg'] = np.random.uniform(28, 40, num_samples_per_case)
df_cotton['crop'] = 'Cotton'
all_crop_data.append(df_cotton)

# Clay Soil -> Rice
df_rice = pd.DataFrame()
df_rice['soil_type'] = ['Clay'] * num_samples_per_case
df_rice['rainfall'] = np.random.uniform(150, 250, num_samples_per_case)
df_rice['temp_avg'] = np.random.uniform(25, 38, num_samples_per_case)
df_rice['crop'] = 'Rice'
all_crop_data.append(df_rice)

# Red Soil -> Maize
df_maize = pd.DataFrame()
df_maize['soil_type'] = ['Red'] * num_samples_per_case
df_maize['rainfall'] = np.random.uniform(60, 120, num_samples_per_case)
df_maize['temp_avg'] = np.random.uniform(20, 35, num_samples_per_case)
df_maize['crop'] = 'Maize'
all_crop_data.append(df_maize)

print("Generating data for versatile soil crops...")

# Loamy Soil + High Rainfall -> Sugarcane
df_sugarcane = pd.DataFrame()
df_sugarcane['soil_type'] = ['Loamy'] * num_samples_per_case
df_sugarcane['rainfall'] = np.random.uniform(120, 200, num_samples_per_case)
df_sugarcane['temp_avg'] = np.random.uniform(27, 35, num_samples_per_case)
df_sugarcane['crop'] = 'Sugarcane'
all_crop_data.append(df_sugarcane)

# Loamy Soil + Low Rainfall -> Wheat
df_wheat = pd.DataFrame()
df_wheat['soil_type'] = ['Loamy'] * num_samples_per_case
df_wheat['rainfall'] = np.random.uniform(50, 100, num_samples_per_case)
df_wheat['temp_avg'] = np.random.uniform(15, 28, num_samples_per_case)
df_wheat['crop'] = 'Wheat'
all_crop_data.append(df_wheat)

# Loamy Soil + Low Rainfall + Cool Temp -> Mustard
df_mustard = pd.DataFrame()
df_mustard['soil_type'] = ['Loamy'] * num_samples_per_case
df_mustard['rainfall'] = np.random.uniform(30, 70, num_samples_per_case)
df_mustard['temp_avg'] = np.random.uniform(10, 25, num_samples_per_case)
df_mustard['crop'] = 'Mustard'
all_crop_data.append(df_mustard)

# Sandy Soil + High Rainfall -> Jute
df_jute = pd.DataFrame()
df_jute['soil_type'] = ['Sandy'] * num_samples_per_case
df_jute['rainfall'] = np.random.uniform(150, 250, num_samples_per_case)
df_jute['temp_avg'] = np.random.uniform(28, 38, num_samples_per_case)
df_jute['crop'] = 'Jute'
all_crop_data.append(df_jute)

# Sandy Soil + Very Low Rainfall + Hot Temp -> Bajra (Pearl Millet)
df_bajra = pd.DataFrame()
df_bajra['soil_type'] = ['Sandy'] * num_samples_per_case
df_bajra['rainfall'] = np.random.uniform(20, 50, num_samples_per_case)
df_bajra['temp_avg'] = np.random.uniform(30, 45, num_samples_per_case)
df_bajra['crop'] = 'Bajra'
all_crop_data.append(df_bajra)

# Sandy Soil + Low Rainfall + Cool Temp -> Gram (Chickpea)
df_gram = pd.DataFrame()
df_gram['soil_type'] = ['Sandy'] * num_samples_per_case
df_gram['rainfall'] = np.random.uniform(40, 80, num_samples_per_case)
df_gram['temp_avg'] = np.random.uniform(15, 25, num_samples_per_case)
df_gram['crop'] = 'Gram'
all_crop_data.append(df_gram)

# --- NEW CROP: TOBACCO ---
print("Generating data for new crop (Tobacco)...")
# Sandy Soil + Moderate Rainfall + Warm Temp -> Tobacco
df_tobacco = pd.DataFrame()
df_tobacco['soil_type'] = ['Sandy'] * num_samples_per_case
df_tobacco['rainfall'] = np.random.uniform(50, 100, num_samples_per_case)
df_tobacco['temp_avg'] = np.random.uniform(20, 32, num_samples_per_case)
df_tobacco['crop'] = 'Tobacco'
all_crop_data.append(df_tobacco)
# --- END OF NEW CROP ---

# --- Combine, Process, and Train ---
crop_data = pd.concat(all_crop_data, ignore_index=True)

# Add other features with some randomness
crop_data['ph'] = np.random.uniform(5.5, 8.0, len(crop_data))
crop_data['humidity'] = np.random.uniform(30, 95, len(crop_data))
crop_data['temp_high'] = crop_data['temp_avg'] + np.random.uniform(4, 8, len(crop_data))
crop_data['temp_low'] = crop_data['temp_avg'] - np.random.uniform(4, 8, len(crop_data))

# IMPORTANT: Shuffle the dataset to ensure randomness
crop_data = crop_data.sample(frac=1).reset_index(drop=True)
print(f"\nTotal dataset size: {len(crop_data)} samples.")
print("Final crop distribution:\n", crop_data['crop'].value_counts())

# Preprocessing and Training
X_crop_raw = crop_data.drop('crop', axis=1)
X_crop_raw = X_crop_raw[['temp_high', 'temp_low', 'temp_avg', 'rainfall', 'humidity', 'ph', 'soil_type']]
X_crop = pd.get_dummies(X_crop_raw, columns=['soil_type'], drop_first=True)
y_crop = crop_data['crop']

model_columns = X_crop.columns
with open('crop_model_columns.pkl', 'wb') as f:
    pickle.dump(model_columns, f)

print("\nTraining the new, larger and more diverse crop recommendation model...")
crop_model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
crop_model.fit(X_crop, y_crop)

with open('crop_model.pkl', 'wb') as f:
    pickle.dump(crop_model, f)

print("New crop recommendation model saved successfully.")
print("\nModel creation process finished.")