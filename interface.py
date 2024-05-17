import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from trend_logger import TrendLogger
from multiprocessing import Process, Event
import json
import os

class Config:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.config = {
            'device_number': 'Blend B',
            'trend_desc': 'Phase 1',
            'cycles': 99999,
            'cycle_time': 1,
            'buffer_size': 10,
            'plc_ip': '192.168.0.1',
            'tags': ["BLD01_PIT01_00.SMTH", "BLD01_PIT04_00.SMTH"]
        }
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

class TrendInterface:
    def __init__(self, root):
        self.root = root
        self.root.title("Trend Logger Interface")
        self.config = Config()
        self.trend_process = None
        self.pause_event = Event()
        self.create_widgets()
        self.load_settings()

    def create_widgets(self):
        # Device Number
        tk.Label(self.root, text="Device Number").grid(row=0, column=0, sticky='nw')
        self.device_number = tk.Entry(self.root)
        self.device_number.grid(row=0, column=1, sticky='ew')

        # Trend Description
        tk.Label(self.root, text="Trend Description").grid(row=1, column=0, sticky='nw')
        self.trend_desc = tk.Entry(self.root)
        self.trend_desc.grid(row=1, column=1, sticky='ew')

        # Cycles
        tk.Label(self.root, text="Cycles").grid(row=2, column=0, sticky='nw')
        self.cycles = tk.Entry(self.root)
        self.cycles.grid(row=2, column=1, sticky='ew')

        # Cycle Time
        tk.Label(self.root, text="Cycle Time").grid(row=3, column=0, sticky='nw')
        self.cycle_time = tk.Entry(self.root)
        self.cycle_time.grid(row=3, column=1, sticky='ew')

        # Buffer Size
        tk.Label(self.root, text="Buffer Size").grid(row=4, column=0, sticky='nw')
        self.buffer_size = tk.Entry(self.root)
        self.buffer_size.grid(row=4, column=1, sticky='ew')

        # PLC IP
        tk.Label(self.root, text="PLC IP").grid(row=5, column=0, sticky='nw')
        self.plc_ip = tk.Entry(self.root)
        self.plc_ip.grid(row=5, column=1, sticky='ew')

        # Tags
        tk.Label(self.root, text="Tags").grid(row=6, column=0, sticky='nw')
        self.tags_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE, height=10)
        self.tags_listbox.grid(row=6, column=1, rowspan=4, sticky='ew')
        
        # Tags Buttons Frame
        self.tags_buttons_frame = tk.Frame(self.root)
        self.tags_buttons_frame.grid(row=10, column=1, sticky='ew')
        
        self.add_tag_button = tk.Button(self.tags_buttons_frame, text="Add Tag", command=self.add_tag)
        self.add_tag_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.remove_tag_button = tk.Button(self.tags_buttons_frame, text="Remove Tag", command=self.remove_tag)
        self.remove_tag_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Actions Label
        tk.Label(self.root, text="Actions").grid(row=11, column=0, sticky='nw')

        # Actions Buttons Frame
        self.actions_buttons_frame = tk.Frame(self.root)
        self.actions_buttons_frame.grid(row=11, column=1, sticky='ew')
        
        self.start_button = tk.Button(self.actions_buttons_frame, text="Start", command=self.start_trend)
        self.start_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.pause_button = tk.Button(self.actions_buttons_frame, text="Pause", command=self.pause_trend)
        self.pause_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.stop_button = tk.Button(self.actions_buttons_frame, text="Stop", command=self.stop_trend)
        self.stop_button.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.save_button = tk.Button(self.actions_buttons_frame, text="Save Settings", command=self.save_settings)
        self.save_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def load_settings(self):
        self.device_number.insert(0, self.config.config['device_number'])
        self.trend_desc.insert(0, self.config.config['trend_desc'])
        self.cycles.insert(0, self.config.config['cycles'])
        self.cycle_time.insert(0, self.config.config['cycle_time'])
        self.buffer_size.insert(0, self.config.config['buffer_size'])
        self.plc_ip.insert(0, self.config.config['plc_ip'])
        for tag in self.config.config['tags']:
            self.tags_listbox.insert(tk.END, tag)

    def save_settings(self):
        self.config.config['device_number'] = self.device_number.get()
        self.config.config['trend_desc'] = self.trend_desc.get()
        self.config.config['cycles'] = int(self.cycles.get())
        self.config.config['cycle_time'] = int(self.cycle_time.get())
        self.config.config['buffer_size'] = int(self.buffer_size.get())
        self.config.config['plc_ip'] = self.plc_ip.get()
        self.config.config['tags'] = list(self.tags_listbox.get(0, tk.END))
        self.config.save_config()
        messagebox.showinfo("Info", "Settings Saved")

    def add_tag(self):
        tag = simpledialog.askstring("Add Tag", "Enter new tag:")
        if tag:
            self.tags_listbox.insert(tk.END, tag)

    def remove_tag(self):
        selected_tags = self.tags_listbox.curselection()
        for tag in reversed(selected_tags):
            self.tags_listbox.delete(tag)

    def start_trend(self):
        if self.trend_process is None or not self.trend_process.is_alive():
            self.pause_event.clear()
            self.trend_process = Process(target=self.run_trend_logger)
            self.trend_process.start()
        else:
            messagebox.showwarning("Warning", "Trend process is already running.")

    def run_trend_logger(self):
        trend_logger = TrendLogger(
            self.config.config['device_number'],
            self.config.config['trend_desc'],
            self.config.config['cycles'],
            self.config.config['cycle_time'],
            self.config.config['buffer_size'],
            self.config.config['plc_ip'],
            self.config.config['tags']
        )
        while not self.pause_event.is_set():
            trend_logger.log_trend()

    def pause_trend(self):
        if self.trend_process and self.trend_process.is_alive():
            self.pause_event.set()
        else:
            messagebox.showwarning("Warning", "No trend process to pause.")

    def stop_trend(self):
        if self.trend_process and self.trend_process.is_alive():
            self.trend_process.terminate()
            self.trend_process.join()
            self.trend_process = None
            self.pause_event.clear()
        else:
            messagebox.showwarning("Warning", "No trend process to stop.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TrendInterface(root)
    root.mainloop()
