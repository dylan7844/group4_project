#include <LiquidCrystal.h>
#include <NewPing.h>

#define TRIGGER_PIN 6
#define ECHO_PIN 5
#define MAX_DISTANCE 200
#define RED_LED_PIN 4
#define GREEN_LED_PIN 3
#define BUZZER_PIN 2
#define IO_PIN1 13
#define IO_PIN2 A0
#define IO_PIN3 A1

LiquidCrystal lcd(12, 11, 10, 9, 8, 7);  // LCD pins: RS, E, D4, D5, D6, D7
NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

unsigned long previousMillis = 0;
unsigned long lcdPreviousMillis = 0;
unsigned long interval = 120000;
unsigned long lcdInterval = 500;  // LCD 闪烁间隔
bool objectDetected = false;
bool lcdBlinkState = false;
String lcdMessage = "";

void setup() {
  pinMode(RED_LED_PIN, OUTPUT);
  pinMode(GREEN_LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(IO_PIN1, OUTPUT);
  pinMode(IO_PIN2, OUTPUT);
  pinMode(IO_PIN3, OUTPUT);
  Serial.begin(9600);
  lcd.begin(16, 2);
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
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print(lcdMessage);
    } else {
      lcd.clear();
    }
  }

  delay(100);
}

void handleCommand(String command) {
  if (command.startsWith("LED")) {
    int state = command.substring(3).toInt();
    digitalWrite(RED_LED_PIN, state);
  } else if (command.startsWith("LCD")) {
    lcdMessage = command.substring(3);
    lcdBlinkState = true;  // 重置闪烁状态
    lcdPreviousMillis = millis();
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
    int pin = command.substring(5, 6).toInt();
    int state = command.substring(6).toInt();
    if (pin == 1) digitalWrite(IO_PIN1, state);
    if (pin == 2) digitalWrite(IO_PIN2, state);
    if (pin == 3) digitalWrite(IO_PIN3, state);
  }
}

void buzz() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(100);
  digitalWrite(BUZZER_PIN, LOW);
}
