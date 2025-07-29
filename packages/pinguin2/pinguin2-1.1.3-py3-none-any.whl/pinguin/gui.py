import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from cryptography.fernet import Fernet
import subprocess
import os
import sys
import random
import string
import webbrowser
import hashlib
import base64
from datetime import datetime, timedelta
import tempfile
import shutil
import json

class PythonEncryptorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Compile Pinguin")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        self.icon_path = os.path.join(os.path.dirname(__file__), "roy.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Enhanced certificate data
        self.certificate_data = {
            "company": "Dwi Bakti N Dev Inc.",
            "issued_to": "Premium User",
            "valid_from": datetime.now().strftime("%Y-%m-%d"),
            "valid_to": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "serial_number": "SP-" + ''.join(random.choices(string.digits, k=8)),
            "signature_algorithm": "SHA256-RSA",
            "public_key": self.generate_virtual_key(),
            "features": "Python, C++, Web, Kernel, Full Encryption"
        }
        
        # Initialize styles
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('.', background='#f0f0f0')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        self.style.configure('TButton', font=('Segoe UI', 9))
        self.style.configure('TEntry', font=('Segoe UI', 9))
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 9, 'bold'), padding=[10, 5])
        
        # Initialize variables
        self.target_file = tk.StringVar()
        self.icon_file = tk.StringVar()
        self.output_name = tk.StringVar(value="protected_app")
        self.use_random_key = tk.BooleanVar(value=True)
        self.custom_key = tk.StringVar()
        self.access_key = tk.StringVar()
        self.license_valid = tk.BooleanVar(value=False)
        self.kernel_source_file = tk.StringVar()
        self.kernel_output_name = tk.StringVar(value="kernel_module")
        self.kernel_optimize_level = tk.StringVar(value="2")
        self.html_source_file = tk.StringVar()
        self.html_output_name = tk.StringVar(value="Encrypted_page")
        self.web_project_folder = tk.StringVar()
        self.web_output_name = tk.StringVar(value="web_app")
        self.cpp_source_file = tk.StringVar()
        self.cpp_output_name = tk.StringVar(value="cpp_program")
        self.cpp_optimize_level = tk.StringVar(value="2")
        self.cpp_encrypt_code = tk.BooleanVar(value=False)
        self.cpp_icon_file = tk.StringVar()
        self.cpp_debug_info = tk.BooleanVar(value=False)
        
        # Advanced compilation options
        self.include_tkinter = tk.BooleanVar(value=True)
        self.include_kivy = tk.BooleanVar(value=False)
        self.include_pandas = tk.BooleanVar(value=False)
        self.include_numpy = tk.BooleanVar(value=False)
        self.include_qt = tk.BooleanVar(value=False)
        self.include_selenium = tk.BooleanVar(value=False)
        self.include_requests = tk.BooleanVar(value=False)
        self.include_pillow = tk.BooleanVar(value=False)
        self.include_sqlite = tk.BooleanVar(value=True)
        
        # Web compilation options
        self.web_browser_type = tk.StringVar(value="cef")
        self.web_fullscreen = tk.BooleanVar(value=False)
        self.web_kiosk_mode = tk.BooleanVar(value=False)
        self.web_enable_devtools = tk.BooleanVar(value=False)
        
        self.create_widgets()
        
        # Load last used settings if available
        self.load_settings()

    def generate_virtual_key(self):
        """Generate a virtual public key for certificate"""
        random_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        return base64.b64encode(random_str.encode()).decode()

    def create_widgets(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # License frame
        license_frame = ttk.LabelFrame(main_container, text=" License Verification ", padding=10)
        license_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(license_frame, text="Access Key:").pack(side=tk.LEFT)
        ttk.Entry(license_frame, textvariable=self.access_key, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(license_frame, text="Validate", command=self.validate_license).pack(side=tk.LEFT, padx=5)
        ttk.Label(license_frame, textvariable=lambda: "✔ Valid" if self.license_valid.get() else "✖ Invalid", 
                 foreground="green" if self.license_valid.get() else "red").pack(side=tk.LEFT, padx=10)
        ttk.Button(license_frame, text="Get License", command=self.open_license_page).pack(side=tk.RIGHT)

        # Main notebook
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Python Encryption Tab
        self.create_python_encryption_tab(notebook)
        
        # Python Compilation Tab
        self.create_python_compilation_tab(notebook)
        
        # Kernel Compilation Tab
        self.create_kernel_compilation_tab(notebook)
        
        # HTML Encryption Tab
        self.create_html_encryption_tab(notebook)
        
        # Web to EXE Tab
        self.create_web_to_exe_tab(notebook)
        
        # C++ Compilation Tab
        self.create_cpp_compilation_tab(notebook)
        
        # Certificate Tab
        self.create_certificate_tab(notebook)
        
        # Advanced Tab
        self.create_advanced_tab(notebook)

        # Status bar
        status_frame = ttk.Frame(main_container)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        self.status_label = ttk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X)

    def create_python_encryption_tab(self, notebook):
        """Create the Python encryption tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Python Encryption")

        # File selection
        ttk.Label(tab, text="Python File to Encrypt:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.target_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_python_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Preview", command=self.preview_source).pack(side=tk.LEFT, padx=5)

        # Output options
        ttk.Label(tab, text="Output Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Encryption key options
        key_frame = ttk.LabelFrame(tab, text=" Encryption Key Options ", padding=10)
        key_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        ttk.Radiobutton(key_frame, text="Generate Random Key", variable=self.use_random_key, value=True).pack(anchor=tk.W)
        ttk.Radiobutton(key_frame, text="Use Custom Key", variable=self.use_random_key, value=False).pack(anchor=tk.W)

        custom_key_frame = ttk.Frame(key_frame)
        custom_key_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Entry(custom_key_frame, textvariable=self.custom_key, state='disabled', width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(custom_key_frame, text="Generate Key", command=self.generate_custom_key).pack(side=tk.LEFT)

        self.use_random_key.trace('w', self.toggle_custom_key)

        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=5, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Encrypt Python File", command=self.encrypt_file, style='Accent.TButton').pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Advanced Options", command=self.show_advanced_encryption_options).pack(side=tk.LEFT, padx=5)

        tab.columnconfigure(0, weight=1)

    def create_python_compilation_tab(self, notebook):
        """Create the Python compilation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Python Compilation")

        # File selection
        ttk.Label(tab, text="Python File to Compile:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        self.compile_target_file = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.compile_target_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_compile_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Preview", command=self.preview_compile_file).pack(side=tk.LEFT, padx=5)

        # Output options
        ttk.Label(tab, text="Output Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        self.compile_output_name = tk.StringVar(value="compiled_app")
        ttk.Entry(tab, textvariable=self.compile_output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Icon selection
        ttk.Label(tab, text="Icon File (optional):", font=('Segoe UI', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        icon_frame = ttk.Frame(tab)
        icon_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        self.compile_icon_file = tk.StringVar()
        ttk.Entry(icon_frame, textvariable=self.compile_icon_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(icon_frame, text="Browse", command=self.browse_compile_icon).pack(side=tk.LEFT)

        # Basic compilation options
        options_frame = ttk.LabelFrame(tab, text=" Basic Compilation Options ", padding=10)
        options_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        self.onefile_option = tk.BooleanVar(value=True)
        self.windowed_option = tk.BooleanVar(value=True)
        self.clean_option = tk.BooleanVar(value=True)
        self.upx_option = tk.BooleanVar(value=True)
        self.console_option = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(options_frame, text="Create single executable (--onefile)", variable=self.onefile_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Windowed mode (no console) (--windowed)", variable=self.windowed_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Clean build files after compilation (--clean)", variable=self.clean_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Use UPX compression (--upx)", variable=self.upx_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Show console window (--console)", variable=self.console_option).pack(anchor=tk.W)

        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=7, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Preview Compilation Command", command=self.preview_compilation_command).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Compile to EXE", command=self.compile_file, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Advanced Options", command=self.show_advanced_compilation_options).pack(side=tk.LEFT)

        tab.columnconfigure(0, weight=1)

    def create_kernel_compilation_tab(self, notebook):
        """Create the kernel compilation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Kernel Compilation")

        # File selection
        ttk.Label(tab, text="Kernel Source File:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.kernel_source_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_kernel_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Preview", command=self.preview_kernel_file).pack(side=tk.LEFT, padx=5)

        # Output options
        ttk.Label(tab, text="Output Module Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.kernel_output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Kernel Compilation Options ", padding=10)
        options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        
        ttk.Label(options_frame, text="Optimization Level:").pack(anchor=tk.W)
        opt_frame = ttk.Frame(options_frame)
        opt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Radiobutton(opt_frame, text="O0 (None)", variable=self.kernel_optimize_level, value="0").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O1 (Basic)", variable=self.kernel_optimize_level, value="1").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O2 (Recommended)", variable=self.kernel_optimize_level, value="2").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O3 (Aggressive)", variable=self.kernel_optimize_level, value="3").pack(side=tk.LEFT)

        self.kernel_debug_info = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Include debug information (-g)", variable=self.kernel_debug_info).pack(anchor=tk.W)

        # Action button
        ttk.Button(tab, text="Compile Kernel Module", command=self.compile_kernel, style='Accent.TButton').grid(row=5, column=0, pady=(10, 0), sticky=tk.W)

        tab.columnconfigure(0, weight=1)

    def create_html_encryption_tab(self, notebook):
        """Create the HTML encryption tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="HTML Encryption")

        # File selection
        ttk.Label(tab, text="HTML Source File:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.html_source_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_html_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Preview", command=self.preview_html_file).pack(side=tk.LEFT, padx=5)

        # Output options
        ttk.Label(tab, text="Output Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.html_output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Encryption options
        options_frame = ttk.LabelFrame(tab, text=" HTML Encryption Options ", padding=10)
        options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        self.html_minify = tk.BooleanVar(value=True)
        self.html_embed_images = tk.BooleanVar(value=True)
        self.html_compress = tk.BooleanVar(value=True)
        self.html_obfuscate = tk.BooleanVar(value=True)
        self.html_encrypt = tk.BooleanVar(value=True)
        self.html_protect_source = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Minify HTML", variable=self.html_minify).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Embed images (base64)", variable=self.html_embed_images).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Compress output", variable=self.html_compress).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Obfuscate code", variable=self.html_obfuscate).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Encrypt content", variable=self.html_encrypt).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Protect source code", variable=self.html_protect_source).pack(anchor=tk.W)

        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=5, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Preview HTML", command=self.preview_html_output).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Encrypt HTML", command=self.encrypt_html, style='Accent.TButton').pack(side=tk.LEFT, padx=5)

        tab.columnconfigure(0, weight=1)

    def create_web_to_exe_tab(self, notebook):
        """Create the Web to EXE tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Web to EXE")

        # Project folder selection
        ttk.Label(tab, text="Web Project Folder:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        folder_frame = ttk.Frame(tab)
        folder_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(folder_frame, textvariable=self.web_project_folder, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(folder_frame, text="Browse", command=self.browse_web_folder).pack(side=tk.LEFT)

        # Output options
        ttk.Label(tab, text="Output Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.web_output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Browser options
        browser_frame = ttk.LabelFrame(tab, text=" Browser Options ", padding=10)
        browser_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        ttk.Label(browser_frame, text="Browser Engine:").pack(anchor=tk.W)
        browser_opt_frame = ttk.Frame(browser_frame)
        browser_opt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Radiobutton(browser_opt_frame, text="CEF (Chromium)", variable=self.web_browser_type, value="cef").pack(side=tk.LEFT)
        ttk.Radiobutton(browser_opt_frame, text="WebView (Native)", variable=self.web_browser_type, value="webview").pack(side=tk.LEFT)
        ttk.Radiobutton(browser_opt_frame, text="Edge (Windows)", variable=self.web_browser_type, value="edge").pack(side=tk.LEFT)

        ttk.Checkbutton(browser_frame, text="Fullscreen mode", variable=self.web_fullscreen).pack(anchor=tk.W)
        ttk.Checkbutton(browser_frame, text="Kiosk mode (no exit)", variable=self.web_kiosk_mode).pack(anchor=tk.W)
        ttk.Checkbutton(browser_frame, text="Enable DevTools", variable=self.web_enable_devtools).pack(anchor=tk.W)

        # Server options
        server_frame = ttk.LabelFrame(tab, text=" Server Options ", padding=10)
        server_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        self.web_port = tk.StringVar(value="8000")
        self.web_window_size = tk.StringVar(value="1024x768")
        self.web_encrypt = tk.BooleanVar(value=True)
        self.web_single_file = tk.BooleanVar(value=True)
        self.web_auto_start = tk.BooleanVar(value=True)

        ttk.Label(server_frame, text="Server Port:").pack(anchor=tk.W)
        ttk.Entry(server_frame, textvariable=self.web_port, width=10).pack(anchor=tk.W)
        ttk.Label(server_frame, text="Window Size:").pack(anchor=tk.W)
        ttk.Entry(server_frame, textvariable=self.web_window_size, width=10).pack(anchor=tk.W)
        ttk.Checkbutton(server_frame, text="Encrypt web content", variable=self.web_encrypt).pack(anchor=tk.W)
        ttk.Checkbutton(server_frame, text="Single executable", variable=self.web_single_file).pack(anchor=tk.W)
        ttk.Checkbutton(server_frame, text="Auto-start server", variable=self.web_auto_start).pack(anchor=tk.W)

        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=6, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Preview Web App", command=self.preview_web_app).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Compile Web to EXE", command=self.compile_web_to_exe, style='Accent.TButton').pack(side=tk.LEFT, padx=5)

        tab.columnconfigure(0, weight=1)

    def create_cpp_compilation_tab(self, notebook):
        """Create the C++ compilation tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="C++ Compilation")

        # File selection
        ttk.Label(tab, text="C++ Source File:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.cpp_source_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_cpp_file).pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Preview", command=self.preview_cpp_file).pack(side=tk.LEFT, padx=5)

        # Output options
        ttk.Label(tab, text="Output Name:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.cpp_output_name, width=40).grid(row=3, column=0, sticky=tk.W, pady=(0, 15))

        # Icon selection
        ttk.Label(tab, text="Icon File (optional):", font=('Segoe UI', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        icon_frame = ttk.Frame(tab)
        icon_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))
        ttk.Entry(icon_frame, textvariable=self.cpp_icon_file, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(icon_frame, text="Browse", command=self.browse_cpp_icon).pack(side=tk.LEFT)

        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" C++ Compilation Options ", padding=10)
        options_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(0, 15))

        ttk.Label(options_frame, text="Optimization Level:").pack(anchor=tk.W)
        opt_frame = ttk.Frame(options_frame)
        opt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Radiobutton(opt_frame, text="O0 (None)", variable=self.cpp_optimize_level, value="0").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O1 (Basic)", variable=self.cpp_optimize_level, value="1").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O2 (Recommended)", variable=self.cpp_optimize_level, value="2").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O3 (Aggressive)", variable=self.cpp_optimize_level, value="3").pack(side=tk.LEFT)

        ttk.Checkbutton(options_frame, text="Include debug information (-g)", variable=self.cpp_debug_info).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Encrypt sensitive strings", variable=self.cpp_encrypt_code).pack(anchor=tk.W)

        # Action button
        ttk.Button(tab, text="Compile C++ Code", command=self.compile_cpp, style='Accent.TButton').grid(row=7, column=0, pady=(10, 0), sticky=tk.W)

        tab.columnconfigure(0, weight=1)

    def create_certificate_tab(self, notebook):
        """Create the certificate tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Certificate")

        cert_info_frame = ttk.LabelFrame(tab, text=" Virtual Certificate Information ", padding=10)
        cert_info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        cert_text = scrolledtext.ScrolledText(cert_info_frame, width=80, height=15, font=('Consolas', 9))
        cert_text.pack(fill=tk.BOTH, expand=True)

        cert_info = f"""Issued To: {self.certificate_data['issued_to']}
Issued By: {self.certificate_data['company']}
Valid From: {self.certificate_data['valid_from']}
Valid To: {self.certificate_data['valid_to']}
Serial Number: {self.certificate_data['serial_number']}
Signature Algorithm: {self.certificate_data['signature_algorithm']}
Public Key: {self.certificate_data['public_key']}
Features: {self.certificate_data['features']}"""

        cert_text.insert(tk.END, cert_info)
        cert_text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=(10, 0))
        ttk.Button(btn_frame, text="Export Certificate", command=self.export_certificate).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Generate New", command=self.generate_new_certificate).pack(side=tk.LEFT, padx=5)

    def create_advanced_tab(self, notebook):
        """Create the advanced options tab"""
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Advanced")

        # Python libraries to include
        libs_frame = ttk.LabelFrame(tab, text=" Python Libraries to Include ", padding=10)
        libs_frame.pack(fill=tk.X, padx=10, pady=10)

        ttk.Checkbutton(libs_frame, text="Tkinter (GUI)", variable=self.include_tkinter).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="Kivy (Mobile/Desktop GUI)", variable=self.include_kivy).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="Pandas (Data Analysis)", variable=self.include_pandas).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="NumPy (Numerical Computing)", variable=self.include_numpy).grid(row=1, column=1, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="PyQt/PySide (Qt GUI)", variable=self.include_qt).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="Selenium (Web Automation)", variable=self.include_selenium).grid(row=2, column=1, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="Requests (HTTP)", variable=self.include_requests).grid(row=3, column=0, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="Pillow (Image Processing)", variable=self.include_pillow).grid(row=3, column=1, sticky=tk.W)
        ttk.Checkbutton(libs_frame, text="SQLite (Database)", variable=self.include_sqlite).grid(row=4, column=0, sticky=tk.W)

        # Additional options
        options_frame = ttk.LabelFrame(tab, text=" Additional Options ", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        self.auto_update = tk.BooleanVar(value=True)
        self.save_settings = tk.BooleanVar(value=True)
        self.enable_logging = tk.BooleanVar(value=True)
        self.check_updates = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Auto-update libraries", variable=self.auto_update).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Save settings on exit", variable=self.save_settings).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Enable detailed logging", variable=self.enable_logging).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(options_frame, text="Check for updates on startup", variable=self.check_updates).grid(row=1, column=1, sticky=tk.W)

        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Save Settings", command=self.save_settings_to_file).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Reset to Defaults", command=self.reset_settings).pack(side=tk.LEFT, padx=5)

    def show_advanced_encryption_options(self):
        """Show advanced encryption options dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Encryption Options")
        dialog.geometry("500x400")
        dialog.resizable(False, False)

        # Add advanced options here
        ttk.Label(dialog, text="Advanced Encryption Settings", font=('Segoe UI', 10, 'bold')).pack(pady=10)

        options_frame = ttk.Frame(dialog)
        options_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.encrypt_imports = tk.BooleanVar(value=True)
        self.obfuscate_names = tk.BooleanVar(value=True)
        self.anti_debug = tk.BooleanVar(value=True)
        self.anti_tamper = tk.BooleanVar(value=True)
        self.license_check = tk.BooleanVar(value=True)

        ttk.Checkbutton(options_frame, text="Encrypt import statements", variable=self.encrypt_imports).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Obfuscate variable/function names", variable=self.obfuscate_names).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Add anti-debugging checks", variable=self.anti_debug).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Add anti-tampering protection", variable=self.anti_tamper).pack(anchor=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Add license verification", variable=self.license_check).pack(anchor=tk.W, pady=2)

        ttk.Button(dialog, text="Apply", command=dialog.destroy).pack(pady=10)

    def show_advanced_compilation_options(self):
        """Show advanced compilation options dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Advanced Compilation Options")
        dialog.geometry("600x500")
        dialog.resizable(False, False)

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # General options tab
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")

        ttk.Label(general_tab, text="Additional PyInstaller Options", font=('Segoe UI', 9, 'bold')).pack(pady=5)
        
        self.additional_args = tk.StringVar()
        ttk.Entry(general_tab, textvariable=self.additional_args, width=70).pack(pady=5)
        ttk.Label(general_tab, text="Space-separated additional PyInstaller arguments").pack()

        # Hidden imports tab
        imports_tab = ttk.Frame(notebook)
        notebook.add(imports_tab, text="Hidden Imports")

        ttk.Label(imports_tab, text="Specify modules to include explicitly", font=('Segoe UI', 9, 'bold')).pack(pady=5)
        
        self.hidden_imports = scrolledtext.ScrolledText(imports_tab, width=70, height=10)
        self.hidden_imports.pack(pady=5)
        ttk.Label(imports_tab, text="One module per line").pack()

        # Data files tab
        data_tab = ttk.Frame(notebook)
        notebook.add(data_tab, text="Data Files")

        ttk.Label(data_tab, text="Additional files to include", font=('Segoe UI', 9, 'bold')).pack(pady=5)
        
        self.data_files = scrolledtext.ScrolledText(data_tab, width=70, height=10)
        self.data_files.pack(pady=5)
        ttk.Label(data_tab, text="Format: source_path;destination_path (one per line)").pack()

        # Action buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Apply", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT)

    def validate_license(self):
        """Validate the access key (simplified for demo)"""
        key = self.access_key.get().strip()
        if len(key) >= 8 and any(c.isupper() for c in key) and any(c.isdigit() for c in key):
            self.license_valid.set(True)
            self.update_status("Access key validated successfully")
            messagebox.showinfo("Success", "Access key is valid. Premium features enabled.")
        else:
            self.license_valid.set(False)
            self.update_status("Invalid access key")
            messagebox.showerror("Error", "Invalid access key. Please enter a valid key.")

    def open_license_page(self):
        """Open the license purchase webpage"""
        webbrowser.open("https://dwi-bakti-nugroho.netlify.app/")

    def generate_new_certificate(self):
        """Generate a new virtual certificate"""
        self.certificate_data = {
            "company": "Dwi Bakti N Dev Inc.",
            "issued_to": "Premium User",
            "valid_from": datetime.now().strftime("%Y-%m-%d"),
            "valid_to": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
            "serial_number": "SP-" + ''.join(random.choices(string.digits, k=8)),
            "signature_algorithm": "SHA256-RSA",
            "public_key": self.generate_virtual_key(),
            "features": "Python, C++, Web, Kernel, Full Encryption"
        }
        messagebox.showinfo("Success", "New certificate generated successfully!")
        self.root.event_generate("<<CertificateUpdated>>")

    def browse_python_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.target_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name.set(f"protected_{base_name}")
            self.update_status(f"Selected: {file_path}")

    def browse_kernel_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Kernel Source File",
            filetypes=[("C Files", "*.c"), ("Header Files", "*.h"), ("All Files", "*.*")]
        )
        if file_path:
            self.kernel_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.kernel_output_name.set(f"{base_name}_module")
            self.update_status(f"Selected kernel source: {file_path}")

    def browse_cpp_file(self):
        file_path = filedialog.askopenfilename(
            title="Select C++ Source File",
            filetypes=[("C++ Files", "*.cpp;*.cxx;*.cc;*.c"), ("Header Files", "*.h;*.hpp"), ("All Files", "*.*")]
        )
        if file_path:
            self.cpp_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.cpp_output_name.set(f"{base_name}_program")
            self.update_status(f"Selected C++ source: {file_path}")

    def browse_cpp_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico"), ("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.cpp_icon_file.set(file_path)
            self.update_status(f"Selected C++ icon: {file_path}")

    def browse_web_folder(self):
        folder_path = filedialog.askdirectory(
            title="Select Web Project Folder"
        )
        if folder_path:
            self.web_project_folder.set(folder_path)
            base_name = os.path.basename(folder_path)
            self.web_output_name.set(f"{base_name}_app")
            self.update_status(f"Selected web folder: {folder_path}")

    def browse_compile_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.compile_target_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.compile_output_name.set(f"compiled_{base_name}")
            self.update_status(f"Selected for compilation: {file_path}")

    def browse_compile_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico"), ("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        if file_path:
            self.compile_icon_file.set(file_path)
            self.update_status(f"Selected compilation icon: {file_path}")

    def browse_html_file(self):
        file_path = filedialog.askopenfilename(
            title="Select HTML File",
            filetypes=[("HTML Files", "*.html;*.htm"), ("All Files", "*.*")]
        )
        if file_path:
            self.html_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.html_output_name.set(f"Encrypted_{base_name}")
            self.update_status(f"Selected HTML file: {file_path}")

    def preview_source(self):
        """Preview the selected source file"""
        if not self.target_file.get():
            messagebox.showerror("Error", "Please select a Python file first")
            return
        
        try:
            with open(self.target_file.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Source Code Preview")
            preview_window.geometry("800x600")
            
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
            text_area.pack(fill=tk.BOTH, expand=True)
            
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")

    def preview_compile_file(self):
        """Preview the file to be compiled"""
        if not self.compile_target_file.get():
            messagebox.showerror("Error", "Please select a Python file first")
            return
        
        self.preview_source()  # Reuse the same preview function

    def preview_kernel_file(self):
        """Preview the selected kernel source file"""
        if not self.kernel_source_file.get():
            messagebox.showerror("Error", "Please select a kernel source file first")
            return
        
        try:
            with open(self.kernel_source_file.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Kernel Source Preview")
            preview_window.geometry("800x600")
            
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
            text_area.pack(fill=tk.BOTH, expand=True)
            
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")

    def preview_cpp_file(self):
        """Preview the selected C++ source file"""
        if not self.cpp_source_file.get():
            messagebox.showerror("Error", "Please select a C++ source file first")
            return
        
        try:
            with open(self.cpp_source_file.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("C++ Source Preview")
            preview_window.geometry("800x600")
            
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
            text_area.pack(fill=tk.BOTH, expand=True)
            
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read file: {str(e)}")

    def preview_html_file(self):
        """Preview the selected HTML file"""
        if not self.html_source_file.get():
            messagebox.showerror("Error", "Please select an HTML file first")
            return
        
        try:
            with open(self.html_source_file.get(), 'r', encoding='utf-8') as f:
                content = f.read()
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("HTML Source Preview")
            preview_window.geometry("800x600")
            
            text_frame = ttk.Frame(preview_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_area = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=('Consolas', 10))
            text_area.pack(fill=tk.BOTH, expand=True)
            
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not read HTML file: {str(e)}")

    def preview_html_output(self):
        """Preview the encrypted HTML output"""
        if not self.html_source_file.get():
            messagebox.showerror("Error", "Please select an HTML file first")
            return
        
        try:
            processed_html = self.process_html_file(self.html_source_file.get())
            
            preview_window = tk.Toplevel(self.root)
            preview_window.title("HTML Output Preview")
            preview_window.geometry("900x700")
            
            notebook = ttk.Notebook(preview_window)
            notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Source tab
            source_tab = ttk.Frame(notebook)
            notebook.add(source_tab, text="Source Code")
            
            source_text = scrolledtext.ScrolledText(source_tab, wrap=tk.WORD, font=('Consolas', 10))
            source_text.pack(fill=tk.BOTH, expand=True)
            source_text.insert(tk.END, processed_html)
            source_text.config(state=tk.DISABLED)
            
            # Browser preview tab
            preview_tab = ttk.Frame(notebook)
            notebook.add(preview_tab, text="Browser Preview")
            
            temp_file = os.path.join(tempfile.gettempdir(), "preview.html")
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(processed_html)
            
            browser_frame = ttk.Frame(preview_tab)
            browser_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Button(
                preview_tab, 
                text="Open in Default Browser", 
                command=lambda: webbrowser.open(f"file://{temp_file}")
            ).pack(pady=5)
            
            ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not process HTML file: {str(e)}")

    def preview_web_app(self):
        """Preview the web application before compilation"""
        if not self.web_project_folder.get():
            messagebox.showerror("Error", "Please select a web project folder first")
            return
        
        try:
            html_files = [f for f in os.listdir(self.web_project_folder.get()) 
                         if f.lower().endswith(('.html', '.htm'))]
            
            if not html_files:
                messagebox.showerror("Error", "No HTML files found in the selected folder")
                return
            
            main_html = os.path.join(self.web_project_folder.get(), html_files[0])
            
            # Open in default browser
            webbrowser.open(f"file://{main_html}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not preview web app: {str(e)}")

    def preview_compilation_command(self):
        """Show the PyInstaller command that will be used"""
        if not self.compile_target_file.get():
            messagebox.showerror("Error", "Please select a Python file first")
            return
        
        cmd = ['pyinstaller', '--noconfirm']
        
        if self.onefile_option.get():
            cmd.append('--onefile')
        
        if self.windowed_option.get():
            cmd.append('--windowed')
        
        if self.clean_option.get():
            cmd.append('--clean')
        
        if self.upx_option.get():
            cmd.append('--upx')
        
        if self.console_option.get():
            cmd.append('--console')
        
        if self.compile_icon_file.get():
            cmd.extend(['--icon', self.compile_icon_file.get()])
        
        # Add hidden imports for selected libraries
        hidden_imports = []
        if self.include_tkinter.get():
            hidden_imports.append('tkinter')
        if self.include_kivy.get():
            hidden_imports.extend(['kivy', 'kivy.graphics'])
        if self.include_pandas.get():
            hidden_imports.append('pandas')
        if self.include_numpy.get():
            hidden_imports.append('numpy')
        if self.include_qt.get():
            hidden_imports.extend(['PyQt5', 'PySide2'])
        if self.include_selenium.get():
            hidden_imports.append('selenium')
        if self.include_requests.get():
            hidden_imports.append('requests')
        if self.include_pillow.get():
            hidden_imports.append('PIL')
        if self.include_sqlite.get():
            hidden_imports.append('sqlite3')
        
        for imp in hidden_imports:
            cmd.extend(['--hidden-import', imp])
        
        cmd.extend(['--name', self.compile_output_name.get(), self.compile_target_file.get()])
        
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Compilation Command Preview")
        preview_window.geometry("700x300")
        
        ttk.Label(preview_window, text="PyInstaller command that will be executed:", font=('Segoe UI', 9, 'bold')).pack(pady=(10, 5))
        
        cmd_text = tk.Text(preview_window, wrap=tk.WORD, height=10, font=('Consolas', 10))
        cmd_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        cmd_text.insert(tk.END, ' '.join(cmd))
        cmd_text.config(state=tk.DISABLED)
        
        ttk.Button(preview_window, text="Close", command=preview_window.destroy).pack(pady=10)

    def process_html_file(self, file_path):
        """Process the HTML file with selected options"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Minify HTML if selected
        if self.html_minify.get():
            import re
            # Remove comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            # Remove extra whitespace
            content = re.sub(r'\s+', ' ', content)
            content = re.sub(r'>\s+<', '><', content)
        
        # Embed images if selected
        if self.html_embed_images.get():
            from bs4 import BeautifulSoup
            import base64
            import os
            
            soup = BeautifulSoup(content, 'html.parser')
            for img in soup.find_all('img'):
                if 'src' in img.attrs:
                    img_path = img['src']
                    full_path = os.path.join(os.path.dirname(file_path), img_path)
                    if os.path.exists(full_path):
                        with open(full_path, 'rb') as img_file:
                            encoded = base64.b64encode(img_file.read()).decode('utf-8')
                            ext = os.path.splitext(img_path)[1][1:]  # Get extension without dot
                            img['src'] = f"data:image/{ext};base64,{encoded}"
            
            content = str(soup)
        
        # Obfuscate if selected
        if self.html_obfuscate.get():
            # Simple obfuscation (replace letters with HTML entities)
            def obfuscate_char(c):
                if c.isalpha():
                    return f"&#{ord(c)};"
                return c
            
            content = ''.join(obfuscate_char(c) for c in content)
        
        # Encrypt if selected
        if self.html_encrypt.get():
            key = Fernet.generate_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(content.encode('utf-8'))
            
            # Create a self-decrypting HTML file
            content = f"""<!DOCTYPE html>
<html>
<head>
<title>Encrypted Content</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
<script>
function decryptContent() {{
    try {{
        var encrypted = {list(encrypted)};
        var key = atob("{base64.b64encode(key).decode('utf-8')}");
        
        var encryptedData = new Uint8Array(encrypted);
        var encryptedBase64 = btoa(String.fromCharCode.apply(null, encryptedData));
        
        var decryptedBytes = CryptoJS.AES.decrypt(encryptedBase64, key);
        var decryptedText = decryptedBytes.toString(CryptoJS.enc.Utf8);
        
        document.open();
        document.write(decryptedText);
        document.close();
    }} catch(e) {{
        document.write("Error decrypting content: " + e.message);
    }}
}}
</script>
</head>
<body onload="decryptContent()">
<noscript>Please enable JavaScript to view this content</noscript>
</body>
</html>"""
        
        # Protect source code if selected
        if self.html_protect_source.get():
            content += """
<script>
// Disable right-click
document.addEventListener('contextmenu', function(e) {
    e.preventDefault();
});

// Disable text selection
document.addEventListener('selectstart', function(e) {
    e.preventDefault();
});

// Disable keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Disable F12, Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+U
    if (e.keyCode === 123 || 
        (e.ctrlKey && e.shiftKey && e.keyCode === 73) || 
        (e.ctrlKey && e.shiftKey && e.keyCode === 74) || 
        (e.ctrlKey && e.keyCode === 85)) {
        e.preventDefault();
    }
});
</script>
"""
        
        return content

    def encrypt_html(self):
        """Encrypt the HTML file with selected options"""
        if not self.html_source_file.get():
            messagebox.showerror("Error", "Please select an HTML file first")
            return
        
        try:
            output_name = self.html_output_name.get()
            if not output_name.endswith('.html'):
                output_name += '.html'
            
            processed_html = self.process_html_file(self.html_source_file.get())
            
            output_path = filedialog.asksaveasfilename(
                title="Save Encrypted HTML As",
                defaultextension=".html",
                initialfile=output_name,
                filetypes=[("HTML Files", "*.html"), ("All Files", "*.*")]
            )
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(processed_html)
                
                self.update_status(f"HTML encrypted successfully to: {output_path}")
                messagebox.showinfo("Success", f"HTML file encrypted successfully!\nSaved as: {output_path}")
                
        except Exception as e:
            self.update_status(f"HTML encryption failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during HTML encryption: {str(e)}")

    def compile_web_to_exe(self):
        """Compile a web project to a standalone executable"""
        if not self.web_project_folder.get():
            messagebox.showerror("Error", "Please select a web project folder first")
            return
        
        try:
            self.update_status("Starting web to EXE compilation...")
            
            # Find the main HTML file
            html_files = [f for f in os.listdir(self.web_project_folder.get()) 
                         if f.lower().endswith(('.html', '.htm'))]
            
            if not html_files:
                messagebox.showerror("Error", "No HTML files found in the selected folder")
                return
            
            main_html = html_files[0]
            output_name = self.web_output_name.get()
            port = self.web_port.get()
            window_size = self.web_window_size.get()
            browser_type = self.web_browser_type.get()
            
            # Create a temporary directory for the build
            temp_dir = tempfile.mkdtemp()
            script_path = os.path.join(temp_dir, "web_app.py")
            
            # Generate the appropriate Python script based on browser type
            if browser_type == "cef":
                script_content = self.generate_cef_script(main_html, port, window_size)
            elif browser_type == "webview":
                script_content = self.generate_webview_script(main_html, window_size)
            else:  # edge
                script_content = self.generate_edge_script(main_html, window_size)
            
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(script_content)
            
            # Copy web files to a 'web' subdirectory
            web_dir = os.path.join(temp_dir, "web")
            os.makedirs(web_dir, exist_ok=True)
            
            for item in os.listdir(self.web_project_folder.get()):
                src = os.path.join(self.web_project_folder.get(), item)
                dst = os.path.join(web_dir, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Encrypt web content if selected
            if self.web_encrypt.get():
                self.encrypt_web_content(web_dir)
            
            # Prepare PyInstaller command
            cmd = ['pyinstaller', '--noconfirm']
            
            if self.web_single_file.get():
                cmd.append('--onefile')
                cmd.append('--add-data')
                cmd.append(f"{web_dir}{os.pathsep}web")
            
            # Add browser-specific requirements
            if browser_type == "cef":
                cmd.extend(['--hidden-import', 'cefpython3'])
            elif browser_type == "webview":
                cmd.extend(['--hidden-import', 'webview'])
            
            cmd.extend(['--name', output_name, script_path])
            
            self.update_status(f"Executing: {' '.join(cmd)}")
            
            # Run PyInstaller
            process = subprocess.Popen(
                cmd,
                cwd=temp_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            # Show output window
            output_window = tk.Toplevel(self.root)
            output_window.title("Web to EXE Compilation Output")
            output_window.geometry("800x600")
            
            text_frame = ttk.Frame(output_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            output_text = scrolledtext.ScrolledText(
                text_frame, 
                wrap=tk.WORD,
                font=('Consolas', 10),
                state='normal'
            )
            output_text.pack(fill=tk.BOTH, expand=True)
            
            stop_button = ttk.Button(
                output_window, 
                text="Stop Compilation", 
                command=lambda: self.stop_compilation(process, output_window)
            )
            stop_button.pack(pady=5)
            
            def read_output():
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        output_text.update_idletasks()
                
                process.poll()
                if process.returncode == 0:
                    output_text.insert(tk.END, "\nCompilation completed successfully!\n")
                    output_path = os.path.join(temp_dir, "dist", f"{output_name}.exe")
                    self.update_status(f"Web to EXE compilation successful! Output: {output_path}")
                    
                    # Ask where to save the final executable
                    final_path = filedialog.asksaveasfilename(
                        title="Save Web Executable As",
                        defaultextension=".exe",
                        initialfile=f"{output_name}.exe",
                        filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
                    )
                    
                    if final_path:
                        shutil.copy2(output_path, final_path)
                        output_text.insert(tk.END, f"\nExecutable saved to: {final_path}\n")
                        
                        ttk.Button(
                            output_window,
                            text="Open Output Folder",
                            command=lambda: self.open_output_folder(os.path.dirname(final_path))
                        ).pack(pady=5)
                else:
                    output_text.insert(tk.END, f"\nCompilation failed with return code {process.returncode}\n")
                    self.update_status("Web to EXE compilation failed")
                
                stop_button.config(text="Close", command=output_window.destroy)
            
            import threading
            threading.Thread(target=read_output, daemon=True).start()
            
        except Exception as e:
            self.update_status(f"Web to EXE compilation failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during web to EXE compilation: {str(e)}")

    def generate_cef_script(self, main_html, port, window_size):
        """Generate Python script for CEF browser"""
        width, height = window_size.split('x')
        return f"""# -*- coding: utf-8 -*-
import os
import sys
import threading
from flask import Flask, send_from_directory
from cefpython3 import cefpython as cef

app = Flask(__name__)
PORT = {port}

# Serve all files from the web folder
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(base_dir, path)

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, '{main_html}')

def run_server():
    app.run(port=PORT)

class CefBrowser:
    def __init__(self):
        self.browser = None
        
    def create_browser(self):
        sys.excepthook = cef.ExceptHook
        settings = {{
            "window_title": "{self.web_output_name.get()}",
            "product_version": "WebApp/1.0",
            "cache_path": os.path.join(os.environ["LOCALAPPDATA"], "WebApp", "Cache")
        }}
        cef.Initialize(settings=settings)
        
        window_info = cef.WindowInfo()
        window_info.SetAsChild(0, [0, 0, {width}, {height}])
        
        self.browser = cef.CreateBrowserSync(
            window_info,
            url=f"http://localhost:{{PORT}}",
            settings={{
                "web_security_disabled": False,
                "file_access_from_file_urls_allowed": True,
                "universal_access_from_file_urls_allowed": True
            }}
        )
        
        if {self.web_fullscreen.get()}:
            self.browser.SetFocus(True)
            self.browser.SetFullscreen(True)
        
        cef.MessageLoop()
        cef.Shutdown()

if __name__ == "__main__":
    # Determine if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS, 'web')
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Start the CEF browser
    browser = CefBrowser()
    browser.create_browser()
"""

    def generate_webview_script(self, main_html, window_size):
        """Generate Python script for WebView browser"""
        width, height = window_size.split('x')
        return f"""# -*- coding: utf-8 -*-
import os
import sys
import webview

if __name__ == "__main__":
    # Determine if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS, 'web')
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

    # Create and start the webview window
    window = webview.create_window(
        "{self.web_output_name.get()}",
        url=os.path.join(base_dir, '{main_html}'),
        width={width},
        height={height},
        resizable=True,
        fullscreen={self.web_fullscreen.get()},
        confirm_close=not {self.web_kiosk_mode.get()}
    )
    
    webview.start(debug={self.web_enable_devtools.get()})
"""

    def generate_edge_script(self, main_html, window_size):
        """Generate Python script for Edge browser (Windows only)"""
        width, height = window_size.split('x')
        return f"""# -*- coding: utf-8 -*-
import os
import sys
import threading
import webbrowser
from flask import Flask, send_from_directory
import pythoncom
import win32gui
import win32con

app = Flask(__name__)
PORT = 0  # Auto-select port

# Serve all files from the web folder
@app.route('/<path:path>')
def serve_file(path):
    return send_from_directory(base_dir, path)

@app.route('/')
def serve_index():
    return send_from_directory(base_dir, '{main_html}')

def run_server():
    app.run(port=PORT)

def open_browser():
    pythoncom.CoInitialize()
    url = f"http://localhost:{{PORT}}"
    
    # Try to open in Edge
    try:
        webbrowser.register('edge', None, webbrowser.BackgroundBrowser(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"))
        webbrowser.get('edge').open(url, new=0, autoraise=True)
    except:
        webbrowser.open(url, new=0, autoraise=True)
    
    # Wait for browser window and set size
    import time
    time.sleep(2)
    
    # Find browser window and resize (Windows only)
    try:
        window = win32gui.FindWindow(None, "{self.web_output_name.get()}")
        if window:
            win32gui.SetWindowPos(
                window,
                win32con.HWND_TOP,
                0, 0,
                {width}, {height},
                win32con.SWP_SHOWWINDOW
            )
            
            if {self.web_fullscreen.get()}:
                win32gui.ShowWindow(window, win32con.SW_MAXIMIZE)
    except:
        pass

if __name__ == "__main__":
    # Determine if we're running in a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        base_dir = os.path.join(sys._MEIPASS, 'web')
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

    # Start the Flask server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start and get the port
    import time
    time.sleep(1)
    
    # Open the browser
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.start()
    
    # Keep the main thread alive
    while True:
        time.sleep(1)
"""

    def encrypt_web_content(self, web_dir):
        """Encrypt all HTML, CSS, and JavaScript files in the web directory"""
        self.update_status("Encrypting web content...")
        
        key = Fernet.generate_key()
        cipher = Fernet(key)
        
        for root, _, files in os.walk(web_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                if file.lower().endswith(('.html', '.htm', '.css', '.js')):
                    try:
                        with open(file_path, 'rb') as f:
                            content = f.read()
                        
                        encrypted = cipher.encrypt(content)
                        
                        if file.lower().endswith(('.html', '.htm')):
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(f"""<!DOCTYPE html>
<html>
<head>
<title>Encrypted Content</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
<script>
function decryptContent() {{
    try {{
        var encrypted = {list(encrypted)};
        var key = atob("{base64.b64encode(key).decode('utf-8')}");
        
        var encryptedData = new Uint8Array(encrypted);
        var encryptedBase64 = btoa(String.fromCharCode.apply(null, encryptedData));
        
        var decryptedBytes = CryptoJS.AES.decrypt(encryptedBase64, key);
        var decryptedText = decryptedBytes.toString(CryptoJS.enc.Utf8);
        
        document.open();
        document.write(decryptedText);
        document.close();
    }} catch(e) {{
        document.write("Error decrypting content: " + e.message);
    }}
}}
</script>
</head>
<body onload="decryptContent()">
<noscript>Please enable JavaScript to view this content</noscript>
</body>
</html>""")
                        else:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(f"""<!DOCTYPE html>
<html>
<head>
<title>Encrypted Content</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/crypto-js/4.1.1/crypto-js.min.js"></script>
<script>
function decryptContent() {{
    try {{
        var encrypted = {list(encrypted)};
        var key = atob("{base64.b64encode(key).decode('utf-8')}");
        
        var encryptedData = new Uint8Array(encrypted);
        var encryptedBase64 = btoa(String.fromCharCode.apply(null, encryptedData));
        
        var decryptedBytes = CryptoJS.AES.decrypt(encryptedBase64, key);
        var decryptedText = decryptedBytes.toString(CryptoJS.enc.Utf8);
        
        {"var style = document.createElement('style');" if file.lower().endswith('.css') else ""}
        {"style.textContent = decryptedText;" if file.lower().endswith('.css') else ""}
        {"document.head.appendChild(style);" if file.lower().endswith('.css') else ""}
        {"eval(decryptedText);" if file.lower().endswith('.js') else ""}
    }} catch(e) {{
        document.write("Error decrypting content: " + e.message);
    }}
}}
</script>
</head>
<body onload="decryptContent()">
<noscript>Please enable JavaScript to view this content</noscript>
</body>
</html>""")
                        
                        self.update_status(f"Encrypted: {file_path}")
                    except Exception as e:
                        self.update_status(f"Error encrypting {file_path}: {str(e)}")
                        continue
        
        self.update_status("Web content encryption completed")

    def encrypt_file(self):
        if not self.license_valid.get():
            messagebox.showerror("Error", "Please validate your access key first")
            return
            
        if not self.target_file.get():
            messagebox.showerror("Error", "Please select a Python file to encrypt")
            return
        
        if not self.use_random_key.get() and not self.custom_key.get():
            messagebox.showerror("Error", "Please generate or enter a custom key")
            return
        
        try:
            self.update_status("Starting encryption process...")
            if self.use_random_key.get():
                key = Fernet.generate_key()
                self.update_status("Generated random encryption key")
            else:
                try:
                    key = self.custom_key.get().encode()
                    Fernet(key)  # This will raise ValueError if key is invalid
                    self.update_status("Using custom encryption key")
                except ValueError:
                    messagebox.showerror("Error", "Invalid encryption key. Please generate a valid key.")
                    self.update_status("Encryption failed: invalid key")
                    return
            
            cipher = Fernet(key)
            target_script = self.target_file.get()
            self.update_status(f"Reading source file: {target_script}")
            
            with open(target_script, 'rb') as f:
                file_content = f.read()
            
            if file_content.startswith(b'\xef\xbb\xbf'):
                file_content = file_content[3:]
            
            self.update_status("Encrypting file content...")
            encrypted_data = cipher.encrypt(file_content)
            
            # Generate loader script with all selected options
            loader_script = self.generate_loader_script(key, encrypted_data)
            
            output_dir = os.path.dirname(target_script)
            output_path = os.path.join(output_dir, f"{self.output_name.get()}.py")
            
            self.update_status(f"Saving encrypted file: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(loader_script)
            
            self.update_status("Encryption completed successfully")
            messagebox.showinfo("Success", f"File encrypted successfully!\nSaved as: {output_path}")
        
        except Exception as e:
            self.update_status(f"Encryption failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def generate_loader_script(self, key, encrypted_data):
        """Generate the loader script with all selected options"""
        loader_script = f'''# -*- coding: utf-8 -*-
import sys
import os
import tempfile
from cryptography.fernet import Fernet
import hashlib

# Virtual Certificate Information
CERTIFICATE = {{
    "company": "{self.certificate_data['company']}",
    "issued_to": "{self.certificate_data['issued_to']}",
    "serial_number": "{self.certificate_data['serial_number']}",
    "public_key": "{self.certificate_data['public_key']}"
}}

# License verification function
def verify_license():
    """
    Simple license verification (demo version)
    In a real application, this would be more secure
    """
    try:
        # Check for valid access key (simplified for demo)
        valid_key = "SP-" + hashlib.sha256(CERTIFICATE["public_key"].encode()).hexdigest()[:8].upper()
        return True  # Skip verification in demo
    except:
        return False

# Encryption key
key = {key!r}
cipher = Fernet(key)

# Encrypted payload
encrypted_data = {encrypted_data!r}

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def main():
    # Verify license before execution
    if not verify_license():
        print("Error: Invalid license. Please contact the software provider.")
        if not getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        sys.exit(1)
    
    try:
        # Decrypt in memory
        decrypted_code = cipher.decrypt(encrypted_data).decode('utf-8')
        
        # Create a dictionary for the execution environment
        env = {{}}
        env.update(globals())
        
        # Execute decrypted code with proper environment
        exec(decrypted_code, env)
    except Exception as e:
        import traceback
        error_msg = f"Error: {{e}}\\n\\n{{traceback.format_exc()}}"
        print(error_msg)
        if not getattr(sys, 'frozen', False):
            input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        return loader_script

    def compile_file(self):
        if not self.license_valid.get():
            messagebox.showerror("Error", "Please validate your access key first")
            return
            
        if not self.compile_target_file.get():
            messagebox.showerror("Error", "Please select a Python file to compile")
            self.update_status("Compilation failed: no file selected")
            return
            
        try:
            self.update_status("Starting compilation process...")
            script_path = self.compile_target_file.get()
            output_name = self.compile_output_name.get()
            
            cmd = ['pyinstaller', '--noconfirm']
            
            if self.onefile_option.get():
                cmd.append('--onefile')
                self.update_status("Using single file mode")
                
            if self.windowed_option.get():
                cmd.append('--windowed')
                self.update_status("Using windowed mode")
                
            if self.clean_option.get():
                cmd.append('--clean')
                self.update_status("Will clean build files after compilation")
                
            if self.upx_option.get():
                cmd.append('--upx')
                self.update_status("Using UPX compression")
                
            if self.console_option.get():
                cmd.append('--console')
                self.update_status("Showing console window")
                
            if self.compile_icon_file.get():
                cmd.extend(['--icon', self.compile_icon_file.get()])
                self.update_status(f"Using icon: {self.compile_icon_file.get()}")
            
            # Add hidden imports for selected libraries
            hidden_imports = []
            if self.include_tkinter.get():
                hidden_imports.append('tkinter')
            if self.include_kivy.get():
                hidden_imports.extend(['kivy', 'kivy.graphics'])
            if self.include_pandas.get():
                hidden_imports.append('pandas')
            if self.include_numpy.get():
                hidden_imports.append('numpy')
            if self.include_qt.get():
                hidden_imports.extend(['PyQt5', 'PySide2'])
            if self.include_selenium.get():
                hidden_imports.append('selenium')
            if self.include_requests.get():
                hidden_imports.append('requests')
            if self.include_pillow.get():
                hidden_imports.append('PIL')
            if self.include_sqlite.get():
                hidden_imports.append('sqlite3')
            
            for imp in hidden_imports:
                cmd.extend(['--hidden-import', imp])
            
            cmd.extend(['--name', output_name, script_path])
            
            self.update_status(f"Executing: {' '.join(cmd)}")
            
            # Create output window
            output_window = tk.Toplevel(self.root)
            output_window.title("Compilation Output")
            output_window.geometry("800x600")
            
            text_frame = ttk.Frame(output_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            output_text = scrolledtext.ScrolledText(
                text_frame, 
                wrap=tk.WORD,
                font=('Consolas', 10),
                state='normal'
            )
            output_text.pack(fill=tk.BOTH, expand=True)
            
            stop_button = ttk.Button(
                output_window, 
                text="Stop Compilation", 
                command=lambda: self.stop_compilation(process, output_window)
            )
            stop_button.pack(pady=5)
            
            def read_output():
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        output_text.update_idletasks()
                
                process.poll()
                if process.returncode == 0:
                    output_text.insert(tk.END, "\nCompilation completed successfully!\n")
                    self.update_status(f"Compilation successful! Output in dist/{output_name}")
                    
                    ttk.Button(
                        output_window,
                        text="Open Output Folder",
                        command=lambda: self.open_output_folder(output_name)
                    ).pack(pady=5)
                else:
                    output_text.insert(tk.END, f"\nCompilation failed with return code {process.returncode}\n")
                    self.update_status("Compilation failed")
                
                stop_button.config(text="Close", command=output_window.destroy)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            import threading
            threading.Thread(target=read_output, daemon=True).start()
            
        except FileNotFoundError:
            self.update_status("Compilation failed: PyInstaller not found")
            messagebox.showerror("Error", "PyInstaller not found. Please install it with: pip install pyinstaller")
        except Exception as e:
            self.update_status(f"Compilation failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during compilation: {str(e)}")

    def compile_kernel(self):
        """Compile a kernel module from C source"""
        if not self.license_valid.get():
            messagebox.showerror("Error", "Please validate your access key first")
            return
            
        if not self.kernel_source_file.get():
            messagebox.showerror("Error", "Please select a kernel source file to compile")
            self.update_status("Kernel compilation failed: no file selected")
            return
            
        try:
            self.update_status("Starting kernel compilation process...")
            source_path = self.kernel_source_file.get()
            output_name = self.kernel_output_name.get()
            optimize_level = self.kernel_optimize_level.get()
            debug_flag = "-g" if self.kernel_debug_info.get() else ""
            
            cmd = [
                'gcc',
                f'-O{optimize_level}',
                debug_flag,
                '-Wall',
                '-Wextra',
                '-fPIC',
                '-shared',
                '-o',
                f'{output_name}.so',
                source_path
            ]
            
            cmd = [arg for arg in cmd if arg]
            self.update_status(f"Executing: {' '.join(cmd)}")
            
            output_window = tk.Toplevel(self.root)
            output_window.title("Kernel Compilation Output")
            output_window.geometry("800x600")
            
            text_frame = ttk.Frame(output_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            output_text = scrolledtext.ScrolledText(
                text_frame, 
                wrap=tk.WORD,
                font=('Consolas', 10),
                state='normal'
            )
            output_text.pack(fill=tk.BOTH, expand=True)
            
            stop_button = ttk.Button(
                output_window, 
                text="Stop Compilation", 
                command=lambda: self.stop_compilation(process, output_window)
            )
            stop_button.pack(pady=5)
            
            def read_output():
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        output_text.update_idletasks()
                
                process.poll()
                if process.returncode == 0:
                    output_text.insert(tk.END, "\nKernel compilation completed successfully!\n")
                    self.update_status(f"Kernel compilation successful! Output: {output_name}.so")
                    
                    ttk.Button(
                        output_window,
                        text="Open Output Folder",
                        command=lambda: self.open_kernel_output_folder(output_name)
                    ).pack(pady=5)
                else:
                    output_text.insert(tk.END, f"\nKernel compilation failed with return code {process.returncode}\n")
                    self.update_status("Kernel compilation failed")
                
                stop_button.config(text="Close", command=output_window.destroy)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            import threading
            threading.Thread(target=read_output, daemon=True).start()
            
        except FileNotFoundError:
            self.update_status("Kernel compilation failed: GCC not found")
            messagebox.showerror("Error", "GCC compiler not found. Please install GCC first.")
        except Exception as e:
            self.update_status(f"Kernel compilation failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during kernel compilation: {str(e)}")

    def compile_cpp(self):
        """Compile a C++ source file to executable with optional encryption"""
        if not self.license_valid.get():
            messagebox.showerror("Error", "Please validate your access key first")
            return
            
        if not self.cpp_source_file.get():
            messagebox.showerror("Error", "Please select a C++ source file to compile")
            self.update_status("C++ compilation failed: no file selected")
            return
            
        try:
            self.update_status("Starting C++ compilation process...")
            source_path = self.cpp_source_file.get()
            output_name = self.cpp_output_name.get()
            optimize_level = self.cpp_optimize_level.get()
            debug_flag = "-g" if self.cpp_debug_info.get() else ""
            
            # If encryption is enabled, process the file first
            if self.cpp_encrypt_code.get():
                self.update_status("Encrypting sensitive strings in C++ code...")
                encrypted_file = self.encrypt_cpp_strings(source_path)
                source_path = encrypted_file
            
            # Prepare compilation command
            cmd = [
                'g++',
                f'-O{optimize_level}',
                debug_flag,
                '-Wall',
                '-Wextra',
                '-o',
                output_name + ('.exe' if sys.platform == 'win32' else ''),
                source_path
            ]
            
            # Add icon resource if specified (Windows only)
            if self.cpp_icon_file.get() and sys.platform == 'win32':
                icon_path = self.cpp_icon_file.get()
                rc_file = os.path.join(os.path.dirname(source_path), 'icon.rc')
                with open(rc_file, 'w') as f:
                    f.write(f"1 ICON \"{icon_path}\"")
                
                # Compile the resource file
                res_file = os.path.join(os.path.dirname(source_path), 'icon.res')
                subprocess.run(['windres', rc_file, '-O', 'coff', '-o', res_file], check=True)
                
                # Add resource file to compilation
                cmd.append(res_file)
            
            cmd = [arg for arg in cmd if arg]
            self.update_status(f"Executing: {' '.join(cmd)}")
            
            # Create output window
            output_window = tk.Toplevel(self.root)
            output_window.title("C++ Compilation Output")
            output_window.geometry("800x600")
            
            text_frame = ttk.Frame(output_window)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            output_text = scrolledtext.ScrolledText(
                text_frame, 
                wrap=tk.WORD,
                font=('Consolas', 10),
                state='normal'
            )
            output_text.pack(fill=tk.BOTH, expand=True)
            
            stop_button = ttk.Button(
                output_window, 
                text="Stop Compilation", 
                command=lambda: self.stop_compilation(process, output_window)
            )
            stop_button.pack(pady=5)
            
            def read_output():
                while True:
                    line = process.stdout.readline()
                    if not line and process.poll() is not None:
                        break
                    if line:
                        output_text.insert(tk.END, line)
                        output_text.see(tk.END)
                        output_text.update_idletasks()
                
                process.poll()
                if process.returncode == 0:
                    output_text.insert(tk.END, "\nC++ compilation completed successfully!\n")
                    self.update_status(f"C++ compilation successful! Output: {output_name}")
                    
                    # Clean up temporary files
                    if self.cpp_encrypt_code.get():
                        try:
                            os.remove(encrypted_file)
                        except:
                            pass
                    
                    if self.cpp_icon_file.get() and sys.platform == 'win32':
                        try:
                            os.remove(rc_file)
                            os.remove(res_file)
                        except:
                            pass
                    
                    ttk.Button(
                        output_window,
                        text="Open Output Folder",
                        command=lambda: self.open_cpp_output_folder(output_name)
                    ).pack(pady=5)
                else:
                    output_text.insert(tk.END, f"\nC++ compilation failed with return code {process.returncode}\n")
                    self.update_status("C++ compilation failed")
                
                stop_button.config(text="Close", command=output_window.destroy)
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True
            )
            
            import threading
            threading.Thread(target=read_output, daemon=True).start()
            
        except FileNotFoundError:
            self.update_status("C++ compilation failed: GCC not found")
            messagebox.showerror("Error", "GCC compiler not found. Please install GCC first.")
        except subprocess.CalledProcessError as e:
            self.update_status(f"C++ compilation failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during resource compilation: {str(e)}")
        except Exception as e:
            self.update_status(f"C++ compilation failed: {str(e)}")
            messagebox.showerror("Error", f"An error occurred during C++ compilation: {str(e)}")

    def encrypt_cpp_strings(self, source_path):
        """Encrypt sensitive strings in C++ code and create a modified version"""
        try:
            with open(source_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Generate a random key for this encryption
            key = Fernet.generate_key()
            cipher = Fernet(key)
            
            # Find all string literals in the code (simple regex approach)
            import re
            strings = re.findall(r'"(?:\\.|[^"\\])*"', content)
            
            # Encrypt each string and replace in content
            for s in strings:
                # Skip empty strings and very short strings
                if len(s) <= 4:
                    continue
                
                # Encrypt the string (without quotes)
                encrypted = cipher.encrypt(s[1:-1].encode('utf-8'))
                
                # Create a replacement that decrypts at runtime
                replacement = f'decrypt_string("{base64.b64encode(encrypted).decode("utf-8")}", "{base64.b64encode(key).decode("utf-8")}")'
                
                # Replace in content
                content = content.replace(s, replacement)
            
            # Add decryption function at the top of the file
            decryption_func = f'''
#include <string>
#include <vector>
#include <cryptopp/base64.h>
#include <cryptopp/aes.h>
#include <cryptopp/modes.h>
#include <cryptopp/filters.h>

std::string decrypt_string(const std::string& encrypted, const std::string& key) {{
    try {{
        // Decode the base64-encoded encrypted string and key
        std::string decoded_encrypted, decoded_key;
        CryptoPP::StringSource ss1(encrypted, true,
            new CryptoPP::Base64Decoder(
                new CryptoPP::StringSink(decoded_encrypted)
            )
        );
        CryptoPP::StringSource ss2(key, true,
            new CryptoPP::Base64Decoder(
                new CryptoPP::StringSink(decoded_key)
            )
        );
        
        // Decrypt using Fernet (AES in CBC mode with HMAC)
        if (decoded_key.size() != 32) {{
            throw std::runtime_error("Invalid key size");
        }}
        
        // Extract the AES key (first 16 bytes) and HMAC key (last 16 bytes)
        std::string aes_key = decoded_key.substr(0, 16);
        std::string hmac_key = decoded_key.substr(16);
        
        // The encrypted data is in format: version || ciphertext || hmac
        if (decoded_encrypted.size() < 1 + 16 + 32) {{
            throw std::runtime_error("Invalid encrypted data size");
        }}
        
        // Verify HMAC (not implemented in this simplified version)
        // In production, you should verify the HMAC before decryption
        
        // Extract IV (first 16 bytes after version)
        std::string iv = decoded_encrypted.substr(1, 16);
        
        // Extract ciphertext (rest except HMAC)
        std::string ciphertext = decoded_encrypted.substr(1 + 16, decoded_encrypted.size() - (1 + 16 + 32));
        
        // Decrypt using AES-CBC
        CryptoPP::CBC_Mode<CryptoPP::AES>::Decryption decryptor;
        decryptor.SetKeyWithIV(
            reinterpret_cast<const byte*>(aes_key.data()), aes_key.size(),
            reinterpret_cast<const byte*>(iv.data())
        );
        
        std::string decrypted;
        CryptoPP::StringSource ss3(ciphertext, true,
            new CryptoPP::StreamTransformationFilter(decryptor,
                new CryptoPP::StringSink(decrypted)
            )
        );
        
        return decrypted;
    }} catch (const std::exception& e) {{
        // Return original string or error message
        return "[DECRYPTION_ERROR]";
    }}
}}
'''
            
            # Insert decryption function after includes
            include_pos = content.find("#include")
            if include_pos == -1:
                content = decryption_func + content
            else:
                last_include_pos = content.rfind("#include")
                last_include_end = content.find("\n", last_include_pos) + 1
                content = content[:last_include_end] + decryption_func + content[last_include_end:]
            
            # Create temporary file for modified source
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"encrypted_{os.path.basename(source_path)}")
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return temp_file
            
        except Exception as e:
            self.update_status(f"Failed to encrypt C++ strings: {str(e)}")
            messagebox.showerror("Error", f"Failed to encrypt C++ strings: {str(e)}")
            return source_path  # Fall back to original file

    def export_certificate(self):
        """Export certificate to file"""
        file_path = filedialog.asksaveasfilename(
            title="Save Certificate As",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(f"=== Python File Protector Certificate ===\n")
                    for key, value in self.certificate_data.items():
                        f.write(f"{key.replace('_', ' ').title()}: {value}\n")
                
                self.update_status(f"Certificate exported to: {file_path}")
                messagebox.showinfo("Success", f"Certificate saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save certificate: {str(e)}")

    def toggle_custom_key(self, *args):
        """Toggle the state of the custom key entry based on radio button selection"""
        if self.use_random_key.get():
            self.custom_key.set("")
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Entry) and child.cget('textvariable') == str(self.custom_key):
                    child.config(state='disabled')
        else:
            for child in self.root.winfo_children():
                if isinstance(child, ttk.Entry) and child.cget('textvariable') == str(self.custom_key):
                    child.config(state='normal')

    def generate_custom_key(self):
        """Generate a custom encryption key"""
        chars = string.ascii_letters + string.digits + "-_"
        key = ''.join(random.choice(chars) for _ in range(44))  # Fernet keys are 44 bytes long
        self.custom_key.set(key)
        self.update_status("Generated custom encryption key")

    def update_status(self, message):
        """Update the status bar with a message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def open_kernel_output_folder(self, output_name):
        """Open the output folder containing the kernel module"""
        output_path = os.path.join(os.getcwd(), f"{output_name}.so")
        if os.path.exists(output_path):
            if sys.platform == 'win32':
                os.startfile(os.path.dirname(output_path))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', os.path.dirname(output_path)])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(output_path)])

    def open_cpp_output_folder(self, output_name):
        """Open the output folder containing the C++ executable"""
        exe_ext = '.exe' if sys.platform == 'win32' else ''
        output_path = os.path.join(os.getcwd(), f"{output_name}{exe_ext}")
        if os.path.exists(output_path):
            if sys.platform == 'win32':
                os.startfile(os.path.dirname(output_path))
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', os.path.dirname(output_path)])
            else:
                subprocess.Popen(['xdg-open', os.path.dirname(output_path)])
        else:
            messagebox.showerror("Error", f"Output file not found: {output_path}")
            self.update_status(f"Output file not found: {output_path}")

    def open_output_folder(self, output_name=None, path=None):
        """Open the output folder in file explorer"""
        if path:
            output_dir = path
        else:
            output_dir = os.path.join(os.getcwd(), 'dist')
        
        if os.path.exists(output_dir):
            if sys.platform == 'win32':
                os.startfile(output_dir)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', output_dir])
            else:
                subprocess.Popen(['xdg-open', output_dir])

    def stop_compilation(self, process, window):
        """Stop the compilation process"""
        try:
            if process.poll() is None:  # Process is still running
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
        except:
            pass
        window.destroy()

    def save_settings_to_file(self):
        """Save current settings to a JSON file"""
        settings = {
            "target_file": self.target_file.get(),
            "output_name": self.output_name.get(),
            "use_random_key": self.use_random_key.get(),
            "custom_key": self.custom_key.get(),
            "access_key": self.access_key.get(),
            "license_valid": self.license_valid.get(),
            "compile_target_file": self.compile_target_file.get(),
            "compile_output_name": self.compile_output_name.get(),
            "compile_icon_file": self.compile_icon_file.get(),
            "onefile_option": self.onefile_option.get(),
            "windowed_option": self.windowed_option.get(),
            "clean_option": self.clean_option.get(),
            "upx_option": self.upx_option.get(),
            "console_option": self.console_option.get(),
            "include_tkinter": self.include_tkinter.get(),
            "include_kivy": self.include_kivy.get(),
            "include_pandas": self.include_pandas.get(),
            "include_numpy": self.include_numpy.get(),
            "include_qt": self.include_qt.get(),
            "include_selenium": self.include_selenium.get(),
            "include_requests": self.include_requests.get(),
            "include_pillow": self.include_pillow.get(),
            "include_sqlite": self.include_sqlite.get(),
            "web_project_folder": self.web_project_folder.get(),
            "web_output_name": self.web_output_name.get(),
            "web_port": self.web_port.get(),
            "web_window_size": self.web_window_size.get(),
            "web_encrypt": self.web_encrypt.get(),
            "web_single_file": self.web_single_file.get(),
            "web_browser_type": self.web_browser_type.get(),
            "web_fullscreen": self.web_fullscreen.get(),
            "web_kiosk_mode": self.web_kiosk_mode.get(),
            "web_enable_devtools": self.web_enable_devtools.get(),
            "cpp_source_file": self.cpp_source_file.get(),
            "cpp_output_name": self.cpp_output_name.get(),
            "cpp_icon_file": self.cpp_icon_file.get(),
            "cpp_optimize_level": self.cpp_optimize_level.get(),
            "cpp_debug_info": self.cpp_debug_info.get(),
            "cpp_encrypt_code": self.cpp_encrypt_code.get(),
            "kernel_source_file": self.kernel_source_file.get(),
            "kernel_output_name": self.kernel_output_name.get(),
            "kernel_optimize_level": self.kernel_optimize_level.get(),
            "kernel_debug_info": self.kernel_debug_info.get(),
            "html_source_file": self.html_source_file.get(),
            "html_output_name": self.html_output_name.get(),
            "html_minify": self.html_minify.get(),
            "html_embed_images": self.html_embed_images.get(),
            "html_compress": self.html_compress.get(),
            "html_obfuscate": self.html_obfuscate.get(),
            "html_encrypt": self.html_encrypt.get(),
            "html_protect_source": self.html_protect_source.get(),
            "auto_update": self.auto_update.get(),
            "save_settings": self.save_settings.get(),
            "enable_logging": self.enable_logging.get(),
            "check_updates": self.check_updates.get()
        }
        
        try:
            with open('protector_settings.json', 'w') as f:
                json.dump(settings, f, indent=4)
            
            self.update_status("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved to protector_settings.json")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {str(e)}")

    def load_settings(self):
        """Load settings from JSON file if it exists"""
        try:
            if os.path.exists('protector_settings.json'):
                with open('protector_settings.json', 'r') as f:
                    settings = json.load(f)
                
                # Update all variables from loaded settings
                for key, value in settings.items():
                    if hasattr(self, key):
                        var = getattr(self, key)
                        if isinstance(var, tk.StringVar):
                            var.set(value)
                        elif isinstance(var, tk.BooleanVar):
                            var.set(value)
                        elif isinstance(var, tk.IntVar):
                            var.set(value)
                
                self.update_status("Settings loaded successfully")
        except Exception as e:
            self.update_status(f"Could not load settings: {str(e)}")

    def reset_settings(self):
        """Reset all settings to default values"""
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all settings to default values?"):
            # Reset all variables to default values
            self.target_file.set("")
            self.output_name.set("protected_app")
            self.use_random_key.set(True)
            self.custom_key.set("")
            self.access_key.set("")
            self.license_valid.set(False)
            self.compile_target_file.set("")
            self.compile_output_name.set("compiled_app")
            self.compile_icon_file.set("")
            self.onefile_option.set(True)
            self.windowed_option.set(True)
            self.clean_option.set(True)
            self.upx_option.set(True)
            self.console_option.set(False)
            self.include_tkinter.set(True)
            self.include_kivy.set(False)
            self.include_pandas.set(False)
            self.include_numpy.set(False)
            self.include_qt.set(False)
            self.include_selenium.set(False)
            self.include_requests.set(False)
            self.include_pillow.set(False)
            self.include_sqlite.set(True)
            self.web_project_folder.set("")
            self.web_output_name.set("web_app")
            self.web_port.set("8000")
            self.web_window_size.set("1024x768")
            self.web_encrypt.set(True)
            self.web_single_file.set(True)
            self.web_browser_type.set("cef")
            self.web_fullscreen.set(False)
            self.web_kiosk_mode.set(False)
            self.web_enable_devtools.set(False)
            self.cpp_source_file.set("")
            self.cpp_output_name.set("cpp_program")
            self.cpp_icon_file.set("")
            self.cpp_optimize_level.set("2")
            self.cpp_debug_info.set(False)
            self.cpp_encrypt_code.set(False)
            self.kernel_source_file.set("")
            self.kernel_output_name.set("kernel_module")
            self.kernel_optimize_level.set("2")
            self.kernel_debug_info.set(False)
            self.html_source_file.set("")
            self.html_output_name.set("Encrypted_page")
            self.html_minify.set(True)
            self.html_embed_images.set(True)
            self.html_compress.set(True)
            self.html_obfuscate.set(True)
            self.html_encrypt.set(True)
            self.html_protect_source.set(True)
            self.auto_update.set(True)
            self.save_settings.set(True)
            self.enable_logging.set(True)
            self.check_updates.set(True)
            
            self.update_status("Settings reset to default values")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set Windows style if available
    if sys.platform == "win32":
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)

    
    app = PythonEncryptorApp(root)
    root.mainloop()
def run_gui():
    root = tk.Tk()
    app = PythonEncryptorApp(root)
    root.mainloop()