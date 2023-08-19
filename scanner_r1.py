import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess


def ping_address(ip):
    try:
        response = subprocess.check_output(
            ['ping', '-c', '1', ip],
            stderr=subprocess.STDOUT,  # Capture the error output
            universal_newlines=True  # Return string not bytes
        )
        # Extract ping time 
        ping_time = response.split("time=")[-1].split(" ")[0]
        return ping_time
    except subprocess.CalledProcessError:
        return False


def threaded_ping():
    ip = ping_ip_entry.get()
    ping_time = ping_address(ip)
    if ping_time:
        messagebox.showinfo("Ping Result", f"{ip} is responsive! (Ping time: {ping_time} ms)")
    else:
        messagebox.showwarning("Ping Result", f"{ip} is not responsive.")


def scan_ports(ip, ports):
    open_ports = []
    results.insert(tk.END, f"Scanning {ip}...\n")
    results.see(tk.END)  # Scroll the Text 

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)

        result = sock.connect_ex((ip, port))
        if result == 0:
            open_ports.append(port)

        sock.close()

    return open_ports

def threaded_scan(ip_start, ip_end, ports):
    open_ports_data = {}
    start_ip_parts = list(map(int, ip_start.split(".")))
    end_ip_parts = list(map(int, ip_end.split(".")))

    for a in range(start_ip_parts[0], end_ip_parts[0] + 1):
        for b in range(start_ip_parts[1], end_ip_parts[1] + 1):
            for c in range(start_ip_parts[2], end_ip_parts[2] + 1):
                for d in range(start_ip_parts[3], end_ip_parts[3] + 1):
                    ip = f"{a}.{b}.{c}.{d}"
                    open_ports = scan_ports(ip, ports)
                    if open_ports:
                        open_ports_data[ip] = open_ports

    for ip, open_ports in open_ports_data.items():
        results.insert(tk.END, f"{ip} has open ports: {', '.join(map(str, open_ports))}\n")

def start_scan():
    ip_start = start_ip_entry.get()
    ip_end = end_ip_entry.get()
    ports = list(map(int, ports_entry.get().split(",")))

    threading.Thread(target=threaded_scan, args=(ip_start, ip_end, ports)).start()

def set_well_known_ports():
    ports = "21,22,23,25,53,80,110,143,443,3389"
    ports_entry.delete(0, tk.END)  # Clear 
    ports_entry.insert(0, ports)  # Insert


def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_text = ("Port Scanner and Pinger\n"
                  "\n"
                  "This tool allows you to scan specific IP address ranges for open ports and also ping a specified IP address to check its responsiveness.\n"
                  "\n"
                  "Developed by: Devrim Savas Yilmaz")
    about_label = ttk.Label(about_window, text=about_text, padding=10)
    about_label.pack()
    about_window.mainloop()


def get_ip(domain_name):
    """Resolve domain name to IP address."""
    try:
        return socket.gethostbyname(domain_name)
    except socket.gaierror:
        return "Invalid domain name or not reachable."



root = tk.Tk()
root.title("Port Scanner and Pinger")
root.geometry("430x660")
root.config(bg="lightgray")
root.resizable(False,False)

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

start_ip_label = ttk.Label(frame, text="Start IP:")
start_ip_label.grid(row=0, column=0, sticky=tk.W, pady=5)
start_ip_entry = ttk.Entry(frame)
start_ip_entry.grid(row=0, column=1, sticky=tk.W, pady=5)

end_ip_label = ttk.Label(frame, text="End IP:")
end_ip_label.grid(row=1, column=0, sticky=tk.W, pady=5)
end_ip_entry = ttk.Entry(frame)
end_ip_entry.grid(row=1, column=1, sticky=tk.W, pady=5)

ports_label = ttk.Label(frame, text="Ports (comma separated):")
ports_label.grid(row=2, column=0, sticky=tk.W, pady=5)
ports_entry = ttk.Entry(frame)
ports_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

start_button = ttk.Button(frame, text="Start Port Scan", command=start_scan)
start_button.grid(row=3, column=0, columnspan=2, pady=10)

results = tk.Text(frame, width=50, height=15)
results.grid(row=4, column=0, columnspan=2, pady=5)

ping_ip_label = ttk.Label(frame, text="Ping IP:")
ping_ip_label.grid(row=5, column=0, sticky=tk.W, pady=5)
ping_ip_entry = ttk.Entry(frame)
ping_ip_entry.grid(row=5, column=1, sticky=tk.W, pady=5)

ping_button = ttk.Button(frame, text="Ping Address", command=lambda: threading.Thread(target=threaded_ping).start())
ping_button.grid(row=6, column=0, columnspan=2, pady=10)

preset_ports_button = ttk.Button(root, text="Use Well-Known Ports", command=set_well_known_ports)
preset_ports_button.place(x=10,y=113)


# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create the 'File' dropdown menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="About", command=show_about)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.destroy)


# Input field for domain
domain_label = ttk.Label(root, text="Enter Domain:")
domain_label.place(x=1,y=500)

domain_entry = ttk.Entry(root, width=30)
domain_entry.place(x=1,y=530)

# Button to resolve domain to IP
def resolve_domain():
    domain_name = domain_entry.get()
    ip_address = get_ip(domain_name)
    ip_text.set(f"IP Address: {ip_address}")

resolve_button = ttk.Button(root, text="Resolve IP", command=resolve_domain)
resolve_button.place(x=200,y=530)
# Label to display IP
ip_text = tk.StringVar()
ip_label = ttk.Label(root, textvariable=ip_text, relief="solid",width=40)
ip_label.place(x=1,y=560)




root.mainloop()
