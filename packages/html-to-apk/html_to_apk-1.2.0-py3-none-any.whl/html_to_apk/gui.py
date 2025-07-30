import os
import shutil
import subprocess
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
import sys
import webbrowser
import http.server
import socketserver
import socket
import time
import platform
import zipfile
from PIL import Image, ImageTk

class HTMLtoEXEConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("HTML To APK")
        self.root.geometry("800x650")
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
        self.version_code = tk.StringVar(value="100")
        self.orientation = tk.StringVar(value="portrait")
        self.fullscreen = tk.BooleanVar(value=True)
        self.requirements_status = tk.StringVar(value="Checking requirements...")
        self.build_mode = tk.StringVar(value="debug")
        self.keystore_path = tk.StringVar()
        self.keystore_password = tk.StringVar()
        self.key_alias = tk.StringVar()
        self.key_password = tk.StringVar()
        
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
            "cordova-plugin-androidx": tk.BooleanVar(value=True),
            "cordova-plugin-androidx-adapter": tk.BooleanVar(value=True),
        }
        
        # Preview server
        self.preview_port = self.find_free_port()
        self.httpd = None
        
        # UI Setup
        self.create_ui()
        
        # Initial checks
        self.check_requirements()
    
    def set_window_icon(self):
        try:
            if platform.system() == "Windows":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("HTMLtoAPK.Pro.1.0")
            
            icon_path = self.resource_path("icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting icon: {e}")
    
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
        ttk.Entry(settings_tab, textvariable=self.version, width=20).grid(row=3, column=1, sticky=tk.W, padx=2)
        
        # Version Code
        ttk.Label(settings_tab, text="Version Code:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.version_code, width=20).grid(row=4, column=1, sticky=tk.W, padx=2)
        
        # Output Directory
        ttk.Label(settings_tab, text="Output Folder:").grid(row=5, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.output_dir, width=50).grid(row=5, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_output, width=8).grid(row=5, column=2)
        
        # Icon File
        ttk.Label(settings_tab, text="App Icon (192x192 PNG):").grid(row=6, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.icon_path, width=50).grid(row=6, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_icon, width=8).grid(row=6, column=2)
        
        # Splash Screen
        ttk.Label(settings_tab, text="Splash Screen (1200x1920 PNG):").grid(row=7, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.splash_path, width=50).grid(row=7, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_splash, width=8).grid(row=7, column=2)
        
        # Orientation
        ttk.Label(settings_tab, text="Orientation:").grid(row=8, column=0, sticky=tk.W, pady=2)
        orientation_frame = ttk.Frame(settings_tab)
        orientation_frame.grid(row=8, column=1, sticky=tk.W)
        ttk.Radiobutton(orientation_frame, text="Portrait", variable=self.orientation, value="portrait").pack(side=tk.LEFT)
        ttk.Radiobutton(orientation_frame, text="Landscape", variable=self.orientation, value="landscape").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(orientation_frame, text="Both", variable=self.orientation, value="default").pack(side=tk.LEFT)
        
        # Fullscreen
        ttk.Checkbutton(settings_tab, text="Fullscreen", variable=self.fullscreen).grid(row=9, column=0, columnspan=2, sticky=tk.W)
        
        # Build Mode
        ttk.Label(settings_tab, text="Build Mode:").grid(row=10, column=0, sticky=tk.W, pady=2)
        build_frame = ttk.Frame(settings_tab)
        build_frame.grid(row=10, column=1, sticky=tk.W)
        ttk.Radiobutton(build_frame, text="Debug", variable=self.build_mode, value="debug").pack(side=tk.LEFT)
        ttk.Radiobutton(build_frame, text="Release", variable=self.build_mode, value="release").pack(side=tk.LEFT, padx=5)
        
        # Keystore Settings
        ttk.Label(settings_tab, text="Keystore Path:").grid(row=11, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.keystore_path, width=50).grid(row=11, column=1, padx=2)
        ttk.Button(settings_tab, text="Browse", command=self.browse_keystore, width=8).grid(row=11, column=2)
        
        ttk.Label(settings_tab, text="Keystore Password:").grid(row=12, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.keystore_password, show="*", width=50).grid(row=12, column=1, padx=2)
        
        ttk.Label(settings_tab, text="Key Alias:").grid(row=13, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.key_alias, width=50).grid(row=13, column=1, padx=2)
        
        ttk.Label(settings_tab, text="Key Password:").grid(row=14, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_tab, textvariable=self.key_password, show="*", width=50).grid(row=14, column=1, padx=2)
        
        # Plugins Tab
        plugins_tab = ttk.Frame(notebook, padding="10")
        notebook.add(plugins_tab, text="Plugins")
        
        ttk.Label(plugins_tab, text="Select Cordova Plugins:", font=("", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        # Create two columns for plugins
        row_num = 1
        col_num = 0
        for i, (plugin, var) in enumerate(self.plugins.items()):
            if i % 10 == 0 and i != 0:
                col_num += 1
                row_num = 1
            ttk.Checkbutton(plugins_tab, text=plugin, variable=var).grid(row=row_num, column=col_num, sticky=tk.W)
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
        console_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="5")
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
    
    def browse_keystore(self):
        file_path = filedialog.askopenfilename(
            title="Select Keystore File",
            filetypes=[("Keystore Files", "*.keystore *.jks"), ("All Files", "*.*")]
        )
        if file_path:
            self.keystore_path.set(file_path)
    
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
        
        # Check Gradle (for Android)
        try:
            gradle_version = subprocess.check_output(
                ["gradle", "--version"],
                stderr=subprocess.STDOUT,
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            ).decode().strip().split('\n')[0]
            self.log(f"✔ {gradle_version} detected")
        except:
            self.log("✖ Gradle not found (required for Android builds)")
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
            self.log("Installing Cordova...")
            process = subprocess.Popen(
                ["npm", "install", "-g", "cordova", "cordova-res"],
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
    
    def run_command_in_cmd(self, command, cwd=None, wait=False):
        """Run command in a visible CMD window and optionally wait for completion"""
        if platform.system() == "Windows":
            # On Windows, create a new CMD window
            cmd = f'start cmd /k "{command} && exit"'
            if wait:
                cmd = f'start /wait cmd /k "{command} && exit"'
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                shell=True
            )
        else:
            # On other platforms, run in terminal
            if sys.platform == "darwin":  # macOS
                terminal_cmd = f'osascript -e \'tell app "Terminal" to do script "cd {cwd} && {command}"\''
            else:  # Linux
                terminal_cmd = f'x-terminal-emulator -e "bash -c \'cd {cwd} && {command}; exec bash\'"'
            
            process = subprocess.Popen(
                terminal_cmd,
                shell=True
            )
        
        if wait:
            process.wait()
        return process
    
    def convert_to_apk(self):
        try:
            self.clear_log() 
            self.log("Starting APK conversion process...")
            
            html_dir = self.html_dir.get()
            app_name = self.app_name.get()
            package_name = self.package_name.get()
            version = self.version.get()
            version_code = self.version_code.get()
            output_dir = self.output_dir.get()
            icon_path = self.icon_path.get()
            splash_path = self.splash_path.get()
            build_mode = self.build_mode.get()
            
            if not os.path.exists(html_dir):
                raise Exception(f"HTML folder not found: {html_dir}")
            
            # Check for index.html
            if not os.path.exists(os.path.join(html_dir, "index.html")):
                raise Exception("No index.html found in the selected folder")
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Create Cordova project directory
            cordova_dir = os.path.join(output_dir, f"{app_name}-cordova")
            
            # Remove existing directory if it exists
            if os.path.exists(cordova_dir):
                self.log(f"Removing existing directory: {cordova_dir}")
                shutil.rmtree(cordova_dir)
            
            # Create the directory first
            os.makedirs(cordova_dir, exist_ok=True)
            self.log(f"Created directory: {cordova_dir}")
            
            # 1. Create Cordova project
            self.log(f"Creating Cordova project in {cordova_dir}")
            self.run_command_in_cmd(
                f"cordova create . {package_name} {app_name}",
                cwd=cordova_dir,
                wait=True
            )
            
            # Verify project creation
            if not os.path.exists(os.path.join(cordova_dir, "config.xml")):
                raise Exception("Failed to create Cordova project")

            # 2. Add Android platform
            self.log("Adding Android platform...")
            self.run_command_in_cmd(
                "cordova platform add android@11.0.0",
                cwd=cordova_dir,
                wait=True
            )
            
            # Verify platform addition
            if not os.path.exists(os.path.join(cordova_dir, "platforms", "android")):
                raise Exception("Failed to add Android platform")

            # 3. Update Gradle configuration
            gradle_wrapper_path = os.path.join(
                cordova_dir, "platforms", "android", "gradle", "wrapper", "gradle-wrapper.properties"
            )
            if os.path.exists(gradle_wrapper_path):
                with open(gradle_wrapper_path, "w") as f:
                    f.write("""distributionBase=GRADLE_USER_HOME
    distributionPath=wrapper/dists
    distributionUrl=https\\://services.gradle.org/distributions/gradle-7.5-all.zip
    zipStoreBase=GRADLE_USER_HOME
    zipStorePath=wrapper/dists
    """)
                self.log("Updated gradle-wrapper.properties to use Gradle 7.5")

            # 4. Add plugins one by one
            self.log("Adding plugins...")
            for plugin, var in self.plugins.items():
                if var.get():
                    self.run_command_in_cmd(
                        f"cordova plugin add {plugin}",
                        cwd=cordova_dir,
                        wait=True
                    )
                    self.log(f"Added plugin: {plugin}")

            # 5. Copy HTML files
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

            # 6. Update config.xml
            config_path = os.path.join(cordova_dir, "config.xml")
            self.log(f"Updating {config_path}")
            
            with open(config_path, "r", encoding="utf-8") as f:
                config_content = f.read()
            
            # Update version and version code
            config_content = config_content.replace('id="{}"'.format(package_name), 
                                    'id="{}" version="{}" android-versionCode="{}"'.format(
                                        package_name, version, version_code))
            
            # Add important preferences
            preferences = [
                f'<preference name="Orientation" value="{self.orientation.get()}" />',
                '<preference name="android-minSdkVersion" value="22" />',
                '<preference name="android-targetSdkVersion" value="33" />',
                '<preference name="GradlePluginGoogleServicesEnabled" value="true" />',
                '<preference name="GradlePluginGoogleServicesVersion" value="4.3.15" />',
                '<preference name="AndroidPersistentFileLocation" value="Internal" />',
                '<preference name="AndroidExtraFilesystems" value="files,files-external,documents,sdcard,cache,cache-external,root" />',
                '<preference name="loadUrlTimeoutValue" value="700000" />'
            ]
            
            if self.fullscreen.get():
                preferences.append('<preference name="Fullscreen" value="true" />')
            
            for pref in preferences:
                config_content = config_content.replace('</widget>', f'{pref}\n</widget>')
            
            # Write updated config
            with open(config_path, "w", encoding="utf-8") as f:
                f.write(config_content)

            # 7. Configure Gradle properties
            gradle_properties_path = os.path.join(cordova_dir, "platforms", "android", "gradle.properties")
            with open(gradle_properties_path, "w") as f:
                f.write("org.gradle.daemon=true\n")
                f.write("org.gradle.parallel=true\n")
                f.write("org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8\n")
                f.write("android.useAndroidX=true\n")
                f.write("android.enableJetifier=true\n")

            # 8. Handle icon and splash screen
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
                
                try:
                    self.run_command_in_cmd(
                        "cordova-res android --skip-config --copy",
                        cwd=cordova_dir,
                        wait=True
                    )
                except:
                    self.log("Note: cordova-res not installed. Using basic icon/splash setup.")

            # 9. Build APK
            self.log("Building APK... (this may take several minutes)")
            
            build_command = "cordova build android -- --warning-mode=none"
            
            if build_mode == "release":
                build_command += " --release"
                if self.keystore_path.get():
                    build_command += f' --keystore "{self.keystore_path.get()}"'
                    build_command += f' --storePassword "{self.keystore_password.get()}"'
                    build_command += f' --alias "{self.key_alias.get()}"'
                    if self.key_password.get():
                        build_command += f' --password "{self.key_password.get()}"'
            
            self.run_command_in_cmd(
                build_command,
                cwd=cordova_dir,
                wait=True
            )

            # 10. Find and copy APK
            apk_dir = os.path.join(
                cordova_dir, "platforms", "android", "app", "build", "outputs", "apk", 
                "debug" if build_mode == "debug" else "release"
            )
            
            # Wait for APK file
            timeout = time.time() + 600  # 10 minutes
            apk_files = []
            
            while time.time() < timeout:
                if os.path.exists(apk_dir):
                    apk_files = [f for f in os.listdir(apk_dir) if f.endswith(".apk")]
                    if apk_files:
                        break
                time.sleep(5)
            
            if apk_files:
                apk_path = os.path.join(apk_dir, apk_files[0])
                final_apk_name = f"{app_name}-{build_mode}.apk"
                final_apk_path = os.path.join(output_dir, final_apk_name)
                
                shutil.copy2(apk_path, final_apk_path)
                
                self.log("\n✔ APK built successfully!")
                self.log(f"APK file: {final_apk_path}")
                
                # Open output directory
                if platform.system() == "Windows":
                    os.startfile(output_dir)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", output_dir])
                else:
                    subprocess.Popen(["xdg-open", output_dir])
                
                messagebox.showinfo("Success", f"APK built successfully!\nOutput file: {final_apk_path}")
            else:
                raise Exception("APK file not found in build directory after waiting")
        
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

    
    app = HTMLtoEXEConverter(root)
    root.mainloop()
def run_gui():
    root = tk.Tk()
    app = HTMLtoEXEConverter(root)
    root.mainloop()