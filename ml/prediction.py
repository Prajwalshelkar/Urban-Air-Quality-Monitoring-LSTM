import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import load_model # Import load_model
from sklearn.preprocessing import StandardScaler

# Load the trained model
# Load trained BiLSTM model
model = '/content/multi_step_bilstm_model.keras'  # Adjust the path if necessary
bilstm_model = load_model(model)

# Upload dataset
from google.colab import files
uploaded = files.upload()

# Load the dataset
filename = list(uploaded.keys())[0]
df = pd.read_csv(filename)

# Drop non-numeric columns (e.g., Date/Time if present)
df = df.select_dtypes(include=[np.number])

# Define target variable
target_column = 'Temperature'  # Update if different
features = [col for col in df.columns if col != target_column]

# Normalize features using the same StandardScaler
scaler = StandardScaler()
X = scaler.fit_transform(df[features].values)

# Reshape input for BiLSTM (last data point used for prediction)
X_input = X[-1].reshape((1, 1, X.shape[1]))  # Last row as input

# Predict the next temperature value
future_temperature = bilstm_model.predict(X_input)[0][0]

print(f"🔮 Predicted Future Temperature: {future_temperature:.2f}°C")