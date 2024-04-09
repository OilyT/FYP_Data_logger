import tkinter as tk
from tkinter import filedialog
import threading
import time
import sys
import Serial_Functions as sf

class LoggingThread(threading.Thread):
    def __init__(self, output_file_path, text_vars, datum_active, vsd_active, error_label):
        self.error_label = error_label
        try:
            super().__init__()
            self.running = False
            self.output_file_path = output_file_path
            self.text_vars = text_vars
            self.datum_active = datum_active
            self.vsd_active = vsd_active
            self.start_time = time.time()
            if self.datum_active.get():
                self.ser1 = sf.open_serial_port(self.text_vars[0].get(), self.text_vars[1].get()) 
            else:
                self.torque = 0
                self.speed = 0  
                
            if self.vsd_active.get():
                self.ser2 = sf.open_serial_port(self.text_vars[2].get(), self.text_vars[3].get())
            else:
                self.pump_rpm = 0
        except Exception as e:
            self.error_label.config(text="Error occured")
            print(e)
    def run(self):
        self.running = True
        try:
            while self.running:
                with open(self.output_file_path, "a") as file:
                    if self.datum_active.get():
                        self.data = sf.read_datum(self.ser1)
                        self.torque = sf.calculate_torque(self.data, float(self.text_vars[4].get()), float(self.text_vars[5].get()), float(self.text_vars[6].get()))
                        self.speed = sf.calculate_speed(self.data)                  
                    if self.vsd_active.get():
                        self.pump_rpm = sf.read_arduino(self.ser2)
                    current_time = time.time() - self.start_time
                    current_time = round(current_time, 2)
                    file.write(str(current_time) + "," + str(self.torque) + "," + str(self.speed) + "," + str(self.pump_rpm) + "\n")                
                time.sleep(0.05)
        except Exception as e:
            if not self.running:
                self.error_label.config(text="No Error")
            else:
                self.error_label.config(text= e)
    def stop(self):
            if self.datum_active.get():
                sf.close_serial_port(self.ser1)
            if self.vsd_active.get():
                sf.close_serial_port(self.ser2)
            self.running = False
            self.join(timeout=2)  # Wait for the thread to complete before exiting

class GUIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Meridian Pico Hydro Datalogger")
        self.root.geometry("1500x700")

        self.output_file_path = ""
        self.text_vars = [tk.StringVar() for _ in range(7)]
        self.logging_thread = None
        self.datum_active = tk.BooleanVar()
        self.datum_active.set(True)
        self.vsd_active = tk.BooleanVar()
        self.vsd_active.set(True)
        self.error_label = tk.Label(root, text="No Error")
        
        self.file_label = tk.Label(root, text="Selected File Path: None")
        self.file_label.place(y=50, x=400)

        self.select_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_button.place(y=10, x=700)

        #Create entry boxes
        self.entries = []
        self.presets = ["COM5", "3000000", "COM4", "9600", "1.8658", "0", "20"]
        self.labels_pos = [(100,600), (100,770), (250,600), (250,770), (400,530), (400,700), (400,870)]
        self.entry_pos = [(125,600), (125,770), (275,600), (275,770), (425,530), (425,700), (425,870)]
        self.buttons_pos = [(150,600), (150,770), (300,600), (300,770), (450,530), (450,700), (450,870)]
        self.enter_buttons = []
        for i, label_text in enumerate(["Datum COM Port", "Datum Baud Rate", "VSD COM Port", "VSD Baud Rate", "Calibration Figure(mV/V)", "Torque Offset", "Torque Range"]):
            entry_label = tk.Label(root, text=label_text)
            entry_label.place(y = self.labels_pos[i][0], x = self.labels_pos[i][1])

            entry = tk.Entry(root, textvariable=self.text_vars[i])
            entry.insert(tk.END, self.presets[i])
            entry.place(y = self.entry_pos[i][0], x = self.entry_pos[i][1])
            self.entries.append(entry)

            enter_button = tk.Button(root, text="Enter", command=lambda i=i: self.update_string(i))
            enter_button.place(y = self.buttons_pos[i][0], x = self.buttons_pos[i][1])
            self.enter_buttons.append(enter_button)
            
        self.check1 = tk.Checkbutton(root, text="Enable Datum", variable=self.datum_active)
        self.check1.place(y=600, x=100)
        self.check2 = tk.Checkbutton(root, text="Enable VSD", variable=self.vsd_active)
        self.check2.place(y=600, x=250)
        
        self.error_label.place(y=600, x=400)

        #Create toggle button
        self.toggle_button = tk.Button(root, text="Stopped", command=self.toggle_thread, state=tk.DISABLED)
        self.toggle_button.place(y=600, x=700)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window close event

    def select_file(self):
        self.output_file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if self.output_file_path:
            self.file_label.config(text="Selected File: " + self.output_file_path)
            self.toggle_button.config(state=tk.NORMAL)

    def update_string(self, index):
        self.text_vars[index].set(self.entries[index].get())

    def toggle_thread(self):
        if not self.logging_thread or not self.logging_thread.is_alive():
            self.logging_thread = LoggingThread(self.output_file_path, self.text_vars, self.datum_active, self.vsd_active, self.error_label)
            self.logging_thread.start()
            self.toggle_button.config(text="Logging")
        else:
            self.logging_thread.stop()
            self.toggle_button.config(text="Stopped")

    def on_closing(self):
        if self.logging_thread and self.logging_thread.is_alive():
            self.logging_thread.stop()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)