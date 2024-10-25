import tkinter as tk
from tkinter import ttk
import sv_ttk



import serial
import serial.tools.list_ports
import threading
import pyautogui
import time

# Function to find the ESP32 COM port
def find_esp32_port():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "USB" in port.description or "CP210x" in port.description or "CH340" in port.description or "FTDI" in port.description:
            return port.device  
    return None

started = False
ser = None

# Function to read data from serial
def read_rfid_data(ser):
    global started
    while started:
        try:
            if ser.in_waiting > 0:
                rfid_data = ser.readline().decode('utf-8', errors='ignore').strip()  # Read RFID data
                # Update the label with the latest RFID data
                latest_tag_label.config(text=f"TAG ID: {rfid_data}")
                pyautogui.write(rfid_data)  
                pyautogui.press('tab')  
        except (serial.SerialException, IOError):
            # If an exception occurs, indicate a disconnection
            status_label.config(text="Error: Device disconnected", foreground="red")
            com_port_label.config(text="COM Port: Not found")
            started = False
            break

# Function to monitor serial connection
def monitor_connection(ser):
    global started
    while started:
        try:
            # Check if the port is still open and working
            if not ser.is_open:
                raise serial.SerialException("Serial port closed")
            # Optional: You could send a small command if your device supports it
            ser.write(b'\x00')  # Write a small byte to the serial port to check if it’s still connected
            time.sleep(1)  # Delay to avoid busy-waiting
        except (serial.SerialException, IOError):
            # If an exception occurs, update the status and break the loop
            status_label.config(text="Error: Device disconnected", foreground="red")
            com_port_label.config(text="COM Port: Not found")
            started = False
            break

# Function to start reading RFID
def start_reading():
    global ser
    global started
    
    if not started:
        try:
            com_port = find_esp32_port()
            if com_port:
                ser = serial.Serial(com_port, 115200, timeout=1)  # Added timeout for better handling
                started = True
                threading.Thread(target=read_rfid_data, args=(ser,), daemon=True).start()
                threading.Thread(target=monitor_connection, args=(ser,), daemon=True).start()
                status_label.config(text=f"Status: Reading RFID from {com_port}...")
                com_port_label.config(text=f"COM Port: {com_port}")
                status_label.config(foreground="black")
            else:
                status_label.config(text="Error: Device not connected", foreground="red")
                com_port_label.config(text="COM Port: Not found")
        except Exception as e:
            status_label.config(text=f"Error: {e}", foreground="red")
            com_port_label.config(text="COM Port: Not found")

# Function to stop reading RFID
def stop_reading():
    global started
    global ser
    started = False
    if ser and ser.is_open:
        ser.close()
    status_label.config(text="Status: Idle")
    com_port_label.config(text="COM Port: Not found")

# GUI setup
root = tk.Tk()
root.title("RFID Reader")
root.configure(bg="black")  # Set background color to white
# Define a modern style for ttk widgets
style = ttk.Style()
style.configure('TButton', background='#007BFF', foreground='white', font=('Arial', 12, 'bold'), padding=10)
style.configure('TLabel', background='white', font=('Arial', 12), padding=5)
style.map('TButton', background=[('active', '#0056b3')])

# Frame for buttons
button_frame = ttk.Frame(root, padding="10")
button_frame.grid(row=0, column=0, columnspan=2, sticky="ew")

# Add buttons and configure their style
start_button = ttk.Button(button_frame, text="Start Reading RFID", command=start_reading)
start_button.pack(side=tk.LEFT, padx=5, pady=10)

stop_button = ttk.Button(button_frame, text="Stop Reading RFID", command=stop_reading)
stop_button.pack(side=tk.RIGHT, padx=5, pady=10)
67890   
# Frame for status and COM port info
info_frame = ttk.Frame(root, padding="10")
info_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

# Add a label to display the latest RFID data
latest_tag_label = ttk.Label(info_frame, text="TAG ID: Not available")
latest_tag_label.pack(pady=10)

# Status label to show if reading is happening
status_label = ttk.Label(info_frame, text="Status: Idle")
status_label.pack(pady=10)

# COM port label
com_port_label = ttk.Label(info_frame, text="COM Port: Not found")
com_port_label.pack(pady=10)

# Configure grid weight for responsive resizing
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Start the GUI loop

67890   
root.mainloop()
