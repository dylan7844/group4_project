import tkinter as tk
from tkinter import ttk
import serial
import time
from threading import Thread

class ArduinoControl:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate)
        self.manual_mode = True
        self.auto_mode = False
        self.timer_mode = False
        self.timers = []

    def send_command(self, command):
        self.ser.write(f"{command}\n".encode())

    def manual_control(self, led_state, buzzer_state, marquee_text):
        self.send_command(f"LED{led_state}")
        self.send_command(f"BUZZER{buzzer_state}")
        if marquee_text:
            self.send_command(f"LCD{marquee_text}")

    def auto_sensor_control(self):
        while self.auto_mode:
            self.send_command("AUTO")
            time.sleep(1)

    def set_timer(self, pin, state, delay):
        time.sleep(delay)
        self.send_command(f"TIMER{pin}{state}")

    def add_timer(self, pin, state, delay):
        timer_thread = Thread(target=self.set_timer, args=(pin, state, delay))
        self.timers.append(timer_thread)
        timer_thread.start()

class ControlPanelApp:
    def __init__(self, root, arduino):
        self.root = root
        self.arduino = arduino
        self.root.title("Arduino Control Panel")
        self.create_widgets()

    def create_widgets(self):
        self.mode_var = tk.StringVar(value="manual")
        modes = [("Manual", "manual"), ("Timer", "timer"), ("Auto Sensor", "auto")]

        for text, mode in modes:
            rb = ttk.Radiobutton(self.root, text=text, variable=self.mode_var, value=mode, command=self.change_mode)
            rb.pack(anchor=tk.W)

        self.led_var = tk.IntVar()
        self.buzzer_var = tk.IntVar()
        self.marquee_var = tk.StringVar()

        self.led_check = ttk.Checkbutton(self.root, text="Red LED", variable=self.led_var, command=self.update_manual_controls)
        self.led_check.pack()

        self.buzzer_check = ttk.Checkbutton(self.root, text="Buzzer", variable=self.buzzer_var, command=self.update_manual_controls)
        self.buzzer_check.pack()

        self.marquee_entry = ttk.Entry(self.root, textvariable=self.marquee_var)
        self.marquee_entry.pack()

        self.confirm_button = ttk.Button(self.root, text="Confirm", command=self.confirm_marquee)
        self.confirm_button.pack()

        self.edit_button = ttk.Button(self.root, text="Edit Marquee", command=self.edit_marquee)
        self.edit_button.pack()

        self.lcd_button = ttk.Button(self.root, text="Send to LCD", command=self.send_to_lcd)
        self.lcd_button.pack()

        self.timer_frame = ttk.LabelFrame(self.root, text="Timer Settings", padding="10")
        self.timer_frame.pack(fill="both", expand="yes")

        ttk.Label(self.timer_frame, text="Pin:").grid(column=0, row=0)
        self.pin_var = tk.IntVar(value=1)
        self.pin_entry = ttk.Entry(self.timer_frame, textvariable=self.pin_var)
        self.pin_entry.grid(column=1, row=0)

        ttk.Label(self.timer_frame, text="State (0/1):").grid(column=0, row=1)
        self.state_var = tk.IntVar(value=0)
        self.state_entry = ttk.Entry(self.timer_frame, textvariable=self.state_var)
        self.state_entry.grid(column=1, row=1)

        ttk.Label(self.timer_frame, text="Delay (s):").grid(column=0, row=2)
        self.delay_var = tk.IntVar(value=0)
        self.delay_entry = ttk.Entry(self.timer_frame, textvariable=self.delay_var)
        self.delay_entry.grid(column=1, row=2)

        self.set_timer_button = ttk.Button(self.timer_frame, text="Set Timer", command=self.set_timer)
        self.set_timer_button.grid(column=0, row=3, columnspan=2)

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
            self.arduino.manual_control(self.led_var.get(), self.buzzer_var.get(), self.marquee_var.get())

    def confirm_marquee(self):
        marquee_text = self.marquee_var.get()
        if marquee_text:
            self.arduino.send_command(f"LCD{marquee_text}")

    def send_to_lcd(self):
        marquee_text = self.marquee_var.get()
        if marquee_text:
            self.arduino.send_command(f"LCD{marquee_text}")

    def edit_marquee(self):
        self.marquee_var.set("")

    def set_timer(self):
        pin = self.pin_var.get()
        state = self.state_var.get()
        delay = self.delay_var.get()
        self.arduino.add_timer(pin, state, delay)

if __name__ == "__main__":
    root = tk.Tk()
    arduino = ArduinoControl("COM9")  # 更换为你的 COM Port
    app = ControlPanelApp(root, arduino)
    root.mainloop()
