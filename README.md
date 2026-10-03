# Urban Air Quality Monitoring & Prediction (LSTM / BiLSTM)

An end-to-end IoT and Deep Learning pipeline that collects real-time ambient air quality metrics using an ESP8266 microcontroller and predicts atmospheric trends using LSTM and BiLSTM recurrent networks.

## Repository Structure

```text
Urban-Air-Quality-Monitoring-LSTM/
├── arduino/
│   ├── air_quality_monitor.ino
│   └── secrets.h.example
├── ml/
│   ├── lstm.py
│   ├── bilstm_temperature.py
│   └── Improved_LSTM_Temperature_Model.keras
├── dataset/
│   └── README.md
├── results/
├── docs/
├── .gitignore
├── README.md
└── requirements.txt