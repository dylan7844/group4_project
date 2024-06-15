import serial
import time

# 连接Arduino
ser = serial.Serial('COM9', 9600)  # 更换为你的COM端口

time.sleep(2)  # 等待串口连接稳定

# 发送显示文本的指令
ser.write(b'LCDHello, World!\n')
time.sleep(5000) 

# 发送清屏指令
ser.write(b'LCD                \n')  # 清除显示内容

ser.close()
