import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
from threading import Thread
from datetime import datetime

class ArduinoControl:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        self.manual_mode = True
        self.auto_mode = False
        self.timer_mode = False
        self.timers = []
        self.mute_state = False

    def send_command(self, command):
        self.ser.write(f"{command}\n".encode())

    def manual_control(self, led_state, buzzer_state, marquee_text):
        if not self.mute_state:
            self.send_command(f"LED{led_state}")
            self.send_command(f"BUZZER{buzzer_state}")
            if marquee_text:
                self.send_command(f"LCD{marquee_text}")

    def auto_sensor_control(self):
        while self.auto_mode:
            if not self.mute_state:
                self.send_command("AUTO")
            time.sleep(1)

    def set_timer(self, index, pin, state, hour, minute, message):
        command = f"TIMER {index} {pin} {state} {hour:02d} {minute:02d} {message}"
        self.send_command(command)
        print(command)

    def add_timer(self, index, pin, state, hour, minute, message):
        timer_thread = Thread(target=self.set_timer, args=(index, pin, state, hour, minute, message))
        self.timers.append(timer_thread)
        timer_thread.start()

    def toggle_mute(self):
        self.mute_state = not self.mute_state
        self.send_command("MUTE")
        return self.mute_state

class ControlPanelApp:
    def __init__(self, root, arduino):
        self.root = root
        self.arduino = arduino
        self.root.title("Arduino Control Panel")
        self.create_widgets()
        self.update_time_label()  # 启动时间更新

    def create_widgets(self):
        self.mode_var = tk.StringVar(value="manual")
        modes = [("Manual", "manual"), ("Timer", "timer"), ("Auto Sensor", "auto")]

        for text, mode in modes:
            rb = ttk.Radiobutton(self.root, text=text, variable=self.mode_var, value=mode, command=self.change_mode)
            rb.pack(anchor=tk.W)

        self.led_var = tk.IntVar()
        self.buzzer_var = tk.IntVar()
        self.marquee_var = tk.StringVar()  # 新增跑马灯文字的变量

        self.led_check = ttk.Checkbutton(self.root, text="Red LED", variable=self.led_var, command=self.update_manual_controls)
        self.led_check.pack()

        self.buzzer_check = ttk.Checkbutton(self.root, text="Buzzer", variable=self.buzzer_var, command=self.update_manual_controls)
        self.buzzer_check.pack()

        # 新增跑马灯文字的输入框
        self.marquee_entry = ttk.Entry(self.root, textvariable=self.marquee_var)
        self.marquee_entry.pack()

        # 新增确认和编辑按钮
        self.confirm_button = ttk.Button(self.root, text="Confirm", command=self.confirm_marquee)
        self.confirm_button.pack()

        self.edit_button = ttk.Button(self.root, text="Edit Marquee", command=self.edit_marquee)
        self.edit_button.pack()

        # 新增静音按钮
        self.mute_button = ttk.Button(self.root, text="Mute", command=self.toggle_mute)
        self.mute_button.pack()

        self.timer_frame = ttk.LabelFrame(self.root, text="Timer Settings", padding="10")
        self.timer_frame.pack(fill="both", expand="yes")

        ttk.Label(self.timer_frame, text="Timer Index:").grid(column=0, row=0)
        self.index_var = tk.IntVar(value=0)
        self.index_entry = ttk.Entry(self.timer_frame, textvariable=self.index_var)
        self.index_entry.grid(column=1, row=0)

        ttk.Label(self.timer_frame, text="Pin:").grid(column=0, row=1)
        self.pin_var = tk.IntVar(value=1)
        self.pin_entry = ttk.Entry(self.timer_frame, textvariable=self.pin_var)
        self.pin_entry.grid(column=1, row=1)

        ttk.Label(self.timer_frame, text="State (0/1):").grid(column=0, row=2)
        self.state_var = tk.IntVar(value=0)
        self.state_entry = ttk.Entry(self.timer_frame, textvariable=self.state_var)
        self.state_entry.grid(column=1, row=2)

        ttk.Label(self.timer_frame, text="Hour:").grid(column=0, row=3)
        self.hour_var = tk.IntVar(value=0)
        self.hour_entry = ttk.Entry(self.timer_frame, textvariable=self.hour_var)
        self.hour_entry.grid(column=1, row=3)

        ttk.Label(self.timer_frame, text="Minute:").grid(column=0, row=4)
        self.minute_var = tk.IntVar(value=0)
        self.minute_entry = ttk.Entry(self.timer_frame, textvariable=self.minute_var)
        self.minute_entry.grid(column=1, row=4)

        ttk.Label(self.timer_frame, text="Message:").grid(column=0, row=5)
        self.message_var = tk.StringVar()
        self.message_entry = ttk.Entry(self.timer_frame, textvariable=self.message_var)
        self.message_entry.grid(column=1, row=5)

        self.set_timer_button = ttk.Button(self.timer_frame, text="Set Timer", command=self.set_timer)
        self.set_timer_button.grid(column=0, row=6, columnspan=2)

        # 增加 LCD 显示时间的 Label
        self.time_label = ttk.Label(self.root, text="Current Time: ")
        self.time_label.pack()

    def change_mode(self):
        mode = self.mode_var.get()
        if mode == "manual":
            self.arduino.manual_mode = True
            self.arduino.auto_mode = False
            self.arduino.timer_mode = False
        elif mode == "timer":
            self.arduino.manual_mode = False
            self.arduino.auto_mode = False
            self.arduino.timer_mode = True
        elif mode == "auto":
            self.arduino.manual_mode = False
            self.arduino.auto_mode = True
            self.arduino.timer_mode = False
            Thread(target=self.arduino.auto_sensor_control).start()

    def update_manual_controls(self):
        if self.arduino.manual_mode:
            marquee_text = self.marquee_var.get()  # 获取跑马灯文字
            self.arduino.manual_control(self.led_var.get(), self.buzzer_var.get(), marquee_text)

    def confirm_marquee(self):
        marquee_text = self.marquee_var.get()
        if marquee_text:
            self.arduino.manual_control(self.led_var.get(), self.buzzer_var.get(), marquee_text)
            self.time_label.config(text=f"Marquee Text: {marquee_text}")  # 更新 Label 显示跑马灯文字
        
    def edit_marquee(self):
        self.marquee_var.set("")  # 清空跑马灯文字

    def update_time_label(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_time_label)  # 每秒更新一次时间

    def toggle_mute(self):
        mute_state = self.arduino.toggle_mute()
        if mute_state:
            self.mute_button.config(text="Unmute")
        else:
            self.mute_button.config(text="Mute")

    def set_timer(self):
        index = self.index_var.get()
        pin = self.pin_var.get()
        state = self.state_var.get()
        hour = self.hour_var.get()
        minute = self.minute_var.get()
        message = self.message_var.get()
        print(index, pin, state, hour, minute, message)
        self.arduino.add_timer(index, pin, state, hour, minute, message)

if __name__ == "__main__":
    root = tk.Tk()
    arduino = ArduinoControl(port='COM7', baudrate=9600)  # 更换为你的 COM Port
    app = ControlPanelApp(root, arduino)
    root.mainloop()
