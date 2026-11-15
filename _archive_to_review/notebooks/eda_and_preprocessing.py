import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# 1. Load Data
df = pd.read_csv(r'C:\Users\USER\Downloads\FinalYearProject\data\advanced_agri_dataset.csv')

# 2. EDA: Visualizations
# Correlation Heatmap
plt.figure(figsize=(12, 8))
# Select only numerical features for correlation
num_df = df.select_dtypes(include=[np.number])
sns.heatmap(num_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Feature Correlation Heatmap')
plt.tight_layout()
plt.savefig(r'C:\Users\USER\Downloads\FinalYearProject\output\correlation_heatmap.png')
plt.close()

# Yield Distribution by Crop Type
plt.figure(figsize=(10, 6))
sns.boxplot(x='Crop_Type', y='Yield_tons_per_ha', data=df)
plt.title('Yield Distribution Across Crop Types')
plt.tight_layout()
plt.savefig(r'C:\Users\USER\Downloads\FinalYearProject\output\yield_distribution.png')
plt.close()

# Risk Distribution
plt.figure(figsize=(8, 6))
sns.countplot(x='Crop_Failure_Risk', data=df)
plt.title('Crop Failure Risk Distribution (0=Low, 1=Medium, 2=High)')
plt.tight_layout()
plt.savefig(r'C:\Users\USER\Downloads\FinalYearProject\output\risk_distribution.png')
plt.close()

print("EDA charts generated successfully in 'output' folder.")

# 3. Preprocessing
# Fill Missing Values (Simulated sensor failures)
df['pH'] = df['pH'].fillna(df['pH'].median())
df['Soil_Moisture_pct'] = df['Soil_Moisture_pct'].fillna(df['Soil_Moisture_pct'].mean())

# One-Hot Encoding for Crop_Type
df_encoded = pd.get_dummies(df, columns=['Crop_Type'], drop_first=True)

# Separate Features and Targets
targets = ['Yield_tons_per_ha', 'Irrigation_Demand_mm', 'Crop_Failure_Risk']
X = df_encoded.drop(columns=targets)
y = df_encoded[targets]

# Scaling Numerical Features
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(X), columns=X.columns)

# Recombine and save preprocessed data
df_processed = pd.concat([X_scaled, y], axis=1)
output_path = r'C:\Users\USER\Downloads\FinalYearProject\data\preprocessed_agri_data.csv'
df_processed.to_csv(output_path, index=False)

print(f"Preprocessing complete. Cleaned data saved to {output_path}")
