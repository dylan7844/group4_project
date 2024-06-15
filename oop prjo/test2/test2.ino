#include <LiquidCrystal.h> 

// 建立 LiquidCrystal 的變數 lcd
// LCD 接腳: RS, R/W, Enable, D4, D5, D6, D7 
// Arduino 接腳: 12, 11, 10, 5, 4, 3, 2
LiquidCrystal lcd(12, 11, 10, 5, 4, 3, 2);

void setup() {
  
  lcd.begin(16, 2); // 初始化 LCD，一行 16 的字元，共 2 行，預設開啟背光
  Serial.begin(9600);// 設定序列埠速率

  lcd.print("Hi, Mirotek !!"); // 列印 "Hello Mirotek !!" 訊息到 LCD 上
}

void loop() {

  lcd.setCursor(0, 1); // 設定游標位置在第二行行首


  // 將類比的數值顯示在第二列
  lcd.print("Analog: ");

  delay(2000);     
}
