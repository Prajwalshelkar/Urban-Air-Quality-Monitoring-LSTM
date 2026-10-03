# Import necessary libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

# Load the dataset (ensure the file is in the correct directory)
data = pd.read_csv('ambazari_data.csv')

# Check if the PM2.5 column exists, if not, throw an error
if 'PM2.5' not in data.columns:
    raise ValueError("Column 'PM2.5' not found in the dataset. Please check the column names in the CSV file.")

# Preprocess the data (scaling between 0 and 1)
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_data = scaler.fit_transform(data[['PM2.5']])

# Function to create dataset for LSTM (time series input-output pairs)
def create_dataset(dataset, time_step=1):
    X, Y = [], []
    for i in range(len(dataset) - time_step - 1):
        X.append(dataset[i:(i + time_step), 0])
        Y.append(dataset[i + time_step, 0])
    return np.array(X), np.array(Y)

# Set time step (number of previous time steps used to predict the next one)
time_step = 10
X, y = create_dataset(scaled_data, time_step)

# Reshape X to fit the LSTM input format (samples, time steps, features)
X = X.reshape(X.shape[0], X.shape[1], 1)

# Build the LSTM model
model = Sequential()
model.add(LSTM(50, return_sequences=True, input_shape=(time_step, 1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))  # Output layer for PM2.5 prediction

# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model (adjust batch_size and epochs as necessary)
model.fit(X, y, batch_size=32, epochs=10)  # You can increase epochs for better results

# Predicting on training data (or you can use test data here)
predicted_pm25 = model.predict(X)

# Optionally scale back predictions to original PM2.5 values
predicted_pm25 = scaler.inverse_transform(predicted_pm25)

# Create a new dataframe for actual and predicted PM2.5 values
# Skip the first 'time_step' rows from both actual and predicted data to match lengths
actual_pm25 = data['PM2.5'][time_step + 1:].values  # Start from time_step+1 to match predicted length
predicted_pm25 = predicted_pm25.flatten()  # Flatten the predictions

# Check if lengths match now
print(f"Length of actual values: {len(actual_pm25)}")
print(f"Length of predicted values: {len(predicted_pm25)}")

# Now create the dataframe
predicted_data = pd.DataFrame({
    'Actual_PM2.5': actual_pm25,
    'Predicted_PM2.5': predicted_pm25
})

# Plot the actual and predicted values using Matplotlib
plt.figure(figsize=(10, 6))
plt.plot(predicted_data['Actual_PM2.5'], label='Actual PM2.5', color='blue')
plt.plot(predicted_data['Predicted_PM2.5'], label='Predicted PM2.5', color='orange')
plt.title('Actual vs Predicted PM2.5')
plt.xlabel('Time')
plt.ylabel('PM2.5')
plt.legend()
plt.show()

# Optional: Save the predictions to a CSV file
predicted_data.to_csv('predicted_pm25.csv', index=False)
