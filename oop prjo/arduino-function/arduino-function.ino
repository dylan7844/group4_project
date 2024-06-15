#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <RTClib.h>
#include <NewPing.h>
#include "DHT.h"

#define DHTPIN 7        // DHT11 data pin
#define DHTTYPE DHT11   // DHT 11

#define TRIGGER_PIN 6
#define ECHO_PIN 5
#define MAX_DISTANCE 200
#define RED_LED_PIN 4
#define GREEN_LED_PIN 3
#define BUZZER_PIN 2
#define IO_PIN1 13
#define IO_PIN2 A0
#define IO_PIN3 A1

DHT dht(DHTPIN, DHTTYPE);
LiquidCrystal_I2C lcd(0x27, 16, 2);  // I2C LCD address 0x27 with 16 chars and 2 lines
RTC_DS3231 rtc;
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

unsigned long previousMillis = 0;
unsigned long lcdPreviousMillis = 0;
unsigned long interval = 10000;
unsigned long lcdInterval = 500;  // LCD blink interval
unsigned long lcdUpdateInterval = 60000;  // 1 minute interval
unsigned long timeBlinkInterval = 500;  // Time blink interval
unsigned long previousTimeBlinkMillis = 0;
bool objectDetected = false;
bool lcdBlinkState = false;
bool timeBlinkState = false;
bool muteState = false;
String lcdMessage = "";
float humidity = 0.0;

struct Timer {
  int pin;
  int state;
  int hour;
  int minute;
  String message;
  bool active;
};

Timer timers[5]; // Max 5 timers

void setup() {
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(IO_PIN1, OUTPUT);
  pinMode(IO_PIN2, OUTPUT);
  pinMode(IO_PIN3, OUTPUT);
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();
  dht.begin();

  if (!rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }

  if (rtc.lostPower()) {
    Serial.println("RTC lost power, let's set the time!");
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
  }

  // Initial display of current time
  displayCurrentTime();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    handleCommand(command);
  }

  unsigned long currentMillis = millis();
  
  // Auto sensor mode logic
  if (objectDetected && currentMillis - previousMillis >= interval) {
    digitalWrite(IO_PIN1, LOW);
    buzz();
    objectDetected = false;
  }

  // LCD blink logic
  if (lcdMessage != "" && currentMillis - lcdPreviousMillis >= lcdInterval) {
    lcdPreviousMillis = currentMillis;
    lcdBlinkState = !lcdBlinkState;
    if (lcdBlinkState) {
      lcd.setCursor(0, 1); // Display on second row
      lcd.print(lcdMessage);
    } else {
      lcd.setCursor(0, 1); // Clear second row
      lcd.print("                "); 
    }
  }

  // Display current time if no update for 1 minute
  if (lcdMessage == "" && currentMillis - lcdPreviousMillis >= lcdUpdateInterval) {
    displayCurrentTime();
    lcdPreviousMillis = currentMillis;  // Reset the timer for LCD updates
  }

  // Time blink logic
  if (currentMillis - previousTimeBlinkMillis >= timeBlinkInterval) {
    previousTimeBlinkMillis = currentMillis;
    timeBlinkState = !timeBlinkState;
    displayCurrentTime();
  }

  // Read humidity
  humidity = dht.readHumidity();
  if (isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Display humidity on the LCD
  lcd.setCursor(8, 0);
  lcd.print("H:");
  lcd.print(humidity);
  lcd.print("%");

  // Check humidity level and control LED, buzzer, and Pin 13
  if (humidity >= 60) {
    if (!muteState) {
      unsigned long currentBlinkMillis = millis();
      if (currentBlinkMillis - previousMillis >= interval) {
        previousMillis = currentBlinkMillis;
        digitalWrite(RED_LED_PIN, !digitalRead(RED_LED_PIN));
        digitalWrite(IO_PIN1, !digitalRead(IO_PIN1));
        buzz();
        blink();
      }
    } else {
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(IO_PIN1, LOW);
      digitalWrite(BUZZER_PIN, LOW);
    }
  } else {
    digitalWrite(RED_LED_PIN, LOW);
    digitalWrite(IO_PIN1, LOW);
  }

  checkTimers(); // Check and execute timers

  delay(100);
}

void handleCommand(String command) {
  if (command.startsWith("LED")) {
    int state = command.substring(3).toInt();
    digitalWrite(RED_LED_PIN, state);
  } else if (command.startsWith("LCD")) {
    lcdMessage = command.substring(3);
    lcdBlinkState = true;  // Reset blink state
    lcdPreviousMillis = millis();
  } else if (command.startsWith("TIME")) {
    // This command is now unnecessary since the time will be handled by the RTC
  } else if (command.startsWith("BUZZER")) {
    int state = command.substring(6).toInt();
    digitalWrite(BUZZER_PIN, state);
  } else if (command.startsWith("AUTO")) {
    int distance = sonar.ping_cm();
    if (distance > 0 && distance <= 50) {
      digitalWrite(IO_PIN1, HIGH);
      buzz();
      
      previousMillis = millis();
      objectDetected = true;
    }
  } else if (command.startsWith("TIMER")) {
    int index = command.substring(5, 6).toInt();
    int pin = command.substring(6, 7).toInt();
    int state = command.substring(7, 8).toInt();
    int hour = command.substring(8, 10).toInt();
    int minute = command.substring(10, 12).toInt();
    String message = command.substring(12);
    if (index >= 0 && index < 5) {
      timers[index] = {pin, state, hour, minute, message, true};
    }
  } else if (command.startsWith("MUTE")) {
    muteState = !muteState;
    if (muteState) {
      digitalWrite(BUZZER_PIN, LOW);
      digitalWrite(RED_LED_PIN, LOW);
      digitalWrite(IO_PIN1, LOW);
    }
  }
}

void blink(){
  while(1){
    digitalWrite(RED_LED_PIN, HIGH);
    digitalWrite(IO_PIN1, LOW);  
    delay(100);
    digitalWrite(IO_PIN1, HIGH);
    digitalWrite(RED_LED_PIN, LOW);
    delay(100);
  }
}

void buzz() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(100);
  digitalWrite(BUZZER_PIN, LOW);
}

void displayCurrentTime() {
  DateTime now = rtc.now();
  lcd.setCursor(0, 0); // Display on first row
  lcd.print("T:");
  lcd.print(now.hour(), DEC);
  if (timeBlinkState) {
    lcd.print(':');
  } else {
    lcd.print(' ');
  }
  if (now.minute() < 10) {
    lcd.print('0');
  }
  lcd.print(now.minute(), DEC);
  lcd.print(" ");
}

void checkTimers() {
  DateTime now = rtc.now();
  for (int i = 0; i < 5; i++) {
    if (timers[i].active && now.hour() == timers[i].hour && now.minute() == timers[i].minute) {
      digitalWrite(timers[i].pin, timers[i].state);
      lcd.setCursor(0, 1);
      lcd.print(timers[i].message);
      timers[i].active = false; // Deactivate the timer after execution
    }
  }
}
