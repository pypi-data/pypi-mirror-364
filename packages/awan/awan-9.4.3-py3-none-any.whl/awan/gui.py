import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import subprocess
import threading
import os
import webbrowser
from datetime import datetime
import socket
import time
import json
import platform
import psutil
from PIL import Image, ImageTk
import ctypes
import shutil
import tempfile
import winshell
import matplotlib
from io import BytesIO
from PIL import Image
import wmi
import win32api
import win32api
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from PIL import Image, ImageDraw, ImageTk
import io
import contextlib
import re
import tempfile
import webbrowser
import sys

class ServerHost:
    def __init__(self, root):
        self.root = root
        self.root.title("Awan Server Host 9.0 - Enhanced 5 End")
        self.root.geometry("1100x750")
        self.root.resizable(True, True)
        icon_path = None
        for root_dir, dirs, files in os.walk(os.getcwd()):
            if "awan.ico" in files:
                icon_path = os.path.join(root_dir, "awan.ico")
            break
        if icon_path:
            try:
                self.root.iconbitmap(icon_path)
            except Exception as e:
                print(f"Failed to set icon: {e}")

        # Server processes
        self.php_server_process = None
        self.apache_process = None
        self.mariadb_process = None
        self.filezilla_process = None
        self.mercury_process = None
        self.tomcat_process = None
        self.laragon_process = None
        self.flutter_process = None
        self.android_emulator_process = None
        
        # Docker status flags
        self.docker_open_process = None
        
        # Server status flags
        self.is_php_running = False
        self.is_apache_running = False
        self.is_mariadb_running = False
        self.is_filezilla_running = False
        self.is_mercury_running = False
        self.is_tomcat_running = False
        self.is_laragon_running = False
        self.is_flutter_running = False
        self.is_emulator_running = False
        self.id_docker_running = False
        
        # Default paths
        self.default_paths = {
            'php': "",
            'apache': "",
            'mariadb': "",
            'filezilla': "",
            'mercury': "",
            'tomcat': "",
            'laragon': "",
            'composer': "",
            'laravel': "",
            'flutter': "",
            'android_sdk': "",
            'emulator': "",
            'docker': "",
            'node': "",
            'password_sql': "",
            'iobit_unlocker': "",
            'go': self.find_go_executable(),
        }
        
        # Config file
        self.config_file = "server_host_config.json"
        
        # Load configuration
        self.load_config()
        
        # Setup UI
        self.setup_ui()
        
        # Check server availability
        self.check_server_availability()
        self.update_system_info()
    
    def load_config(self):
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.default_paths.update(config.get('paths', {}))
            except Exception as e:
                print(f"Error loading config: {e}")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump({'paths': self.default_paths}, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_ui(self):
        """Setup the main user interface"""
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Logo and title
        logo_frame = ttk.Frame(header_frame)
        logo_frame.pack(side=tk.LEFT)
        
        try:
            logo_img = Image.open("awan.ico").resize((30, 30))
            self.logo_photo = ImageTk.PhotoImage(logo_img)
            ttk.Label(logo_frame, image=self.logo_photo).pack(side=tk.LEFT, padx=(0, 5))
        except:
            pass
        
        ttk.Label(header_frame, text="Awan Server - Enhanced 5 End 🔑", style='Header.TLabel').pack(side=tk.LEFT)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create all tabs
        self.create_php_server_tab(ttk.Frame(notebook))
        self.create_apache_server_tab(ttk.Frame(notebook))
        self.create_mariadb_server_tab(ttk.Frame(notebook))
        self.create_filezilla_server_tab(ttk.Frame(notebook))
        self.create_mercury_server_tab(ttk.Frame(notebook))
        self.create_tomcat_server_tab(ttk.Frame(notebook))
        self.create_laragon_tab(ttk.Frame(notebook))
        self.create_laravel_tab(ttk.Frame(notebook))
        self.create_flutter_tab(ttk.Frame(notebook))
        self.create_android_tab(ttk.Frame(notebook))
        self.create_admin_tools_tab(ttk.Frame(notebook))
        self.create_terminal_tab(ttk.Frame(notebook))
        self.create_terminal_tab2(ttk.Frame(notebook))
        self.create_terminal_tab3(ttk.Frame(notebook))
        self.create_docker_tab(ttk.Frame(notebook))
        self.create_go_tab(ttk.Frame(notebook))
        self.create_encryption_tab(ttk.Frame(notebook))
        
        # Add tabs to notebook
        try:
            tab_icon_img = Image.open("awan.ico").resize((16, 16))
            self.tab_icon = ImageTk.PhotoImage(tab_icon_img)
        except Exception:
            self.tab_icon = None

        notebook.add(self.php_tab, text="PHP Server", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.apache_tab, text="Apache", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.mariadb_tab, text="MariaDB", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.filezilla_tab, text="FileZilla", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.mercury_tab, text="Mercury", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.tomcat_tab, text="Tomcat", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.nodejs_tab, text="Nodejs", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.laravel_tab, text="Laravel", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.flutter_tab, text="Flutter", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.android_tab, text="Android", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.admin_tab, text="Tools", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.terminal_tab, text="Terminal", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.terminal_tab2, text="Htmx", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.terminal_tab3, text="Py", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.docker_tab, text="Docker", image=self.tab_icon, compound=tk.LEFT) 
        notebook.add(self.go_tab, text="Go", image=self.tab_icon, compound=tk.LEFT)
        notebook.add(self.encryption_tab, text="key", image=self.tab_icon, compound=tk.LEFT)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="Server Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=False, pady=(10, 0))
        try:
            icon_img = Image.open("awan.ico").resize((20, 20))
            self.log_icon = ImageTk.PhotoImage(icon_img)
            log_icon_label = ttk.Label(log_frame, image=self.log_icon)
            log_icon_label.pack(side=tk.LEFT, padx=(0, 5), pady=(0, 5))
        except Exception as e:
            self.log_icon = None 

        self.log_text = scrolledtext.ScrolledText(
            log_frame, 
            wrap=tk.WORD, 
            width=100, 
            height=10,
            font=('Consolas', 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log_message("Awan Server Enhanced 3 End dimulai")
        
        sys_info_frame = ttk.Frame(header_frame)
        sys_info_frame.pack(side=tk.RIGHT)
        
        self.cpu_label = ttk.Label(sys_info_frame, text="CPU: Sacha Checking CPU", font=('Segoe UI', 8))
        self.cpu_label.pack(anchor=tk.E)
        self.mem_label = ttk.Label(sys_info_frame, text="RAM: Sacha Checking RAM", font=('Segoe UI', 8))
        self.mem_label.pack(anchor=tk.E)
        self.disk_label = ttk.Label(sys_info_frame, text="Disk: Sacha Checking Disk", font=('Segoe UI', 8))
        self.disk_label.pack(anchor=tk.E)

        # --- Button for popup bar/statistics like Task Manager ---
        self.stat_btn = ttk.Button(sys_info_frame, text="Statistik Lengkap", command=self.show_full_stats)
        self.stat_btn.pack(anchor=tk.E, pady=(5, 0))
        
    
    def find_go_executable(self):
        """Try to find Go executable in common locations"""
        go_path = shutil.which('go')
        if go_path:
            return go_path
        
        # Check common installation paths
        common_paths = [
            'C:\\Go\\bin\\go.exe',
            'C:\\Program Files\\Go\\bin\\go.exe',
        ]
        
        for path in common_paths:
            if os.path.isfile(path):
                return path
        
        return ''

    def update_system_info(self):
        """Update system information display with color status"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            if cpu_percent < 50:
                cpu_color = "green"
            elif cpu_percent < 80:
                cpu_color = "orange"
            else:
                cpu_color = "red"
            self.cpu_label.config(text=f"CPU: {cpu_percent}%", foreground=cpu_color)
            
            # Memory usage
            mem = psutil.virtual_memory()
            mem_percent = mem.percent
            mem_total = mem.total / (1024 ** 3)
            mem_used = mem.used / (1024 ** 3)
            if mem_percent < 50:
                mem_color = "green"
            elif mem_percent < 80:
                mem_color = "orange"
            else:
                mem_color = "red"
            self.mem_label.config(
            text=f"RAM: {mem_percent:.1f}% ({mem_used:.1f}GB/{mem_total:.1f}GB)",
            foreground=mem_color
            )
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_total = disk.total / (1024 ** 3)
            disk_used = disk.used / (1024 ** 3)
            if disk_percent < 50:
                disk_color = "green"
            elif disk_percent < 80:
                disk_color = "orange"
            else:
                disk_color = "red"
            self.disk_label.config(
            text=f"Disk: {disk_percent:.1f}% ({disk_used:.1f}GB/{disk_total:.1f}GB)",
            foreground=disk_color
            )
            
            # Update every 2 seconds
            self.root.after(2000, self.update_system_info)
        except:
            pass

    def show_full_stats(self):
        """Show popup with full bar/statistics and stock-like chart, like Task Manager, plus temperature, uptime, and network info."""
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        # Gather stats
        cpu_percent = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        try:
            battery = psutil.sensors_battery()
        except Exception:
            battery = None

        # Temperatur (CPU/GPU)
        temp_lines = []
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for name, entries in temps.items():
                    for entry in entries:
                        label = entry.label or name
                        temp_lines.append(f"{label}: {entry.current:.1f}°C")
            else:
                temp_lines.append("Temperatur: Tidak tersedia")
        except Exception:
            temp_lines.append("Temperatur: Tidak tersedia")

        # Uptime
        try:
            boot_time = psutil.boot_time()
            uptime_sec = int(time.time() - boot_time)
            hours, rem = divmod(uptime_sec, 3600)
            minutes, seconds = divmod(rem, 60)
            uptime_str = f"{hours} jam {minutes} menit {seconds} detik"
        except Exception:
            uptime_str = "Tidak tersedia"

        # Network info
        try:
            net = psutil.net_io_counters()
            net_sent = net.bytes_sent / (1024 ** 2)
            net_recv = net.bytes_recv / (1024 ** 2)
            net_lines = [
                f"Network Sent: {net_sent:.2f} MB",
                f"Network Received: {net_recv:.2f} MB"
            ]
        except Exception:
            net_lines = ["Network: Tidak tersedia"]

        # Create popup window
        top = tk.Toplevel(self.root)
        top.title("Statistik Lengkap Sistem")
        top.geometry("600x800")
        top.resizable(False, False)

        # --- Bar charts for CPU, RAM, Disk ---
        fig, axs = plt.subplots(2, 1, figsize=(6, 5), gridspec_kw={'height_ratios': [2, 3]})
        fig.subplots_adjust(hspace=0.5)

        # Bar chart (like Task Manager)
        labels = ['CPU', 'RAM', 'Disk']
        values = [cpu_percent, mem.percent, disk.percent]
        bar_colors = ['#4caf50', '#2196f3', '#ff9800']
        axs[0].bar(labels, values, color=bar_colors)
        axs[0].set_ylim(0, 100)
        axs[0].set_ylabel('Usage (%)')
        axs[0].set_title('Penggunaan Resource (Bar Chart)')
        for i, v in enumerate(values):
            axs[0].text(i, v + 2, f"{v:.1f}%", ha='center', fontweight='bold')

        # --- Stock-like line chart (simulate for demo) ---
        stock_x = list(range(30))
        stock_cpu = [cpu_percent + random.uniform(-10, 10) for _ in stock_x]
        stock_mem = [mem.percent + random.uniform(-5, 5) for _ in stock_x]
        stock_disk = [disk.percent + random.uniform(-3, 3) for _ in stock_x]
        axs[1].plot(stock_x, stock_cpu, label='CPU', color='#4caf50')
        axs[1].plot(stock_x, stock_mem, label='RAM', color='#2196f3')
        axs[1].plot(stock_x, stock_disk, label='Disk', color='#ff9800')
        axs[1].set_ylim(0, 100)
        axs[1].set_xlabel('Waktu (simulasi)')
        axs[1].set_ylabel('Usage (%)')
        axs[1].set_title('Grafik Statistik')
        axs[1].legend()

        # Render matplotlib figure to Tkinter
        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        canvas.get_tk_widget().pack(pady=10)

        # --- Keterangan lengkap ---
        info_lines = [
            f"CPU Usage: {cpu_percent:.1f}%",
            f"RAM Usage: {mem.percent:.1f}% ({mem.used // (1024 ** 2)} MB / {mem.total // (1024 ** 2)} MB)",
            f"Disk Usage: {disk.percent:.1f}% ({disk.used // (1024 ** 3)} GB / {disk.total // (1024 ** 3)} GB)",
        ]
        if battery:
            info_lines.append(f"Battery: {battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}")
        else:
            info_lines.append("Battery: Tidak tersedia")

        uname = platform.uname()
        info_lines += [
            f"Komputer: {uname.node}",
            f"Sistem Operasi: {uname.system} {uname.release}",
            f"Processor: {uname.processor}",
            f"Uptime: {uptime_str}",
        ]
        info_lines += temp_lines
        info_lines += net_lines

        info_label = tk.Label(top, text="\n".join(info_lines), font=("Segoe UI", 10), justify=tk.LEFT)
        info_label.pack(pady=(10, 0), anchor=tk.W, padx=10)

        # --- Gambar ilustrasi (gunakan awan.ico jika ada) ---
        try:
            img = Image.open("awan.ico").resize((64, 64))
            photo = ImageTk.PhotoImage(img)
            img_label = ttk.Label(top, image=photo)
            img_label.image = photo
            img_label.pack(pady=(10, 0))
        except Exception:
            pass

        # --- Close button ---
        close_btn = ttk.Button(top, text="Tutup", command=top.destroy)
        close_btn.pack(pady=(10, 10))
    
    def check_server_availability(self):
        """Check for available servers on the system"""
        self.check_php_availability()
        self.check_apache_availability()
        self.check_mariadb_availability()
        self.check_filezilla_availability()
        self.check_mercury_availability()
        self.check_tomcat_availability()
        self.check_nodejs_availability()
        self.check_composer_availability()
        self.check_flutter_availability()
        self.check_android_sdk_availability()
    
    def check_php_availability(self):
        """Check if PHP is available"""
        possible_paths = [
            "C:\\xampp\\awanserver\\php\\php.exe",
            "C:\\Program Files\\PHP\\php.exe",
            "C:\\Program Files (x86)\\PHP\\php.exe",
            "C:\\laragon\\bin\\php\\php.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "PHP" in result.stdout:
                    self.default_paths['php'] = path
                    self.php_path_entry.delete(0, tk.END)
                    self.php_path_entry.insert(0, path)
                    self.log_message(f"PHP ditemukan di: {path}")
                    self.log_message(f"Versi PHP: {result.stdout.splitlines()[0]}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log_message("Peringatan: PHP tidak ditemukan secara otomatis")
        return False
    
    def check_apache_availability(self):
        """Check if Apache is available"""
        possible_paths = [
            "httpd",
            "apache",
            "C:\\xampp\\apache\\bin\\httpd.exe",
            "C:\\Program Files\\Apache Software Foundation\\Apache2.4\\bin\\httpd.exe",
            "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.4\\bin\\httpd.exe",
            "C:\\laragon\\bin\\apache\\bin\\httpd.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "Apache" in result.stderr or "Apache" in result.stdout:
                    self.default_paths['apache'] = path
                    self.apache_path_entry.delete(0, tk.END)
                    self.apache_path_entry.insert(0, path)
                    self.log_message(f"Apache ditemukan di: {path}")
                    version_line = result.stderr.splitlines()[0] if "Apache" in result.stderr else result.stdout.splitlines()[0]
                    self.log_message(f"Versi Apache: {version_line}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log_message("Peringatan: Apache tidak ditemukan secara otomatis")
        return False
    
    def check_mariadb_availability(self):
        """Check if MariaDB/MySQL is available"""
        possible_paths = [
            "mysqld",
            "C:\\xampp\\mysql\\bin\\mysqld.exe",
            "C:\\Program Files\\MariaDB\\bin\\mysqld.exe",
            "C:\\Program Files\\MySQL\\MySQL Server\\bin\\mysqld.exe",
            "C:\\laragon\\bin\\mysql\\bin\\mysqld.exe",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "mysqld" in result.stdout or "MariaDB" in result.stdout:
                    self.default_paths['mariadb'] = path
                    self.mariadb_path_entry.delete(0, tk.END)
                    self.mariadb_path_entry.insert(0, path)
                    self.log_message(f"MariaDB/MySQL ditemukan di: {path}")
                    self.log_message(f"Versi: {result.stdout.splitlines()[0]}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log_message("Peringatan: MariaDB/MySQL tidak ditemukan secara otomatis")
        return False
    
    def check_filezilla_availability(self):
        """Check if FileZilla Server is available"""
        possible_paths = [
            "C:\\Program Files\\FileZilla Server\\FileZilla Server.exe",
            "C:\\Program Files (x86)\\FileZilla Server\\FileZilla Server.exe",
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                self.default_paths['filezilla'] = path
                self.filezilla_path_entry.delete(0, tk.END)
                self.filezilla_path_entry.insert(0, path)
                self.log_message(f"FileZilla Server ditemukan di: {path}")
                return True
        
        self.log_message("Peringatan: FileZilla Server tidak ditemukan secara otomatis")
        return False
    
    def check_mercury_availability(self):
        """Check if Mercury Mail Server is available"""
        possible_paths = [
            "C:\\xampp\\MercuryMail\\MERCURY.EXE",
            "C:\\Program Files\\Mercury\\MERCURY.EXE",
            "C:\\Program Files (x86)\\Mercury\\MERCURY.EXE",
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                self.default_paths['mercury'] = path
                self.mercury_path_entry.delete(0, tk.END)
                self.mercury_path_entry.insert(0, path)
                self.log_message(f"Mercury Mail Server ditemukan di: {path}")
                return True
        
        self.log_message("Peringatan: Mercury Mail Server tidak ditemukan secara otomatis")
        return False
    
    def check_tomcat_availability(self):
        """Check if Apache Tomcat is available (prefer catalina_start.bat for running)"""
        possible_paths = [
            "C:\\xampp\\tomcat\\catalina_start.bat",
            "C:\\Program Files\\Apache Software Foundation\\Tomcat\\bin\\catalina_start.bat",
            "C:\\Program Files (x86)\\Apache Software Foundation\\Tomcat\\bin\\catalina_start.bat",
        ]

        for path in possible_paths:
            if os.path.isfile(path):
                self.default_paths['tomcat'] = path
                self.tomcat_path_entry.delete(0, tk.END)
                self.tomcat_path_entry.insert(0, path)
                self.log_message(f"Apache Tomcat (catalina_start.bat) ditemukan di: {path}")
                return True

        self.log_message("Peringatan: Apache Tomcat (catalina_start.bat) tidak ditemukan secara otomatis")
        return False
    
    def check_nodejs_availability(self):
        """Check if Node.js is available"""
        possible_paths = [
            "C:\\xampp\\nodejs\\node.exe",
            "C:\\Program Files\\nodejs\\node.exe",
            "C:\\Program Files (x86)\\nodejs\\node.exe",
        ]

        for path in possible_paths:
            try:
                result = subprocess.run([path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if result.stdout.startswith("v"):
                    self.default_paths['node'] = path
                    self.node_path_entry.delete(0, tk.END)
                    self.node_path_entry.insert(0, path)
                    self.log_message(f"Node.js ditemukan di: {path}")
                    self.log_message(f"Versi Node.js: {result.stdout.strip()}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue

        self.log_message("Peringatan: Node.js tidak ditemukan secara otomatis")
        return False
    
    def check_composer_availability(self):
        """Check if Composer is available"""
        possible_paths = [
            "composer",
            "C:\\xampp\\ComposerSetup\\bin\\composer.phar",
            "C:\\ProgramData\\ComposerSetup\\bin\\composer.phar",
            "C:\\xampp\\php\\composer.phar",
            "C:\\laragon\\bin\\composer\\composer.phar",
        ]
        
        for path in possible_paths:
            try:
                if path.endswith('.phar'):
                    result = subprocess.run(['php', path, '--version'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    result = subprocess.run([path, '--version'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                if "Composer" in result.stdout:
                    self.default_paths['composer'] = path
                    self.log_message(f"Composer ditemukan di: {path}")
                    self.log_message(f"Versi Composer: {result.stdout.splitlines()[0]}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log_message("Peringatan: Composer tidak ditemukan secara otomatis")
        return False
    
    def check_flutter_availability(self):
        """Check if Flutter is available"""
        possible_paths = [
            "flutter",
            os.path.expandvars("%LOCALAPPDATA%\\flutter\\bin\\flutter.bat"),
            "C:\\src\\flutter\\bin\\flutter.bat",
            "C:\\flutter\\bin\\flutter.bat",
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if "Flutter" in result.stdout:
                    self.default_paths['flutter'] = path
                    self.flutter_path_entry.delete(0, tk.END)
                    self.flutter_path_entry.insert(0, path)
                    self.log_message(f"Flutter ditemukan di: {path}")
                    version_line = result.stdout.splitlines()[0]
                    self.log_message(f"Versi Flutter: {version_line}")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                continue
        
        self.log_message("Peringatan: Flutter tidak ditemukan secara otomatis")
        return False
    
    def check_android_sdk_availability(self):
        """Check if Android SDK is available with better auto-detection"""
        # Check for Android SDK
        possible_sdk_paths = [
            os.path.expandvars("%ANDROID_HOME%"),
            os.path.expandvars("%LOCALAPPDATA%\\Android\\Sdk"),
            "C:\\Android\\Sdk",
            os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Android", "Sdk"),
            "C:\\Program Files\\Android\\Android Studio\\Sdk",
            "C:\\Program Files (x86)\\Android\\android-sdk",
        ]
        
        sdk_found = False
        for path in possible_sdk_paths:
            if os.path.isdir(path):
                self.default_paths['android_sdk'] = path
                self.android_sdk_entry.delete(0, tk.END)
                self.android_sdk_entry.insert(0, path)
                self.log_message(f"Android SDK ditemukan di: {path}")
                sdk_found = True
                break
        
        # Check for emulator
        possible_emulator_paths = [
            os.path.join(self.default_paths['android_sdk'], "emulator", "emulator.exe"),
            os.path.expandvars("%ANDROID_HOME%\\emulator\\emulator.exe"),
            os.path.expandvars("%LOCALAPPDATA%\\Android\\Sdk\\emulator\\emulator.exe"),
            os.path.expandvars("C:\\xampp\\Android\\Sdk\\emulator\\emulator.exe"),
            "C:\\Android\\Sdk\\emulator\\emulator.exe",
            "emulator",
        ]
        
        emulator_found = False
        for path in possible_emulator_paths:
            if os.path.isfile(path):
                self.default_paths['emulator'] = path
                self.emulator_path_entry.delete(0, tk.END)
                self.emulator_path_entry.insert(0, path)
                self.log_message(f"Android Emulator ditemukan di: {path}")
                emulator_found = True
                break
        
        if not sdk_found:
            self.log_message("Peringatan: Android SDK tidak ditemukan secara otomatis")
        
        if not emulator_found:
            self.log_message("Peringatan: Android Emulator tidak ditemukan secara otomatis")
        
        return sdk_found
    
    def create_flutter_tab(self, parent):
        """Create Flutter development tab with APK building capabilities"""
        self.flutter_tab = parent

        # Status Frame
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.flutter_status_label = ttk.Label(status_frame, text="Status: Flutter Server Tidak Aktif", style='Status.TLabel')
        self.flutter_status_label.pack(side=tk.LEFT)

        # Control Frame for Server Operations
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create tooltip for buttons
        self.tooltips = {}
        
        # Start Server button
        self.flutter_start_btn = ttk.Button(control_frame, text="Start Flutter Server", command=self.start_flutter_server)
        self.flutter_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['start'] = self.create_tooltip(self.flutter_start_btn, "Mulai server Flutter development")
        
        # Stop Server button
        self.flutter_stop_btn = ttk.Button(control_frame, text="Stop Flutter Server", command=self.stop_flutter_server, state=tk.DISABLED)
        self.flutter_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['stop'] = self.create_tooltip(self.flutter_stop_btn, "Hentikan server Flutter development")
        
        # Open Browser button
        self.flutter_open_browser_btn = ttk.Button(control_frame, text="Buka di Browser", command=self.open_flutter_in_browser)
        self.flutter_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['browser'] = self.create_tooltip(self.flutter_open_browser_btn, "Buka aplikasi di browser default")
        
        # Run on Android Emulator button
        self.flutter_run_android_btn = ttk.Button(control_frame, text="Run on Android Emulator", command=self.run_flutter_android)
        self.flutter_run_android_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['android'] = self.create_tooltip(self.flutter_run_android_btn, "Jalankan aplikasi di emulator Android")

        # APK Building Frame
        apk_frame = ttk.LabelFrame(parent, text="Build APK", padding="5")  # Padding diperkecil dari "10" ke "5"
        apk_frame.pack(fill=tk.X, pady=(5, 5))  # pady diperkecil dari (10, 5) ke (5, 5)

        # Icon Selection
        icon_frame = ttk.Frame(apk_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 2))  # pady diperkecil dari (0, 5) ke (0, 3)

        ttk.Label(icon_frame, text="Icon Path:").pack(side=tk.LEFT)
        self.flutter_icon_path = tk.StringVar()
        self.flutter_icon_entry = ttk.Entry(icon_frame, textvariable=self.flutter_icon_path)
        self.flutter_icon_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(2, 2))  # padx diperkecil dari (5,5) ke (3,3)

        self.flutter_icon_browse_btn = ttk.Button(icon_frame, text="Browse...", command=self.browse_flutter_icon)
        self.flutter_icon_browse_btn.pack(side=tk.LEFT)
        self.tooltips['icon'] = self.create_tooltip(self.flutter_icon_browse_btn, "Pilih file icon (PNG) untuk aplikasi")

        # APK Build Options
        build_options_frame = ttk.Frame(apk_frame)
        build_options_frame.pack(fill=tk.X, pady=(2, 0))  # pady diperkecil dari (5,0) ke (3,0)

        # Build APK button
        self.flutter_build_apk_btn = ttk.Button(build_options_frame, text="Build APK", command=self.build_flutter_apk)
        self.flutter_build_apk_btn.pack(side=tk.LEFT, padx=(0, 2))  # padx diperkecil dari (0,5) ke (0,3)
        self.tooltips['build'] = self.create_tooltip(self.flutter_build_apk_btn, "Buat file APK untuk instalasi di Android")

        # Install APK button
        self.flutter_install_apk_btn = ttk.Button(build_options_frame, text="Install APK", command=self.install_flutter_apk)
        self.flutter_install_apk_btn.pack(side=tk.LEFT)
        self.tooltips['install'] = self.create_tooltip(self.flutter_install_apk_btn, "Install APK ke perangkat Android yang terhubung")

        # Output Frame
        output_frame = ttk.LabelFrame(parent, text="Output", padding="3")  # Padding diperkecil dari "5" ke "3"
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))  # pady diperkecil dari (5,0) ke (3,0)

        self.flutter_output = tk.Text(output_frame, wrap=tk.WORD, height=2)  # height diperkecil dari 5 ke 3
        self.flutter_output.pack(fill=tk.BOTH, expand=True)
        

        # Pub Get button with tooltip
        def flutter_pub_get():
            project_dir = self.flutter_project_entry.get()
            flutter_path = self.flutter_path_entry.get()
            if not project_dir or not os.path.isdir(project_dir):
                messagebox.showerror("Error", "Project directory tidak valid!")
                return
            if not flutter_path or not os.path.isfile(flutter_path):
                messagebox.showerror("Error", "Path Flutter tidak valid!")
                return
            
            cmd = [flutter_path, "pub", "get"]
            self.log_message(f"Menjalankan: {' '.join(cmd)}")
            
            def run():
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    output = result.stdout + ("\n" + result.stderr if result.stderr else "")
                    self.root.after(0, lambda: messagebox.showinfo("Flutter Pub Get", output))
                    self.root.after(0, self.log_message, "Flutter pub get selesai")
                except Exception as e:
                    self.root.after(0, self.log_message, f"Error pub get: {str(e)}")
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
            threading.Thread(target=run, daemon=True).start()
        
        self.flutter_pub_get_btn = ttk.Button(control_frame, text="Pub Get", command=flutter_pub_get)
        self.flutter_pub_get_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['pubget'] = self.create_tooltip(self.flutter_pub_get_btn, "Jalankan 'flutter pub get' untuk mendapatkan dependencies")

        # Open in VS Code button with tooltip
        def open_flutter_vscode():
            project_dir = self.flutter_project_entry.get()
            if not project_dir or not os.path.isdir(project_dir):
                messagebox.showerror("Error", "Project directory tidak valid!")
                return
            try:
                subprocess.Popen(["code", project_dir], creationflags=subprocess.CREATE_NO_WINDOW)
                self.log_message("Membuka project Flutter di VS Code")
            except Exception as e:
                self.log_message(f"Gagal membuka VS Code: {str(e)}")
                messagebox.showerror("Error", f"Gagal membuka VS Code: {str(e)}")
        
        self.flutter_vscode_btn = ttk.Button(control_frame, text="Open in VS Code", command=open_flutter_vscode)
        self.flutter_vscode_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['vscode'] = self.create_tooltip(self.flutter_vscode_btn, "Buka project di Visual Studio Code")

        # Open in Explorer button with tooltip
        def open_flutter_explorer():
            project_dir = self.flutter_project_entry.get()
            if not project_dir or not os.path.isdir(project_dir):
                messagebox.showerror("Error", "Project directory tidak valid!")
                return
            os.startfile(project_dir)
            self.log_message("Membuka project Flutter di Explorer")
        
        self.flutter_explorer_btn = ttk.Button(control_frame, text="Open in Explorer", command=open_flutter_explorer)
        self.flutter_explorer_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['explorer'] = self.create_tooltip(self.flutter_explorer_btn, "Buka folder project di File Explorer")

        # Doctor button with tooltip
        def flutter_doctor():
            flutter_path = self.flutter_path_entry.get()
            if not flutter_path or not os.path.isfile(flutter_path):
                messagebox.showerror("Error", "Path Flutter tidak valid!")
                return
            
            cmd = [flutter_path, "doctor"]
            self.log_message(f"Menjalankan: {' '.join(cmd)}")
            
            def run():
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    output = result.stdout + ("\n" + result.stderr if result.stderr else "")
                    self.root.after(0, lambda: messagebox.showinfo("Flutter Doctor", output))
                    self.root.after(0, self.log_message, "Flutter doctor selesai")
                except Exception as e:
                    self.root.after(0, self.log_message, f"Error flutter doctor: {str(e)}")
                    self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            
            threading.Thread(target=run, daemon=True).start()
        
        self.flutter_doctor_btn = ttk.Button(control_frame, text="Doctor", command=flutter_doctor)
        self.flutter_doctor_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.tooltips['doctor'] = self.create_tooltip(self.flutter_doctor_btn, "Jalankan 'flutter doctor' untuk memeriksa lingkungan development")
        
        # Configuration section
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Flutter", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        host_frame = ttk.Frame(config_frame)
        host_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT)
        self.flutter_host_entry = ttk.Entry(host_frame)
        self.flutter_host_entry.insert(0, "localhost")
        self.flutter_host_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.flutter_port_entry = ttk.Entry(port_frame)
        self.flutter_port_entry.insert(0, "8080")
        self.flutter_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        project_frame = ttk.Frame(config_frame)
        project_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(project_frame, text="Project Directory:").pack(side=tk.LEFT)
        self.flutter_project_entry = ttk.Entry(project_frame)
        self.flutter_project_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(project_frame, text="Browse...", command=lambda: self.browse_directory(self.flutter_project_entry))
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        flutter_path_frame = ttk.Frame(config_frame)
        flutter_path_frame.pack(fill=tk.X)
        ttk.Label(flutter_path_frame, text="Flutter Path:").pack(side=tk.LEFT)
        self.flutter_path_entry = ttk.Entry(flutter_path_frame)
        self.flutter_path_entry.insert(0, self.default_paths['flutter'])
        self.flutter_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        flutter_browse_btn = ttk.Button(flutter_path_frame, text="Browse...", command=lambda: self.browse_executable(self.flutter_path_entry))
        flutter_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Project creation section
        project_creation_frame = ttk.LabelFrame(parent, text="Buat Project Flutter", padding="10")
        project_creation_frame.pack(fill=tk.X, pady=(0, 10))
        
        project_name_frame = ttk.Frame(project_creation_frame)
        project_name_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(project_name_frame, text="Nama Project:").pack(side=tk.LEFT)
        self.new_flutter_project_entry = ttk.Entry(project_name_frame)
        self.new_flutter_project_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        project_dir_frame = ttk.Frame(project_creation_frame)
        project_dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(project_dir_frame, text="Lokasi:").pack(side=tk.LEFT)
        self.new_flutter_dir_entry = ttk.Entry(project_dir_frame)
        self.new_flutter_dir_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(project_dir_frame, text="Browse...", command=lambda: self.browse_directory(self.new_flutter_dir_entry))
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        create_btn = ttk.Button(project_creation_frame, text="Buat Project Flutter", command=self.create_flutter_project)
        create_btn.pack(fill=tk.X)
        self.tooltips['create'] = self.create_tooltip(create_btn, "Buat project Flutter baru dengan nama yang ditentukan")

    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        
        label = ttk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, padding=5)
        label.pack()
        
        def enter(event):
            x = widget.winfo_rootx() + widget.winfo_width() + 5
            y = widget.winfo_rooty()
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        
        def leave(event):
            tooltip.withdraw()
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        
        return tooltip
    
    def browse_flutter_icon(self):
        """Open file dialog to select icon file"""
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=(("PNG files", "*.png"), ("All files", "*.*"))
        )
        if file_path:
            self.flutter_icon_path.set(file_path)

    def build_flutter_apk(self):
        """Build Flutter APK with custom icon"""
        if not self.check_dependencies():
            self.show_path_help()  # Show help dialog if dependencies are missing
            return
        if not os.path.exists("pubspec.yaml"):
            self.log_output("Error: Not in a Flutter project directory (pubspec.yaml not found)")
            return
        icon_path = self.flutter_icon_path.get()
        
        if icon_path:
            # Create android resources directory if it doesn't exist
            res_dir = os.path.join("android", "app", "src", "main", "res")
            os.makedirs(res_dir, exist_ok=True)
            
            # Copy icon to all mipmap directories
            try:
                for density in ["mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", 
                                "mipmap-xxhdpi", "mipmap-xxxhdpi"]:
                    dest_dir = os.path.join(res_dir, density)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.copy2(icon_path, os.path.join(dest_dir, "ic_launcher.png"))
                self.log_output("Icon copied to all density folders")
            except Exception as e:
                self.log_output(f"Error copying icon: {str(e)}")
                return
        
        # Build APK command
        build_command = "flutter build apk --release"
        self.log_output("Building APK...")
        
        # Run build command in background
        threading.Thread(target=self.run_flutter_command, args=(build_command,), daemon=True).start()
        
    def find_flutter():
        """Try to find Flutter executable in common locations"""
        common_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools"),
            os.path.join("C:", "src", "flutter", "bin"),
            os.path.join(os.environ.get("ProgramFiles", ""), "flutter", "bin"),
        ]
        
        for path in common_paths:
            flutter_path = os.path.join(path, "flutter.exe")
            if os.path.exists(flutter_path):
                return flutter_path
        return None

    def find_adb():
        """Try to find ADB executable in common locations"""
        common_paths = [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Android", "Sdk", "platform-tools"),
            os.path.join(os.environ.get("ProgramFiles", ""), "Android", "Android Studio", "platform-tools"),
        ]
        
        for path in common_paths:
            adb_path = os.path.join(path, "adb.exe")
            if os.path.exists(adb_path):
                return adb_path
        return None
        
    def check_dependencies(self):
        """Check if Flutter and ADB are available with better error handling"""
        try:
            # Check Flutter
            flutter_check = subprocess.run(
                ["flutter", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True  # Add shell=True for Windows
            )
            if flutter_check.returncode != 0:
                raise Exception("Flutter not found or not working")
            
            # Check ADB
            adb_check = subprocess.run(
                ["adb", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=True  # Add shell=True for Windows
            )
            if adb_check.returncode != 0:
                raise Exception("ADB not found or not working")
                
            return True
            
        except Exception as e:
            self.log_output("Dependency check failed:")
            self.log_output(str(e))
            self.log_output("\nPlease ensure:")
            self.log_output("1. Flutter is installed and added to PATH")
            self.log_output("2. Android SDK is installed and platform-tools (contains adb) is in PATH")
            self.log_output("3. On Windows, you may need to restart after adding to PATH")
            return False
        
    def show_path_help(self):
        """Show help message for setting up PATH"""
        help_text = """
        How to set up Flutter and ADB on Windows:
        
        1. Install Flutter:
        - Download from https://flutter.dev/docs/get-started/install/windows
        - Extract to C:\\src\\flutter (or another location)
        - Add to PATH: C:\\src\\flutter\\bin
        
        2. Install Android Studio:
        - Download from https://developer.android.com/studio
        - During installation, make sure to install Android SDK
        - After installation, add to PATH:
            C:\\Users\\[YOUR_USER]\\AppData\\Local\\Android\\Sdk\\platform-tools
        
        3. Restart your computer after modifying PATH
        
        4. Verify in command prompt:
        - flutter doctor
        - adb --version
        """
        messagebox.showinfo("Environment Setup Help", help_text)

    def install_flutter_apk(self):
        """Install the built APK to connected device"""
        apk_path = os.path.join("build", "app", "outputs", "flutter-apk", "app-release.apk")
        
        if not os.path.exists(apk_path):
            self.log_output("APK not found. Please build first.")
            return
        
        install_command = f"adb install -r {apk_path}"
        self.log_output("Installing APK...")
        
        # Run install command in background
        threading.Thread(target=self.run_flutter_command, args=(install_command,), daemon=True).start()

    def run_flutter_command(self, command):
        """Run flutter command and capture output"""
        try:
            self.log_output(f"Executing: {command}")
            
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Read both stdout and stderr
            while True:
                output = process.stdout.readline()
                error = process.stderr.readline()
                
                if output == '' and error == '' and process.poll() is not None:
                    break
                    
                if output:
                    self.flutter_output.insert(tk.END, output)
                    self.flutter_output.see(tk.END)
                if error:
                    self.flutter_output.insert(tk.END, f"Error: {error}")
                    self.flutter_output.see(tk.END)
                    
                self.flutter_output.update()
                
            process.wait()
            
            if process.returncode != 0:
                self.log_output(f"Command failed with exit code {process.returncode}")
            
        except Exception as e:
            self.flutter_output.insert(tk.END, f"Error: {str(e)}\n")
            self.flutter_output.see(tk.END)

    def log_output(self, message):
        """Helper to log messages to output"""
        self.flutter_output.insert(tk.END, f"{message}\n")
        self.flutter_output.see(tk.END)
        
    def create_android_tab(self, parent):
        """Create Android emulator tab with enhanced features"""
        self.android_tab = parent
        
        # Status Frame
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.emulator_status_label = ttk.Label(status_frame, text="Status: Emulator Tidak Aktif", style='Status.TLabel')
        self.emulator_status_label.pack(side=tk.LEFT)
        
        # Control Buttons Frame
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        self.emulator_start_btn = ttk.Button(control_frame, text="Start Emulator", command=self.start_android_emulator)
        self.emulator_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.emulator_stop_btn = ttk.Button(control_frame, text="Stop Emulator", command=self.stop_android_emulator, state=tk.DISABLED)
        self.emulator_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.emulator_open_btn = ttk.Button(control_frame, text="Buka Emulator", command=self.open_emulator_ui, state=tk.DISABLED)
        self.emulator_open_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Configuration Frame
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Android Emulator", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # SDK Path with auto-detection
        sdk_frame = ttk.Frame(config_frame)
        sdk_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(sdk_frame, text="Android SDK Path:").pack(side=tk.LEFT)
        self.android_sdk_entry = ttk.Entry(sdk_frame)
        self.android_sdk_entry.insert(0, self.default_paths['android_sdk'])
        self.android_sdk_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        browse_btn = ttk.Button(sdk_frame, text="Browse...", command=lambda: self.browse_directory(self.android_sdk_entry))
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # Emulator Path with auto-detection
        emulator_frame = ttk.Frame(config_frame)
        emulator_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(emulator_frame, text="Emulator Path:").pack(side=tk.LEFT)
        self.emulator_path_entry = ttk.Entry(emulator_frame)
        self.emulator_path_entry.insert(0, self.default_paths['emulator'])
        self.emulator_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Add detect button for emulator path
        emulator_detect_btn = ttk.Button(emulator_frame, text="Detect", command=self.detect_emulator_path)
        emulator_detect_btn.pack(side=tk.LEFT, padx=(5, 0))
        emulator_browse_btn = ttk.Button(emulator_frame, text="Browse...", command=lambda: self.browse_executable(self.emulator_path_entry))
        emulator_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # AVD Selection with dropdown
        avd_frame = ttk.Frame(config_frame)
        avd_frame.pack(fill=tk.X)
        ttk.Label(avd_frame, text="Nama AVD:").pack(side=tk.LEFT)
        
        # Create a combobox for AVD selection
        self.avd_combobox = ttk.Combobox(avd_frame)
        self.avd_combobox.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        self.avd_combobox.insert(0, "Pixel_4_API_30")
        
        # Button to refresh AVD list
        refresh_avd_btn = ttk.Button(avd_frame, text="Refresh", command=self.refresh_avd_list)
        refresh_avd_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        # List available AVDs button
        list_avd_btn = ttk.Button(parent, text="List Available AVDs", command=self.list_android_avds)
        list_avd_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Advanced options
        adv_frame = ttk.LabelFrame(parent, text="Opsi Lanjutan", padding="10")
        adv_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.no_snapshot_var = tk.BooleanVar(value=True)
        no_snapshot_cb = ttk.Checkbutton(adv_frame, text="No Snapshot (Start Fresh)", variable=self.no_snapshot_var)
        no_snapshot_cb.pack(anchor=tk.W)
        
        self.no_boot_anim_var = tk.BooleanVar(value=True)
        no_boot_anim_cb = ttk.Checkbutton(adv_frame, text="No Boot Animation", variable=self.no_boot_anim_var)
        no_boot_anim_cb.pack(anchor=tk.W)
        
        self.wipe_data_var = tk.BooleanVar()
        wipe_data_cb = ttk.Checkbutton(adv_frame, text="Wipe Data", variable=self.wipe_data_var)
        wipe_data_cb.pack(anchor=tk.W)

        # Add additional features
        self.add_extra_features(parent)
        
        # Initialize AVD list
        self.refresh_avd_list()
        
    
    def detect_emulator_path(self):
        """Detect emulator.exe path based on SDK path"""
        sdk_path = self.android_sdk_entry.get()
        if not sdk_path or not os.path.isdir(sdk_path):
            messagebox.showerror("Error", "Android SDK path tidak valid!")
            return
        emulator_path = os.path.join(sdk_path, "emulator", "emulator.exe")
        if os.path.isfile(emulator_path):
            self.emulator_path_entry.delete(0, tk.END)
            self.emulator_path_entry.insert(0, emulator_path)
            self.default_paths['emulator'] = emulator_path
            self.log_message(f"Emulator path terdeteksi: {emulator_path}")
            self.save_config()
        else:
            messagebox.showwarning("Peringatan", "emulator.exe tidak ditemukan di SDK path tersebut.")

    def refresh_avd_list(self):
        """Refresh the list of available AVDs in the combobox"""
        emulator_path = self.emulator_path_entry.get()
        if not emulator_path or not os.path.isfile(emulator_path):
            self.avd_combobox['values'] = []
            self.avd_combobox.set('')
            return
        try:
            result = subprocess.run([emulator_path, "-list-avds"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            avds = result.stdout.splitlines()
            self.avd_combobox['values'] = avds
            if avds:
                self.avd_combobox.set(avds[0])
            else:
                self.avd_combobox.set('')
        except Exception as e:
            self.avd_combobox['values'] = []
            self.avd_combobox.set('')
            self.log_message(f"Gagal mendapatkan daftar AVD: {str(e)}")

    def add_extra_features(self, parent):
        """Add additional features to the Android tab"""
        extra_frame = ttk.LabelFrame(parent, text="Fitur Tambahan", padding="10")
        extra_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Screen recording option
        self.record_screen_var = tk.BooleanVar()
        record_cb = ttk.Checkbutton(extra_frame, text="Record Screen on Start", variable=self.record_screen_var)
        record_cb.pack(anchor=tk.W)
        
        # Screen resolution options
        res_frame = ttk.Frame(extra_frame)
        res_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(res_frame, text="Resolution:").pack(side=tk.LEFT)
        self.resolution_var = tk.StringVar(value="1080x1920")
        resolutions = ["720x1280", "1080x1920", "1440x2560", "Custom"]
        res_dropdown = ttk.Combobox(res_frame, textvariable=self.resolution_var, values=resolutions)
        res_dropdown.pack(side=tk.LEFT, padx=(5, 0))
        
        # Custom resolution entry
        self.custom_res_frame = ttk.Frame(extra_frame)
        self.custom_res_entry = ttk.Entry(self.custom_res_frame)
        ttk.Label(self.custom_res_frame, text="Custom:").pack(side=tk.LEFT)
        self.custom_res_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # Show/hide custom resolution based on selection
        def update_resolution_ui(*args):
            if self.resolution_var.get() == "Custom":
                self.custom_res_frame.pack(fill=tk.X, pady=(5, 0))
            else:
                self.custom_res_frame.pack_forget()
        
        self.resolution_var.trace("w", update_resolution_ui)
        update_resolution_ui()
        
    
    def open_emulator_ui(self):
        """Open emulator UI window"""
        if not self.is_emulator_running:
            messagebox.showwarning("Peringatan", "Emulator belum berjalan!")
            return
        
        emulator_ui_path = os.path.join(os.path.dirname(self.emulator_path_entry.get()), "emulator-ui.exe")
        if os.path.isfile(emulator_ui_path):
            try:
                subprocess.Popen(
                    [emulator_ui_path],
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
                )
                self.log_message("Membuka Emulator UI")
            except Exception as e:
                self.log_message(f"Gagal membuka Emulator UI: {str(e)}")
        else:
            self.log_message("Emulator UI tidak ditemukan")
    
    # Flutter methods
    def start_flutter_server(self):
        """Start Flutter development server"""
        if self.is_flutter_running:
            messagebox.showwarning("Peringatan", "Flutter Server sudah berjalan!")
            return
        
        host = self.flutter_host_entry.get()
        port = self.flutter_port_entry.get()
        project_dir = self.flutter_project_entry.get()
        flutter_path = self.flutter_path_entry.get()
        
        if not all([host, port, project_dir, flutter_path]):
            messagebox.showerror("Error", "Semua field harus diisi!")
            return
        
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Port harus berupa angka antara 1 dan 65535!")
            return
        
        if not os.path.isdir(project_dir):
            messagebox.showerror("Error", "Project directory tidak valid!")
            return
        
        if not os.path.isfile(flutter_path):
            messagebox.showerror("Error", "Path Flutter tidak valid!")
            return
        
        cmd = [flutter_path, "run", "-d", "chrome", "--web-port", str(port), "--web-hostname", host]
        
        self.log_message(f"Memulai Flutter Server pada {host}:{port}")
        self.log_message(f"Project directory: {project_dir}")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.flutter_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=project_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_flutter_running = True
                self.update_flutter_ui_state()
                
                while True:
                    output = self.flutter_process.stdout.readline()
                    if output == '' and self.flutter_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.flutter_process.poll()
                self.is_flutter_running = False
                self.update_flutter_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Flutter Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Flutter Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_flutter_running = False
                self.update_flutter_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_flutter_server(self):
        """Stop Flutter development server"""
        if self.flutter_process and self.is_flutter_running:
            self.log_message("Menghentikan Flutter Server...")
            self.flutter_process.terminate()
            try:
                self.flutter_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.flutter_process.kill()
            self.is_flutter_running = False
            self.update_flutter_ui_state()
            self.log_message("Flutter Server dihentikan")
    
    def create_flutter_project(self):
        """Create new Flutter project"""
        project_name = self.new_flutter_project_entry.get()
        if not project_name:
            messagebox.showerror("Error", "Nama project harus diisi!")
            return
        
        project_dir = self.new_flutter_dir_entry.get()
        if not project_dir:
            messagebox.showerror("Error", "Lokasi project harus dipilih!")
            return
        
        flutter_path = self.flutter_path_entry.get()
        if not flutter_path:
            messagebox.showerror("Error", "Path Flutter harus diisi!")
            return
        
        full_path = os.path.join(project_dir, project_name)
        
        if os.path.exists(full_path):
            messagebox.showerror("Error", f"Direktori {full_path} sudah ada!")
            return
        
        self.log_message(f"Membuat project Flutter baru: {project_name}")
        
        cmd = [flutter_path, "create", project_name]
        
        def run_command():
            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.root.after(0, self.log_message, f"Project Flutter berhasil dibuat di: {full_path}")
                    self.root.after(0, self.flutter_project_entry.delete, 0, tk.END)
                    self.root.after(0, self.flutter_project_entry.insert, 0, full_path)
                    self.root.after(0, messagebox.showinfo, "Sukses", f"Project Flutter berhasil dibuat di:\n{full_path}")
                else:
                    self.root.after(0, self.log_message, f"Gagal membuat project Flutter. Kode error: {return_code}")
                    self.root.after(0, messagebox.showerror, "Error", "Gagal membuat project Flutter")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.root.after(0, messagebox.showerror, "Error", f"Gagal membuat project Flutter: {str(e)}")
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
    
    def open_flutter_in_browser(self):
        """Open Flutter server in browser"""
        if not self.is_flutter_running:
            messagebox.showwarning("Peringatan", "Flutter Server belum berjalan!")
            return
        
        host = self.flutter_host_entry.get()
        port = self.flutter_port_entry.get()
        
        url = f"http://{host}:{port}"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    def update_flutter_ui_state(self):
        """Update Flutter server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: Flutter Server Aktif"):
            if not self.is_flutter_running:
                self.flutter_status_label.config(
                    text="Status: Flutter Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.flutter_start_btn.config(state=tk.NORMAL)
                self.flutter_stop_btn.config(state=tk.DISABLED)
                self.flutter_open_browser_btn.config(state=tk.DISABLED)
                return
            # Running text animation
            display_text = text[idx:] + "   " + text[:idx]
            self.flutter_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.flutter_start_btn.config(state=tk.DISABLED)
            self.flutter_stop_btn.config(state=tk.NORMAL)
            self.flutter_open_browser_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            # Create green/red circle images
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_flutter_running:
            animate_status()
        else:
            self.flutter_status_label.config(
                text="Status: Flutter Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.flutter_start_btn.config(state=tk.NORMAL)
            self.flutter_stop_btn.config(state=tk.DISABLED)
            self.flutter_open_browser_btn.config(state=tk.DISABLED)

    def start_android_emulator(self):
        """Start Android emulator with advanced options and animated status"""
        if self.is_emulator_running:
            messagebox.showwarning("Peringatan", "Emulator sudah berjalan!")
            return

        emulator_path = self.emulator_path_entry.get()
        avd_name = self.avd_combobox.get()

        if not all([emulator_path, avd_name]):
            messagebox.showerror("Error", "Emulator path dan nama AVD harus diisi!")
            return

        if not os.path.isfile(emulator_path):
            messagebox.showerror("Error", "Path emulator tidak valid!")
            return

        # Build command with advanced options
        cmd = [emulator_path, "-avd", avd_name]

        if self.no_snapshot_var.get():
            cmd.extend(["-no-snapshot"])
        if self.no_boot_anim_var.get():
            cmd.extend(["-no-boot-anim"])
        if self.wipe_data_var.get():
            cmd.extend(["-wipe-data"])

        self.log_message(f"Memulai Android Emulator: {avd_name}")
        self.log_message(f"Perintah: {' '.join(cmd)}")

        def animate_emulator_status(idx=0, text="Status: Emulator Aktif"):
            if not self.is_emulator_running:
                self.emulator_status_label.config(
                    text="Status: Emulator Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.emulator_start_btn.config(state=tk.NORMAL)
                self.emulator_stop_btn.config(state=tk.DISABLED)
                self.emulator_open_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.emulator_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.emulator_start_btn.config(state=tk.DISABLED)
            self.emulator_stop_btn.config(state=tk.NORMAL)
            self.emulator_open_btn.config(state=tk.DISABLED)
            self.root.after(200, animate_emulator_status, (idx + 1) % len(text), text)

        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")

        try:
            # Start emulator directly without capturing output
            self.android_emulator_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
            )

            self.is_emulator_running = True
            animate_emulator_status()
            self.log_message("Emulator Android berhasil dijalankan")

            threading.Thread(target=self.check_emulator_ready, daemon=True).start()

        except Exception as e:
            self.log_message(f"Gagal menjalankan emulator: {str(e)}")
            messagebox.showerror("Error", f"Gagal menjalankan emulator: {str(e)}")
            self.is_emulator_running = False
            self.update_emulator_ui_state()

    def check_emulator_ready(self):
        """Check if Android emulator is ready by polling adb devices, but don't wait long (fast check)."""
        adb_path = None
        # Try to find adb in common locations or in Android SDK
        possible_adb = [
            os.path.join(self.android_sdk_entry.get(), "platform-tools", "adb.exe"),
            "adb"
        ]
        for path in possible_adb:
            if os.path.isfile(path) or path == "adb":
                adb_path = path
                break

        if not adb_path:
            self.root.after(0, self.log_message, "adb tidak ditemukan, tidak bisa cek status emulator.")
            return

        self.root.after(0, self.log_message, "Cek cepat status emulator (tidak menunggu lama)...")
        # Fast check: only try 2 times, 0.5s interval
        booted = False
        for _ in range(2):
            try:
                result = subprocess.run(
                    [adb_path, "shell", "getprop", "sys.boot_completed"],
                    capture_output=True,
                    text=True,
                    timeout=1,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                if result.stdout.strip() == "1":
                    booted = True
                    break
            except Exception:
                pass
            time.sleep(0.5)
        if booted:
            self.root.after(0, self.log_message, "Emulator Android siap digunakan.")
            self.root.after(0, self.emulator_open_btn.config, {"state": tk.NORMAL})
        else:
            self.root.after(0, self.log_message, "Emulator belum siap, tapi proses tidak menunggu lama (fast mode).")
    
    def stop_android_emulator(self):
        """Stop Android emulator"""
        if self.android_emulator_process and self.is_emulator_running:
            self.log_message("Menghentikan Android Emulator...")
            self.android_emulator_process.terminate()
            try:
                self.android_emulator_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.android_emulator_process.kill()
            self.is_emulator_running = False
            self.update_emulator_ui_state()
            self.log_message("Android Emulator dihentikan")
    
    def list_android_avds(self):
        """List available Android Virtual Devices"""
        emulator_path = self.emulator_path_entry.get()
        
        if not emulator_path:
            messagebox.showerror("Error", "Emulator path harus diisi!")
            return
        
        if not os.path.isfile(emulator_path):
            messagebox.showerror("Error", "Path emulator tidak valid!")
            return
        
        cmd = [emulator_path, "-list-avds"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                avds = result.stdout.splitlines()
                if avds:
                    message = "Available AVDs:\n" + "\n".join(avds)
                    messagebox.showinfo("Available AVDs", message)
                    self.log_message("Daftar AVD yang tersedia:\n" + "\n".join(avds))
                else:
                    messagebox.showinfo("Available AVDs", "Tidak ada AVD yang tersedia")
                    self.log_message("Tidak ada AVD yang tersedia")
            else:
                messagebox.showerror("Error", f"Gagal mendapatkan daftar AVD:\n{result.stderr}")
                self.log_message(f"Gagal mendapatkan daftar AVD: {result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendapatkan daftar AVD: {str(e)}")
            self.log_message(f"Gagal mendapatkan daftar AVD: {str(e)}")
    
    def run_flutter_android(self):
        """Run Flutter app on Android emulator"""
        project_dir = self.flutter_project_entry.get()
        if not project_dir:
            messagebox.showerror("Error", "Project directory harus dipilih!")
            return
        
        flutter_path = self.flutter_path_entry.get()
        if not flutter_path:
            messagebox.showerror("Error", "Path Flutter harus diisi!")
            return
        
        cmd = [flutter_path, "run", "-d", "android"]
        
        self.log_message(f"Menjalankan Flutter di Android: {project_dir}")
        
        def run_command():
            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = process.poll()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Flutter Android berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Flutter Android dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
    
    def update_emulator_ui_state(self):
        """Update Android emulator UI state"""
        if self.is_emulator_running:
            self.emulator_status_label.config(text="Status: Emulator Aktif", foreground="green")
            self.emulator_start_btn.config(state=tk.DISABLED)
            self.emulator_stop_btn.config(state=tk.NORMAL)
        else:
            self.emulator_status_label.config(text="Status: Emulator Tidak Aktif", foreground="red")
            self.emulator_start_btn.config(state=tk.NORMAL)
            self.emulator_stop_btn.config(state=tk.DISABLED)
            
    def create_php_server_tab(self, parent):
        """Create PHP Server tab with more complete features"""
        self.php_tab = parent

        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.php_status_label = ttk.Label(status_frame, text="Status: PHP Server Tidak Aktif", style='Status.TLabel')
        self.php_status_label.pack(side=tk.LEFT)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        self.php_start_btn = ttk.Button(control_frame, text="Start PHP Server", command=self.start_php_server)
        self.php_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.php_stop_btn = ttk.Button(control_frame, text="Stop PHP Server", command=self.stop_php_server, state=tk.DISABLED)
        self.php_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.php_open_browser_btn = ttk.Button(control_frame, text="Buka di Browser", command=self.open_php_in_browser)
        self.php_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))

        # New: Quick access to phpinfo and php.ini
        self.php_info_btn = ttk.Button(control_frame, text="phpinfo()", command=self.show_php_info)
        self.php_info_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.php_ini_btn = ttk.Button(control_frame, text="Edit php.ini", command=self.edit_php_ini)
        self.php_ini_btn.pack(side=tk.LEFT, padx=(0, 5))

        # New: Button to open document root in explorer
        self.php_open_folder_btn = ttk.Button(control_frame, text="Open Folder", command=lambda: os.startfile(self.doc_root_entry.get()))
        self.php_open_folder_btn.pack(side=tk.LEFT, padx=(0, 5))

        config_frame = ttk.LabelFrame(parent, text="Konfigurasi PHP Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        host_frame = ttk.Frame(config_frame)
        host_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(host_frame, text="Host:").pack(side=tk.LEFT)
        self.host_entry = ttk.Entry(host_frame)
        self.host_entry.insert(0, "localhost")
        self.host_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.port_entry = ttk.Entry(port_frame)
        self.port_entry.insert(0, "8000")
        self.port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        doc_root_frame = ttk.Frame(config_frame)
        doc_root_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(doc_root_frame, text="Document Root:").pack(side=tk.LEFT)
        self.doc_root_entry = ttk.Entry(doc_root_frame)
        default_root = os.getcwd()
        self.doc_root_entry.insert(0, default_root)
        self.doc_root_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(doc_root_frame, text="Browse...", command=lambda: self.browse_directory(self.doc_root_entry))
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        php_path_frame = ttk.Frame(config_frame)
        php_path_frame.pack(fill=tk.X)
        ttk.Label(php_path_frame, text="PHP Path:").pack(side=tk.LEFT)
        self.php_path_entry = ttk.Entry(php_path_frame)
        self.php_path_entry.insert(0, self.default_paths['php'])
        self.php_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        php_browse_btn = ttk.Button(php_path_frame, text="Browse...", command=lambda: self.browse_executable(self.php_path_entry))
        php_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        # New: PHP version info
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.php_version_label = ttk.Label(version_frame, text="PHP Version: -")
        self.php_version_label.pack(side=tk.LEFT)
        # Try to show version if path valid
        def update_php_version_label(*args):
            php_path = self.php_path_entry.get()
            if os.path.isfile(php_path):
                try:
                    result = subprocess.run([php_path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.stdout:
                        self.php_version_label.config(text="PHP Version: " + result.stdout.splitlines()[0])
                except Exception:
                    self.php_version_label.config(text="PHP Version: -")
            else:
                self.php_version_label.config(text="PHP Version: -")
        self.php_path_entry.bind("<FocusOut>", update_php_version_label)
        update_php_version_label()

        # New: List all .php files in doc root
        files_frame = ttk.LabelFrame(parent, text="Daftar File PHP di Document Root", padding="10")
        files_frame.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        self.php_files_listbox = tk.Listbox(files_frame, height=5)
        self.php_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(files_frame, orient="vertical", command=self.php_files_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.php_files_listbox.config(yscrollcommand=scrollbar.set)

        def refresh_php_files_list(*args):
            self.php_files_listbox.delete(0, tk.END)
            doc_root = self.doc_root_entry.get()
            if os.path.isdir(doc_root):
                for f in os.listdir(doc_root):
                    if f.lower().endswith(".php"):
                        self.php_files_listbox.insert(tk.END, f)
        self.doc_root_entry.bind("<FocusOut>", refresh_php_files_list)
        refresh_php_files_list()

        # Double click to open in browser
        def open_selected_php_file(event):
            if not self.is_php_running:
                messagebox.showwarning("Peringatan", "PHP Server belum berjalan!")
                return
            selection = self.php_files_listbox.curselection()
            if selection:
                filename = self.php_files_listbox.get(selection[0])
                host = self.host_entry.get()
                port = self.port_entry.get()
                url = f"http://{host}:{port}/{filename}"
                webbrowser.open(url)
                self.log_message(f"Membuka browser ke: {url}")
        self.php_files_listbox.bind("<Double-Button-1>", open_selected_php_file)

        # New: Button to refresh file list
        refresh_btn = ttk.Button(files_frame, text="Refresh", command=refresh_php_files_list)
        refresh_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        # New: Button to open selected file in default editor
        def open_in_editor():
            selection = self.php_files_listbox.curselection()
            if selection:
                filename = self.php_files_listbox.get(selection[0])
                doc_root = self.doc_root_entry.get()
                file_path = os.path.join(doc_root, filename)
                if os.path.isfile(file_path):
                    os.startfile(file_path)
        open_editor_btn = ttk.Button(files_frame, text="Open in Editor", command=open_in_editor)
        open_editor_btn.pack(side=tk.BOTTOM, fill=tk.X, pady=(0, 5))
    
    def create_apache_server_tab(self, parent):
        """Create Apache Server tab"""
        self.apache_tab = parent
        
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.apache_status_label = ttk.Label(status_frame, text="Status: Apache Server Tidak Aktif", style='Status.TLabel')
        self.apache_status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        self.apache_start_btn = ttk.Button(control_frame, text="Start Apache", command=self.start_apache)
        self.apache_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_stop_btn = ttk.Button(control_frame, text="Stop Apache", command=self.stop_apache, state=tk.DISABLED)
        self.apache_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_restart_btn = ttk.Button(control_frame, text="Restart Apache", command=self.restart_apache, state=tk.DISABLED)
        self.apache_restart_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_open_browser_btn = ttk.Button(control_frame, text="Buka di Browser", command=self.open_apache_in_browser)
        self.apache_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Fitur tambahan: Buka folder conf, edit httpd.conf, lihat error.log, reload config
        self.apache_open_conf_btn = ttk.Button(control_frame, text="Open conf Folder", command=self.open_apache_conf_folder)
        self.apache_open_conf_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_edit_httpd_btn = ttk.Button(control_frame, text="Edit httpd.conf", command=self.edit_apache_httpd_conf)
        self.apache_edit_httpd_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_view_errorlog_btn = ttk.Button(control_frame, text="View error.log", command=self.view_apache_error_log)
        self.apache_view_errorlog_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.apache_reload_btn = ttk.Button(control_frame, text="Reload Config", command=self.reload_apache_config)
        self.apache_reload_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Tambahan: Buat Project Python Website (Flask)
        self.apache_create_python_btn = ttk.Button(control_frame, text="Buat Project Python Website", command=self.create_python_website_project)
        self.apache_create_python_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Apache Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        apache_path_frame = ttk.Frame(config_frame)
        apache_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(apache_path_frame, text="Apache Path:").pack(side=tk.LEFT)
        self.apache_path_entry = ttk.Entry(apache_path_frame)
        self.apache_path_entry.insert(0, self.default_paths['apache'])
        self.apache_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        apache_browse_btn = ttk.Button(apache_path_frame, text="Browse...", command=lambda: self.browse_executable(self.apache_path_entry))
        apache_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        config_file_frame = ttk.Frame(config_frame)
        config_file_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(config_file_frame, text="Config File:").pack(side=tk.LEFT)
        self.apache_config_entry = ttk.Entry(config_file_frame)
        possible_configs = [
            "C:\\xampp\\apache\\conf\\httpd.conf",
            "C:\\Program Files\\Apache Software Foundation\\Apache2.4\\conf\\httpd.conf",
            "C:\\Program Files (x86)\\Apache Software Foundation\\Apache2.4\\conf\\httpd.conf",
        ]
        
        for config in possible_configs:
            if os.path.isfile(config):
                self.apache_config_entry.insert(0, config)
                break
        
        self.apache_config_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        config_browse_btn = ttk.Button(config_file_frame, text="Browse...", command=lambda: self.browse_file(self.apache_config_entry, [("Config Files", "*.conf"), ("All Files", "*.*")]))
        config_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Fitur tambahan: Info versi Apache
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.apache_version_label = ttk.Label(version_frame, text="Apache Version: -")
        self.apache_version_label.pack(side=tk.LEFT)
        def update_apache_version_label(*args):
            apache_path = self.apache_path_entry.get()
            if os.path.isfile(apache_path):
                try:
                    result = subprocess.run([apache_path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.stderr or result.stdout:
                        version_line = result.stderr.splitlines()[0] if result.stderr else result.stdout.splitlines()[0]
                        self.apache_version_label.config(text="Apache Version: " + version_line)
                except Exception:
                    self.apache_version_label.config(text="Apache Version: -")
            else:
                self.apache_version_label.config(text="Apache Version: -")
        self.apache_path_entry.bind("<FocusOut>", update_apache_version_label)
        update_apache_version_label()

    # Fitur tambahan: fungsi pendukung Apache
    def open_apache_conf_folder(self):
        """Open Apache conf folder in explorer"""
        config_file = self.apache_config_entry.get()
        if config_file and os.path.isfile(config_file):
            conf_dir = os.path.dirname(config_file)
            os.startfile(conf_dir)
            self.log_message(f"Membuka folder conf: {conf_dir}")
        else:
            messagebox.showerror("Error", "Config file tidak valid!")

    def edit_apache_httpd_conf(self):
        """Open httpd.conf in default editor"""
        config_file = self.apache_config_entry.get()
        if config_file and os.path.isfile(config_file):
            os.startfile(config_file)
            self.log_message(f"Membuka httpd.conf: {config_file}")
        else:
            messagebox.showerror("Error", "Config file tidak valid!")

    def view_apache_error_log(self):
        """View Apache error.log in a window"""
        config_file = self.apache_config_entry.get()
        if config_file and os.path.isfile(config_file):
            conf_dir = os.path.dirname(config_file)
            error_log = os.path.join(conf_dir, "..", "logs", "error.log")
            error_log = os.path.abspath(error_log)
            if os.path.isfile(error_log):
                top = tk.Toplevel(self.root)
                top.title("Apache error.log")
                top.geometry("900x500")
                text_area = scrolledtext.ScrolledText(top, wrap=tk.NONE, font=("Consolas", 9))
                text_area.pack(fill=tk.BOTH, expand=True)
                try:
                    with open(error_log, "r", encoding="utf-8", errors="ignore") as f:
                        text_area.insert(tk.END, f.read())
                except Exception as e:
                    text_area.insert(tk.END, f"Gagal membaca error.log: {str(e)}")
                text_area.see(tk.END)
                self.log_message("Menampilkan Apache error.log")
            else:
                messagebox.showerror("Error", "error.log tidak ditemukan!")
        else:
            messagebox.showerror("Error", "Config file tidak valid!")

    def reload_apache_config(self):
        """Reload Apache config (graceful restart)"""
        apache_path = self.apache_path_entry.get()
        config_file = self.apache_config_entry.get()
        if not apache_path or not config_file:
            messagebox.showerror("Error", "Apache path dan config file harus diisi!")
            return
        if not os.path.isfile(apache_path) or not os.path.isfile(config_file):
            messagebox.showerror("Error", "Apache path atau config file tidak valid!")
            return
        cmd = [apache_path, "-k", "graceful", "-f", config_file]
        try:
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Reload konfigurasi Apache (graceful) berhasil")
            messagebox.showinfo("Apache", "Reload konfigurasi Apache berhasil!")
        except Exception as e:
            self.log_message(f"Gagal reload konfigurasi Apache: {str(e)}")
            messagebox.showerror("Error", f"Gagal reload konfigurasi Apache: {str(e)}")

    def create_python_website_project(self):
        """Buat project Python Website sederhana (Flask)"""
        project_dir = filedialog.askdirectory(title="Pilih Lokasi Project Python Website")
        if not project_dir:
            return
        project_name = simpledialog.askstring("Nama Project", "Masukkan nama project Python Website:")
        if not project_name:
            return
        full_path = os.path.join(project_dir, project_name)
        if os.path.exists(full_path):
            messagebox.showerror("Error", f"Direktori {full_path} sudah ada!")
            return
        try:
            os.makedirs(full_path)
            # Create app.py
            app_py = (
                "from flask import Flask, render_template\n"
                "app = Flask(__name__)\n\n"
                "@app.route('/')\n"
                "def home():\n"
                "    return render_template('index.html')\n\n"
                "if __name__ == '__main__':\n"
                "    app.run(debug=True)\n"
            )
            with open(os.path.join(full_path, "app.py"), "w", encoding="utf-8") as f:
                f.write(app_py)
            # Create requirements.txt
            with open(os.path.join(full_path, "requirements.txt"), "w", encoding="utf-8") as f:
                f.write("flask\n")
            # Create templates/index.html
            templates_dir = os.path.join(full_path, "templates")
            os.makedirs(templates_dir, exist_ok=True)
            index_html = (
                "<!DOCTYPE html>\n"
                "<html lang='en'>\n"
                "<head>\n"
                "    <meta charset='UTF-8'>\n"
                "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n"
                "    <title>Python Website</title>\n"
                "</head>\n"
                "<body>\n"
                "    <h1>Hello from Flask!</h1>\n"
                "    <p>This is a simple Python website project.</p>\n"
                "</body>\n"
                "</html>\n"
            )
            with open(os.path.join(templates_dir, "index.html"), "w", encoding="utf-8") as f:
                f.write(index_html)
            # Optionally create static dir
            static_dir = os.path.join(full_path, "static")
            os.makedirs(static_dir, exist_ok=True)
            # Show info and offer to open folder
            self.log_message(f"Project Python Website berhasil dibuat di: {full_path}")
            messagebox.showinfo("Sukses", f"Project Python Website berhasil dibuat di:\n{full_path}\n\n"
                                        "Jalankan dengan:\n"
                                        "  pip install -r requirements.txt\n"
                                        "  python app.py")
            if messagebox.askyesno("Buka Folder", "Buka folder project sekarang?"):
                os.startfile(full_path)
        except Exception as e:
            self.log_message(f"Gagal membuat project Python Website: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuat project Python Website: {str(e)}")

    def create_mariadb_server_tab(self, parent):
        """Create MariaDB Server tab"""
        self.mariadb_tab = parent
        
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mariadb_status_label = ttk.Label(status_frame, text="Status: MariaDB Server Tidak Aktif", style='Status.TLabel')
        self.mariadb_status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mariadb_start_btn = ttk.Button(control_frame, text="Start MariaDB", command=self.start_mariadb)
        self.mariadb_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mariadb_stop_btn = ttk.Button(control_frame, text="Stop MariaDB", command=self.stop_mariadb, state=tk.DISABLED)
        self.mariadb_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.mariadb_shell_btn = ttk.Button(control_frame, text="MySQL Shell", command=self.open_mysql_shell)
        self.mariadb_shell_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Fitur tambahan: buka folder data, edit my.ini, lihat error log
        self.mariadb_open_data_btn = ttk.Button(control_frame, text="Open Data Folder", command=self.open_mariadb_data_folder)
        self.mariadb_open_data_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.mariadb_edit_myini_btn = ttk.Button(control_frame, text="Edit my.ini", command=self.edit_mariadb_myini)
        self.mariadb_edit_myini_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.mariadb_view_errorlog_btn = ttk.Button(control_frame, text="View error.log", command=self.view_mariadb_error_log)
        self.mariadb_view_errorlog_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.mariadb_create_project_btn = ttk.Button(control_frame, text="Create SQL Project", command=self.create_sql_project)
        self.mariadb_create_project_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi MariaDB Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        mariadb_path_frame = ttk.Frame(config_frame)
        mariadb_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(mariadb_path_frame, text="MariaDB Path:").pack(side=tk.LEFT)
        self.mariadb_path_entry = ttk.Entry(mariadb_path_frame)
        self.mariadb_path_entry.insert(0, self.default_paths['mariadb'])
        self.mariadb_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        mariadb_browse_btn = ttk.Button(mariadb_path_frame, text="Browse...", command=lambda: self.browse_executable(self.mariadb_path_entry))
        mariadb_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        password_frame = ttk.Frame(config_frame)
        password_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(password_frame, text="Root Password:").pack(side=tk.LEFT)
        self.mariadb_password_entry = ttk.Entry(password_frame, show="*")
        self.mariadb_password_entry.insert(0, "")
        self.mariadb_password_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X)
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.mariadb_port_entry = ttk.Entry(port_frame)
        self.mariadb_port_entry.insert(0, "3306")
        self.mariadb_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Fitur tambahan: Info versi MariaDB
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.mariadb_version_label = ttk.Label(version_frame, text="MariaDB Version: -")
        self.mariadb_version_label.pack(side=tk.LEFT)
        def update_mariadb_version_label(*args):
            mariadb_path = self.mariadb_path_entry.get()
            if os.path.isfile(mariadb_path):
                try:
                    result = subprocess.run([mariadb_path, "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.stdout:
                        self.mariadb_version_label.config(text="MariaDB Version: " + result.stdout.splitlines()[0])
                except Exception:
                    self.mariadb_version_label.config(text="MariaDB Version: -")
            else:
                self.mariadb_version_label.config(text="MariaDB Version: -")
        self.mariadb_path_entry.bind("<FocusOut>", update_mariadb_version_label)
        update_mariadb_version_label()

    # Fitur tambahan: fungsi pendukung MariaDB
    def open_mariadb_data_folder(self):
        """Open MariaDB data folder in explorer"""
        mariadb_path = self.mariadb_path_entry.get()
        if mariadb_path and os.path.isfile(mariadb_path):
            base_dir = os.path.dirname(os.path.dirname(mariadb_path))
            data_dir = os.path.join(base_dir, "data")
            if os.path.isdir(data_dir):
                os.startfile(data_dir)
                self.log_message(f"Membuka folder data MariaDB: {data_dir}")
            else:
                messagebox.showerror("Error", "Data folder tidak ditemukan!")
        else:
            messagebox.showerror("Error", "MariaDB path tidak valid!")

    def edit_mariadb_myini(self):
        """Selalu buka C:\\xampp\\mysql\\bin\\my.ini secara paksa di editor default."""
        myini = r"C:\xampp\mysql\bin\my.ini"
        if os.path.isfile(myini):
            try:
                os.startfile(myini)
                self.log_message(f"Membuka konfigurasi MariaDB: {myini}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuka my.ini: {str(e)}")
        else:
            try:
                # Buat file my.ini baru jika belum ada, dengan template minimal XAMPP
                xampp_myini = (
                    "[mysqld]\n"
                    "port=3306\n"
                    "socket=\"/tmp/mysql.sock\"\n"
                    "basedir=\"C:/xampp/mysql\"\n"
                    "datadir=\"C:/xampp/mysql/data\"\n"
                    "tmpdir=\"C:/xampp/mysql/tmp\"\n"
                    "lc-messages-dir=\"C:/xampp/mysql/share\"\n"
                    "skip-external-locking\n"
                    "key_buffer_size=16M\n"
                    "max_allowed_packet=1M\n"
                    "sort_buffer_size=512K\n"
                    "net_buffer_length=8K\n"
                    "read_buffer_size=256K\n"
                    "read_rnd_buffer_size=512K\n"
                    "myisam_sort_buffer_size=8M\n"
                    "log_error=\"mysql_error.log\"\n"
                )
                with open(myini, "w", encoding="utf-8") as f:
                    f.write(xampp_myini)
                os.startfile(myini)
                self.log_message(f"File my.ini baru (template XAMPP) dibuat: {myini}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membuat my.ini: {str(e)}")

    def view_mariadb_error_log(self):
        """View MariaDB error log in a window"""
        mariadb_path = self.mariadb_path_entry.get()
        if mariadb_path and os.path.isfile(mariadb_path):
            base_dir = os.path.dirname(os.path.dirname(mariadb_path))
            error_log = os.path.join(base_dir, "data", "mysql_error.log")
            if not os.path.isfile(error_log):
                # Coba cari error.log lain
                for fname in os.listdir(os.path.join(base_dir, "data")):
                    if fname.endswith(".err") or fname.endswith(".log"):
                        error_log = os.path.join(base_dir, "data", fname)
                        break
            if os.path.isfile(error_log):
                top = tk.Toplevel(self.root)
                top.title("MariaDB error.log")
                top.geometry("900x500")
                text_area = scrolledtext.ScrolledText(top, wrap=tk.NONE, font=("Consolas", 9))
                text_area.pack(fill=tk.BOTH, expand=True)
                try:
                    with open(error_log, "r", encoding="utf-8", errors="ignore") as f:
                        text_area.insert(tk.END, f.read())
                except Exception as e:
                    text_area.insert(tk.END, f"Gagal membaca error.log: {str(e)}")
                text_area.see(tk.END)
                self.log_message("Menampilkan MariaDB error.log")
            else:
                messagebox.showerror("Error", "error.log tidak ditemukan!")
        else:
            messagebox.showerror("Error", "MariaDB path tidak valid!")
            
    
    def create_sql_project(self):
        """Create a new SQL project folder with basic structure"""
        project_path = filedialog.askdirectory(title="Select Project Location")
        if not project_path:
            return
        
        project_name = simpledialog.askstring("Project Name", "Enter project name:", parent=self.root)
        if not project_name:
            return
        
        try:
            # Create project directory structure
            project_dir = os.path.join(project_path, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(project_dir, "sql"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "migrations"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "data"), exist_ok=True)
            os.makedirs(os.path.join(project_dir, "docs"), exist_ok=True)
            
            # Create basic files
            with open(os.path.join(project_dir, "README.md"), "w") as f:
                f.write(f"# {project_name}\n\nSQL Project\n")
                
            # Create sample SQL file
            sample_sql = os.path.join(project_dir, "sql", "init.sql")
            with open(sample_sql, "w") as f:
                f.write("-- Database initialization script\n")
                f.write(f"CREATE DATABASE IF NOT EXISTS `{project_name.lower()}`;\n")
                f.write(f"USE `{project_name.lower()}`;\n\n")
                f.write("-- Add your tables and other database objects here\n")
            
            # Create basic config file
            config = {
                "project_name": project_name,
                "database_name": project_name.lower(),
                "created": datetime.now().isoformat(),  # Fixed this line
                "mariadb_path": self.mariadb_path_entry.get()
            }
            
            with open(os.path.join(project_dir, "project_config.json"), "w") as f:
                json.dump(config, f, indent=2)
            
            messagebox.showinfo("Success", f"SQL project '{project_name}' created successfully!")
            self.log_message(f"Created SQL project: {project_dir}")
            
            # Optionally open the project folder
            if messagebox.askyesno("Open Project", "Would you like to open the project folder?"):
                os.startfile(project_dir)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create project: {str(e)}")
            self.log_message(f"Error creating SQL project: {str(e)}")
    
    def create_filezilla_server_tab(self, parent):
        """Create FileZilla Server tab"""
        self.filezilla_tab = parent
        
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filezilla_status_label = ttk.Label(status_frame, text="Status: FileZilla Server Tidak Aktif", style='Status.TLabel')
        self.filezilla_status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filezilla_start_btn = ttk.Button(control_frame, text="Start FileZilla", command=self.start_filezilla)
        self.filezilla_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.filezilla_stop_btn = ttk.Button(control_frame, text="Stop FileZilla", command=self.stop_filezilla, state=tk.DISABLED)
        self.filezilla_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.filezilla_admin_btn = ttk.Button(control_frame, text="Admin Interface", command=self.open_filezilla_admin)
        self.filezilla_admin_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi FileZilla Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        filezilla_path_frame = ttk.Frame(config_frame)
        filezilla_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(filezilla_path_frame, text="FileZilla Path:").pack(side=tk.LEFT)
        self.filezilla_path_entry = ttk.Entry(filezilla_path_frame)
        self.filezilla_path_entry.insert(0, self.default_paths['filezilla'])
        self.filezilla_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        filezilla_browse_btn = ttk.Button(filezilla_path_frame, text="Browse...", command=lambda: self.browse_executable(self.filezilla_path_entry))
        filezilla_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        ftp_port_frame = ttk.Frame(config_frame)
        ftp_port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(ftp_port_frame, text="FTP Port:").pack(side=tk.LEFT)
        self.filezilla_port_entry = ttk.Entry(ftp_port_frame)
        self.filezilla_port_entry.insert(0, "21")
        self.filezilla_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        admin_port_frame = ttk.Frame(config_frame)
        admin_port_frame.pack(fill=tk.X)
        ttk.Label(admin_port_frame, text="Admin Port:").pack(side=tk.LEFT)
        self.filezilla_admin_port_entry = ttk.Entry(admin_port_frame)
        self.filezilla_admin_port_entry.insert(0, "14147")
        self.filezilla_admin_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Tambahan: Info versi FileZilla
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.filezilla_version_label = ttk.Label(version_frame, text="FileZilla Version: -")
        self.filezilla_version_label.pack(side=tk.LEFT)
        def update_filezilla_version_label(*args):
            filezilla_path = self.filezilla_path_entry.get()
            if os.path.isfile(filezilla_path):
                try:
                    # FileZilla Server does not support --version, so try to get version from file properties
                    info = win32api.GetFileVersionInfo(filezilla_path, '\\')
                    ms = info['FileVersionMS']
                    ls = info['FileVersionLS']
                    version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
                    self.filezilla_version_label.config(text="FileZilla Version: " + version)
                except Exception:
                    self.filezilla_version_label.config(text="FileZilla Version: -")
                else:
                    self.filezilla_version_label.config(text="FileZilla Version: -")
        try:
            self.filezilla_path_entry.bind("<FocusOut>", update_filezilla_version_label)
            update_filezilla_version_label()
        except ImportError:
            self.filezilla_version_label.config(text="FileZilla Version: (win32api not installed)")
    
    def create_mercury_server_tab(self, parent):
        """Create Mercury Server tab"""
        self.mercury_tab = parent

        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.mercury_status_label = ttk.Label(status_frame, text="Status: Mercury Server Tidak Aktif", style='Status.TLabel')
        self.mercury_status_label.pack(side=tk.LEFT)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.mercury_start_btn = ttk.Button(control_frame, text="Start Mercury", command=self.start_mercury)
        self.mercury_start_btn.pack(side=tk.LEFT, padx=(0, 5))

        self.mercury_stop_btn = ttk.Button(control_frame, text="Stop Mercury", command=self.stop_mercury, state=tk.DISABLED)
        self.mercury_stop_btn.pack(side=tk.LEFT, padx=(0, 5))

        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Mercury Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))

        mercury_path_frame = ttk.Frame(config_frame)
        mercury_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(mercury_path_frame, text="Mercury Path:").pack(side=tk.LEFT)
        self.mercury_path_entry = ttk.Entry(mercury_path_frame)
        self.mercury_path_entry.insert(0, self.default_paths['mercury'])
        self.mercury_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        mercury_browse_btn = ttk.Button(mercury_path_frame, text="Browse...", command=lambda: self.browse_executable(self.mercury_path_entry))
        mercury_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        smtp_port_frame = ttk.Frame(config_frame)
        smtp_port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(smtp_port_frame, text="SMTP Port:").pack(side=tk.LEFT)
        self.mercury_smtp_port_entry = ttk.Entry(smtp_port_frame)
        self.mercury_smtp_port_entry.insert(0, "25")
        self.mercury_smtp_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        pop3_port_frame = ttk.Frame(config_frame)
        pop3_port_frame.pack(fill=tk.X)
        ttk.Label(pop3_port_frame, text="POP3 Port:").pack(side=tk.LEFT)
        self.mercury_pop3_port_entry = ttk.Entry(pop3_port_frame)
        self.mercury_pop3_port_entry.insert(0, "110")
        self.mercury_pop3_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Tambahan: Info versi Mercury
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.mercury_version_label = ttk.Label(version_frame, text="Mercury Version: -")
        self.mercury_version_label.pack(side=tk.LEFT)
        def update_mercury_version_label(*args):
            mercury_path = self.mercury_path_entry.get()
            if os.path.isfile(mercury_path):
                try:
                    # Mercury doesn't have --version, so try to get version from file properties
                    info = win32api.GetFileVersionInfo(mercury_path, '\\')
                    ms = info['FileVersionMS']
                    ls = info['FileVersionLS']
                    version = f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"
                    self.mercury_version_label.config(text="Mercury Version: " + version)
                except Exception:
                    self.mercury_version_label.config(text="Mercury Version: -")
                else:
                    self.mercury_version_label.config(text="Mercury Version: -")
        try:
            self.mercury_path_entry.bind("<FocusOut>", update_mercury_version_label)
            update_mercury_version_label()
        except ImportError:
            self.mercury_version_label.config(text="Mercury Version: (win32api not installed)")
            
            
    def create_tomcat_server_tab(self, parent):
        """Create Tomcat Server tab"""
        self.tomcat_tab = parent
        
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tomcat_status_label = ttk.Label(status_frame, text="Status: Tomcat Server Tidak Aktif", style='Status.TLabel')
        self.tomcat_status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.tomcat_start_btn = ttk.Button(control_frame, text="Start Tomcat", command=self.start_tomcat)
        self.tomcat_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.tomcat_stop_btn = ttk.Button(control_frame, text="Stop Tomcat", command=self.stop_tomcat, state=tk.DISABLED)
        self.tomcat_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.tomcat_restart_btn = ttk.Button(control_frame, text="Restart Tomcat", command=self.start_tomcat, state=tk.DISABLED)
        self.tomcat_restart_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        self.tomcat_open_browser_btn = ttk.Button(control_frame, text="Buka di Browser", command=self.open_tomcat_in_browser)
        self.tomcat_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Tomcat Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        tomcat_path_frame = ttk.Frame(config_frame)
        tomcat_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(tomcat_path_frame, text="Tomcat Path:").pack(side=tk.LEFT)
        self.tomcat_path_entry = ttk.Entry(tomcat_path_frame)
        self.tomcat_path_entry.insert(0, self.default_paths['tomcat'])
        self.tomcat_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        tomcat_browse_btn = ttk.Button(tomcat_path_frame, text="Browse...", command=lambda: self.browse_executable(self.tomcat_path_entry))
        tomcat_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        tomcat_port_frame = ttk.Frame(config_frame)
        tomcat_port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(tomcat_port_frame, text="HTTP Port:").pack(side=tk.LEFT)
        self.tomcat_port_entry = ttk.Entry(tomcat_port_frame)
        self.tomcat_port_entry.insert(0, "8080")
        self.tomcat_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        shutdown_port_frame = ttk.Frame(config_frame)
        shutdown_port_frame.pack(fill=tk.X)
        ttk.Label(shutdown_port_frame, text="Shutdown Port:").pack(side=tk.LEFT)
        self.tomcat_shutdown_port_entry = ttk.Entry(shutdown_port_frame)
        self.tomcat_shutdown_port_entry.insert(0, "8005")
        self.tomcat_shutdown_port_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Tambahan: Info versi Tomcat
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.tomcat_version_label = ttk.Label(version_frame, text="Tomcat Version: -")
        self.tomcat_version_label.pack(side=tk.LEFT)
        def update_tomcat_version_label(*args):
            tomcat_path = self.tomcat_path_entry.get()
            if os.path.isfile(tomcat_path):
                try:
                    # Tomcat .exe does not support --version, so try to parse version from RELEASE-NOTES or manifest if possible
                    tomcat_dir = os.path.dirname(os.path.dirname(tomcat_path))
                    release_notes = os.path.join(tomcat_dir, "RELEASE-NOTES")
                    if os.path.isfile(release_notes):
                        with open(release_notes, "r", encoding="utf-8", errors="ignore") as f:
                            for line in f:
                                if "Apache Tomcat Version" in line or "Apache Tomcat" in line:
                                    self.tomcat_version_label.config(text="Tomcat Version: " + line.strip())
                            return
                    # Fallback: try to run with -v (may not work)
                    result = subprocess.run([tomcat_path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.stdout:
                        self.tomcat_version_label.config(text="Tomcat Version: " + result.stdout.splitlines()[0])
                    elif result.stderr:
                        self.tomcat_version_label.config(text="Tomcat Version: " + result.stderr.splitlines()[0])
                    else:
                        self.tomcat_version_label.config(text="Tomcat Version: -")
                except Exception:
                    self.tomcat_version_label.config(text="Tomcat Version: -")
                else:
                    self.tomcat_version_label.config(text="Tomcat Version: -")
            self.tomcat_path_entry.bind("<FocusOut>", update_tomcat_version_label)
            update_tomcat_version_label()
    
    def create_laragon_tab(self, parent):
        """Create Node.js Server tab with enhanced features"""
        self.nodejs_tab = parent
        
        status_frame = ttk.Frame(parent, style='Server.TFrame', padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.nodejs_status_label = ttk.Label(status_frame, text="Status: Node.js Server Tidak Aktif", style='Status.TLabel')
        self.nodejs_status_label.pack(side=tk.LEFT)
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        self.nodejs_start_btn = ttk.Button(control_frame, text="Start Node.js", command=self.start_nodejs)
        self.nodejs_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.nodejs_stop_btn = ttk.Button(control_frame, text="Stop Node.js", command=self.stop_nodejs, state=tk.DISABLED)
        self.nodejs_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.nodejs_restart_btn = ttk.Button(control_frame, text="Restart Node.js", command=self.restart_nodejs, state=tk.DISABLED)
        self.nodejs_restart_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.nodejs_open_browser_btn = ttk.Button(control_frame, text="Buka di Browser", command=self.open_nodejs_in_browser)
        self.nodejs_open_browser_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.laragon_menu_btn = ttk.Button(control_frame, text="Open Pyserver Menu", command=self.open_pyserver_menu)
        self.laragon_menu_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Project creation and management
        project_frame = ttk.Frame(parent)
        project_frame.pack(fill=tk.X, pady=(0, 10))
        self.nodejs_create_project_btn = ttk.Button(project_frame, text="Buat Project Baru", command=self.create_nodejs_project)
        self.nodejs_create_project_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.nodejs_open_project_btn = ttk.Button(project_frame, text="Buka Project", command=self.open_nodejs_project)
        self.nodejs_open_project_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        # Enhanced npm install button with dropdown menu
        npm_menu = tk.Menu(self.root, tearoff=0)
        npm_menu.add_command(label="npm install", command=self.nodejs_npm_install)
        npm_menu.add_command(label="npm install [package]", command=lambda: self.nodejs_custom_npm_install(""))
        npm_menu.add_command(label="npm install --save-dev [package]", command=lambda: self.nodejs_custom_npm_install("--save-dev"))
        npm_menu.add_command(label="npm install -g [package]", command=lambda: self.nodejs_custom_npm_install("-g"))
        
        self.npm_btn_var = tk.StringVar(value="npm install")
        self.nodejs_npm_btn = ttk.Menubutton(project_frame, textvariable=self.npm_btn_var, menu=npm_menu)
        self.nodejs_npm_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        config_frame = ttk.LabelFrame(parent, text="Konfigurasi Node.js Server", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        node_path_frame = ttk.Frame(config_frame)
        node_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(node_path_frame, text="Node.js Path:").pack(side=tk.LEFT)
        self.node_path_entry = ttk.Entry(node_path_frame)
        self.node_path_entry.insert(0, self.default_paths.get('node', ''))
        self.node_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        node_browse_btn = ttk.Button(node_path_frame, text="Browse...", command=lambda: self.browse_executable(self.node_path_entry))
        node_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        project_path_frame = ttk.Frame(config_frame)
        project_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(project_path_frame, text="Project Path:").pack(side=tk.LEFT)
        self.node_project_entry = ttk.Entry(project_path_frame)
        self.node_project_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        project_browse_btn = ttk.Button(project_path_frame, text="Browse...", command=lambda: self.browse_directory(self.node_project_entry))
        project_browse_btn.pack(side=tk.LEFT, padx=(5, 0))
        
        port_frame = ttk.Frame(config_frame)
        port_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
        self.node_port_entry = ttk.Entry(port_frame, width=10)
        self.node_port_entry.insert(0, "3000")
        self.node_port_entry.pack(side=tk.LEFT, padx=(5, 0))
        
        # Auto-detect web files checkbox
        auto_detect_frame = ttk.Frame(config_frame)
        auto_detect_frame.pack(fill=tk.X, pady=(0, 5))
        self.auto_detect_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(auto_detect_frame, text="Auto-detect web files (index.html/style.css/script.js/index.php)", 
                    variable=self.auto_detect_var).pack(side=tk.LEFT)
        
        # Version info
        version_frame = ttk.Frame(config_frame)
        version_frame.pack(fill=tk.X, pady=(0, 5))
        self.node_version_label = ttk.Label(version_frame, text="Node.js Version: -")
        self.node_version_label.pack(side=tk.LEFT)
        def update_node_version_label(*args):
            node_path = self.node_path_entry.get()
            if os.path.isfile(node_path):
                try:
                    result = subprocess.run([node_path, "-v"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    if result.stdout:
                        self.node_version_label.config(text="Node.js Version: " + result.stdout.strip())
                except Exception:
                    self.node_version_label.config(text="Node.js Version: -")
            else:
                self.node_version_label.config(text="Node.js Version: -")
        self.node_path_entry.bind("<FocusOut>", update_node_version_label)
        update_node_version_label()

        # Console output
        console_frame = ttk.LabelFrame(parent, text="Console Output", padding="10")
        console_frame.pack(fill=tk.BOTH, expand=True)
        self.node_console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, font=("Consolas", 9), height=6)
        self.node_console.pack(fill=tk.BOTH, expand=True)
        
    def nodejs_npm_install(self):
        """Run npm install for the current project"""
        project_path = self.node_project_entry.get()
        node_path = self.node_path_entry.get()
        
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("Error", "Project path tidak valid!")
            return
        
        if not node_path or not os.path.isfile(node_path):
            messagebox.showerror("Error", "Node.js path tidak valid!")
            return
        
        try:
            npm_path = os.path.join(os.path.dirname(node_path), "npm.cmd")
            if not os.path.isfile(npm_path):
                npm_path = "npm"  # Fallback to system npm
            
            self.node_console.delete('1.0', tk.END)
            self.node_console.insert(tk.END, "Running npm install...\n")
            
            # Run in separate thread
            threading.Thread(
                target=self._run_npm_install,
                args=([npm_path, "install"], project_path),
                daemon=True
            ).start()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan npm install: {str(e)}")
        
    def open_nodejs_project(self):
        """Open an existing Node.js project"""
        project_path = filedialog.askdirectory(title="Pilih Folder Project Node.js")
        if project_path:
            self.node_project_entry.delete(0, tk.END)
            self.node_project_entry.insert(0, project_path)
            
            # Auto-detect port from package.json if exists
            package_json_path = os.path.join(project_path, 'package.json')
            if os.path.exists(package_json_path):
                try:
                    with open(package_json_path) as f:
                        package_data = json.load(f)
                        if 'scripts' in package_data and 'start' in package_data['scripts']:
                            # Try to extract port from start script
                            start_script = package_data['scripts']['start']
                            port_match = re.search(r'port\s*=\s*(\d+)', start_script)
                            if port_match:
                                self.node_port_entry.delete(0, tk.END)
                                self.node_port_entry.insert(0, port_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            self.log_message(f"Node.js project dibuka: {project_path}")
        
    def open_nodejs_in_browser(self):
        """Open the Node.js server in default web browser"""
        port = self.node_port_entry.get()
        project_path = self.node_project_entry.get()
        
        if not port.isdigit():
            messagebox.showerror("Error", "Port harus berupa angka!")
            return
        
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("Error", "Project path tidak valid!")
            return
        
        try:
            url = f"http://localhost:{port}"
            webbrowser.open_new_tab(url)
            self.log_message(f"Membuka Node.js server di browser: {url}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuka browser: {str(e)}")
            self.log_message(f"Gagal membuka Node.js di browser: {str(e)}")
            
            

    def nodejs_custom_npm_install(self, option=""):
        """Run custom npm install with options"""
        project_path = self.node_project_entry.get()
        node_path = self.node_path_entry.get()
        
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("Error", "Project path tidak valid!")
            return
        
        if not node_path or not os.path.isfile(node_path):
            messagebox.showerror("Error", "Node.js path tidak valid!")
            return
        
        package = simpledialog.askstring("NPM Install", f"Masukkan nama package (kosongkan untuk install semua):", parent=self.root)
        if package is None:  # User cancelled
            return
        
        try:
            npm_path = os.path.join(os.path.dirname(node_path), "npm.cmd")
            if not os.path.isfile(npm_path):
                npm_path = "npm"  # Fallback to system npm
            
            self.node_console.delete('1.0', tk.END)
            
            if package:
                cmd = [npm_path, "install", option, package] if option else [npm_path, "install", package]
                self.node_console.insert(tk.END, f"Running: {' '.join(cmd)}\n")
            else:
                cmd = [npm_path, "install"]
                self.node_console.insert(tk.END, "Running npm install...\n")
            
            # Run in separate thread
            threading.Thread(target=self._run_npm_install, args=(cmd, project_path), daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan npm install: {str(e)}")

    def _run_npm_install(self, cmd, project_path):
        """Helper function to run npm install in background"""
        try:
            process = subprocess.Popen(
                cmd,
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            for line in process.stdout:
                self.node_console.insert(tk.END, line)
                self.node_console.see(tk.END)
                self.node_console.update()
            
            process.wait()
            self.node_console.insert(tk.END, "\nNPM command selesai!\n")
        except Exception as e:
            self.node_console.insert(tk.END, f"\nError: {str(e)}\n")

    def create_nodejs_project(self):
        """Create a new Node.js project with automatic web file detection"""
        project_path = filedialog.askdirectory(title="Pilih folder untuk project baru")
        if not project_path:
            return
        
        try:
            # Create package.json
            package_json = {
                "name": os.path.basename(project_path),
                "version": "1.0.0",
                "description": "",
                "main": "server.js",
                "scripts": {
                    "start": "node server.js",
                    "test": "echo \"Error: no test specified\" && exit 1"
                },
                "author": "",
                "license": "ISC"
            }
            
            with open(os.path.join(project_path, "package.json"), "w") as f:
                json.dump(package_json, f, indent=2)
            
            # Create server.js that serves static files
            with open(os.path.join(project_path, "server.js"), "w") as f:
                f.write("const express = require('express');\n")
                f.write("const path = require('path');\n")
                f.write("const app = express();\n\n")
                f.write("// Serve static files\n")
                f.write("app.use(express.static(path.join(__dirname, 'public')));\n\n")
                f.write("// Default to index.html\n")
                f.write("app.get('/', (req, res) => {\n")
                f.write("  res.sendFile(path.join(__dirname, 'public', 'index.html'));\n")
                f.write("});\n\n")
                f.write("const port = process.env.PORT || 3000;\n")
                f.write("app.listen(port, () => {\n")
                f.write("  console.log(`Server running on port ${port}`);\n")
                f.write("});\n")
            
            # Create public directory with default web files
            public_dir = os.path.join(project_path, 'public')
            os.makedirs(public_dir, exist_ok=True)
            
            # Create default index.html
            with open(os.path.join(public_dir, 'index.html'), 'w') as f:
                f.write("<!DOCTYPE html>\n")
                f.write("<html lang='en'>\n")
                f.write("<head>\n")
                f.write("  <meta charset='UTF-8'>\n")
                f.write("  <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n")
                f.write("  <title>New Project</title>\n")
                f.write("  <link rel='stylesheet' href='style.css'>\n")
                f.write("</head>\n")
                f.write("<body>\n")
                f.write("  <h1>Hello World!</h1>\n")
                f.write("  <script src='script.js'></script>\n")
                f.write("</body>\n")
                f.write("</html>\n")
            
            # Create default style.css
            with open(os.path.join(public_dir, 'style.css'), 'w') as f:
                f.write("body {\n")
                f.write("  font-family: Arial, sans-serif;\n")
                f.write("  margin: 0;\n")
                f.write("  padding: 20px;\n")
                f.write("  text-align: center;\n")
                f.write("}\n")
            
            # Create default script.js
            with open(os.path.join(public_dir, 'script.js'), 'w') as f:
                f.write("console.log('Hello from JavaScript!');\n")
            
            # Create empty index.php if requested
            if messagebox.askyesno("PHP Support", "Tambahkan file index.php juga?"):
                with open(os.path.join(public_dir, 'index.php'), 'w') as f:
                    f.write("<?php\n")
                    f.write("echo '<p>Hello from PHP!</p>';\n")
                    f.write("?>\n")
            
            self.node_project_entry.delete(0, tk.END)
            self.node_project_entry.insert(0, project_path)
            
            # Auto install express if requested
            if messagebox.askyesno("Install Dependencies", "Install Express.js untuk static file serving?"):
                self.nodejs_custom_npm_install("express")
            
            messagebox.showinfo("Sukses", "Project Node.js berhasil dibuat!")
            self.log_message(f"Project Node.js dibuat di: {project_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal membuat project: {str(e)}")
            self.log_message(f"Gagal membuat project Node.js: {str(e)}")

    def start_nodejs(self):
        """Start Node.js server with automatic web file support and animated status"""
        project_path = self.node_project_entry.get()
        node_path = self.node_path_entry.get()
        port = self.node_port_entry.get()
        
        if not project_path or not os.path.isdir(project_path):
            messagebox.showerror("Error", "Project path tidak valid!")
            return
        
        if not node_path or not os.path.isfile(node_path):
            messagebox.showerror("Error", "Node.js path tidak valid!")
            return
        
        try:
            # Stop if already running
            if hasattr(self, 'node_process') and self.node_process:
                self.node_process.terminate()
                self.node_process = None
            
            self.node_console.delete('1.0', tk.END)
            self.node_console.insert(tk.END, "Starting Node.js server...\n")
            
            # Check if we need to install express
            if self.auto_detect_var.get():
                package_json_path = os.path.join(project_path, 'package.json')
                if os.path.exists(package_json_path):
                    with open(package_json_path) as f:
                        try:
                            package_data = json.load(f)
                            if 'express' not in package_data.get('dependencies', {}):
                                if messagebox.askyesno("Express.js Required", 
                                                    "Express.js diperlukan untuk static file serving. Install sekarang?"):
                                    self.nodejs_custom_npm_install("express")
                                    self.node_console.insert(tk.END, "\nExpress.js installed. Starting server...\n")
                        except json.JSONDecodeError:
                            pass
            
            # Update environment variables
            env = os.environ.copy()
            env['PORT'] = port
            
            # Determine entry file (server.js or index.js)
            entry_file = 'server.js' if os.path.exists(os.path.join(project_path, 'server.js')) else 'index.js'
            
            self.node_process = subprocess.Popen(
                [node_path, entry_file],
                cwd=project_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            # Start thread to read output
            threading.Thread(target=self._read_node_output, daemon=True).start()
            
            # Animated status
            def animate_status(idx=0, text="Status: Node.js Server Aktif"):
                if not hasattr(self, 'node_process') or self.node_process is None:
                    self.nodejs_status_label.config(
                        text="Status: Node.js Server Tidak Aktif   ",
                        foreground="red",
                        image=getattr(self, "status_circle_red", None),
                        compound=tk.LEFT
                    )
                    self.nodejs_start_btn.config(state=tk.NORMAL)
                    self.nodejs_stop_btn.config(state=tk.DISABLED)
                    self.nodejs_restart_btn.config(state=tk.DISABLED)
                    return
                display_text = text[idx:] + "   " + text[:idx]
                self.nodejs_status_label.config(
                    text=display_text,
                    foreground="green",
                    image=getattr(self, "status_circle_green", None),
                    compound=tk.LEFT
                )
                self.nodejs_start_btn.config(state=tk.DISABLED)
                self.nodejs_stop_btn.config(state=tk.NORMAL)
                self.nodejs_restart_btn.config(state=tk.NORMAL)
                self.nodejs_status_label.after(200, animate_status, (idx + 1) % len(text), text)
            if not hasattr(self, "status_circle_green"):
                self.status_circle_green = self._create_circle_image("#00cc00")
                self.status_circle_red = self._create_circle_image("#cc0000")
            animate_status()
            self.log_message(f"Node.js server started on port {port}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal memulai Node.js: {str(e)}")
            self.log_message(f"Gagal memulai Node.js: {str(e)}")
    
    def _read_node_output(self):
        """Read output from the running Node.js process and display it in the console."""
        if hasattr(self, 'node_process') and self.node_process and self.node_process.stdout:
            try:
                for line in self.node_process.stdout:
                    self.node_console.insert(tk.END, line)
                    self.node_console.see(tk.END)
                    self.node_console.update()
            except Exception as e:
                self.node_console.insert(tk.END, f"\nError reading Node.js output: {str(e)}\n")
                    
    def stop_nodejs(self):
        """Stop the running Node.js server and reset animated status"""
        if hasattr(self, 'node_process') and self.node_process:
            try:
                self.node_process.terminate()
                self.node_process = None
                self.nodejs_status_label.config(
                    text="Status: Node.js Server Tidak Aktif   ",
                    foreground="red",
                    image=getattr(self, "status_circle_red", None),
                    compound=tk.LEFT
                )
                self.nodejs_start_btn.config(state=tk.NORMAL)
                self.nodejs_stop_btn.config(state=tk.DISABLED)
                self.nodejs_restart_btn.config(state=tk.DISABLED)
                self.node_console.insert(tk.END, "\nNode.js server stopped\n")
                self.log_message("Node.js server stopped")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menghentikan Node.js: {str(e)}")
                self.log_message(f"Gagal menghentikan Node.js: {str(e)}")
        else:
            self.node_console.insert(tk.END, "\nNo Node.js server running\n")

    def restart_nodejs(self):
        """Restart the Node.js server"""
        if hasattr(self, 'node_process') and self.node_process:
            self.stop_nodejs()
            # Small delay to ensure process is fully stopped
            self.root.after(500, self.start_nodejs)
        else:
            self.start_nodejs()
            
    def open_pyserver_menu(self):
        """Buka Menu Utama Pyserver Python Running"""
        laragon_path = r"C:\xampp\pyserver\pyserver.exe"  # Default Pyserver path
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path pyserver.exe tidak ditemukan!\nDefault path: C:\\xampp\\pyserver\\pyserver.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama Pyserver")
        except Exception as e:
            self.log_message(f"Gagal membuka menu Pyserver: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu Pyserver: {str(e)}")
        
    
    def create_laravel_tab(self, parent):
        """Create Laravel Server tab with more complete Laravel features"""
        self.laravel_tab = parent

        # Composer section
        composer_frame = ttk.LabelFrame(parent, text="Composer", padding="10")
        composer_frame.pack(fill=tk.X, pady=(0, 10))

        composer_path_frame = ttk.Frame(composer_frame)
        composer_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(composer_path_frame, text="Composer Path:").pack(side=tk.LEFT)
        self.composer_path_entry = ttk.Entry(composer_path_frame)
        self.composer_path_entry.insert(0, self.default_paths['composer'])
        self.composer_path_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        composer_browse_btn = ttk.Button(composer_path_frame, text="Browse...", command=lambda: self.browse_executable(self.composer_path_entry))
        composer_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        composer_btn_frame = ttk.Frame(composer_frame)
        composer_btn_frame.pack(fill=tk.X)
        ttk.Button(composer_btn_frame, text="Update Composer", command=self.update_composer).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(composer_btn_frame, text="Show Version", command=self.show_composer_version).pack(side=tk.LEFT)

        # Laravel section
        laravel_frame = ttk.LabelFrame(parent, text="Laravel", padding="10")
        laravel_frame.pack(fill=tk.X, pady=(0, 10))

        laravel_project_frame = ttk.Frame(laravel_frame)
        laravel_project_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(laravel_project_frame, text="Project Directory:").pack(side=tk.LEFT)
        self.laravel_project_entry = ttk.Entry(laravel_project_frame)
        self.laravel_project_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        laravel_browse_btn = ttk.Button(laravel_project_frame, text="Browse...", command=lambda: self.browse_directory(self.laravel_project_entry))
        laravel_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        laravel_btn_frame = ttk.Frame(laravel_frame)
        laravel_btn_frame.pack(fill=tk.X)
        ttk.Button(laravel_btn_frame, text="Create New Project", command=self.create_laravel_project).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(laravel_btn_frame, text="Start Dev Server", command=self.start_laravel_server).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(laravel_btn_frame, text="Open in Browser", command=self.open_laravel_in_browser).pack(side=tk.LEFT, padx=(0, 5))
        self.laragon_menu_btn = ttk.Button(laravel_btn_frame, text="Open Laragon Menu Server Host", command=self.open_laragon_menu)
        self.laragon_menu_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Laravel CLI commands section
        cli_frame = ttk.LabelFrame(parent, text="Laravel Artisan Commands", padding="10")
        cli_frame.pack(fill=tk.X, pady=(0, 10))

        def run_artisan_command(command, show_output=True):
            project_dir = self.laravel_project_entry.get()
            php_path = self.php_path_entry.get()
            if not project_dir or not os.path.isdir(project_dir):
                messagebox.showerror("Error", "Project directory tidak valid!")
                return
            if not php_path or not os.path.isfile(php_path):
                messagebox.showerror("Error", "PHP path tidak valid!")
                return
            cmd = [php_path, "artisan"] + command.split()
            self.log_message(f"Menjalankan: {' '.join(cmd)}")
            def run():
                try:
                    result = subprocess.run(
                        cmd,
                        cwd=project_dir,
                        capture_output=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    if show_output:
                        output = result.stdout + ("\n" + result.stderr if result.stderr else "")
                        self.root.after(0, lambda: messagebox.showinfo("Artisan Output", output))
                    self.root.after(0, self.log_message, f"Artisan selesai: {command}")
                except Exception as e:
                    self.root.after(0, self.log_message, f"Error artisan: {str(e)}")
                    if show_output:
                        self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
            threading.Thread(target=run, daemon=True).start()

        cli_btn_frame = ttk.Frame(cli_frame)
        cli_btn_frame.pack(fill=tk.X)
        ttk.Button(cli_btn_frame, text="Migrate", command=lambda: run_artisan_command("migrate")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="Migrate Fresh", command=lambda: run_artisan_command("migrate:fresh")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="DB Seed", command=lambda: run_artisan_command("db:seed")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="Config Cache", command=lambda: run_artisan_command("config:cache")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="Route List", command=lambda: run_artisan_command("route:list")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="Clear Cache", command=lambda: run_artisan_command("cache:clear")).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cli_btn_frame, text="View Log", command=lambda: self.open_laravel_log()).pack(side=tk.LEFT, padx=(0, 5))

        # Laravel generator section
        generator_frame = ttk.LabelFrame(parent, text="Laravel Generator", padding="10")
        generator_frame.pack(fill=tk.X, pady=(0, 10))

        gen_type_var = tk.StringVar(value="controller")
        gen_name_var = tk.StringVar()

        gen_type_menu = ttk.Combobox(generator_frame, textvariable=gen_type_var, values=[
            "controller", "model", "migration", "seeder", "factory", "middleware", "event", "listener", "job", "command"
        ], width=15, state="readonly")
        gen_type_menu.pack(side=tk.LEFT, padx=(0, 5))
        gen_name_entry = ttk.Entry(generator_frame, textvariable=gen_name_var, width=25)
        gen_name_entry.pack(side=tk.LEFT, padx=(0, 5))
        def generate_artisan():
            t = gen_type_var.get()
            n = gen_name_var.get()
            if not n:
                messagebox.showerror("Error", "Nama harus diisi!")
                return
            run_artisan_command(f"make:{t} {n}")
        ttk.Button(generator_frame, text="Generate", command=generate_artisan).pack(side=tk.LEFT, padx=(0, 5))

        # Laravel log viewer
        def open_laravel_log():
            project_dir = self.laravel_project_entry.get()
            log_path = os.path.join(project_dir, "storage", "logs", "laravel.log")
            if not os.path.isfile(log_path):
                messagebox.showerror("Error", "Log file tidak ditemukan!")
                return
            top = tk.Toplevel(self.root)
            top.title("Laravel Log Viewer")
            top.geometry("900x500")
            text_area = scrolledtext.ScrolledText(top, wrap=tk.NONE, font=("Consolas", 9))
            text_area.pack(fill=tk.BOTH, expand=True)
            try:
                with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
                    text_area.insert(tk.END, f.read())
            except Exception as e:
                text_area.insert(tk.END, f"Gagal membaca log: {str(e)}")
            text_area.see(tk.END)
            self.log_message("Menampilkan Laravel log")
        self.open_laravel_log = open_laravel_log

        # Laravel .env editor
        env_frame = ttk.LabelFrame(parent, text="Laravel .env Editor", padding="10")
        env_frame.pack(fill=tk.X, pady=(0, 10))
        def edit_env():
            project_dir = self.laravel_project_entry.get()
            env_path = os.path.join(project_dir, ".env")
            if not os.path.isfile(env_path):
                messagebox.showerror("Error", ".env file tidak ditemukan!")
                return
            os.startfile(env_path)
            self.log_message("Membuka .env file")
        ttk.Button(env_frame, text="Edit .env", command=edit_env).pack(side=tk.LEFT, padx=(0, 5))

        # Laravel artisan custom command
        custom_frame = ttk.LabelFrame(parent, text="Custom Artisan Command", padding="10")
        custom_frame.pack(fill=tk.X, pady=(0, 10))
        custom_cmd_var = tk.StringVar()
        custom_entry = ttk.Entry(custom_frame, textvariable=custom_cmd_var, width=40)
        custom_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(custom_frame, text="Run", command=lambda: run_artisan_command(custom_cmd_var.get())).pack(side=tk.LEFT, padx=(0, 5))
    
    def open_laragon_menu(self):
        """Buka menu utama Laragon secara langsung"""
        laragon_path = r"c:\xampp\laragon\laragon.exe"  # Default Laragon path
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path laragon.exe tidak ditemukan!\nDefault path: C:\\laragon\\laragon.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama Laragon")
        except Exception as e:
            self.log_message(f"Gagal membuka menu Laragon: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu Laragon: {str(e)}")
    
    def create_admin_tools_tab(self, parent):
        """Create Admin Tools tab"""
        self.admin_tab = parent
        
        tools_frame = ttk.Frame(parent, padding="10")
        tools_frame.pack(fill=tk.BOTH, expand=True)
        
        # PHP tools
        php_tools_frame = ttk.LabelFrame(tools_frame, text="PHP Tools", padding="10")
        php_tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        php_info_btn = ttk.Button(php_tools_frame, text="PHP Info", command=self.show_php_info)
        php_info_btn.pack(fill=tk.X, pady=(0, 5))
        
        php_ini_btn = ttk.Button(php_tools_frame, text="Nested PHP Info", command=self.edit_php_ini)
        php_ini_btn.pack(fill=tk.X, pady=(0, 5))
        
        
        php_ini_btn = ttk.Button(php_tools_frame, text="Set Weather Server", command=self.server_weather_api_key)
        php_ini_btn.pack(fill=tk.X, pady=(0, 5))
        
        php_ini_btn = ttk.Button(php_tools_frame, text="License Awan Server", command=self.information)
        php_ini_btn.pack(fill=tk.X, pady=(0, 5))
        
        
        # Database tools
        db_tools_frame = ttk.LabelFrame(tools_frame, text="Database Tools", padding="10")
        db_tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        adminer_btn = ttk.Button(db_tools_frame, text="Adminer (Database Manager)", command=self.launch_adminer)
        adminer_btn.pack(fill=tk.X, pady=(0, 5))
        
        phpmyadmin_btn = ttk.Button(db_tools_frame, text="phpMyAdmin", command=self.launch_phpmyadmin)
        phpmyadmin_btn.pack(fill=tk.X, pady=(0, 5))
        
        backup_btn = ttk.Button(db_tools_frame, text="Backup Database", command=self.backup_database)
        backup_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        restore_btn = ttk.Button(db_tools_frame, text="Restore Database", command=self.restore_database)
        restore_btn.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # System tools
        sys_tools_frame = ttk.LabelFrame(tools_frame, text="System Tools", padding="10")
        sys_tools_frame.pack(fill=tk.X, pady=(0, 10))
        
        ports_btn = ttk.Button(sys_tools_frame, text="Cek Port yang Digunakan", command=self.check_used_ports)
        ports_btn.pack(fill=tk.X, pady=(0, 5))
        
        services_btn = ttk.Button(sys_tools_frame, text="Cek Windows Services", command=self.check_windows_services)
        services_btn.pack(fill=tk.X, pady=(0, 5))
        
        # XAMPP tools
        xampp_tools_frame = ttk.LabelFrame(tools_frame, text="XAMPP Tools", padding="10")
        xampp_tools_frame.pack(fill=tk.X)
        
        xampp_control_btn = ttk.Button(xampp_tools_frame, text="XAMPP Control Panel", command=self.open_xampp_control)
        xampp_control_btn.pack(fill=tk.X, pady=(0, 5))
        
        xampp_shell_btn = ttk.Button(xampp_tools_frame, text="XAMPP Shell", command=self.open_xampp_shell)
        xampp_shell_btn.pack(fill=tk.X)

    def server_weather_api_key(self):
        """Set or show the server weather API key and provide weather search functionality"""
        import tkinter as tk
        from tkinter import simpledialog, messagebox, Toplevel, Label, Entry, Button
        import requests
        import json
        
        # API key management
        api_key = getattr(self, '_weather_api_key', '2686cbd9ceb0896ba3999b20e8a4406d')
        
        # Ask for new API key if needed
        new_key = simpledialog.askstring(
            "Weather API Key",
            "Enter Weather API Key (OpenWeatherMap):",
            initialvalue=api_key,
            parent=self.root
        )
        
        if new_key is not None:
            self._weather_api_key = new_key
            masked_key = f"{new_key[:6]}{'*' * (len(new_key)-6)}" if len(new_key) > 6 else new_key
            self.log_message(f"Weather API key updated: {masked_key}")
            api_key = new_key
        
        # Create search window
        search_window = Toplevel(self.root)
        search_window.title("Weather Search")
        search_window.geometry("400x200")
        
        Label(search_window, text="Enter Location (City or City,Country):").pack(pady=10)
        location_entry = Entry(search_window, width=40)
        location_entry.pack(pady=5)
        
        def fetch_weather():
            location = location_entry.get().strip()
            if not location:
                messagebox.showerror("Error", "Please enter a location")
                return
            
            try:
                # Fetch weather data
                base_url = "http://api.openweathermap.org/data/2.5/weather"
                params = {
                    'q': location,
                    'appid': api_key,
                    'units': 'metric',  # For Celsius
                    'lang': 'id'  # Indonesian language
                }
                
                response = requests.get(base_url, params=params)
                data = response.json()
                
                if response.status_code != 200:
                    raise Exception(data.get('message', 'Unknown error from weather API'))
                
                # Parse weather data
                city = data['name']
                country = data['sys']['country']
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                pressure = data['main']['pressure']
                wind_speed = data['wind']['speed']
                wind_deg = data['wind'].get('deg', 0)
                weather_desc = data['weather'][0]['description'].capitalize()
                visibility = data.get('visibility', 'N/A')
                clouds = data['clouds']['all']
                lat = data['coord']['lat']
                lon = data['coord']['lon']
                
                # Wind direction calculation
                directions = ['Utara', 'Timur Laut', 'Timur', 'Tenggara', 
                            'Selatan', 'Barat Daya', 'Barat', 'Barat Laut']
                wind_dir = directions[round(wind_deg / 45) % 8] if 'deg' in data['wind'] else 'Tidak diketahui'
                
                # Create detailed weather report
                weather_report = (
                    f"Lokasi: {city}, {country}\n"
                    f"Koordinat: {lat:.4f}°N, {lon:.4f}°E\n\n"
                    f"Kondisi cuaca: {weather_desc}\n"
                    f"Suhu: {temp}°C (Terasa seperti: {feels_like}°C)\n"
                    f"Kelembaban: {humidity}%\n"
                    f"Tekanan: {pressure} hPa\n"
                    f"Angin: {wind_speed} m/s ({wind_dir})\n"
                    f"Visibilitas: {visibility if visibility != 'N/A' else 'Tidak tersedia'} meter\n"
                    f"Persentase awan: {clouds}%"
                )
                
                # Show weather information
                messagebox.showinfo(
                    f"Informasi Cuaca untuk {city}, {country}",
                    weather_report
                )
                self.log_message(f"Weather data retrieved for {city}, {country}")
                
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Gagal mendapatkan data cuaca: {str(e)}\n"
                    f"Pastikan API key valid dan nama lokasi benar."
                )
                self.log_message(f"Error getting weather data for {location}: {str(e)}")
        
        search_button = Button(search_window, text="Search Weather", command=fetch_weather)
        search_button.pack(pady=15)
        
        # Add close button
        Button(search_window, text="Close", command=search_window.destroy).pack()
    
    def create_terminal_tab(self, parent):
        """Create Terminal tab with command buttons"""
        self.terminal_tab = parent
        
        terminal_frame = ttk.Frame(parent)
        terminal_frame.pack(fill=tk.BOTH, expand=True)
        
        # Command buttons frame
        cmd_btn_frame = ttk.Frame(terminal_frame)
        cmd_btn_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Common command buttons
        # Load awan.ico icon for buttons if available
        try:
            wsl_icon_img = Image.open("awan.ico").resize((16, 16))
            self.wsl_icon = ImageTk.PhotoImage(wsl_icon_img)
        except Exception:
            self.wsl_icon = None

        ttk.Button(cmd_btn_frame, text="CMD", command=self.open_cmd, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="PowerShell", command=self.open_powershell, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="Git Bash", command=self.open_git_bash, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="MySQL Shell", command=self.open_mysql_shell, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="WSL Linux", command=self.open_wsl, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(cmd_btn_frame, text="Cloud Shell", command=self.cloud, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="IObit Unlock", command=self.unlocker, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="Cache Trash", command=self.Deles, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="Healty System", command=self.Emu, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(cmd_btn_frame, text="Notpad++", command=self.note, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(cmd_btn_frame, text="Ino", command=self.patch_ino_setup_compiler, image=self.wsl_icon, compound=tk.LEFT).pack(side=tk.LEFT, padx=(0, 5))
        
        # Terminal output
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame, 
            wrap=tk.WORD, 
            width=100, 
            height=20,
            font=('Consolas', 9)
        )

        try:
            terminal_icon_img = Image.open("awan.ico").resize((24, 24))
            self.terminal_icon = ImageTk.PhotoImage(terminal_icon_img)
        except Exception:
            self.terminal_icon = None

        # Insert logo as image at the top of the text widget
        if self.terminal_icon:
            self.terminal_output.image_create(tk.END, image=self.terminal_icon)
            self.terminal_output.insert(tk.END, "\n")

        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        self.terminal_output.insert(tk.END, "Terminal commands:\n")
        self.terminal_output.insert(tk.END, "- Klik tombol di atas untuk membuka terminal tertentu\n")
        self.terminal_output.insert(tk.END, "Awan Server - Enhanced 3 End\n")
        self.terminal_output.insert(tk.END, "Dibuat oleh Dwi Bakti N Dev\n")
            
    def open_Lnx(self):
        """Membuka terminal/command line interface untuk operasi hacking."""
        import tkinter as tk
        from tkinter import messagebox
        
        # Membuka terminal (versi cross-platform)
        try:
            if os.name == 'posix':  # Linux/Unix
                os.system('x-terminal-emulator &')  # Terminal default
            elif os.name == 'nt':    # Windows
                os.system('start cmd')
        except Exception as e:
            print(f"Gagal membuka terminal: {e}")
        
        # Menampilkan pop-up instalasi Metasploit
        install_info = """
        Instalasi Metasploit Framework:
        
        # Untuk Debian/Ubuntu/Kali
        sudo apt update
        sudo apt install metasploit-framework

        # Untuk Arch Linux
        sudo pacman -S metasploit

        # Untuk Fedora
        sudo dnf install metasploit-framework
        
        # Instal Nmap
        sudo apt install nmap          # Debian/Ubuntu
        sudo pacman -S nmap            # Arch
        sudo dnf install nmap          # Fedora
        
        # Instal Wireshark
        sudo apt install wireshark     # Debian/Ubuntu
        sudo pacman -S wireshark-qt    # Arch
        sudo dnf install wireshark     # Fedora
        
        # Instal John the Ripper
        sudo apt install john          # Debian/Ubuntu
        sudo pacman -S john            # Arch
        sudo dnf install john          # Fedora
        
        # Instal Aircrack-ng
        sudo apt install aircrack-ng   # Debian/Ubuntu
        sudo pacman -S aircrack-ng     # Arch
        sudo dnf install aircrack-ng   # Fedora
        """
        
        messagebox.showinfo(
            title="Instalasi Tools Hacking", 
            message=install_info,
            detail="Pastikan Anda memiliki hak akses root/sudo"
        )
                
    
    
    
    
    
    
    def create_terminal_tab2(self, parent):
        """Create Web Editor tab with HTML/CSS/JS features and server preview"""
        self.terminal_tab2 = parent
        web_frame = ttk.Frame(parent)
        web_frame.pack(fill=tk.BOTH, expand=True)

        # Top bar with buttons and help
        top_frame = ttk.Frame(web_frame)
        top_frame.pack(fill=tk.X, pady=(0, 2))
        
        # Help button with web development info
        def show_help():
            help_text = """Web Editor Usage:
            
    - Load: Open web files (.html, .css, .js)
    - Save: Save web code to file
    - Preview: View in web browser
    - Terminal: Show output in terminal panel

    Features:
    - HTML/CSS/JS editing
    - Live server preview
    - Basic syntax highlighting
    - Line numbers

    Server Information:
    When you click Preview, it will:
    1. Start a local server
    2. Open your default browser
    3. Show "Server running" status
    4. Display your web content"""

            help_dialog = tk.Toplevel()
            help_dialog.title("Web Editor Help")
            help_dialog.resizable(False, False)
            
            text = tk.Text(help_dialog, wrap=tk.WORD, width=60, height=18, 
                        font=('Segoe UI', 9), padx=10, pady=10)
            text.insert(tk.END, help_text)
            text.config(state="disabled")
            text.pack(fill=tk.BOTH, expand=True)
            
            ttk.Button(help_dialog, text="Close", 
                    command=help_dialog.destroy).pack(pady=5)
        
        ttk.Button(top_frame, text="?", width=2, command=show_help).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(top_frame, text="Web Editor:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        # Buttons
        preview_btn = ttk.Button(top_frame, text="Preview", width=10, command=self.preview_in_browser)
        preview_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        terminal_btn = ttk.Button(top_frame, text="Terminal", width=8, command=self.open_cmd)
        terminal_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        save_btn = ttk.Button(top_frame, text="Save", width=8, command=self.save_web_code)
        save_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        load_btn = ttk.Button(top_frame, text="Load", width=8, command=self.load_web_code)
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        preview_btn = ttk.Button (top_frame, text = "Compile", width = 8, command= self.open_html_menu_apk)
        preview_btn.pack (side = tk.RIGHT, padx= (2, 0))
        
        preview_btn = ttk.Button (top_frame, text = "HTMX", width = 8, command= self.open_HTMX)
        preview_btn.pack (side = tk.RIGHT, padx= (2, 0))

        # Main editor with line numbers
        editor_frame = ttk.Frame(web_frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = tk.Text(
            editor_frame,
            width=4,
            padx=4,
            pady=2,
            takefocus=0,
            border=0,
            background="#f0f0f0",
            foreground="#555",
            state="disabled",
            font=('Consolas', 9)
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Text editor
        self.web_editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            width=80,
            height=20,
            font=('Consolas', 10),
            undo=True,
            maxundo=-1,
            background="white",
            foreground="black",
            insertbackground="black",
            selectbackground="#b5d5ff",
            selectforeground="black",
            padx=5,
            pady=5
        )
        self.web_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_frame, command=self.web_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.web_editor.config(yscrollcommand=scrollbar.set)

        # Output panel
        output_frame = ttk.LabelFrame(web_frame, text="Server Output", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 0))
        
        self.server_output = tk.Text(
            output_frame,
            wrap=tk.WORD,
            height=6,
            font=('Consolas', 9),
            background="#f8f8f8",
            foreground="#333",
            state="disabled"
        )
        self.server_output.pack(fill=tk.BOTH, expand=True)

        # Line number update function
        def update_line_numbers(event=None):
            lines = self.web_editor.get(1.0, "end-1c").split('\n')
            line_numbers_text = "\n".join(str(i) for i in range(1, len(lines)+1))
            self.line_numbers.config(state="normal")
            self.line_numbers.delete(1.0, tk.END)
            self.line_numbers.insert(1.0, line_numbers_text)
            self.line_numbers.config(state="disabled")
            
            # Auto-resize line numbers width
            max_width = len(str(len(lines))) + 1
            self.line_numbers.config(width=max_width if max_width > 3 else 3)

        # Bind events for line numbers
        self.web_editor.bind("<KeyRelease>", update_line_numbers)
        self.web_editor.bind("<MouseWheel>", update_line_numbers)
        self.web_editor.bind("<Button-1>", update_line_numbers)
        self.web_editor.bind("<<Paste>>", update_line_numbers)
        update_line_numbers()

    def load_web_code(self):
        """Load web code from a file"""
        file_path = filedialog.askopenfilename(
            title="Select Web File",
            filetypes=[("HTML Files", "*.html"), ("CSS Files", "*.css"), 
                    ("JS Files", "*.js"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                self.web_editor.delete(1.0, tk.END)
                self.web_editor.insert(tk.END, code)
                self.log_message(f"Loaded web file: {file_path}")
        except Exception as e:
            self.log_message(f"Error loading web file: {str(e)}", level="error")
            messagebox.showerror("Error", f"Failed to load web file:\n{str(e)}")

    def save_web_code(self):
        """Save the web code to a file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Web File",
            defaultextension=".html",
            filetypes=[("HTML Files", "*.html"), ("CSS Files", "*.css"), 
                    ("JS Files", "*.js"), ("All Files", "*.*")]
        )
        if not file_path:
            return
            
        try:
            code = self.web_editor.get(1.0, tk.END)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
                self.log_message(f"Saved web file: {file_path}")
                messagebox.showinfo("Saved", f"Web file saved:\n{file_path}")
        except Exception as e:
            self.log_message(f"Error saving web file: {str(e)}", level="error")
            messagebox.showerror("Error", f"Failed to save web file:\n{str(e)}")

    def preview_in_browser(self):
        """Preview web content with server simulation"""
        code = self.web_editor.get(1.0, tk.END).strip()
        if not code:
            self.log_message("No content to preview", level="warning")
            return
        
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile("w", delete=False, suffix=".html", encoding="utf-8") as f:
                f.write(code)
                temp_path = f.name
                
            # Update server output
            self.server_output.config(state="normal")
            self.server_output.delete(1.0, tk.END)
            self.server_output.insert(tk.END, "Server running at http://localhost:8000\n")
            self.server_output.insert(tk.END, f"Serving file: {temp_path}\n")
            self.server_output.insert(tk.END, "Press Ctrl+C in terminal to stop server")
            self.server_output.config(state="disabled")
            
            # Open in browser (simulating server)
            webbrowser.open(f"file:///{temp_path}")
            self.log_message("Preview opened in browser with server simulation")
            
        except Exception as e:
            self.log_message(f"Preview error: {str(e)}", level="error")
            messagebox.showerror("Preview Error", f"Failed to preview:\n{str(e)}")
            
            
    
    
    
    def create_encryption_tab(self, parent):
        """Create tab for file encryption/decryption"""
        self.encryption_tab = parent
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        # Top bar
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=(0, 2))

        ttk.Label(top_frame, text="File Encryption/Decryption:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        
        encrypt_btn = ttk.Button(top_frame, text="Encrypt", width=10, command=self.encrypt_file_content)
        encrypt_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        decrypt_btn = ttk.Button(top_frame, text="Decrypt", width=10, command=self.decrypt_file_content)
        decrypt_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        save_btn = ttk.Button(top_frame, text="Save", width=8, command=self.save_encrypted_file)
        save_btn.pack(side=tk.RIGHT, padx=(2, 0))
        
        load_btn = ttk.Button(top_frame, text="Load", width=8, command=self.load_file_content)
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))

        # Editor
        editor_frame = ttk.Frame(frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.encryption_editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            width=80,
            height=18,
            font=('Consolas', 10),
            undo=True,
            maxundo=-1,
            background="white",
            foreground="black",
            insertbackground="black",
            selectbackground="#b5d5ff",
            selectforeground="black",
            padx=5,
            pady=5
        )
        self.encryption_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_frame, command=self.encryption_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.encryption_editor.config(yscrollcommand=scrollbar.set)

        # Status bar
        status_frame = ttk.Frame(frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.encryption_status = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.encryption_status.pack(fill=tk.X)
        
        # Store original file extension
        self.current_file_extension = None

    def encrypt_file_content(self):
        """Encrypt file content while maintaining the ability to decrypt it later"""
        content = self.encryption_editor.get(1.0, tk.END).strip()
        if not content:
            self.encryption_status.config(text="Error: No content to encrypt")
            return
        
        try:
            import base64
            import zlib
            
            # Compress and encode the content
            compressed = zlib.compress(content.encode('utf-8'))
            encrypted = base64.b64encode(compressed).decode('utf-8')
            
            # Create a wrapper that clearly marks this as encrypted content
            wrapper = f"""=== ENCRYPTED FILE ===
    Original extension: {self.current_file_extension or 'txt'}
    === DO NOT MODIFY THIS HEADER ===
    {encrypted}"""
            
            self.encryption_editor.delete(1.0, tk.END)
            self.encryption_editor.insert(tk.END, wrapper)
            self.encryption_status.config(text="Content encrypted successfully")
        except Exception as e:
            self.encryption_status.config(text=f"Encryption error: {str(e)}")

    def decrypt_file_content(self):
        """Decrypt previously encrypted file content"""
        content = self.encryption_editor.get(1.0, tk.END).strip()
        if not content:
            self.encryption_status.config(text="Error: No content to decrypt")
            return
        
        try:
            # Check if this is our format
            if "=== ENCRYPTED FILE ===" not in content:
                self.encryption_status.config(text="Error: Not a recognized encrypted format")
                return
                
            # Extract the original extension
            ext_line = [line for line in content.split('\n') if "Original extension:" in line]
            if ext_line:
                self.current_file_extension = ext_line[0].split(":")[1].strip()
                
            # Extract the encrypted part (everything after the header)
            encrypted = content.split("=== DO NOT MODIFY THIS HEADER ===\n")[-1].strip()
            
            # Decode and decompress
            import base64
            import zlib
            decoded = base64.b64decode(encrypted)
            decompressed = zlib.decompress(decoded).decode('utf-8')
            
            self.encryption_editor.delete(1.0, tk.END)
            self.encryption_editor.insert(tk.END, decompressed)
            self.encryption_status.config(text="Content decrypted successfully")
        except Exception as e:
            self.encryption_status.config(text=f"Decryption error: {str(e)}")

    def save_encrypted_file(self):
        """Save encrypted/decrypted content to file"""
        if not self.current_file_extension:
            # Default to .txt if no extension is known
            self.current_file_extension = "txt"
        
        file_path = filedialog.asksaveasfilename(
            title="Save File",
            defaultextension=f".{self.current_file_extension}",
            filetypes=[("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            content = self.encryption_editor.get(1.0, tk.END)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.encryption_status.config(text=f"Saved to: {file_path}")
        except Exception as e:
            self.encryption_status.config(text=f"Error saving file: {str(e)}")

    def load_file_content(self):
        """Load file content from any file"""
        file_path = filedialog.askopenfilename(
            title="Select File",
            filetypes=[("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            # Store the original file extension
            import os
            self.current_file_extension = os.path.splitext(file_path)[1][1:]  # Remove the dot
            
            # Try to read as text first
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                # If UTF-8 fails, try reading as binary and encode as base64
                with open(file_path, "rb") as f:
                    import base64
                    content = base64.b64encode(f.read()).decode('ascii')
                    self.encryption_status.config(text="Loaded binary file (base64 encoded)")
            
            self.encryption_editor.delete(1.0, tk.END)
            self.encryption_editor.insert(tk.END, content)
            self.encryption_status.config(text=f"Loaded: {file_path}")
        except Exception as e:
            self.encryption_status.config(text=f"Error loading file: {str(e)}")
    
    
    
    
    
    
    
    
    
    
    
    def create_terminal_tab3(self, parent):
        """Create Python Editor tab with code runner and interactive input/output panel"""
        self.terminal_tab3 = parent
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        # Top bar
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, pady=(0, 2))

        ttk.Label(top_frame, text="Python Editor:", font=("Segoe UI", 9)).pack(side=tk.LEFT)
        run_btn = ttk.Button(top_frame, text="Run ▶", width=8, command=self.run_python_editor_code)
        run_btn.pack(side=tk.RIGHT, padx=(2, 0))
        save_btn = ttk.Button(top_frame, text="Save", width=8, command=self.save_python_editor_code)
        save_btn.pack(side=tk.RIGHT, padx=(2, 0))
        load_btn = ttk.Button(top_frame, text="Load", width=8, command=self.load_python_editor_code)
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))
        load_btn = ttk.Button(top_frame, text="Compile Backend", width=8, command=self.open_linux_compile)
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))
        load_btn = ttk.Button(top_frame, text="Linux", width=8, command=self.open_Lnx)
        load_btn.pack(side=tk.RIGHT, padx=(2, 0))

        # Editor
        editor_frame = ttk.Frame(frame)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.python_editor = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            width=80,
            height=18,
            font=('Consolas', 10),
            undo=True,
            maxundo=-1,
            background="white",
            foreground="black",
            insertbackground="black",
            selectbackground="#b5d5ff",
            selectforeground="black",
            padx=5,
            pady=5
        )
        self.python_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_frame, command=self.python_editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.python_editor.config(yscrollcommand=scrollbar.set)

        # Output panel (interactive)
        output_frame = ttk.LabelFrame(frame, text="Output (Interactive)", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=False, pady=(5, 0))
        self.python_output = tk.Text(
            output_frame,
            wrap=tk.WORD,
            height=8,
            font=('Consolas', 9),
            background="#f8f8f8",
            foreground="#333",
            state="normal"
        )
        self.python_output.pack(fill=tk.BOTH, expand=True)
        self.python_output.config(state="disabled")

        # Input entry for interactive input()
        input_bar = ttk.Frame(output_frame)
        input_bar.pack(fill=tk.X, pady=(2, 0))
        ttk.Label(input_bar, text="Input:").pack(side=tk.LEFT)
        self.python_input_entry = ttk.Entry(input_bar)
        self.python_input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        send_btn = ttk.Button(input_bar, text="Send", command=self._send_python_input)
        send_btn.pack(side=tk.LEFT, padx=(5, 0))

        self._python_input_queue = []
        self._python_input_event = threading.Event()
        self._python_running = False

    def _send_python_input(self):
        """Send input from entry to the running code"""
        if not self._python_running:
            return
        value = self.python_input_entry.get()
        self.python_input_entry.delete(0, tk.END)
        self._python_input_queue.append(value)
        self._python_input_event.set()

    def run_python_editor_code(self):
        """Run code from Python editor and show output in output panel with interactive input() support"""
        code = self.python_editor.get(1.0, tk.END)
        self.python_output.config(state="normal")
        self.python_output.delete(1.0, tk.END)
        self.python_output.config(state="disabled")
        self._python_input_queue = []
        self._python_input_event = threading.Event()
        self._python_running = True

        def custom_input(prompt=""):
            # Show prompt in output
            self.python_output.config(state="normal")
            self.python_output.insert(tk.END, prompt)
            self.python_output.see(tk.END)
            self.python_output.config(state="disabled")
            # Wait for user input
            self._python_input_event.clear()
            self.python_input_entry.focus_set()
            self._python_input_event.wait()
            value = self._python_input_queue.pop(0)
            self.python_output.config(state="normal")
            self.python_output.insert(tk.END, value + "\n")
            self.python_output.see(tk.END)
            self.python_output.config(state="disabled")
            return value

        def run_code():
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
                    # Provide custom input() to code
                    exec(code, {"input": custom_input})
            except Exception as e:
                buf.write(f"\nError: {e}\n")
            output = buf.getvalue()
            self.python_output.config(state="normal")
            self.python_output.insert(tk.END, output)
            self.python_output.see(tk.END)
            self.python_output.config(state="disabled")
            self._python_running = False

        threading.Thread(target=run_code, daemon=True).start()

    def save_python_editor_code(self):
        """Save Python code to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Python File",
            defaultextension=".py",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            code = self.python_editor.get(1.0, tk.END)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            self.log_message(f"Saved Python file: {file_path}")
            messagebox.showinfo("Saved", f"Python file saved:\n{file_path}")
        except Exception as e:
            self.log_message(f"Error saving Python file: {str(e)}")
            messagebox.showerror("Error", f"Failed to save Python file:\n{str(e)}")

    def load_python_editor_code(self):
        """Load Python code from file"""
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
                self.python_editor.delete(1.0, tk.END)
                self.python_editor.insert(tk.END, code)
            self.log_message(f"Loaded Python file: {file_path}")
        except Exception as e:
            self.log_message(f"Error loading Python file: {str(e)}")
            messagebox.showerror("Error", f"Failed to load Python file:\n{str(e)}")
            
    def open_html_menu_apk(self):
        """Buka Menu Utama Compile Html To Apk"""
        laragon_path = r"c:\xampp\html\main.exe"  # Default Laragon path
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path main.exe tidak ditemukan!\nDefault path: c:\\xampp\\html\\main.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama Html To Apk")
        except Exception as e:
            self.log_message(f"Gagal membuka menu Html To Apk: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu Html To Apk: {str(e)}")
            
            
    def open_linux_compile(self):
        """Buka menu utama Linux Compile"""
        laragon_path = r"c:\xampp\linux\Compile Pinguin.exe"  # Default Laragon path
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path Compile pinguin.exe tidak ditemukan!\nDefault path: c:\\xampp\\linux\\Compile Pinguin.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama Linux Compile")
        except Exception as e:
            self.log_message(f"Gagal membuka menu Linux Compile: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu Linux Compile: {str(e)}")
            
        
    def create_go_tab(self, parent):
        """Create simplified Go project tab with essential features"""
        self.go_tab = parent
        
        # Project Creation Section
        project_frame = ttk.LabelFrame(parent, text="Go Project", padding=10)
        project_frame.pack(fill=tk.X, pady=5, padx=5)

        # Project Name
        ttk.Label(project_frame, text="Project Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.go_project_name_entry = ttk.Entry(project_frame)
        self.go_project_name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        # Project Location
        ttk.Label(project_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=2)
        location_frame = ttk.Frame(project_frame)
        location_frame.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.go_project_location_entry = ttk.Entry(location_frame)
        self.go_project_location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(location_frame, text="...", width=3,
                command=lambda: self.browse_directory(self.go_project_location_entry)).pack(side=tk.LEFT, padx=2)

        # Go Executable Path
        ttk.Label(project_frame, text="Go Path:").grid(row=2, column=0, sticky=tk.W, pady=2)
        go_path_frame = ttk.Frame(project_frame)
        go_path_frame.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=2)
        self.go_path_entry = ttk.Entry(go_path_frame)
        self.go_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.go_path_entry.insert(0, self.default_paths.get('go', ''))
        ttk.Button(go_path_frame, text="...", width=3,
                command=lambda: self.browse_executable(self.go_path_entry)).pack(side=tk.LEFT, padx=2)

        # Project Buttons
        btn_frame = ttk.Frame(project_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=5)
        
        self.create_go_project_btn = ttk.Button(btn_frame, text="Create Project", 
                                            command=self.create_go_project)
        self.create_go_project_btn.pack(side=tk.LEFT, padx=2)
        
        self.run_go_project_btn = ttk.Button(btn_frame, text="Run",
                                            command=self.run_go_project)
        self.run_go_project_btn.pack(side=tk.LEFT, padx=2)
        self.run_go_project_btn.config(state=tk.DISABLED)
        
        self.stop_go_project_btn = ttk.Button(btn_frame, text="Stop",
                                            command=self.stop_go_project)
        self.stop_go_project_btn.pack(side=tk.LEFT, padx=2)
        self.stop_go_project_btn.config(state=tk.DISABLED)

        # Compile Section
        compile_frame = ttk.LabelFrame(parent, text="Compile to Executable", padding=10)
        compile_frame.pack(fill=tk.X, pady=5, padx=5)

        # Project to Compile
        ttk.Label(compile_frame, text="Project Dir:").grid(row=0, column=0, sticky=tk.W, pady=2)
        compile_dir_frame = ttk.Frame(compile_frame)
        compile_dir_frame.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.go_compile_project_entry = ttk.Entry(compile_dir_frame)
        self.go_compile_project_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(compile_dir_frame, text="...", width=3,
                command=lambda: self.browse_directory(self.go_compile_project_entry)).pack(side=tk.LEFT, padx=2)

        # Output Name
        ttk.Label(compile_frame, text="Output Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.go_exe_name_entry = ttk.Entry(compile_frame)
        self.go_exe_name_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)
        self.go_exe_name_entry.insert(0, "myapp")

        # Platform Selection
        ttk.Label(compile_frame, text="Platform:").grid(row=2, column=0, sticky=tk.W, pady=2)
        platform_frame = ttk.Frame(compile_frame)
        platform_frame.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        self.go_platform_var = tk.StringVar(value="windows")
        ttk.Radiobutton(platform_frame, text="Windows", variable=self.go_platform_var, value="windows").pack(side=tk.LEFT)
        ttk.Radiobutton(platform_frame, text="Linux", variable=self.go_platform_var, value="linux").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(platform_frame, text="Mac", variable=self.go_platform_var, value="darwin").pack(side=tk.LEFT)

        # Compile Button
        # First button on the left (column 0)
        self.compile_go_btn = ttk.Button(compile_frame, text="Compile", 
                                        command=self.compile_go_project)
        self.compile_go_btn.grid(row=3, column=0, pady=5, sticky="e")  # sticky="w" aligns left

        # Second button on the right (column 1)
        self.gotab_btn = ttk.Button(compile_frame, text="Golang Tab Pro", 
                                command=self.open_gotab)
        self.gotab_btn.grid(row=3, column=1, pady=5, sticky="e")  # sticky="e" aligns right

        # Output Console
        console_frame = ttk.LabelFrame(parent, text="Output", padding=3)
        console_frame.pack(fill=tk.BOTH, expand=True, pady=3, padx=3)
        
        # Create text widget with scrollbar
        self.go_output = tk.Text(console_frame, wrap=tk.WORD, height=4)
        scrollbar = ttk.Scrollbar(console_frame, command=self.go_output.yview)
        self.go_output.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.go_output.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Status Bar
        self.go_status = ttk.Label(parent, text="Ready", relief=tk.SUNKEN)
        self.go_status.pack(fill=tk.X, pady=(0, 5), padx=5)
        
        # Initialize server process variable
        self.go_server_process = None
        
        
    def open_gotab(self):
        """Buka menu utama Golang [PRO]"""
        laragon_path = r"c:\xampp\golang\golang.exe"  
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path [PRO] golang.exe tidak ditemukan!\nDefault path: c:\\xampp\\golang\\golang.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama Golang [PRO]")
        except Exception as e:
            self.log_message(f"Gagal membuka menu Golang [PRO]: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu Golang [PRO]: {str(e)}")
            
            
        
    def open_HTMX(self):
        """Buka menu utama HTMX [PRO]"""
        laragon_path = r"c:\xampp\htmx\htmx.exe"  
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path [PRO] htmx.exe tidak ditemukan!\nDefault path: c:\\xampp\\htmx\\htmx.exe")
            return
        try:
            subprocess.Popen([laragon_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka menu utama HTMX [PRO]")
        except Exception as e:
            self.log_message(f"Gagal membuka menu HTMX [PRO]: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuka menu HTMX [PRO]: {str(e)}")
        
        


    def create_go_project(self):
        """Create a basic Go project"""
        project_name = self.go_project_name_entry.get()
        project_location = self.go_project_location_entry.get()
        go_path = self.go_path_entry.get()
        
        if not all([project_name, project_location, go_path]):
            self.log_go_output("Error: All fields are required")
            return
        
        project_path = os.path.join(project_location, project_name)
        
        if os.path.exists(project_path):
            self.log_go_output(f"Error: Directory {project_path} already exists")
            return
        
        try:
            os.makedirs(project_path)
            
            # Create main.go file
            with open(os.path.join(project_path, "main.go"), "w") as f:
                f.write(f"""package main

    import "fmt"

    func main() {{
        fmt.Println("Hello, {project_name}!")
    }}
    """)
            
            # Create go.mod file
            with open(os.path.join(project_path, "go.mod"), "w") as f:
                f.write(f"""module {project_name}

    go 1.21
    """)
            
            self.log_go_output(f"Go project created at {project_path}")
            self.go_status.config(text="Project created")
            
            # Enable run button and set compile path
            self.run_go_project_btn.config(state=tk.NORMAL)
            self.go_compile_project_entry.delete(0, tk.END)
            self.go_compile_project_entry.insert(0, project_path)
            
        except Exception as e:
            self.log_go_output(f"Error creating project: {str(e)}")
            self.go_status.config(text=f"Error: {str(e)}")

    def compile_go_project(self):
        """Compile Go project to executable"""
        project_dir = self.go_compile_project_entry.get()
        exe_name = self.go_exe_name_entry.get()
        platform = self.go_platform_var.get()
        go_path = self.go_path_entry.get()

        if not all([project_dir, exe_name, go_path]):
            self.log_go_output("Error: Project directory, output name, and Go path are required")
            return

        if not os.path.isdir(project_dir):
            self.log_go_output(f"Error: Directory {project_dir} does not exist")
            return

        try:
            # Set environment variables
            env = os.environ.copy()
            env["GOOS"] = platform
            env["GOARCH"] = "amd64"  # Default to 64-bit

            # Determine output path
            output_path = os.path.join(project_dir, exe_name)
            if platform == "windows" and not output_path.endswith(".exe"):
                output_path += ".exe"

            # Build the command
            cmd = [go_path, "build", "-o", output_path]

            # Run the compilation
            self.log_go_output(f"Compiling for {platform}...")
            result = subprocess.run(cmd, cwd=project_dir, env=env, 
                                capture_output=True, text=True)

            if result.returncode == 0:
                self.log_go_output(f"Success! Executable created: {output_path}")
                self.go_status.config(text="Compilation successful")
            else:
                self.log_go_output(f"Compilation failed:")
                self.log_go_output(result.stderr)
                self.go_status.config(text="Compilation failed")

        except Exception as e:
            self.log_go_output(f"Error during compilation: {str(e)}")
            self.go_status.config(text=f"Error: {str(e)}")

    def run_go_project(self):
        """Run the Go project"""
        project_dir = self.go_compile_project_entry.get()
        go_path = self.go_path_entry.get()
        
        if not project_dir or not go_path:
            self.log_go_output("Error: Project directory and Go path are required")
            return
        
        if not os.path.isdir(project_dir):
            self.log_go_output(f"Error: Directory {project_dir} does not exist")
            return
        
        try:
            if self.go_server_process and self.go_server_process.poll() is None:
                self.log_go_output("Server is already running")
                return
            
            cmd = [go_path, "run", "."]
            
            self.go_server_process = subprocess.Popen(
                cmd,
                cwd=project_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            threading.Thread(
                target=self.read_go_process_output,
                args=(self.go_server_process.stdout, False),
                daemon=True
            ).start()
            
            threading.Thread(
                target=self.read_go_process_output,
                args=(self.go_server_process.stderr, True),
                daemon=True
            ).start()
            
            self.log_go_output("Running Go project...")
            self.run_go_project_btn.config(state=tk.DISABLED)
            self.stop_go_project_btn.config(state=tk.NORMAL)
            self.go_status.config(text="Project running")
            
        except Exception as e:
            self.log_go_output(f"Error running project: {str(e)}")
            self.go_status.config(text=f"Error: {str(e)}")

    def stop_go_project(self):
        """Stop the running Go project"""
        if self.go_server_process and self.go_server_process.poll() is None:
            try:
                if os.name == 'nt':
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.go_server_process.pid)], 
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    self.go_server_process.terminate()
                    try:
                        self.go_server_process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.go_server_process.kill()
                
                self.log_go_output("Project stopped")
                self.go_status.config(text="Project stopped")
                
            except Exception as e:
                self.log_go_output(f"Error stopping project: {str(e)}")
                self.go_status.config(text=f"Error: {str(e)}")
        else:
            self.log_go_output("No project is currently running")
        
        self.run_go_project_btn.config(state=tk.NORMAL)
        self.stop_go_project_btn.config(state=tk.DISABLED)

    def read_go_process_output(self, stream, is_error):
        """Read output from the Go process"""
        for line in iter(stream.readline, ''):
            if is_error:
                self.log_go_output(f"ERROR: {line.strip()}")
            else:
                self.log_go_output(line.strip())
        
        stream.close()

    def log_go_output(self, message):
        """Add message to Go output log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.go_output.insert(tk.END, f"[{timestamp}] {message}\n")
        self.go_output.see(tk.END)
        self.go_output.update()
    
    def create_docker_tab(self, parent):
        """Create Docker tab for running containers and creating new projects"""
        self.docker_tab = parent

        status_frame = ttk.Frame(parent, padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        self.docker_status_label = ttk.Label(status_frame, text="Status: Docker Tidak Aktif", style='Status.TLabel')
        self.docker_status_label.pack(side=tk.LEFT)
        
        # Compile Python to EXE section
        compile_frame = ttk.LabelFrame(parent, text="Compile Python ke EXE", padding="10")
        compile_frame.pack(fill=tk.X, pady=(0, 10))

        py_file_frame = ttk.Frame(compile_frame)
        py_file_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(py_file_frame, text="Python File:").pack(side=tk.LEFT)
        self.py_compile_file_entry = ttk.Entry(py_file_frame)
        self.py_compile_file_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        py_browse_btn = ttk.Button(py_file_frame, text="Browse...", 
                    command=lambda: self.browse_file(self.py_compile_file_entry, [("Python Files", "*.py"), ("All Files", "*.*")]))
        py_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        output_dir_frame = ttk.Frame(compile_frame)
        output_dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(output_dir_frame, text="Output Folder:").pack(side=tk.LEFT)
        self.py_compile_output_entry = ttk.Entry(output_dir_frame)
        self.py_compile_output_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        output_browse_btn = ttk.Button(output_dir_frame, text="Browse...", 
                        command=lambda: self.browse_directory(self.py_compile_output_entry))
        output_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        self.py_compile_onefile_var = tk.BooleanVar(value=True)
        onefile_cb = ttk.Checkbutton(compile_frame, text="One File (single exe)", variable=self.py_compile_onefile_var)
        onefile_cb.pack(anchor=tk.W, pady=(0, 5))

        compile_btn = ttk.Button(compile_frame, text="Compile ke EXE", command=self.compile_python_to_exe)
        compile_btn.pack(fill=tk.X, pady=(5, 0))
        
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        self.docker_start_btn = ttk.Button(control_frame, text="Start Docker", command=self.start_docker)
        self.docker_start_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.docker_stop_btn = ttk.Button(control_frame, text="Stop Docker", command=self.stop_docker, state=tk.DISABLED)
        self.docker_stop_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.docker_open_btn = ttk.Button(control_frame, text="Open Docker Desktop", command=self.open_docker_desktop)
        self.docker_open_btn.pack(side=tk.LEFT, padx=(0, 5))
        self.docker_ps_btn = ttk.Button(control_frame, text="List Containers", command=self.list_docker_containers)
        self.docker_ps_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Patch: Add button to run Docker project/server
        self.docker_run_btn = ttk.Button(control_frame, text="Run Project (docker build & run)", command=self.run_docker_project)
        self.docker_run_btn.pack(side=tk.LEFT, padx=(0, 5))

        # Project creation section
        project_frame = ttk.LabelFrame(parent, text="Buat Project Docker Baru", padding="10")
        project_frame.pack(fill=tk.X, pady=(0, 10))

        name_frame = ttk.Frame(project_frame)
        name_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(name_frame, text="Nama Project:").pack(side=tk.LEFT)
        self.docker_project_name_entry = ttk.Entry(name_frame)
        self.docker_project_name_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        dir_frame = ttk.Frame(project_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(dir_frame, text="Lokasi:").pack(side=tk.LEFT)
        self.docker_project_dir_entry = ttk.Entry(dir_frame)
        self.docker_project_dir_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        browse_btn = ttk.Button(dir_frame, text="Browse...", command=lambda: self.browse_directory(self.docker_project_dir_entry))
        browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        create_btn = ttk.Button(project_frame, text="Buat Project Docker", command=self.create_docker_project)
        create_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Add a new section for force run options
        force_run_frame = ttk.LabelFrame(parent, text="Force Run Docker Project", padding="10")
        force_run_frame.pack(fill=tk.X, pady=(0, 10))

        force_dir_frame = ttk.Frame(force_run_frame)
        force_dir_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(force_dir_frame, text="Project Directory:").pack(side=tk.LEFT)
        self.force_docker_dir_entry = ttk.Entry(force_dir_frame)
        self.force_docker_dir_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        force_browse_btn = ttk.Button(force_dir_frame, text="Browse...", 
                                    command=lambda: self.browse_directory(self.force_docker_dir_entry))
        force_browse_btn.pack(side=tk.LEFT, padx=(5, 0))

        force_options_frame = ttk.Frame(force_run_frame)
        force_options_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(force_options_frame, text="Force Options:").pack(side=tk.LEFT)
        self.force_rebuild_var = tk.BooleanVar(value=True)
        force_rebuild_cb = ttk.Checkbutton(force_options_frame, text="Force Rebuild", 
                                        variable=self.force_rebuild_var)
        force_rebuild_cb.pack(side=tk.LEFT, padx=(5, 0))
        
        self.force_remove_var = tk.BooleanVar(value=True)
        force_remove_cb = ttk.Checkbutton(force_options_frame, text="Remove Existing", 
                                        variable=self.force_remove_var)
        force_remove_cb.pack(side=tk.LEFT, padx=(5, 0))
        
        self.force_cleanup_var = tk.BooleanVar(value=False)
        force_cleanup_cb = ttk.Checkbutton(force_options_frame, text="Cleanup After", 
                                        variable=self.force_cleanup_var)
        force_cleanup_cb.pack(side=tk.LEFT, padx=(5, 0))

        force_run_btn = ttk.Button(force_run_frame, text="Force Run Project", 
                                command=self.force_run_docker_project,
                                style='Accent.TButton')
        force_run_btn.pack(fill=tk.X, pady=(5, 0))
        
    def compile_python_to_exe(self):
        """Compile selected Python file to EXE using pyinstaller"""
        py_file = self.py_compile_file_entry.get()
        output_dir = self.py_compile_output_entry.get()
        onefile = self.py_compile_onefile_var.get()

        if not py_file or not os.path.isfile(py_file):
            messagebox.showerror("Error", "File Python tidak valid!")
            return
        if not output_dir or not os.path.isdir(output_dir):
            messagebox.showerror("Error", "Output folder tidak valid!")
            return

        # Check pyinstaller
        try:
            result = subprocess.run(["pyinstaller", "--version"], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("pyinstaller tidak ditemukan")
        except Exception:
            messagebox.showerror("Error", "pyinstaller tidak ditemukan! Install dulu dengan: pip install pyinstaller")
            return

        cmd = ["pyinstaller", "--distpath", output_dir]
        if onefile:
            cmd.append("--onefile")
        cmd.append(py_file)

        self.log_message(f"Compile: {' '.join(cmd)}")

        def run_compile():
            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                while True:
                    line = proc.stdout.readline()
                    if line == '' and proc.poll() is not None:
                        break
                    if line:
                        self.root.after(0, self.log_message, "[pyinstaller] " + line.strip())
                if proc.poll() == 0:
                    self.root.after(0, self.log_message, "Compile selesai!")
                    messagebox.showinfo("Sukses", "Compile Python ke EXE selesai!")
                else:
                    self.root.after(0, self.log_message, "Compile gagal!")
                    messagebox.showerror("Error", "Compile Python ke EXE gagal!")
            except Exception as e:
                self.root.after(0, self.log_message, f"Compile error: {str(e)}")
            messagebox.showerror("Error", f"Compile error: {str(e)}")

        threading.Thread(target=run_compile, daemon=True).start()

    def force_run_docker_project(self):
        """Forcefully run a Docker project with additional options and patch for running"""
        project_dir = self.force_docker_dir_entry.get()
        if not project_dir:
            messagebox.showerror("Error", "Project directory harus dipilih!")
            return
        
        if not os.path.isdir(project_dir):
            messagebox.showerror("Error", f"Directory tidak ditemukan: {project_dir}")
            return
        
        # Get project name from directory name
        project_name = os.path.basename(os.path.normpath(project_dir))
        image_tag = f"{project_name.lower().replace(' ', '_')}:latest"
        container_name = f"{project_name.lower().replace(' ', '_')}_container"
        
        # Prepare commands based on options
        commands = []
        
        # Stop and remove existing container if needed
        if self.force_remove_var.get():
            commands.append(("Stop existing container", 
                        ["docker", "stop", container_name]))
            commands.append(("Remove existing container", 
                        ["docker", "rm", container_name]))
        
        # Build with --no-cache if force rebuild is selected
        build_cmd = ["docker", "build"]
        if self.force_rebuild_var.get():
            build_cmd.append("--no-cache")
        build_cmd.extend(["-t", image_tag, "."])
        commands.append(("Build Docker image", build_cmd))
        
        # Run command
        run_cmd = ["docker", "run", "--name", container_name]
        if self.force_cleanup_var.get():
            run_cmd.append("--rm")
        run_cmd.extend(["-it", image_tag])
        commands.append(("Run Docker container", run_cmd))
        
        # Cleanup image if needed
        if self.force_cleanup_var.get():
            commands.append(("Remove Docker image", 
                        ["docker", "rmi", image_tag]))
        
        # Run all commands in sequence
        def execute_commands():
            try:
                for desc, cmd in commands:
                    self.root.after(0, self.log_message, f"{desc}: {' '.join(cmd)}")
                    
                    proc = subprocess.Popen(
                        cmd,
                        cwd=project_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                    
                    while True:
                        line = proc.stdout.readline()
                        if line == '' and proc.poll() is not None:
                            break
                        if line:
                            self.root.after(0, self.log_message, f"[{desc}] {line.strip()}")
                    
                    if proc.poll() != 0:
                        self.root.after(0, self.log_message, f"{desc} gagal!")
                        if "Build" in desc or "Run" in desc:
                            messagebox.showerror("Error", f"{desc} gagal!")
                            return
                
                self.root.after(0, self.log_message, "Force run selesai!")
                messagebox.showinfo("Sukses", "Docker project force run selesai!")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error force run: {str(e)}")
                messagebox.showerror("Error", f"Force run gagal: {str(e)}")
        
        threading.Thread(target=execute_commands, daemon=True).start()

    def start_docker(self):
        """Try to start Docker Desktop with animated status and patch"""
        possible_paths = [
            r"C:\xampp\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files\Docker\Docker\Docker.exe",
            r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
        ]
        docker_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                docker_path = path
                break
        if not docker_path:
            messagebox.showerror("Error", "Docker Desktop tidak ditemukan!")
            return
        try:
            subprocess.Popen([docker_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Menjalankan Docker Desktop")
            self.is_docker_running = True
            self._animate_docker_status()
            self.docker_start_btn.config(state=tk.DISABLED)
            self.docker_stop_btn.config(state=tk.NORMAL)
        except Exception as e:
            self.log_message(f"Gagal menjalankan Docker: {str(e)}")

    def stop_docker(self):
        """Try to stop Docker Desktop (Windows only, force close) with animated status and patch"""
        try:
            subprocess.run(["taskkill", "/IM", "Docker Desktop.exe", "/F"], creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Docker Desktop dihentikan")
            self.is_docker_running = False
            self._animate_docker_status()
            self.docker_start_btn.config(state=tk.NORMAL)
            self.docker_stop_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.log_message(f"Gagal menghentikan Docker: {str(e)}")

    def _animate_docker_status(self, idx=0, text="Status: Docker Aktif"):
        """Animasi status Docker di label"""
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if getattr(self, "is_docker_running", False):
            display_text = text[idx:] + "   " + text[:idx]
            self.docker_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.docker_start_btn.config(state=tk.DISABLED)
            self.docker_stop_btn.config(state=tk.NORMAL)
            self.docker_tab.after(200, self._animate_docker_status, (idx + 1) % len(text), text)
        else:
            self.docker_status_label.config(
                text="Status: Docker Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.docker_start_btn.config(state=tk.NORMAL)
            self.docker_stop_btn.config(state=tk.DISABLED)

    def open_docker_desktop(self):
        """Open Docker Desktop if available"""
        possible_paths = [
            r"C:\xampp\Docker\Docker\Docker Desktop.exe",  # Windows 10
            r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
            r"C:\Program Files (x86)\Docker\Docker\Docker Desktop.exe",
        ]
        docker_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                docker_path = path
                break
        if not docker_path:
            messagebox.showerror("Error", "Docker Desktop tidak ditemukan!")
            return
        try:
            subprocess.Popen([docker_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka Docker Desktop")
        except Exception as e:
            self.log_message(f"Gagal membuka Docker Desktop: {str(e)}")

    def list_docker_containers(self):
        """List running Docker containers"""
        try:
            result = subprocess.run(["docker", "ps", "-a"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                output = result.stdout
                top = tk.Toplevel(self.root)
                top.title("Docker Containers")
                text_area = scrolledtext.ScrolledText(top, wrap=tk.NONE, font=("Consolas", 9))
                text_area.pack(fill=tk.BOTH, expand=True)
                text_area.insert(tk.END, output)
                text_area.see(tk.END)
                self.log_message("Menampilkan daftar container Docker")
            else:
                messagebox.showerror("Error", f"Gagal mendapatkan daftar container:\n{result.stderr}")
        except Exception as e:
            self.log_message(f"Gagal menjalankan docker ps: {str(e)}")

    def create_docker_project(self):
        """Create a new Docker project with a simple Dockerfile"""
        project_name = self.docker_project_name_entry.get()
        project_dir = self.docker_project_dir_entry.get()
        if not project_name:
            messagebox.showerror("Error", "Nama project harus diisi!")
            return
        if not project_dir:
            messagebox.showerror("Error", "Lokasi project harus dipilih!")
            return
        full_path = os.path.join(project_dir, project_name)
        if os.path.exists(full_path):
            messagebox.showerror("Error", f"Direktori {full_path} sudah ada!")
            return
        try:
            os.makedirs(full_path)
            # Create a simple Dockerfile
            dockerfile_content = (
                "FROM python:3.11-slim\n"
                "WORKDIR /app\n"
                "COPY . .\n"
                "RUN pip install --no-cache-dir -r requirements.txt || true\n"
                'CMD ["python", "app.py"]\n'
            )
            with open(os.path.join(full_path, "Dockerfile"), "w") as f:
                f.write(dockerfile_content)
            # Create a sample app.py and requirements.txt
            with open(os.path.join(full_path, "app.py"), "w") as f:
                f.write('print("Hello from Docker!")\n')
            with open(os.path.join(full_path, "requirements.txt"), "w") as f:
                f.write('')
            self.log_message(f"Project Docker berhasil dibuat di: {full_path}")
            messagebox.showinfo("Sukses", f"Project Docker berhasil dibuat di:\n{full_path}")
        except Exception as e:
            self.log_message(f"Gagal membuat project Docker: {str(e)}")
            messagebox.showerror("Error", f"Gagal membuat project Docker: {str(e)}")

    def run_docker_project(self):
        """Build and run the selected Docker project (docker build & run) with patch"""
        project_name = self.docker_project_name_entry.get()
        project_dir = self.docker_project_dir_entry.get()
        if not project_name:
            messagebox.showerror("Error", "Nama project harus diisi!")
            return
        if not project_dir:
            messagebox.showerror("Error", "Lokasi project harus dipilih!")
            return
        full_path = os.path.join(project_dir, project_name)
        if not os.path.isdir(full_path):
            messagebox.showerror("Error", f"Direktori project tidak ditemukan: {full_path}")
            return

        image_tag = f"{project_name.lower().replace(' ', '_')}:latest"
        build_cmd = ["docker", "build", "-t", image_tag, "."]
        run_cmd = ["docker", "run", "--rm", "-it", image_tag]

        self.log_message(f"Build Docker image: {' '.join(build_cmd)}")
        self.log_message(f"Run Docker container: {' '.join(run_cmd)}")

        def run_build_and_run():
            try:
                # Build image
                build_proc = subprocess.Popen(
                    build_cmd,
                    cwd=full_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                while True:
                    line = build_proc.stdout.readline()
                    if line == '' and build_proc.poll() is not None:
                        break
                    if line:
                        self.root.after(0, self.log_message, "[docker build] " + line.strip())
                if build_proc.poll() != 0:
                    self.root.after(0, self.log_message, "Build image gagal.")
                    messagebox.showerror("Error", "Build Docker image gagal.")
                    return

                # Run container
                run_proc = subprocess.Popen(
                    run_cmd,
                    cwd=full_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                while True:
                    line = run_proc.stdout.readline()
                    if line == '' and run_proc.poll() is not None:
                        break
                    if line:
                        self.root.after(0, self.log_message, "[docker run] " + line.strip())
                if run_proc.poll() != 0:
                    self.root.after(0, self.log_message, "Menjalankan container gagal.")
                    messagebox.showerror("Error", "Menjalankan Docker container gagal.")
                else:
                    self.root.after(0, self.log_message, "Docker container selesai dijalankan.")
            except Exception as e:
                self.root.after(0, self.log_message, f"Error Docker run: {str(e)}")
                messagebox.showerror("Error", f"Gagal menjalankan Docker: {str(e)}")

        threading.Thread(target=run_build_and_run, daemon=True).start()

        
    # Server control methods
    def start_php_server(self):
        """Start PHP development server"""
        if self.is_php_running:
            messagebox.showwarning("Peringatan", "PHP Server sudah berjalan!")
            return
        
        host = self.host_entry.get()
        port = self.port_entry.get()
        doc_root = self.doc_root_entry.get()
        php_path = self.php_path_entry.get()
        
        if not all([host, port, doc_root, php_path]):
            messagebox.showerror("Error", "Semua field harus diisi!")
            return
        
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Port harus berupa angka antara 1 dan 65535!")
            return
        
        if not os.path.isdir(doc_root):
            messagebox.showerror("Error", "Document root tidak valid!")
            return
        
        if not os.path.isfile(php_path):
            messagebox.showerror("Error", "Path PHP tidak valid!")
            return
        
        cmd = [php_path, "-S", f"{host}:{port}", "-t", doc_root]
        
        self.log_message(f"Memulai PHP Server pada {host}:{port}")
        self.log_message(f"Document root: {doc_root}")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.php_server_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=doc_root,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_php_running = True
                self.update_php_ui_state()
                
                while True:
                    output = self.php_server_process.stdout.readline()
                    if output == '' and self.php_server_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.php_server_process.poll()
                self.is_php_running = False
                self.update_php_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"PHP Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "PHP Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_php_running = False
                self.update_php_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_php_server(self):
        """Stop PHP development server"""
        if self.php_server_process and self.is_php_running:
            self.log_message("Menghentikan PHP Server...")
            self.php_server_process.terminate()
            try:
                self.php_server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.php_server_process.kill()
            self.is_php_running = False
            self.update_php_ui_state()
            self.log_message("PHP Server dihentikan")
    
    def start_apache(self):
        """Start Apache server"""
        if self.is_apache_running:
            messagebox.showwarning("Peringatan", "Apache Server sudah berjalan!")
            return
        
        apache_path = self.apache_path_entry.get()
        config_file = self.apache_config_entry.get()
        
        if not all([apache_path, config_file]):
            messagebox.showerror("Error", "Apache path dan config file harus diisi!")
            return
        
        if not os.path.isfile(apache_path):
            messagebox.showerror("Error", "Path Apache tidak valid!")
            return
        
        if not os.path.isfile(config_file):
            messagebox.showerror("Error", "Config file tidak valid!")
            return
        
        cmd = [apache_path, "-f", config_file]
        
        self.log_message(f"Memulai Apache Server")
        self.log_message(f"Config file: {config_file}")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
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
                self.update_apache_ui_state()
            
                while True:
                    output = self.apache_process.stdout.readline()
                    if output == '' and self.apache_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.apache_process.poll()
                self.is_apache_running = False
                self.update_apache_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Apache Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Apache Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_apache_running = False
                self.update_apache_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_apache(self):
        """Stop Apache server"""
        if self.apache_process and self.is_apache_running:
            self.log_message("Menghentikan Apache Server...")
            self.apache_process.terminate()
            try:
                self.apache_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.apache_process.kill()
            self.is_apache_running = False
            self.update_apache_ui_state()
            self.log_message("Apache Server dihentikan")
    
    def restart_apache(self):
        """Restart Apache server"""
        if not self.is_apache_running:
            messagebox.showwarning("Peringatan", "Apache Server belum berjalan!")
            return
        
        self.log_message("Merestart Apache Server...")
        self.stop_apache()
        time.sleep(2)
        self.start_apache()
    
    def start_mariadb(self):
        """Start MariaDB/MySQL server"""
        if self.is_mariadb_running:
            messagebox.showwarning("Peringatan", "MariaDB Server sudah berjalan!")
            return
        
        mariadb_path = self.mariadb_path_entry.get()
        port = self.mariadb_port_entry.get()
        
        if not all([mariadb_path, port]):
            messagebox.showerror("Error", "MariaDB path dan port harus diisi!")
            return
        
        try:
            port = int(port)
            if not (1 <= port <= 65535):
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Port harus berupa angka antara 1 dan 65535!")
            return
        
        if not os.path.isfile(mariadb_path):
            messagebox.showerror("Error", "Path MariaDB tidak valid!")
            return
        
        cmd = [mariadb_path, "--port", str(port)]
        
        self.log_message(f"Memulai MariaDB Server pada port {port}")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
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
                self.update_mariadb_ui_state()
                
                while True:
                    output = self.mariadb_process.stdout.readline()
                    if output == '' and self.mariadb_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.mariadb_process.poll()
                self.is_mariadb_running = False
                self.update_mariadb_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"MariaDB Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "MariaDB Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_mariadb_running = False
                self.update_mariadb_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_mariadb(self):
        """Stop MariaDB/MySQL server"""
        if self.mariadb_process and self.is_mariadb_running:
            self.log_message("Menghentikan MariaDB Server...")
            self.mariadb_process.terminate()
            try:
                self.mariadb_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mariadb_process.kill()
            self.is_mariadb_running = False
            self.update_mariadb_ui_state()
            self.log_message("MariaDB Server dihentikan")
    
    def start_filezilla(self):
        """Start FileZilla server"""
        if self.is_filezilla_running:
            messagebox.showwarning("Peringatan", "FileZilla Server sudah berjalan!")
            return
        
        filezilla_path = self.filezilla_path_entry.get()
        
        if not filezilla_path:
            messagebox.showerror("Error", "FileZilla path harus diisi!")
            return
        
        if not os.path.isfile(filezilla_path):
            messagebox.showerror("Error", "Path FileZilla tidak valid!")
            return
        
        cmd = [filezilla_path]
        
        self.log_message(f"Memulai FileZilla Server")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.filezilla_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_filezilla_running = True
                self.update_filezilla_ui_state()
                
                while True:
                    output = self.filezilla_process.stdout.readline()
                    if output == '' and self.filezilla_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.filezilla_process.poll()
                self.is_filezilla_running = False
                self.update_filezilla_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"FileZilla Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "FileZilla Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_filezilla_running = False
                self.update_filezilla_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_filezilla(self):
        """Stop FileZilla server"""
        if self.filezilla_process and self.is_filezilla_running:
            self.log_message("Menghentikan FileZilla Server...")
            self.filezilla_process.terminate()
            try:
                self.filezilla_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.filezilla_process.kill()
            self.is_filezilla_running = False
            self.update_filezilla_ui_state()
            self.log_message("FileZilla Server dihentikan")
    
    def start_mercury(self):
        """Start Mercury server"""
        if self.is_mercury_running:
            messagebox.showwarning("Peringatan", "Mercury Server sudah berjalan!")
            return
        
        mercury_path = self.mercury_path_entry.get()
        
        if not mercury_path:
            messagebox.showerror("Error", "Mercury path harus diisi!")
            return
        
        if not os.path.isfile(mercury_path):
            messagebox.showerror("Error", "Path Mercury tidak valid!")
            return
        
        cmd = [mercury_path]
        
        self.log_message(f"Memulai Mercury Server")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.mercury_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_mercury_running = True
                self.update_mercury_ui_state()
                
                while True:
                    output = self.mercury_process.stdout.readline()
                    if output == '' and self.mercury_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.mercury_process.poll()
                self.is_mercury_running = False
                self.update_mercury_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Mercury Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Mercury Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_mercury_running = False
                self.update_mercury_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_mercury(self):
        """Stop Mercury server"""
        if self.mercury_process and self.is_mercury_running:
            self.log_message("Menghentikan Mercury Server...")
            self.mercury_process.terminate()
            try:
                self.mercury_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.mercury_process.kill()
            self.is_mercury_running = False
            self.update_mercury_ui_state()
            self.log_message("Mercury Server dihentikan")
    
    def start_tomcat(self):
        """Start Tomcat server"""
        if self.is_tomcat_running:
            messagebox.showwarning("Peringatan", "Tomcat Server sudah berjalan!")
            return
        
        tomcat_path = self.tomcat_path_entry.get()
        
        if not tomcat_path:
            messagebox.showerror("Error", "Tomcat path harus diisi!")
            return
        
        if not os.path.isfile(tomcat_path):
            messagebox.showerror("Error", "Path Tomcat tidak valid!")
            return
        
        if "JAVA_HOME" not in os.environ:
            messagebox.showerror("Error", "JAVA_HOME environment variable tidak ditemukan!")
            return
        
        cmd = [tomcat_path, "//TS", "Tomcat"]
        
        self.log_message(f"Memulai Tomcat Server")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.tomcat_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_tomcat_running = True
                self.update_tomcat_ui_state()
                
                while True:
                    output = self.tomcat_process.stdout.readline()
                    if output == '' and self.tomcat_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.tomcat_process.poll()
                self.is_tomcat_running = False
                self.update_tomcat_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Tomcat Server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Tomcat Server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_tomcat_running = False
                self.update_tomcat_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_tomcat(self):
        """Stop Tomcat server"""
        if self.tomcat_process and self.is_tomcat_running:
            self.log_message("Menghentikan Tomcat Server...")
            self.tomcat_process.terminate()
            try:
                self.tomcat_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tomcat_process.kill()
            self.is_tomcat_running = False
            self.update_tomcat_ui_state()
            self.log_message("Tomcat Server dihentikan")
    
    def start_laragon(self):
        """Start pyserver server"""
        if self.is_laragon_running:
            messagebox.showwarning("Peringatan", "pyserver sudah berjalan!")
            return
        
        laragon_path = self.laragon_path_entry.get()
        
        if not laragon_path:
            messagebox.showerror("Error", "pyserver path harus diisi!")
            return
        
        if not os.path.isfile(laragon_path):
            messagebox.showerror("Error", "Path pyserver tidak valid!")
            return
        
        cmd = [laragon_path, "start"]
        
        self.log_message(f"Memulai pyserver")
        self.log_message(f"Perintah: {' '.join(cmd)}")
        
        def run_server():
            try:
                self.laragon_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                self.is_laragon_running = True
                self.update_laragon_ui_state()
                
                while True:
                    output = self.laragon_process.stdout.readline()
                    if output == '' and self.laragon_process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = self.laragon_process.poll()
                self.is_laragon_running = False
                self.update_laragon_ui_state()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"pyserver berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "pyserver dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.is_laragon_running = False
                self.update_laragon_ui_state()
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    def stop_laragon(self):
        """Stop pyserver server"""
        if self.laragon_process and self.is_laragon_running:
            self.log_message("Menghentikan pyserver...")
            self.laragon_process.terminate()
            try:
                self.laragon_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.laragon_process.kill()
            self.is_laragon_running = False
            self.update_laragon_ui_state()
            self.log_message("pyserver dihentikan")
    
    def restart_laragon(self):
        """Restart pyserver server"""
        if not self.is_laragon_running:
            messagebox.showwarning("Peringatan", "pyserver belum berjalan!")
            return
        
        self.log_message("Merestart pyserver...")
        self.stop_laragon()
        time.sleep(2)
        self.start_laragon()
    
    # Utility methods
    def browse_directory(self, entry_widget=None):
        """Browse for directory and update entry widget if provided"""
        directory = filedialog.askdirectory()
        if directory:
            if entry_widget:
                entry_widget.delete(0, tk.END)
                entry_widget.insert(0, directory)
            return directory
        return None
    
    def browse_executable(self, entry_widget):
        """Browse for executable file"""
        filepath = filedialog.askopenfilename(
            title="Pilih Executable",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
            # Save the path to config
            if entry_widget == self.php_path_entry:
                self.default_paths['php'] = filepath
            elif entry_widget == self.apache_path_entry:
                self.default_paths['apache'] = filepath
            elif entry_widget == self.mariadb_path_entry:
                self.default_paths['mariadb'] = filepath
            elif entry_widget == self.filezilla_path_entry:
                self.default_paths['filezilla'] = filepath
            elif entry_widget == self.mercury_path_entry:
                self.default_paths['mercury'] = filepath
            elif entry_widget == self.tomcat_path_entry:
                self.default_paths['tomcat'] = filepath
            elif entry_widget == self.laragon_path_entry:
                self.default_paths['pyserver'] = filepath
            elif entry_widget == self.composer_path_entry:
                self.default_paths['composer'] = filepath
            
            self.save_config()
    
    def browse_file(self, entry_widget, filetypes):
        """Browse for file with specific types"""
        filepath = filedialog.askopenfilename(
            title="Pilih File",
            filetypes=filetypes
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)
    
    def log_message(self, message):
        """Log message to the log text area with simple animation effect"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        # Simple animation: fade-in effect by gradually inserting characters
        def animate_insert(idx=0):
            if idx <= len(formatted_message):
                self.log_text.insert(tk.END, formatted_message[:idx])
                self.log_text.see(tk.END)
                self.log_text.update_idletasks()
                self.log_text.delete("end-1c linestart", tk.END)  # Remove incomplete line
                self.log_text.insert(tk.END, formatted_message[:idx])
                self.log_text.see(tk.END)
                self.log_text.update_idletasks()
                self.log_text.after(5, animate_insert, idx + 1)
            else:
                self.log_text.insert(tk.END, formatted_message)
                self.log_text.see(tk.END)
        # Start animation
        animate_insert(1)
    
    # UI update methods
    def update_php_ui_state(self):
        """Update PHP server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: PHP Server Aktif"):
            if not self.is_php_running:
                self.php_status_label.config(
                    text="Status: PHP Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.php_start_btn.config(state=tk.NORMAL)
                self.php_stop_btn.config(state=tk.DISABLED)
                self.php_open_browser_btn.config(state=tk.DISABLED)
                return
            # Running text animation
            display_text = text[idx:] + "   " + text[:idx]
            self.php_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.php_start_btn.config(state=tk.DISABLED)
            self.php_stop_btn.config(state=tk.NORMAL)
            self.php_open_browser_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            # Create green/red circle images
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_php_running:
            animate_status()
        else:
            self.php_status_label.config(
                text="Status: PHP Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.php_start_btn.config(state=tk.NORMAL)
            self.php_stop_btn.config(state=tk.DISABLED)
            self.php_open_browser_btn.config(state=tk.DISABLED)

    def update_apache_ui_state(self):
        """Update Apache server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: Apache Server Aktif"):
            if not self.is_apache_running:
                self.apache_status_label.config(
                    text="Status: Apache Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.apache_start_btn.config(state=tk.NORMAL)
                self.apache_stop_btn.config(state=tk.DISABLED)
                self.apache_restart_btn.config(state=tk.DISABLED)
                self.apache_open_browser_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.apache_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.apache_start_btn.config(state=tk.DISABLED)
            self.apache_stop_btn.config(state=tk.NORMAL)
            self.apache_restart_btn.config(state=tk.NORMAL)
            self.apache_open_browser_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_apache_running:
            animate_status()
        else:
            self.apache_status_label.config(
                text="Status: Apache Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.apache_start_btn.config(state=tk.NORMAL)
            self.apache_stop_btn.config(state=tk.DISABLED)
            self.apache_restart_btn.config(state=tk.DISABLED)
            self.apache_open_browser_btn.config(state=tk.DISABLED)

    def update_mariadb_ui_state(self):
        """Update MariaDB server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: MariaDB Server Aktif"):
            if not self.is_mariadb_running:
                self.mariadb_status_label.config(
                    text="Status: MariaDB Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.mariadb_start_btn.config(state=tk.NORMAL)
                self.mariadb_stop_btn.config(state=tk.DISABLED)
                self.mariadb_shell_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.mariadb_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.mariadb_start_btn.config(state=tk.DISABLED)
            self.mariadb_stop_btn.config(state=tk.NORMAL)
            self.mariadb_shell_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_mariadb_running:
            animate_status()
        else:
            self.mariadb_status_label.config(
                text="Status: MariaDB Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.mariadb_start_btn.config(state=tk.NORMAL)
            self.mariadb_stop_btn.config(state=tk.DISABLED)
            self.mariadb_shell_btn.config(state=tk.DISABLED)

    def update_filezilla_ui_state(self):
        """Update FileZilla server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: FileZilla Server Aktif"):
            if not self.is_filezilla_running:
                self.filezilla_status_label.config(
                    text="Status: FileZilla Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.filezilla_start_btn.config(state=tk.NORMAL)
                self.filezilla_stop_btn.config(state=tk.DISABLED)
                self.filezilla_admin_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.filezilla_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.filezilla_start_btn.config(state=tk.DISABLED)
            self.filezilla_stop_btn.config(state=tk.NORMAL)
            self.filezilla_admin_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_filezilla_running:
            animate_status()
        else:
            self.filezilla_status_label.config(
                text="Status: FileZilla Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.filezilla_start_btn.config(state=tk.NORMAL)
            self.filezilla_stop_btn.config(state=tk.DISABLED)
            self.filezilla_admin_btn.config(state=tk.DISABLED)

    def update_mercury_ui_state(self):
        """Update Mercury server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: Mercury Server Aktif"):
            if not self.is_mercury_running:
                self.mercury_status_label.config(
                    text="Status: Mercury Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.mercury_start_btn.config(state=tk.NORMAL)
                self.mercury_stop_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.mercury_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.mercury_start_btn.config(state=tk.DISABLED)
            self.mercury_stop_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_mercury_running:
            animate_status()
        else:
            self.mercury_status_label.config(
                text="Status: Mercury Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.mercury_start_btn.config(state=tk.NORMAL)
            self.mercury_stop_btn.config(state=tk.DISABLED)

    def update_tomcat_ui_state(self):
        """Update Tomcat server UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: Tomcat Server Aktif"):
            if not self.is_tomcat_running:
                self.tomcat_status_label.config(
                    text="Status: Tomcat Server Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.tomcat_start_btn.config(state=tk.NORMAL)
                self.tomcat_stop_btn.config(state=tk.DISABLED)
                self.tomcat_restart_btn.config(state=tk.DISABLED)
                self.tomcat_open_browser_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.tomcat_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.tomcat_start_btn.config(state=tk.DISABLED)
            self.tomcat_stop_btn.config(state=tk.NORMAL)
            self.tomcat_restart_btn.config(state=tk.NORMAL)
            self.tomcat_open_browser_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_tomcat_running:
            animate_status()
        else:
            self.tomcat_status_label.config(
                text="Status: Tomcat Server Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.tomcat_start_btn.config(state=tk.NORMAL)
            self.tomcat_stop_btn.config(state=tk.DISABLED)
            self.tomcat_restart_btn.config(state=tk.DISABLED)
            self.tomcat_open_browser_btn.config(state=tk.DISABLED)

    def update_laragon_ui_state(self):
        """Update pyserver UI state with running text and status circle"""
        def animate_status(idx=0, text="Status: pyserver Aktif"):
            if not self.is_laragon_running:
                self.laragon_status_label.config(
                    text="Status: pyserver Tidak Aktif   ",
                    foreground="red",
                    image=self.status_circle_red,
                    compound=tk.LEFT
                )
                self.laragon_start_btn.config(state=tk.NORMAL)
                self.laragon_stop_btn.config(state=tk.DISABLED)
                self.laragon_restart_btn.config(state=tk.DISABLED)
                self.laragon_open_browser_btn.config(state=tk.DISABLED)
                return
            display_text = text[idx:] + "   " + text[:idx]
            self.laragon_status_label.config(
                text=display_text,
                foreground="green",
                image=self.status_circle_green,
                compound=tk.LEFT
            )
            self.laragon_start_btn.config(state=tk.DISABLED)
            self.laragon_stop_btn.config(state=tk.NORMAL)
            self.laragon_restart_btn.config(state=tk.NORMAL)
            self.laragon_open_browser_btn.config(state=tk.NORMAL)
            self.root.after(200, animate_status, (idx + 1) % len(text), text)
        if not hasattr(self, "status_circle_green"):
            self.status_circle_green = self._create_circle_image("#00cc00")
            self.status_circle_red = self._create_circle_image("#cc0000")
        if self.is_laragon_running:
            animate_status()
        else:
            self.laragon_status_label.config(
                text="Status: pyserver Tidak Aktif   ",
                foreground="red",
                image=self.status_circle_red,
                compound=tk.LEFT
            )
            self.laragon_start_btn.config(state=tk.NORMAL)
            self.laragon_stop_btn.config(state=tk.DISABLED)
            self.laragon_restart_btn.config(state=tk.DISABLED)
            self.laragon_open_browser_btn.config(state=tk.DISABLED)

    def _create_circle_image(self, color, size=16):
        """Create a circle image for status indicator"""
        img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        draw.ellipse((2, 2, size-2, size-2), fill=color, outline="#444444")
        return ImageTk.PhotoImage(img)
    
    # Browser methods
    def open_php_in_browser(self):
        """Open PHP server in browser"""
        if not self.is_php_running:
            messagebox.showwarning("Peringatan", "PHP Server belum berjalan!")
            return
        
        host = self.host_entry.get()
        port = self.port_entry.get()
        
        url = f"http://{host}:{port}"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    def open_apache_in_browser(self):
        """Open Apache server in browser"""
        if not self.is_apache_running:
            messagebox.showwarning("Peringatan", "Apache Server belum berjalan!")
            return
        
        url = "http://localhost"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    def open_tomcat_in_browser(self):
        """Open Tomcat server in browser"""
        if not self.is_tomcat_running:
            messagebox.showwarning("Peringatan", "Tomcat Server belum berjalan!")
            return
        
        port = self.tomcat_port_entry.get()
        url = f"http://localhost:{port}"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    def open_laragon_in_browser(self):
        """Open Laragon in browser"""
        if not self.is_laragon_running:
            messagebox.showwarning("Peringatan", "Pyserver belum berjalan!")
            return
        
        url = "http://localhost"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    def open_laravel_in_browser(self):
        """Open Laravel project in browser"""
        project_dir = self.laravel_project_entry.get()
        if not project_dir:
            messagebox.showwarning("Peringatan", "Project directory belum dipilih!")
            return
        
        project_name = os.path.basename(project_dir)
        url = f"http://127.0.0.1:8000"
        webbrowser.open(url)
        self.log_message(f"Membuka browser ke: {url}")
    
    # Terminal methods
    def open_cmd(self):
        """Open CMD terminal"""
        try:
            subprocess.Popen("cmd", creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka CMD terminal")
        except Exception as e:
            self.log_message(f"Gagal membuka CMD: {str(e)}")
    
    def open_powershell(self):
        """Open PowerShell terminal"""
        try:
            subprocess.Popen("powershell", creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka PowerShell terminal")
        except Exception as e:
            self.log_message(f"Gagal membuka PowerShell: {str(e)}")
    
    def open_git_bash(self):
        """Open Git Bash terminal"""
        try:
            subprocess.Popen("git-bash", creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka Git Bash terminal")
        except Exception as e:
            self.log_message(f"Gagal membuka Git Bash: {str(e)}")
    
    def open_wsl(self):
        """Open WSL (Windows Subsystem for Linux) terminal"""
        try:
            subprocess.Popen("wsl", creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka WSL terminal")
        except Exception as e:
            self.log_message(f"Gagal membuka WSL: {str(e)}")
    
    def unlocker(self):
        """Run IObit Unlocker as administrator if available, else offer to download or input path."""

        possible_paths = [
            "C:\\Program Files (x86)\\IObit\\IObit Unlocker\\IObitUnlocker.exe",
            "C:\\xampp\\unlocker\\IObitUnlocker.exe"
        ]
        unlocker_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                unlocker_path = path
                break

        if not unlocker_path:
            # Prompt user to paste path or download
            answer = messagebox.askyesnocancel(
                "IObit Unlocker",
                "IObit Unlocker tidak ditemukan.\n"
                "Klik Yes untuk memasukkan path manual.\n"
                "Klik No untuk download dari situs resmi.\n"
                "Klik Cancel untuk batal."
            )
            if answer is None:
                self.log_message("Batal menjalankan IObit Unlocker")
                return
            elif answer:
                # User wants to paste path
                manual_path = simpledialog.askstring(
                    "Path IObit Unlocker",
                    "Paste path lengkap ke IObitUnlocker.exe:"
                )
                if manual_path and os.path.isfile(manual_path):
                    unlocker_path = manual_path
                else:
                    messagebox.showerror("Error", "Path tidak valid atau file tidak ditemukan!")
                    self.log_message("Path IObit Unlocker tidak valid")
                    return
            else:
                webbrowser.open("https://www.iobit.com/en/iobit-unlocker.php")
                self.log_message("Membuka halaman download IObit Unlocker")
                return

        try:
            # Run as administrator using ShellExecuteEx
            params = ""
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", unlocker_path, params, None, 1
            )
            self.log_message("Menjalankan IObit Unlocker sebagai administrator")
        except Exception as e:
            self.log_message(f"Gagal menjalankan IObit Unlocker: {str(e)}")
    
    def cloud(self):
        """Open Azure Cloud Shell as a local CMD with az login if available, else open browser"""
        try:
            # Try to run Azure CLI in CMD if installed
            result = subprocess.run(["az", "--version"], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if result.returncode == 0:
                subprocess.Popen("cmd /k az login", creationflags=subprocess.CREATE_NEW_CONSOLE)
                self.log_message("Membuka CMD dengan Azure CLI (az login)")
            else:
                raise FileNotFoundError
        except Exception:
            url = "https://shell.azure.com/"
            webbrowser.open(url)
            self.log_message("Azure CLI tidak ditemukan, membuka Azure Cloud Shell di browser")
    def Deles(self):
        """Delete Windows cache/trash (temp, recycle bin, prefetch, etc) with improved cleaning and performance optimization."""
        
        # List of trash/cache locations with more comprehensive cleaning
        trash_info = [
            {
                "name": "Recycle Bin",
                "path": None,
                "desc": "Sampah file yang dihapus dari Windows Explorer.",
                "suggestion": "Wajib dikosongkan untuk membebaskan ruang disk."
            },
            {
                "name": "Windows Temp Files",
                "path": tempfile.gettempdir(),
                "desc": "File sementara sistem dan aplikasi.",
                "suggestion": "Penting dibersihkan secara rutin."
            },
            {
                "name": "System Temp Files",
                "path": r"C:\Windows\Temp",
                "desc": "File sementara sistem Windows.",
                "suggestion": "Bersihkan untuk optimasi sistem."
            },
            {
                "name": "Windows Prefetch",
                "path": r"C:\Windows\Prefetch",
                "desc": "Cache loading aplikasi.",
                "suggestion": "Bersihkan untuk refresh cache prefetch."
            },
            {
                "name": "Internet Explorer Cache",
                "path": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"),
                "desc": "Cache browser Internet Explorer/Edge.",
                "suggestion": "Bersihkan jika tidak digunakan."
            },
            {
                "name": "Windows Update Cache",
                "path": r"C:\Windows\SoftwareDistribution\Download",
                "desc": "File download update Windows.",
                "suggestion": "Bersihkan setelah update selesai."
            },
            {
                "name": "Error Reports",
                "path": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\WER"),
                "desc": "Laporan error sistem dan aplikasi.",
                "suggestion": "Aman dibersihkan."
            },
            {
                "name": "Thumbnail Cache",
                "path": os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer"),
                "desc": "Cache thumbnail file explorer.",
                "suggestion": "Bersihkan untuk refresh thumbnail."
            },
            {
                "name": "Delivery Optimization Files",
                "path": r"C:\Windows\DeliveryOptimization",
                "desc": "Cache update delivery optimization.",
                "suggestion": "Bersihkan untuk hemat ruang."
            },
            {
                "name": "DNS Cache",
                "path": None,
                "desc": "Cache alamat DNS.",
                "suggestion": "Refresh untuk perbaikan koneksi."
            }
        ]

        # Show cleanup information
        info_lines = []
        for t in trash_info:
            info_lines.append(f"• {t['name']}\n  {t['desc']}\n  Saran: {t['suggestion']}\n")

        msg = "Lokasi sampah/cache Windows yang akan dibersihkan:\n\n"
        msg += "\n".join(info_lines)
        msg += "\nLanjutkan pembersihan untuk meningkatkan performa sistem?"

        if not messagebox.askyesno("Konfirmasi Pembersihan Sistem", msg):
            self.log_message("Pembersihan dibatalkan.")
            return

        # Start cleanup process
        self.log_message("Memulai pembersihan sistem...")

        # 1. Empty Recycle Bin with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
                self.log_message("Recycle Bin berhasil dikosongkan.")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    self.log_message(f"Gagal mengosongkan Recycle Bin: {str(e)}")
                else:
                    time.sleep(1)  # Wait before retrying

        # 2. Clean other locations with improved error handling
        for t in trash_info[1:]:
            path = t["path"]
            name = t["name"]
            
            try:
                # Special case for DNS cache
                if name == "DNS Cache":
                    os.system('ipconfig /flushdns')
                    self.log_message("DNS Cache berhasil di-flush")
                    continue
                    
                if not path:
                    continue
                    
                if not os.path.exists(path):
                    self.log_message(f"{name} tidak ditemukan, dilewati.")
                    continue

                # Delete directory contents (preserve directory structure)
                if os.path.isdir(path):
                    deleted_files = 0
                    deleted_size = 0
                    
                    for root, dirs, files in os.walk(path):
                        for f in files:
                            try:
                                fp = os.path.join(root, f)
                                file_size = os.path.getsize(fp)
                                os.unlink(fp)
                                deleted_files += 1
                                deleted_size += file_size
                            except Exception as e:
                                pass  # Skip files that can't be deleted
                                
                        for d in dirs:
                            try:
                                dp = os.path.join(root, d)
                                if os.path.islink(dp):
                                    os.unlink(dp)
                                else:
                                    shutil.rmtree(dp, ignore_errors=True)
                            except Exception:
                                pass
                                
                    self.log_message(f"{name}: {deleted_files} file dihapus (~{deleted_size/1024/1024:.1f} MB dibebaskan)")
                    
                elif os.path.isfile(path):
                    try:
                        os.unlink(path)
                        self.log_message(f"{name} file dihapus.")
                    except Exception as e:
                        self.log_message(f"Gagal menghapus file {name}: {str(e)}")
                        
            except Exception as e:
                self.log_message(f"Error membersihkan {name}: {str(e)}")

        # Additional performance optimization
        try:
            # Clear Windows Store cache
            os.system('wsreset.exe')
            self.log_message("Windows Store cache dibersihkan")
        except Exception as e:
            self.log_message(f"Gagal membersihkan Windows Store cache: {str(e)}")

        # Run disk cleanup (silent mode)
        try:
            os.system('cleanmgr /sagerun:1')
            self.log_message("Disk Cleanup dijalankan")
        except Exception as e:
            self.log_message(f"Gagal menjalankan Disk Cleanup: {str(e)}")

        self.log_message("Pembersihan sistem selesai. Disarankan untuk restart komputer untuk hasil optimal.")
        messagebox.showinfo("Selesai", "Pembersihan sistem selesai!\n\nUntuk hasil terbaik, restart komputer Anda.")
                
                
    def Emu(self):
        """Menampilkan popup statistik kesehatan dan spesifikasi lengkap laptop dengan bagan statistik"""
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        try:
            # Statistik kesehatan
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None

            # Spesifikasi detail
            uname = platform.uname()
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            gpu_info = ""
            try:
                w = wmi.WMI()
                for gpu in w.Win32_VideoController():
                    gpu_info = f"{gpu.Name} ({gpu.AdapterRAM // (1024**2)} MB)" if hasattr(gpu, "AdapterRAM") else gpu.Name
                    break
            except Exception:
                gpu_info = "Tidak tersedia"

            info_lines = [
                f"Nama Komputer: {uname.node}",
                f"Sistem Operasi: {uname.system} {uname.release} ({uname.version})",
                f"Processor: {uname.processor}",
                f"CPU Fisik: {cpu_count}, Logical: {cpu_count_logical}",
                f"CPU Frequency: {cpu_freq.current:.2f} MHz" if cpu_freq else "CPU Frequency: Tidak tersedia",
                f"GPU: {gpu_info}",
                f"RAM: {mem.total // (1024**3)} GB",
                f"Disk: {disk.total // (1024**3)} GB",
                f"Battery: {battery.percent}% {'(Charging)' if battery and battery.power_plugged else '(Discharging)' if battery else 'Tidak tersedia'}",
            ]

            stat_lines = [
                f"CPU Usage: {cpu_percent}%",
                f"RAM Usage: {mem.percent:.1f}% ({mem.used // (1024**2)} MB / {mem.total // (1024**2)} MB)",
                f"Disk Usage: {disk.percent:.1f}% ({disk.used // (1024**3)} GB / {disk.total // (1024**3)} GB)",
            ]
            if battery:
                stat_lines.append(f"Battery: {battery.percent}% {'(Charging)' if battery.power_plugged else '(Discharging)'}")
            else:
                stat_lines.append("Battery: Tidak tersedia")

            # Bagan statistik (pie chart)
            labels = ['CPU', 'RAM', 'Disk']
            values = [cpu_percent, mem.percent, disk.percent]
            colors = ['#ff9999','#66b3ff','#99ff99']

            fig, ax = plt.subplots(figsize=(3, 3))
            wedges, texts, autotexts = ax.pie(
                values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors
            )
            ax.set_title('Statistik Penggunaan Resource')
            plt.tight_layout()

            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)
            img = Image.open(buf)

            # Tampilkan popup dengan gambar dan info
            top = tk.Toplevel(self.root)
            top.title("Statistik & Spesifikasi Laptop")
            top.geometry("480x700")
            top.resizable(False, False)

            # Gambar bagan statistik
            img = img.resize((220, 220))
            photo = ImageTk.PhotoImage(img)
            img_label = ttk.Label(top, image=photo)
            img_label.image = photo
            img_label.pack(pady=(10, 0))

            # Statistik singkat
            stat_label = tk.Label(top, text="\n".join(stat_lines), font=("Segoe UI", 10, "bold"))
            stat_label.pack(pady=(10, 0))

            # Spesifikasi detail
            spec_frame = ttk.LabelFrame(top, text="Spesifikasi Lengkap", padding="10")
            spec_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))
            spec_text = scrolledtext.ScrolledText(spec_frame, wrap=tk.WORD, font=("Segoe UI", 9), height=12)
            spec_text.insert(tk.END, "\n".join(info_lines))
            spec_text.config(state=tk.DISABLED)
            spec_text.pack(fill=tk.BOTH, expand=True)

            close_btn = ttk.Button(top, text="Tutup", command=top.destroy)
            close_btn.pack(pady=(0, 10))

            self.log_message("Menampilkan statistik & spesifikasi laptop:\n" + "\n".join(stat_lines + info_lines))
        except Exception as e:
            self.log_message(f"Gagal mengambil statistik/spesifikasi: {str(e)}")
            messagebox.showerror("Error", f"Gagal mengambil statistik/spesifikasi: {str(e)}")
            
            
    def note(self):
        """Open Notepad++ if available, else prompt to download or select path."""
        possible_paths = [
            "C:\\Program Files\\Notepad++\\notepad++.exe",
            "C:\\Program Files (x86)\\Notepad++\\notepad++.exe",
            "C:\\xampp\\notepad++\\notepad++.exe",
        ]
        notepadpp_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                notepadpp_path = path
                break

        if not notepadpp_path:
            answer = messagebox.askyesnocancel(
                "Notepad++",
                "Notepad++ tidak ditemukan.\n"
                "Klik Yes untuk memilih path manual.\n"
                "Klik No untuk download dari situs resmi.\n"
                "Klik Cancel untuk batal."
            )
            if answer is None:
                self.log_message("Batal membuka Notepad++")
                return
            elif answer:
                manual_path = filedialog.askopenfilename(
                    title="Pilih Notepad++ Executable",
                    filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
                )
                if manual_path and os.path.isfile(manual_path):
                    notepadpp_path = manual_path
                else:
                    messagebox.showerror("Error", "Path tidak valid atau file tidak ditemukan!")
                    self.log_message("Path Notepad++ tidak valid")
                    return
            else:
                webbrowser.open("https://notepad-plus-plus.org/downloads/")
                self.log_message("Membuka halaman download Notepad++")
                return

        try:
            subprocess.Popen(notepadpp_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka Notepad++")
        except Exception as e:
            self.log_message(f"Gagal membuka Notepad++: {str(e)}")
            
    def patch_ino_setup_compiler(self):
        inno_path = r"C:\xampp\Inno Setup 6\Compil32.exe"
        if os.path.isfile(inno_path):
            try:
                # Jalankan sebagai administrator
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", inno_path, "", None, 1
                )
                self.log_message(f"Menjalankan paksa Inno Setup Compiler: {inno_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Gagal menjalankan Inno Setup Compiler: {str(e)}")
                self.log_message(f"Gagal menjalankan Inno Setup Compiler: {str(e)}")
        else:
            messagebox.showerror("Error", f"Inno Setup Compiler tidak ditemukan di:\n{inno_path}")
            self.log_message(f"Inno Setup Compiler tidak ditemukan di: {inno_path}")
        
        
        
    def open_mysql_shell(self):
        """Open MySQL shell"""
        possible_paths = [
            "mysql",
            "C:\\xampp\\mysql\\bin\\mysql.exe",
            "C:\\Program Files\\MariaDB\\bin\\mysql.exe",
            "C:\\Program Files\\MySQL\\MySQL Server\\bin\\mysql.exe",
        ]
        mysql_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                mysql_path = path
                break
        
        if not mysql_path:
            messagebox.showerror("Error", "MySQL client tidak ditemukan!")
            return
        
        port = self.mariadb_port_entry.get()
        password = self.mariadb_password_entry.get()
        
        cmd = [mysql_path, "-u", "root", f"-p{password}", "-P", port]
        
        try:
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka MySQL shell")
        except Exception as e:
            self.log_message(f"Gagal membuka MySQL shell: {str(e)}")
    
    def open_filezilla_admin(self):
        """Open FileZilla admin interface"""
        possible_paths = [
            "C:\\Program Files\\FileZilla Server\\FileZilla Server Interface.exe",
            "C:\\Program Files (x86)\\FileZilla Server\\FileZilla Server Interface.exe",
            "C:\\xampp\\FileZilla Server\\FileZilla Server Interface.exe"
        ]
        
        admin_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                admin_path = path
                break
        
        if not admin_path:
            messagebox.showerror("Error", "FileZilla Server Interface tidak ditemukan!")
            return
        
        admin_port = self.filezilla_admin_port_entry.get()
        
        cmd = [admin_path, "localhost", admin_port]
        
        try:
            subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka FileZilla Server Admin Interface")
        except Exception as e:
            self.log_message(f"Gagal membuka FileZilla Admin Interface: {str(e)}")
    
    def open_xampp_control(self):
        """Open XAMPP control panel"""
        possible_paths = [
            "C:\\xampp\\xampp-control.exe",
            "C:\\Program Files\\xampp\\xampp-control.exe",
        ]
        
        xampp_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                xampp_path = path
                break
        
        if not xampp_path:
            messagebox.showerror("Error", "XAMPP Control Panel tidak ditemukan!")
            return
        
        try:
            subprocess.Popen(xampp_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka XAMPP Control Panel")
        except Exception as e:
            self.log_message(f"Gagal membuka XAMPP Control Panel: {str(e)}")
    
    def open_xampp_shell(self):
        """Open XAMPP shell"""
        possible_paths = [
            "C:\\xampp\\xampp_shell.bat",
            "C:\\Program Files\\xampp\\shell.bat",
        ]
        
        shell_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                shell_path = path
                break
        
        if not shell_path:
            messagebox.showerror("Error", "XAMPP Shell tidak ditemukan!")
            return
        
        try:
            subprocess.Popen(shell_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
            self.log_message("Membuka XAMPP Shell")
        except Exception as e:
            self.log_message(f"Gagal membuka XAMPP Shell: {str(e)}")
    
    # Laravel methods
    def create_laravel_project(self):
        """Create new Laravel project"""
        project_dir = filedialog.askdirectory(title="Pilih Direktori untuk Project Baru")
        if not project_dir:
            return
        
        project_name = simpledialog.askstring("Nama Project", "Masukkan nama project Laravel:")
        if not project_name:
            return
        
        composer_path = self.composer_path_entry.get()
        if not composer_path:
            messagebox.showerror("Error", "Path Composer harus diisi!")
            return
        
        full_path = os.path.join(project_dir, project_name)
        
        if os.path.exists(full_path):
            messagebox.showerror("Error", f"Direktori {full_path} sudah ada!")
            return
        
        self.log_message(f"Membuat project Laravel baru: {project_name}")
        
        cmd = []
        if composer_path.endswith('.phar'):
            cmd.extend(['php', composer_path, 'create-project', '--prefer-dist', 'laravel/laravel', project_name])
        else:
            cmd.extend([composer_path, 'create-project', '--prefer-dist', 'laravel/laravel', project_name])
        
        def run_command():
            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.root.after(0, self.log_message, f"Project Laravel berhasil dibuat di: {full_path}")
                    self.root.after(0, self.laravel_project_entry.delete, 0, tk.END)
                    self.root.after(0, self.laravel_project_entry.insert, 0, full_path)
                    self.root.after(0, messagebox.showinfo, "Sukses", f"Project Laravel berhasil dibuat di:\n{full_path}")
                else:
                    self.root.after(0, self.log_message, f"Gagal membuat project Laravel. Kode error: {return_code}")
                    self.root.after(0, messagebox.showerror, "Error", "Gagal membuat project Laravel")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.root.after(0, messagebox.showerror, "Error", f"Gagal membuat project Laravel: {str(e)}")
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
    
    def start_laravel_server(self):
        """Start Laravel development server"""
        project_dir = self.laravel_project_entry.get()
        if not project_dir:
            messagebox.showwarning("Peringatan", "Project directory belum dipilih!")
            return
        
        if not os.path.isdir(project_dir):
            messagebox.showerror("Error", "Project directory tidak valid!")
            return
        
        php_path = self.php_path_entry.get()
        if not php_path:
            messagebox.showerror("Error", "PHP path harus diisi!")
            return
        
        if not os.path.isfile(php_path):
            messagebox.showerror("Error", "Path PHP tidak valid!")
            return
        
        cmd = [php_path, "artisan", "serve"]
        
        self.log_message(f"Memulai Laravel development server di {project_dir}")
        
        def run_server():
            try:
                process = subprocess.Popen(
                    cmd,
                    cwd=project_dir,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = process.poll()
                
                if return_code != 0:
                    self.root.after(0, self.log_message, f"Laravel server berhenti dengan kode error: {return_code}")
                else:
                    self.root.after(0, self.log_message, "Laravel server dihentikan")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
    
    # Composer methods
    def update_composer(self):
        """Update Composer"""
        composer_path = self.composer_path_entry.get()
        if not composer_path:
            messagebox.showerror("Error", "Composer path harus diisi!")
            return
        
        self.log_message("Memperbarui Composer...")
        
        cmd = []
        if composer_path.endswith('.phar'):
            cmd.extend(['php', composer_path, 'self-update'])
        else:
            cmd.extend([composer_path, 'self-update'])
        
        def run_command():
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        self.root.after(0, self.log_message, output.strip())
                
                return_code = process.poll()
                
                if return_code == 0:
                    self.root.after(0, self.log_message, "Composer berhasil diperbarui")
                    self.root.after(0, messagebox.showinfo, "Sukses", "Composer berhasil diperbarui")
                else:
                    self.root.after(0, self.log_message, f"Gagal memperbarui Composer. Kode error: {return_code}")
                    self.root.after(0, messagebox.showerror, "Error", "Gagal memperbarui Composer")
            
            except Exception as e:
                self.root.after(0, self.log_message, f"Error: {str(e)}")
                self.root.after(0, messagebox.showerror, "Error", f"Gagal memperbarui Composer: {str(e)}")
        
        thread = threading.Thread(target=run_command, daemon=True)
        thread.start()
    
    def show_composer_version(self):
        """Show Composer version"""
        composer_path = self.composer_path_entry.get()
        if not composer_path:
            messagebox.showerror("Error", "Composer path harus diisi!")
            return
        
        cmd = []
        if composer_path.endswith('.phar'):
            cmd.extend(['php', composer_path, '--version'])
        else:
            cmd.extend([composer_path, '--version'])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Composer Version", result.stdout)
            else:
                messagebox.showerror("Error", f"Gagal mendapatkan versi Composer:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mendapatkan versi Composer: {str(e)}")
    
    # Admin tools methods
    def show_php_info(self):
        """Show PHP info"""
        if not self.is_php_running:
            messagebox.showwarning("Peringatan", "PHP Server belum berjalan!")
            return
        
        host = self.host_entry.get()
        port = self.port_entry.get()
        
        url = f"http://{host}:{port}/?phpinfodwibaktindev=1"
        webbrowser.open(url)
        self.log_message(f"Membuka PHP info di: {url}")
    
    def edit_php_ini(self):
        """Tampilkan proses dan port dengan netstat"""
        try:
            # Jalankan netstat untuk melihat port yang digunakan dan proses terkait
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            if result.returncode != 0:
                messagebox.showerror("Error", f"Gagal menjalankan netstat:\n{result.stderr}")
                return

            # Tampilkan hasil di jendela baru
            output_window = tk.Toplevel(self.root)
            output_window.title("Netstat - Port dan Proses")
            output_window.geometry("900x500")
            text_area = scrolledtext.ScrolledText(output_window, wrap=tk.NONE, font=("Consolas", 9))
            text_area.pack(fill=tk.BOTH, expand=True)
            text_area.insert(tk.END, result.stdout)
            text_area.see(tk.END)
            self.log_message("Menampilkan hasil netstat -ano")
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menjalankan netstat: {str(e)}")
    def information(self):
        info_text = (
            "Awan Server Host 9.0 - Enhanced 5 End\n"
            "License: GPLv3 - GNU General Public License v3.0\n"
            "Dibuat oleh: Dwi Bakti N Dev\n"
            "Email: dwibakti76v@gmail.com\n"
            "Phone: +6289652969323\n\n"
            "GitHub: https://github.com/DwiDevelopes\n"
            "GitHub: https://github.com/Royhtml\n\n"
            "Awan Server adalah aplikasi manajemen server lokal berbasis GUI yang memudahkan developer "
            "untuk mengelola berbagai layanan seperti PHP,Golang, Apache, MariaDB/MySQL, FileZilla, Mercury, Tomcat, "
            "Laragon, pyserver, Flutter, Android Emulator, dan Laravel dll dalam satu aplikasi terpadu.\n\n"
            "Fitur utama:\n"
            "- Start/Stop berbagai server lokal dengan mudah\n"
            "- Deteksi otomatis executable server\n"
            "- Monitoring resource sistem (CPU, RAM, Disk)\n"
            "- Tools database (Adminer, phpMyAdmin, backup/restore)\n"
            "- Terminal & shell terintegrasi\n"
            "- Pembuatan project Laravel & Flutter\n"
            "- Pengelolaan Android Emulator\n"
            "- Konfigurasi path dan port yang fleksibel\n\n"
            "Cara Penggunaan:\n"
            "1. Pastikan file awan.ico berada di folder aplikasi untuk menampilkan icon di dialog ini.\n"
            "2. Pilih tab server yang ingin dijalankan (misal: PHP, Apache, MariaDB, dst).\n"
            "3. Atur path executable dan konfigurasi lain jika belum terdeteksi otomatis.\n"
            "4. Klik tombol Start untuk menjalankan server, Stop untuk menghentikan.\n"
            "5. Gunakan tab Tools untuk akses Adminer, phpMyAdmin, backup/restore database, dan cek port/services.\n"
            "6. Tab Terminal menyediakan shortcut ke CMD, PowerShell, Git Bash, dan MySQL Shell.\n"
            "7. Untuk Flutter/Android, pastikan SDK dan emulator sudah terinstall dan path sudah benar.\n"
            "8. Semua log aktivitas akan tampil di bagian bawah aplikasi.\n\n"
            "Aplikasi ini ditujukan untuk mempermudah workflow pengembangan web dan mobile secara lokal, "
            "khususnya bagi pengguna Windows.\n\n"
            "Terima kasih telah menggunakan Awan Server!"
        )
        top = tk.Toplevel(self.root)
        top.title("Informasi License Awan Server")
        top.geometry("500x600")
        top.resizable(False, False)
        try:
            icon_img = Image.open("awan.ico").resize((64, 64))
            icon_photo = ImageTk.PhotoImage(icon_img)
            icon_label = ttk.Label(top, image=icon_photo)
            icon_label.image = icon_photo
            icon_label.pack(pady=(10, 0))
        except Exception:
            pass
        info_label = tk.Label(top, text="Awan Server Host 9.0 - Enhanced 5 End", font=("Segoe UI", 12, "bold"))
        info_label.pack(pady=(10, 0))
        text_area = scrolledtext.ScrolledText(top, wrap=tk.WORD, font=("Segoe UI", 10), height=28, width=60)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        close_btn = ttk.Button(top, text="Tutup", command=top.destroy)
        close_btn.pack(pady=(0, 10))
        self.log_message("Menampilkan informasi pembuat Awan Server")
        
    def launch_adminer(self):
        """Launch Adminer database manager"""
        doc_root = self.doc_root_entry.get()
        adminer_path = os.path.join(doc_root, "adminer.php")
        
        if not os.path.isfile(adminer_path):
            if messagebox.askyesno("Adminer", "Adminer tidak ditemukan. Download Adminer sekarang?"):
                try:
                    import urllib.request
                    adminer_url = "https://www.adminer.org/latest.php"
                    urllib.request.urlretrieve(adminer_url, adminer_path)
                    self.log_message("Adminer berhasil didownload")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal mendownload Adminer: {str(e)}")
                    return
        
        if os.path.isfile(adminer_path):
            if self.is_php_running:
                host = self.host_entry.get()
                port = self.port_entry.get()
                url = f"http://{host}:{port}/adminer.php"
                webbrowser.open(url)
                self.log_message(f"Membuka Adminer di: {url}")
            else:
                messagebox.showwarning("Peringatan", "PHP Server belum berjalan!")
        else:
            messagebox.showerror("Error", "Adminer tidak ditemukan di document root!")
    
    def launch_phpmyadmin(self):
        """Launch phpMyAdmin"""
        possible_paths = [
            os.path.join(self.doc_root_entry.get(), "phpmyadmin"),
            "C:\\xampp\\phpMyAdmin",
            "C:\\Program Files\\phpMyAdmin",
        ]
        
        phpmyadmin_path = None
        for path in possible_paths:
            if os.path.isdir(path):
                phpmyadmin_path = path
                break
        
        if phpmyadmin_path:
            if self.is_php_running or self.is_apache_running:
                host = self.host_entry.get()
                port = self.port_entry.get()
                url = f"http://{host}:{port}/phpmyadmin/" if self.is_php_running else "http://localhost/phpmyadmin/"
                webbrowser.open(url)
                self.log_message(f"Membuka phpMyAdmin di: {url}")
            else:
                messagebox.showwarning("Peringatan", "Server belum berjalan!")
        else:
            messagebox.showinfo("phpMyAdmin", "phpMyAdmin tidak ditemukan. Pastikan sudah terinstall.")
    
    def backup_database(self):
        """Backup database using mysqldump"""
        if not self.is_mariadb_running:
            messagebox.showwarning("Peringatan", "MariaDB Server belum berjalan!")
            return
        
        possible_paths = [
            "mysqldump",
            "C:\\xampp\\mysql\\bin\\mysqldump.exe",
            "C:\\Program Files\\MariaDB\\bin\\mysqldump.exe",
            "C:\\Program Files\\MySQL\\MySQL Server\\bin\\mysqldump.exe",
        ]
        
        mysqldump_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                mysqldump_path = path
                break
        
        if not mysqldump_path:
            messagebox.showerror("Error", "mysqldump tidak ditemukan!")
            return
        
        output_file = filedialog.asksaveasfilename(
            title="Simpan Backup Database",
            defaultextension=".sql",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
        )
        
        if not output_file:
            return
        
        port = self.mariadb_port_entry.get()
        password = self.mariadb_password_entry.get()
        
        cmd = [mysqldump_path, "-u", "root", f"-p{password}", "-P", port, "--all-databases", "--result-file", output_file]
        
        try:
            self.log_message(f"Memulai backup database ke {output_file}")
            subprocess.run(cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Backup database berhasil")
            messagebox.showinfo("Backup", "Backup database berhasil!")
        except subprocess.CalledProcessError as e:
            self.log_message(f"Gagal backup database: {str(e)}")
            messagebox.showerror("Error", f"Gagal backup database: {str(e)}")
    
    def restore_database(self):
        """Restore database from backup"""
        if not self.is_mariadb_running:
            messagebox.showwarning("Peringatan", "MariaDB Server belum berjalan!")
            return
        
        possible_paths = [
            "mysql",
            "C:\\xampp\\mysql\\bin\\mysql.exe",
            "C:\\Program Files\\MariaDB\\bin\\mysql.exe",
            "C:\\Program Files\\MySQL\\MySQL Server\\bin\\mysql.exe",
        ]
        
        mysql_path = None
        for path in possible_paths:
            if os.path.isfile(path):
                mysql_path = path
                break
        
        if not mysql_path:
            messagebox.showerror("Error", "mysql client tidak ditemukan!")
            return
        
        input_file = filedialog.askopenfilename(
            title="Pilih File Backup Database",
            filetypes=[("SQL Files", "*.sql"), ("All Files", "*.*")]
        )
        
        if not input_file:
            return
        
        port = self.mariadb_port_entry.get()
        password = self.mariadb_password_entry.get()
        
        cmd = [mysql_path, "-u", "root", f"-p{password}", "-P", port, "<", input_file]
        
        try:
            self.log_message(f"Memulai restore database dari {input_file}")
            subprocess.run(" ".join(cmd), shell=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
            self.log_message("Restore database berhasil")
            messagebox.showinfo("Restore", "Restore database berhasil!")
        except subprocess.CalledProcessError as e:
            self.log_message(f"Gagal restore database: {str(e)}")
            messagebox.showerror("Error", f"Gagal restore database: {str(e)}")
    
    def check_used_ports(self):
        """Check which ports are in use"""
        ports_to_check = [
            ("PHP Server", self.port_entry.get()),
            ("Apache", "80"),
            ("MariaDB", self.mariadb_port_entry.get()),
            ("FileZilla FTP", self.filezilla_port_entry.get()),
            ("FileZilla Admin", self.filezilla_admin_port_entry.get()),
            ("Mercury SMTP", self.mercury_smtp_port_entry.get()),
            ("Mercury POP3", self.mercury_pop3_port_entry.get()),
            ("Tomcat", self.tomcat_port_entry.get()),
            ("Tomcat Shutdown", self.tomcat_shutdown_port_entry.get()),
        ]
        
        results = []
        for name, port in ports_to_check:
            try:
                port = int(port)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('localhost', port))
                    if result == 0:
                        results.append(f"{name} port {port}: Digunakan")
                    else:
                        results.append(f"{name} port {port}: Tidak digunakan")
            except ValueError:
                results.append(f"{name} port {port}: Port tidak valid")
            except Exception as e:
                results.append(f"{name} port {port}: Error - {str(e)}")
        
        messagebox.showinfo("Port Check", "\n".join(results))
        self.log_message("Melakukan pengecekan port:\n" + "\n".join(results))
    
    def check_windows_services(self):
        """Check Windows services status for common servers"""
        services = [
            "Apache",
            "MySQL",
            "FileZilla Server",
            "Tomcat",
        ]
        
        results = []
        for service in services:
            try:
                result = subprocess.run(
                    ["sc", "query", service],
                    capture_output=True,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                
                if "RUNNING" in result.stdout:
                    results.append(f"{service}: Berjalan")
                elif "STOPPED" in result.stdout:
                    results.append(f"{service}: Berhenti")
                else:
                    results.append(f"{service}: Tidak terinstall")
            except Exception as e:
                results.append(f"{service}: Error - {str(e)}")
        
        messagebox.showinfo("Service Check", "\n".join(results))
        self.log_message("Melakukan pengecekan service:\n" + "\n".join(results))
    
    def on_closing(self):
        """Handle window closing event"""
        # Stop all running servers
        if self.is_php_running:
            self.stop_php_server()
        
        if self.is_apache_running:
            self.stop_apache()
        
        if self.is_mariadb_running:
            self.stop_mariadb()
        
        if self.is_filezilla_running:
            self.stop_filezilla()
        
        if self.is_mercury_running:
            self.stop_mercury()
        
        if self.is_tomcat_running:
            self.stop_tomcat()
        
        if self.is_laragon_running:
            self.stop_laragon()
        
        if self.is_flutter_running:
            self.stop_flutter_server()
        
        if self.is_emulator_running:
            self.stop_android_emulator()
        
        # Save configuration
        self.save_config()
        
        # Close the application
        self.root.destroy()

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