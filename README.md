# 🌍 Urban Air Quality Monitoring & Forecasting Pipeline

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![ESP8266](https://img.shields.io/badge/Hardware-ESP8266%20NodeMCU-E7352C?style=for-the-badge&logo=espressif&logoColor=white)](https://www.espressif.com/)
[![Blynk IoT](https://img.shields.io/badge/Cloud-Blynk%20IoT-24C48E?style=for-the-badge&logo=blynk&logoColor=white)](https://blynk.io/)
[![ThingSpeak](https://img.shields.io/badge/Cloud-ThingSpeak-005C8A?style=for-the-badge&logo=mathworks&logoColor=white)](https://thingspeak.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

An end-to-end, IoT-enabled intelligent environmental monitoring system. This project integrates micro-sensing edge hardware, dual cloud telemetry streams (**Blynk IoT** & **ThingSpeak IoT**), and deep learning sequence architectures (**Stacked LSTM** and **Bidirectional LSTM with Keras Tuner**) to measure, alert, and forecast urban air quality dynamics in real time.

---

## 📌 System Architecture

```text
                      +-----------------------------+
                      |       Physical Sensors      |
                      |  MQ-135  |  GP2Y  |  DHT11  |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   74HC4067 Multiplexer      |
                      +--------------+--------------+
                                     | Analog (A0)
                                     v
                      +-----------------------------+
                      |       ESP8266 NodeMCU       |
                      +-------+--------------+------+
                              |              |
             Wi-Fi HTTP POST  |              |  Blynk Protocol
                              v              v
               +------------------+   +-------------------+
               |  ThingSpeak IoT  |   |     Blynk IoT     |
               | (Cloud Logging & |   |  (Mobile App UI & |
               |  Field Analytics)|   | Push Thresholds)  |
               +------------------+   +-------------------+
                                       
                                     |
                     Batch Historical Extraction
                                     |
                                     v
                      +-----------------------------+
                      |     Deep Learning Models    |
                      | Stacked LSTM | Tuned BiLSTM |
                      +-----------------------------+