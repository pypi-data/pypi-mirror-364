import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import webbrowser
import psutil
import json
import sys

class ServerHost:
    def __init__(self, root):
        self.root = root
        self.root.title("Awan Server Lite")
        self.root.geometry("400x400")
        self.icon_path = os.path.join(os.path.dirname(__file__), "awan.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Server processes and status flags
        self.php_server_process = None
        self.apache_process = None
        self.mariadb_process = None
        self.is_php_running = False
        self.is_apache_running = False
        self.is_mariadb_running = False
        
        # Default paths
        self.default_paths = {
            'php': "",
            'apache': "",
            'mariadb': "",
        }
        
        # Config file
        self.config_file = "server_host_config.json"
        self.load_config()
        
        # Setup UI
        self.setup_ui()
        self.check_server_availability()
        self.update_system_info()

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_paths.update(config.get('paths', {}))
            except Exception:
                pass

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'paths': self.default_paths}, f, indent=4)
        except Exception:
            pass

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.php_tab = ttk.Frame(notebook)
        self.apache_tab = ttk.Frame(notebook)
        self.mariadb_tab = ttk.Frame(notebook)
        self.admin_tab = ttk.Frame(notebook)
        
        self.create_php_server_tab(self.php_tab)
        self.create_apache_server_tab(self.apache_tab)
        self.create_mariadb_server_tab(self.mariadb_tab)
        self.create_admin_tools_tab(self.admin_tab)
        
        notebook.add(self.php_tab, text="PHP Server")
        notebook.add(self.apache_tab, text="Apache")
        notebook.add(self.mariadb_tab, text="MariaDB")
        notebook.add(self.admin_tab, text="Tools")
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Server Log", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=False)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            height=8,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_message("Awan Server Lite started")

    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)

    def update_system_info(self):
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            cpu_color = "green" if cpu_percent < 50 else "orange" if cpu_percent < 80 else "red"
            
            # Memory usage
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            mem_total = mem.total / (1024 ** 3)
            mem_used = mem.used / (1024 ** 3)
            mem_color = "green" if mem_percent < 50 else "orange" if mem_percent < 80 else "red"
            
            # Update every 5 seconds
            self.root.after(5000, self.update_system_info)
        except:
            pass

    def check_server_availability(self):
        self.check_php_availability()
        self.check_apache_availability()
        self.check_mariadb_availability()

    def check_php_availability(self):
        possible_paths = [
            "php",
            "C:\\xampp\\php\\php.exe",
            "C:\\Program Files\\PHP\\php.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "PHP" in result.stdout:
                    self.default_paths['php'] = path
                    self.php_path_entry.delete(0, tk.END)
                    self.php_path_entry.insert(0, path)
                    self.log_message(f"PHP found: {path}")
                    return True
            except:
                continue
        
        self.log_message("Warning: PHP not found automatically")
        return False

    def check_apache_availability(self):
        possible_paths = [
            "httpd",
            "apache",
            "C:\\xampp\\apache\\bin\\httpd.exe",
            "C:\\Program Files\\Apache\\bin\\httpd.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "Apache" in result.stderr or "Apache" in result.stdout:
                    self.default_paths['apache'] = path
                    self.apache_path_entry.delete(0, tk.END)
                    self.apache_path_entry.insert(0, path)
                    self.log_message(f"Apache found: {path}")
                    return True
            except:
                continue
        
        self.log_message("Warning: Apache not found automatically")
        return False

    def check_mariadb_availability(self):
        possible_paths = [
            "mysql",
            "mariadb",
            "C:\\xampp\\mysql\\bin\\mysqld.exe",
            "C:\\Program Files\\MariaDB\\bin\\mysqld.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "MariaDB" in result.stdout or "MySQL" in result.stdout:
                    self.default_paths['mariadb'] = path
                    self.mariadb_path_entry.delete(0, tk.END)
                    self.mariadb_path_entry.insert(0, path)
                    self.log_message(f"MariaDB found: {path}")
                    return True
            except:
                continue
        
        self.log_message("Warning: MariaDB not found automatically")
        return False

    def create_php_server_tab(self, parent):
        self.php_tab = parent
        
        status_frame = ttk.Frame(parent, padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.php_status_label = ttk.Label(status_frame, text="Status: PHP Server Not Active")
        self.php_status_label.pack(side=tk.LEFT)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        self.php_start_btn = ttk.Button(control_frame, text="Start PHP", command=self.start_php_server)
        self.php_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.php_stop_btn = ttk.Button(control_frame, text="Stop PHP", command=self.stop_php_server, state=tk.DISABLED)
        self.php_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.php_open_browser_btn = ttk.Button(control_frame, text="Open Browser", command=self.open_php_in_browser)
        self.php_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))

        config_frame = ttk.LabelFrame(parent, text="PHP Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 5))

        host_frame = ttk.Frame(config_frame)
        host_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT)
        self.host_entry = ttk.Entry(host_frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)

        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = ttk.Entry(port_frame)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)

        doc_root_frame = ttk.Frame(config_frame)
        doc_root_frame.pack(fill=tk.X, pady=(0, 2))
        ttk.Label(doc_root_frame, text="Document Root:").pack(side=tk.LEFT)
        self.doc_root_entry = ttk.Entry(doc_root_frame)
        self.doc_root_entry.insert(0, os.getcwd())
        self.doc_root_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        ttk.Button(doc_root_frame, text="Browse", command=lambda: self.browse_directory(self.doc_root_entry)).pack(side=tk.LEFT, padx=(2, 0))

        php_path_frame = ttk.Frame(config_frame)
        php_path_frame.pack(fill=tk.X)
        ttk.Label(php_path_frame, text="PHP Path:").pack(side=tk.LEFT)
        self.php_path_entry = ttk.Entry(php_path_frame)
        self.php_path_entry.insert(0, self.default_paths['php'])
        self.php_path_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        ttk.Button(php_path_frame, text="Browse", command=lambda: self.browse_executable(self.php_path_entry)).pack(side=tk.LEFT, padx=(2, 0))

    def create_apache_server_tab(self, parent):
        self.apache_tab = parent
        
        status_frame = ttk.Frame(parent, padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.apache_status_label = ttk.Label(status_frame, text="Status: Apache Not Active")
        self.apache_status_label.pack(side=tk.LEFT)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        self.apache_start_btn = ttk.Button(control_frame, text="Start Apache", command=self.start_apache)
        self.apache_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_stop_btn = ttk.Button(control_frame, text="Stop Apache", command=self.stop_apache, state=tk.DISABLED)
        self.apache_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_open_browser_btn = ttk.Button(control_frame, text="Open Browser", command=self.open_apache_in_browser)
        self.apache_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))

        config_frame = ttk.LabelFrame(parent, text="Apache Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 5))

        apache_path_frame = ttk.Frame(config_frame)
        apache_path_frame.pack(fill=tk.X)
        ttk.Label(apache_path_frame, text="Apache Path:").pack(side=tk.LEFT)
        self.apache_path_entry = ttk.Entry(apache_path_frame)
        self.apache_path_entry.insert(0, self.default_paths['apache'])
        self.apache_path_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        ttk.Button(apache_path_frame, text="Browse", command=lambda: self.browse_executable(self.apache_path_entry)).pack(side=tk.LEFT, padx=(2, 0))

        conf_path_frame = ttk.Frame(config_frame)
        conf_path_frame.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(conf_path_frame, text="Config File:").pack(side=tk.LEFT)
        self.apache_conf_entry = ttk.Entry(conf_path_frame)
        self.apache_conf_entry.insert(0, "C:\\xampp\\apache\\conf\\httpd.conf")
        self.apache_conf_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        ttk.Button(conf_path_frame, text="Browse", command=lambda: self.browse_file(self.apache_conf_entry)).pack(side=tk.LEFT, padx=(2, 0))

    def create_mariadb_server_tab(self, parent):
        self.mariadb_tab = parent
        
        status_frame = ttk.Frame(parent, padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 5))
        self.mariadb_status_label = ttk.Label(status_frame, text="Status: MariaDB Not Active")
        self.mariadb_status_label.pack(side=tk.LEFT)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        self.mariadb_start_btn = ttk.Button(control_frame, text="Start MariaDB", command=self.start_mariadb)
        self.mariadb_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.mariadb_stop_btn = ttk.Button(control_frame, text="Stop MariaDB", command=self.stop_mariadb, state=tk.DISABLED)
        self.mariadb_stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        config_frame = ttk.LabelFrame(parent, text="MariaDB Configuration", padding="5")
        config_frame.pack(fill=tk.X, pady=(0, 5))

        mariadb_path_frame = ttk.Frame(config_frame)
        mariadb_path_frame.pack(fill=tk.X)
        ttk.Label(mariadb_path_frame, text="MariaDB Path:").pack(side=tk.LEFT)
        self.mariadb_path_entry = ttk.Entry(mariadb_path_frame)
        self.mariadb_path_entry.insert(0, self.default_paths['mariadb'])
        self.mariadb_path_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)
        ttk.Button(mariadb_path_frame, text="Browse", command=lambda: self.browse_executable(self.mariadb_path_entry)).pack(side=tk.LEFT, padx=(2, 0))

    def start_php_server(self):
        if self.is_php_running:
            messagebox.showwarning("Warning", "PHP Server already running!")
            return
        
        host = self.host_entry.get()
        port = self.port_entry.get()
        doc_root = self.doc_root_entry.get()
        php_path = self.php_path_entry.get()
        
        if not all([host, port, doc_root, php_path]):
            messagebox.showerror("Error", "All fields must be filled!")
            return
        
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Port must be a number between 1-65535!")
            return
        
        cmd = [php_path, "-S", f"{host}:{port}", "-t", doc_root]
        
        def run_server():
            try:
                self.php_server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.is_php_running = True
                self.php_start_btn.config(state=tk.DISABLED)
                self.php_stop_btn.config(state=tk.NORMAL)
                self.php_status_label.config(text="Status: PHP Server Active", foreground="green")
                
                while True:
                    output = self.php_server_process.stdout.readline()
                    if output == '' and self.php_server_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                self.is_php_running = False
                self.php_start_btn.config(state=tk.NORMAL)
                self.php_stop_btn.config(state=tk.DISABLED)
                self.php_status_label.config(text="Status: PHP Server Not Active", foreground="red")
                
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_php_running = False
        
        self.log_message(f"Starting PHP server on {host}:{port}")
        threading.Thread(target=run_server, daemon=True).start()

    def stop_php_server(self):
        if self.php_server_process and self.is_php_running:
            self.php_server_process.terminate()
            self.is_php_running = False
            self.php_start_btn.config(state=tk.NORMAL)
            self.php_stop_btn.config(state=tk.DISABLED)
            self.php_status_label.config(text="Status: PHP Server Not Active", foreground="red")
            self.log_message("PHP server stopped")

    def start_apache(self):
        if self.is_apache_running:
            messagebox.showwarning("Warning", "Apache already running!")
            return
        
        apache_path = self.apache_path_entry.get()
        conf_path = self.apache_conf_entry.get()
        
        if not apache_path:
            messagebox.showerror("Error", "Apache path must be specified!")
            return
        
        cmd = [apache_path, "-f", conf_path]
        
        def run_server():
            try:
                self.apache_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.is_apache_running = True
                self.apache_start_btn.config(state=tk.DISABLED)
                self.apache_stop_btn.config(state=tk.NORMAL)
                self.apache_status_label.config(text="Status: Apache Active", foreground="green")
                
                while True:
                    output = self.apache_process.stdout.readline()
                    if output == '' and self.apache_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                self.is_apache_running = False
                self.apache_start_btn.config(state=tk.NORMAL)
                self.apache_stop_btn.config(state=tk.DISABLED)
                self.apache_status_label.config(text="Status: Apache Not Active", foreground="red")
                
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_apache_running = False
        
        self.log_message("Starting Apache server")
        threading.Thread(target=run_server, daemon=True).start()

    def stop_apache(self):
        if self.apache_process and self.is_apache_running:
            self.apache_process.terminate()
            self.is_apache_running = False
            self.apache_start_btn.config(state=tk.NORMAL)
            self.apache_stop_btn.config(state=tk.DISABLED)
            self.apache_status_label.config(text="Status: Apache Not Active", foreground="red")
            self.log_message("Apache server stopped")

    def start_mariadb(self):
        if self.is_mariadb_running:
            messagebox.showwarning("Warning", "MariaDB already running!")
            return
        
        mariadb_path = self.mariadb_path_entry.get()
        
        if not mariadb_path:
            messagebox.showerror("Error", "MariaDB path must be specified!")
            return
        
        cmd = [mariadb_path]
        
        def run_server():
            try:
                self.mariadb_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                self.is_mariadb_running = True
                self.mariadb_start_btn.config(state=tk.DISABLED)
                self.mariadb_stop_btn.config(state=tk.NORMAL)
                self.mariadb_status_label.config(text="Status: MariaDB Active", foreground="green")
                
                while True:
                    output = self.mariadb_process.stdout.readline()
                    if output == '' and self.mariadb_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                self.is_mariadb_running = False
                self.mariadb_start_btn.config(state=tk.NORMAL)
                self.mariadb_stop_btn.config(state=tk.DISABLED)
                self.mariadb_status_label.config(text="Status: MariaDB Not Active", foreground="red")
                
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_mariadb_running = False
        
        self.log_message("Starting MariaDB server")
        threading.Thread(target=run_server, daemon=True).start()

    def stop_mariadb(self):
        if self.mariadb_process and self.is_mariadb_running:
            self.mariadb_process.terminate()
            self.is_mariadb_running = False
            self.mariadb_start_btn.config(state=tk.NORMAL)
            self.mariadb_stop_btn.config(state=tk.DISABLED)
            self.mariadb_status_label.config(text="Status: MariaDB Not Active", foreground="red")
            self.log_message("MariaDB server stopped")

    def open_php_in_browser(self):
        if not self.is_php_running:
            messagebox.showwarning("Warning", "PHP Server not running!")
            return
        
        host = self.host_entry.get()
        port = self.port_entry.get()
        webbrowser.open(f"http://{host}:{port}")

    def open_apache_in_browser(self):
        webbrowser.open("http://localhost")

    def browse_directory(self, entry_widget):
        dir_path = filedialog.askdirectory()
        if dir_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, dir_path)

    def browse_executable(self, entry_widget):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def browse_file(self, entry_widget):
        file_path = filedialog.askopenfilename()
        if file_path:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, file_path)

    def create_admin_tools_tab(self, parent):
        self.admin_tab = parent
        
        tools_frame = ttk.Frame(parent, padding="5")
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(tools_frame, text="Open CMD", command=self.open_cmd).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="Open PowerShell", command=self.open_powershell).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="Check Ports", command=self.check_used_ports).pack(fill=tk.X, pady=2)
        ttk.Button(tools_frame, text="System Info", command=self.show_system_info).pack(fill=tk.X, pady=2)

    def open_cmd(self):
        subprocess.Popen("cmd", creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.log_message("Opened CMD")

    def open_powershell(self):
        subprocess.Popen("powershell", creationflags=subprocess.CREATE_NEW_CONSOLE)
        self.log_message("Opened PowerShell")

    def check_used_ports(self):
        try:
            result = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Used ports:\n" + result.stdout)
        except:
            self.log_message("Failed to check ports")

    def show_system_info(self):
        try:
            info = f"""
            System Information:
            CPU: {psutil.cpu_percent()}% usage
            Memory: {psutil.virtual_memory().percent}% used
            Disk: {psutil.disk_usage('/').percent}% used
            """
            messagebox.showinfo("System Info", info)
        except:
            messagebox.showerror("Error", "Failed to get system information")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    
    app = ServerHost(root)
    root.mainloop()
def run_gui():
    root = tk.Tk()
    app = ServerHost(root)
    root.mainloop()