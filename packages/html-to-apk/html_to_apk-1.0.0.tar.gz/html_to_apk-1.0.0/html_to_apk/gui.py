import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import json
import sys
import webbrowser
import tempfile
import http.server
import socketserver
import socket
import time
import platform

class HTMLtoAPKConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML To APK")
        self.root.geometry("730x580")
        self.root.resizable(True, True)
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Variables
        self.html_dir = tk.StringVar()
        self.app_name = tk.StringVar(value="MyApp")
        self.package_name = tk.StringVar(value="com.example.myapp")
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "dist"))
        self.icon_path = tk.StringVar()
        self.splash_path = tk.StringVar()
        self.version = tk.StringVar(value="1.0.0")
        self.orientation = tk.StringVar(value="portrait")
        self.fullscreen = tk.BooleanVar(value=False)
        self.requirements_status = tk.StringVar(value="Checking requirements...")
        
        # Cordova plugins
        self.plugins = {
            "cordova-plugin-whitelist": tk.BooleanVar(value=True),
            "cordova-plugin-file": tk.BooleanVar(value=False),
            "cordova-plugin-camera": tk.BooleanVar(value=False),
            "cordova-plugin-geolocation": tk.BooleanVar(value=False),
            "cordova-plugin-device": tk.BooleanVar(value=False),
            "cordova-plugin-network-information": tk.BooleanVar(value=False),
            "cordova-plugin-splashscreen": tk.BooleanVar(value=True),
            "cordova-plugin-statusbar": tk.BooleanVar(value=False),
            "cordova-plugin-inappbrowser": tk.BooleanVar(value=False),
        }
        
        # Preview server
        self.preview_port = self.find_free_port()
        self.httpd = None
        self.preview_process = None
        
        # UI Setup
        self.create_ui()
        
        # Initial checks
        self.root.after(100, self.check_requirements)
    
    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    def find_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            return s.getsockname()[1]
    
    def create_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Settings Tab
        settings_tab = ttk.Frame(notebook, padding="10")
        notebook.add(settings_tab, text="Settings")
        
        # HTML Folder
        ttk.Label(settings_tab, text="HTML Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.html_dir, width=50).grid(row=0, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_html, width=8).grid(row=0, column=2)
        
        # App Name
        ttk.Label(settings_tab, text="App Name:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.app_name, width=50).grid(row=1, column=1, padx=2)
        
        # Package Name
        ttk.Label(settings_tab, text="Package Name:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.package_name, width=50).grid(row=2, column=1, padx=2)
        
        # Version
        ttk.Label(settings_tab, text="Version:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.version, width=50).grid(row=3, column=1, padx=2)
        
        # Output Directory
        ttk.Label(settings_tab, text="Output Folder:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.output_dir, width=50).grid(row=4, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_output, width=8).grid(row=4, column=2)
        
        # Icon File
        ttk.Label(settings_tab, text="App Icon (192x192 PNG):").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.icon_path, width=50).grid(row=5, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_icon, width=8).grid(row=5, column=2)
        
        # Splash Screen
        ttk.Label(settings_tab, text="Splash Screen (1200x1920 PNG):").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.splash_path, width=50).grid(row=6, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_splash, width=8).grid(row=6, column=2)
        
        # Orientation
        ttk.Label(settings_tab, text="Orientation:").grid(row=7, column=0, sticky=tk.W, pady=2)
        orientation_frame = ttk.Frame(settings_tab)
        orientation_frame.grid(row=7, column=1, sticky=tk.W)
        ttk.Radiobutton(orientation_frame, text="Portrait", variable=self.orientation, value="portrait").pack(side=tk.LEFT)
        ttk.Radiobutton(orientation_frame, text="Landscape", variable=self.orientation, value="landscape").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orientation_frame, text="Both", variable=self.orientation, value="default").pack(side=tk.LEFT)
        
        # Fullscreen
        ttk.Checkbutton(settings_tab, text="Fullscreen", variable=self.fullscreen).grid(row=8, column=0, columnspan=2, sticky=tk.W)
        
        # Plugins Tab
        plugins_tab = ttk.Frame(notebook, padding="10")
        notebook.add(plugins_tab, text="Plugins")
        
        ttk.Label(plugins_tab, text="Select Cordova Plugins:", font=("", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        row_num = 1
        for plugin, var in self.plugins.items():
            ttk.Checkbutton(plugins_tab, text=plugin, variable=var).grid(row=row_num, column=0, sticky=tk.W)
            row_num += 1
        
        # Preview Tab
        preview_tab = ttk.Frame(notebook)
        notebook.add(preview_tab, text="Preview")
        
        preview_frame = ttk.Frame(preview_tab, padding="10")
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.preview_label = ttk.Label(preview_frame, text="No preview available", anchor=tk.CENTER)
        self.preview_label.pack(fill=tk.BOTH, expand=True)
        
        preview_btn_frame = ttk.Frame(preview_tab)
        preview_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(preview_btn_frame, text="Start Preview", command=self.start_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_btn_frame, text="Stop Preview", command=self.stop_preview).pack(side=tk.LEFT, padx=5)
        ttk.Button(preview_btn_frame, text="Open in Browser", command=self.open_in_browser).pack(side=tk.RIGHT, padx=5)
        
        # Console Output
        console_frame = ttk.LabelFrame(main_frame, text="Output Log - Dwi Bakti N Dev", padding="5")
        console_frame.pack(fill=tk.BOTH, expand=False, pady=5)
        
        console_container = ttk.Frame(console_frame, height=150)
        console_container.pack(fill=tk.BOTH, expand=True)
        console_container.pack_propagate(False)
        
        self.console = scrolledtext.ScrolledText(
            console_container, 
            wrap=tk.WORD,
            font=("Consolas", 8),
            state='disabled'
        )
        self.console.pack(fill=tk.BOTH, expand=True)
        
        # Status and Buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(bottom_frame, textvariable=self.requirements_status).pack(side=tk.LEFT, padx=5)
        
        self.install_btn = ttk.Button(
            bottom_frame, 
            text="Install Requirements", 
            command=self.install_requirements,
            width=20
        )
        self.install_btn.pack(side=tk.RIGHT, padx=2)
        
        self.convert_btn = ttk.Button(
            bottom_frame, 
            text="Convert to APK", 
            command=self.start_conversion,
            state=tk.DISABLED,
            width=20
        )
        self.convert_btn.pack(side=tk.RIGHT, padx=2)
    
    def browse_html(self):
        dir_path = filedialog.askdirectory(title="Select HTML Folder")
        if dir_path:
            self.html_dir.set(dir_path)
            default_name = os.path.basename(dir_path)
            if default_name:
                self.app_name.set(default_name)
                default_package = f"com.example.{default_name.lower().replace(' ', '')}"
                self.package_name.set(default_package)
    
    def browse_output(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.output_dir.set(dir_path)
    
    def browse_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File (192x192 PNG)",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.icon_path.set(file_path)
    
    def browse_splash(self):
        file_path = filedialog.askopenfilename(
            title="Select Splash Screen (1200x1920 PNG)",
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.splash_path.set(file_path)
    
    def log(self, message):
        self.console.configure(state='normal')
        self.console.insert(tk.END, message + "\n")
        self.console.see(tk.END)
        self.console.configure(state='disabled')
        self.root.update()
    
    def clear_log(self):
        self.console.configure(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.configure(state='disabled')
    
    def check_requirements(self):
        self.clear_log()
        self.log("Checking system requirements...")
        
        requirements_met = True
        
        # Check Node.js
        try:
            node_version = subprocess.check_output(
                ["node", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log(f"✔ Node.js {node_version} detected")
        except:
            self.log("✖ Node.js not found")
            requirements_met = False
        
        # Check npm
        try:
            npm_version = subprocess.check_output(
                ["npm", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log(f"✔ npm {npm_version} detected")
        except:
            self.log("✖ npm not found")
            requirements_met = False
        
        # Check Cordova
        try:
            cordova_version = subprocess.check_output(
                ["cordova", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log(f"✔ Cordova {cordova_version} detected")
        except:
            self.log("✖ Cordova not found")
            requirements_met = False
        
        # Check Java (for Android)
        try:
            java_version = subprocess.check_output(
                ["java", "-version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip()
            self.log("✔ Java detected")
        except:
            self.log("✖ Java not found (required for Android builds)")
            requirements_met = False
        
        if requirements_met:
            self.requirements_status.set("Requirements satisfied")
            self.convert_btn.config(state=tk.NORMAL)
        else:
            self.requirements_status.set("Requirements missing")
        
        return requirements_met
    
    def install_requirements(self):
        self.clear_log()
        self.log("Installing required packages...")
        
        try:
            # Install Cordova globally
            process = subprocess.Popen(
                ["npm", "install", "-g", "cordova"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                self.log("\n✔ Cordova installed successfully")
                self.requirements_status.set("Requirements satisfied")
                self.convert_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Success", "Cordova installed successfully")
            else:
                raise Exception("Installation failed")
        
        except Exception as e:
            self.log(f"\n✖ Error: {str(e)}")
            self.requirements_status.set("Installation failed")
            messagebox.showerror("Error", f"Failed to install requirements: {str(e)}")
    
    def start_conversion(self):
        if not self.html_dir.get():
            messagebox.showerror("Error", "Please select an HTML folder to convert")
            return
            
        self.convert_btn.config(state=tk.DISABLED)
        self.install_btn.config(state=tk.DISABLED)
        Thread(target=self.convert_to_apk, daemon=True).start()
    
    def convert_to_apk(self):
        try:
            self.clear_log()
            self.log("Starting APK conversion process...")
            
            html_dir = self.html_dir.get()
            app_name = self.app_name.get()
            package_name = self.package_name.get()
            version = self.version.get()
            output_dir = self.output_dir.get()
            icon_path = self.icon_path.get()
            splash_path = self.splash_path.get()
            
            if not os.path.exists(html_dir):
                raise Exception(f"HTML folder not found: {html_dir}")
            
            # Check for index.html
            if not os.path.exists(os.path.join(html_dir, "index.html")):
                raise Exception("No index.html found in the selected folder")
            
            os.makedirs(output_dir, exist_ok=True)
            
            # Create Cordova project
            cordova_dir = os.path.join(output_dir, f"{app_name}-cordova")
            if os.path.exists(cordova_dir):
                shutil.rmtree(cordova_dir)
            
            self.log(f"Creating Cordova project in {cordova_dir}")
            
            process = subprocess.Popen(
                ["cordova", "create", cordova_dir, package_name, app_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Failed to create Cordova project")
            
            # Add Android platform
            self.log("Adding Android platform...")
            process = subprocess.Popen(
                ["cordova", "platform", "add", "android"],
                cwd=cordova_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode != 0:
                raise Exception("Failed to add Android platform")
            
            # Add selected plugins
            self.log("Adding plugins...")
            for plugin, var in self.plugins.items():
                if var.get():
                    process = subprocess.Popen(
                        ["cordova", "plugin", "add", plugin],
                        cwd=cordova_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )
                    
                    for line in process.stdout:
                        self.log(line.strip())
                    
                    process.wait()
                    
                    if process.returncode != 0:
                        self.log(f"Warning: Failed to add plugin {plugin}")
            
            # Copy HTML files to www directory
            www_dir = os.path.join(cordova_dir, "www")
            self.log(f"Copying HTML files from {html_dir} to {www_dir}")
            
            # Clear existing www directory
            for item in os.listdir(www_dir):
                item_path = os.path.join(www_dir, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.unlink(item_path)
            
            # Copy new files
            for item in os.listdir(html_dir):
                s = os.path.join(html_dir, item)
                d = os.path.join(www_dir, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)
            
            # Update config.xml
            config_path = os.path.join(cordova_dir, "config.xml")
            self.log(f"Updating {config_path}")
            
            with open(config_path, "r", encoding="utf-8") as f:
                config_content = f.read()
            
            # Update version
            config_content = config_content.replace('id="{}"'.format(package_name), 
                                            'id="{}" version="{}"'.format(package_name, version))
            
            # Update orientation preference
            orientation_pref = f'<preference name="Orientation" value="{self.orientation.get()}" />'
            config_content = config_content.replace('</widget>', f'{orientation_pref}\n</widget>')
            
            # Add fullscreen preference if needed
            if self.fullscreen.get():
                fullscreen_pref = '<preference name="Fullscreen" value="true" />'
                config_content = config_content.replace('</widget>', f'{fullscreen_pref}\n</widget>')
            
            # Write updated config
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)
            
            # Handle icon and splash screen
            if icon_path or splash_path:
                self.log("Processing icon and splash screen...")
                resources_dir = os.path.join(cordova_dir, "resources")
                os.makedirs(resources_dir, exist_ok=True)
                
                # Create Android subdirectories
                android_icon_dir = os.path.join(resources_dir, "android", "icon")
                android_splash_dir = os.path.join(resources_dir, "android", "splash")
                os.makedirs(android_icon_dir, exist_ok=True)
                os.makedirs(android_splash_dir, exist_ok=True)
                
                if icon_path:
                    # Copy icon to all required sizes (simplified - in a real app you'd resize properly)
                    icon_sizes = {
                        "ldpi.png": 36,
                        "mdpi.png": 48,
                        "hdpi.png": 72,
                        "xhdpi.png": 96,
                        "xxhdpi.png": 144,
                        "xxxhdpi.png": 192
                    }
                    
                    for filename, size in icon_sizes.items():
                        dest_path = os.path.join(android_icon_dir, filename)
                        shutil.copy2(icon_path, dest_path)
                
                if splash_path:
                    # Copy splash to all required sizes (simplified)
                    splash_sizes = {
                        "ldpi.png": [200, 320],
                        "mdpi.png": [320, 480],
                        "hdpi.png": [480, 800],
                        "xhdpi.png": [720, 1280],
                        "xxhdpi.png": [960, 1600],
                        "xxxhdpi.png": [1280, 1920]
                    }
                    
                    for filename, size in splash_sizes.items():
                        dest_path = os.path.join(android_splash_dir, filename)
                        shutil.copy2(splash_path, dest_path)
                
                # Run cordova-res to generate resources
                try:
                    process = subprocess.Popen(
                        ["cordova-res", "android", "--skip-config", "--copy"],
                        cwd=cordova_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        shell=True,
                        text=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )
                    
                    for line in process.stdout:
                        self.log(line.strip())
                    
                    process.wait()
                except:
                    self.log("Note: cordova-res not installed. Using basic icon/splash setup.")
            
            # Build APK
            self.log("Building APK... (this may take several minutes)")
            process = subprocess.Popen(
                ["cordova", "build", "android"],
                cwd=cordova_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            )
            
            for line in process.stdout:
                self.log(line.strip())
            
            process.wait()
            
            if process.returncode == 0:
                # Find the APK file
                apk_dir = os.path.join(cordova_dir, "platforms", "android", "app", "build", "outputs", "apk", "debug")
                if os.path.exists(apk_dir):
                    apk_files = [f for f in os.listdir(apk_dir) if f.endswith(".apk")]
                    if apk_files:
                        apk_path = os.path.join(apk_dir, apk_files[0])
                        final_apk_path = os.path.join(output_dir, f"{app_name}.apk")
                        
                        # Copy APK to output directory
                        shutil.copy2(apk_path, final_apk_path)
                        
                        self.log("\n✔ APK built successfully!")
                        self.log(f"APK file: {final_apk_path}")
                        
                        messagebox.showinfo("Success", f"APK built successfully!\nOutput file: {final_apk_path}")
                    else:
                        raise Exception("APK file not found in build directory")
                else:
                    raise Exception("Build directory not found")
            else:
                raise Exception("Build failed")
        
        except Exception as e:
            self.log(f"\n✖ Error: {str(e)}")
            messagebox.showerror("Error", f"APK conversion failed: {str(e)}")
        finally:
            self.convert_btn.config(state=tk.NORMAL)
            self.install_btn.config(state=tk.NORMAL)
    
    def start_preview(self):
        if not self.html_dir.get():
            messagebox.showerror("Error", "Please select an HTML folder first")
            return
        
        html_dir = self.html_dir.get()
        
        if not os.path.exists(os.path.join(html_dir, "index.html")):
            messagebox.showerror("Error", "No index.html found in the selected folder")
            return
        
        # Stop any existing preview
        self.stop_preview()
        
        # Start HTTP server in a thread
        preview_thread = Thread(target=self.run_preview_server, args=(html_dir,), daemon=True)
        preview_thread.start()
        
        # Wait a moment for server to start
        time.sleep(1)
        
        # Update UI
        self.preview_label.config(text=f"Preview running at http://localhost:{self.preview_port}")
        
        # Open in default browser
        self.open_in_browser()
    
    def run_preview_server(self, directory):
        os.chdir(directory)
        handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", self.preview_port), handler) as httpd:
            self.httpd = httpd
            httpd.serve_forever()
    
    def stop_preview(self):
        if hasattr(self, 'httpd') and self.httpd:
            self.httpd.shutdown()
            self.httpd.server_close()
            self.httpd = None
        
        self.preview_label.config(text="Preview stopped")
    
    def open_in_browser(self):
        if self.preview_port:
            webbrowser.open(f"http://localhost:{self.preview_port}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    
    app = HTMLtoAPKConverter(root)
    root.mainloop()
def run_gui():
    root = tk.Tk()
    app = HTMLtoAPKConverter(root)
    root.mainloop()