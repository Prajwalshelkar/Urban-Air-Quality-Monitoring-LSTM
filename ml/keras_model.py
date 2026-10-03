# Import necessary libraries
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Bidirectional, LSTM
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from math import sqrt
import keras_tuner as kt
from google.colab import files

# Load preprocessed dataset
uploaded = files.upload()
filename = list(uploaded.keys())[0]
df = pd.read_csv(filename)

# Drop non-numeric columns (like Date/Time)
df = df.select_dtypes(include=[np.number])

# Define target variable
target_column = 'Temperature'
if target_column not in df.columns:
    raise ValueError(f"Target column '{target_column}' not found in dataset.")

# Define features
features = [col for col in df.columns if col != target_column]

# Convert to NumPy arrays
X = df[features].values
y = df[target_column].values

# Normalize features
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Reshape for BiLSTM (required 3D shape: (samples, timesteps, features))
X_train = X_train.reshape((X_train.shape[0], 1, X_train.shape[1]))
X_test = X_test.reshape((X_test.shape[0], 1, X_test.shape[1]))

# Function to create the BiLSTM model with tunable parameters
def build_bilstm_model(hp):
    model = Sequential([
        Bidirectional(LSTM(
            units=hp.Int("units", min_value=32, max_value=128, step=32),
            return_sequences=False, input_shape=(1, X_train.shape[2])
        )),
        Dropout(hp.Float("dropout_rate", min_value=0.2, max_value=0.5, step=0.1)),
        Dense(1)  # Single output for regression
    ])
    model.compile(optimizer="adam", loss="mse", metrics=["mse", "mae"])
    return model

# Use Keras Tuner for Hyperparameter Optimization
tuner = kt.RandomSearch(
    build_bilstm_model,
    objective="val_loss",
    max_trials=10,  # Reduce trials for quick testing
    executions_per_trial=1,
    directory="bilstm_tuning",
    project_name="AQI_BiLSTM"
)

# Run Hyperparameter Tuning
tuner.search(X_train, y_train, validation_split=0.2, epochs=50, batch_size=32, verbose=2)

# Get Best Model
best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
best_model = tuner.hypermodel.build(best_hps)

# Train Best Model
best_model.fit(X_train, y_train, epochs=100, batch_size=32, verbose=2, validation_split=0.2)

# Evaluate Best Model
y_pred = best_model.predict(X_test)

# Compute Evaluation Metrics
rmse = sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Best BiLSTM Model -> RMSE: {rmse:.5f}, MAE: {mae:.5f}, R^2 Score: {r2:.5f}")

# Save the best model
tf.keras.models.save_model(best_model, 'my_model.keras') # This line was moved here