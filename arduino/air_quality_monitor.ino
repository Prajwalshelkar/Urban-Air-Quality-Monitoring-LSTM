#define BLYNK_TEMPLATE_ID "TMPL3dR8zutN3"
#define BLYNK_TEMPLATE_NAME "Air Quality Monitoring"
#define BLYNK_AUTH_TOKEN "YOUR_BLYNK_TOKEN" //YOUR_BLYNK_TOKEN

#define BLYNK_PRINT Serial
#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <DHT.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include "MQ135.h"

// Multiplexer control pins
#define S0 D0
#define S1 D3
#define S2 D5
#define S3 D7

// Pin definitions
#define DHTPIN 2       // DHT11 sensor connected to D4 (NodeMCU D2)
#define DHTTYPE DHT11
#define GP2Y1014_PIN_LED D6  // Pin to control LED of GP2Y1014AU0F
#define SIG_PIN A0      // SIG pin of the multiplexer (connected to A0 on ESP8266)

// Initialize components
DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);  // I2C address for 16x2 LCD
WiFiClient client;

// Blynk credentials
char auth[] = BLYNK_AUTH_TOKEN;
BlynkTimer timer;

// Variables for sensor data
int gasValue, dustValue;
float temperature, humidity;

// Thresholds for alerts
int gasThreshold = 120;      // Gas value threshold for alert
int dustThreshold = 300;     // Dust value threshold for alert

// ThingSpeak API details
String apiKey = "";  // Your ThingSpeak API key
const char *ssid = "";   // Your WiFi SSID
const char *pass = "";       // Your WiFi password
const char *server = "api.thingspeak.com";

// Function to select the multiplexer channel
void selectMuxChannel(int channel) {
  digitalWrite(S0, channel & 0x01);
  digitalWrite(S1, channel & 0x02);
  digitalWrite(S2, channel & 0x04);
  digitalWrite(S3, channel & 0x08);
}

// Function to read dust sensor (GP2Y1014AU0F)
int readDustSensor() {
  digitalWrite(GP2Y1014_PIN_LED, LOW);   // Turn on the LED
  delayMicroseconds(280);                // Wait for the LED to stabilize
  int dustVal = analogRead(SIG_PIN);     // Read analog value from MUX (C1)
  delayMicroseconds(40);
  digitalWrite(GP2Y1014_PIN_LED, HIGH);  // Turn off the LED
  delayMicroseconds(9680);               // Wait for the next reading
  return dustVal;
}

// Function to read MQ135 (Air Quality) sensor
int readGasSensor() {
  return analogRead(SIG_PIN);            // Read analog value from MUX (C0)
}

// Function to send data to ThingSpeak
void sendToThingSpeak(float temperature, float humidity, int gasValue, int dustValue) {
  if (client.connect(server, 80)) {
    String postStr = apiKey;
    postStr += "&field1=" + String(temperature);
    postStr += "&field2=" + String(humidity);
    postStr += "&field3=" + String(gasValue);
    postStr += "&field4=" + String(dustValue);
    postStr += "\r\n\r\n";

    client.print("POST /update HTTP/1.1\n");
    client.print("Host: api.thingspeak.com\n");
    client.print("Connection: close\n");
    client.print("X-THINGSPEAKAPIKEY: " + apiKey + "\n");
    client.print("Content-Type: application/x-www-form-urlencoded\n");
    client.print("Content-Length: " + String(postStr.length()) + "\n\n");
    client.print(postStr);

    Serial.println("Data sent to ThingSpeak.");
  }
  client.stop();
}

// Function to send sensor data
void sendSensorData() {
  temperature = dht.readTemperature();
  humidity = dht.readHumidity();

  // Read from MQ135 (Air Quality)
  selectMuxChannel(0);  // Select C0
  gasValue = readGasSensor();

  // Read from GP2Y1014AU0F (Dust Sensor)
  selectMuxChannel(1);  // Select C1
  dustValue = readDustSensor();

  // Send values to Blynk
  Blynk.virtualWrite(V0, temperature);
  Blynk.virtualWrite(V1, humidity);
  Blynk.virtualWrite(V2, gasValue);
  Blynk.virtualWrite(V3, dustValue);

  // Display values on Serial
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.print(" C, Humidity: ");
  Serial.print(humidity);
  Serial.print("%, Gas: ");
  Serial.print(gasValue);
  Serial.print(" PPM, Dust: ");
  Serial.println(dustValue);

  // Send data to ThingSpeak
  sendToThingSpeak(temperature, humidity, gasValue, dustValue);

  // Trigger alerts if thresholds are exceeded
  if (gasValue > gasThreshold) {
    Blynk.logEvent("pollution_alert", "High Gas Levels Detected");
    Serial.println("High gas levels detected!");
  }

  if (dustValue > dustThreshold) {
    Blynk.logEvent("dust_alert", "High Dust Levels Detected");
    Serial.println("High dust levels detected!");
  }
}

// LCD display update function
void updateLCD() {
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Air Quality");
  lcd.setCursor(0, 1);
  lcd.print("Monitoring");

  delay(1000);  // Wait for 1 second before displaying sensor data

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Hum: ");
  lcd.print(humidity);
  lcd.print("%");

  delay(2000);  // Display temperature and humidity for 2 seconds

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Gas Value: ");
  lcd.print(gasValue);
  lcd.print("ppm");

  lcd.setCursor(0, 1);
  lcd.print("Dust Density: ");
  lcd.print(dustValue);

  delay(2000);  // Display gas and dust values for 2 seconds
}

void setup() {
  Serial.begin(115200);

  // Blynk setup
  Blynk.begin(auth, ssid, pass);

  // DHT sensor setup
  dht.begin();

  // LCD setup
  lcd.begin();
  lcd.backlight();

  // Pin modes
  pinMode(S0, OUTPUT);
  pinMode(S1, OUTPUT);
  pinMode(S2, OUTPUT);
  pinMode(S3, OUTPUT);
  pinMode(GP2Y1014_PIN_LED, OUTPUT);
  digitalWrite(GP2Y1014_PIN_LED, HIGH);  // Turn off LED by default

  // Set timers for sensor readings and updates
  timer.setInterval(2000L, sendSensorData);  // Send sensor data every 2 seconds
  timer.setInterval(2000L, updateLCD);       // Update LCD every 2 seconds
}

void loop() {
  Blynk.run();     // Run Blynk
  timer.run();     // Run timers for sensor updates and LCD display
}
