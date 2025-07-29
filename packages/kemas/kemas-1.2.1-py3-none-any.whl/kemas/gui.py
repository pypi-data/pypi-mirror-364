import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
from cryptography.fernet import Fernet
import subprocess
import os
import sys
import random
import string
import webbrowser
import base64
from datetime import datetime, timedelta
import json
import sys
    
class HTMLtoEXEConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Kemas - EXE Converter")
        self.root.geometry("450x500")
        self.root.resizable(True, True)
        self.icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_path):
            self.root.iconbitmap(self.icon_path)
        
        # Initialize variables
        self.target_file = tk.StringVar()
        self.output_name = tk.StringVar(value="output")
        self.use_random_key = tk.BooleanVar(value=True)
        self.custom_key = tk.StringVar()
        self.access_key = tk.StringVar()
        self.license_valid = tk.BooleanVar(value=False)
        
        # Python compilation options
        self.onefile_option = tk.BooleanVar(value=True)
        self.windowed_option = tk.BooleanVar(value=True)
        self.icon_file = tk.StringVar()
        self.upx_dir = tk.StringVar()
        self.python_embed = tk.BooleanVar(value=False)
        
        # C++ compilation options
        self.cpp_source_file = tk.StringVar()
        self.cpp_output_name = tk.StringVar(value="program")
        self.cpp_optimize_level = tk.StringVar(value="2")
        self.cpp_icon_file = tk.StringVar()
        self.cpp_compiler = tk.StringVar(value="g++")
        
        # Go compilation options
        self.go_source_file = tk.StringVar()
        self.go_output_name = tk.StringVar(value="program")
        self.go_os_target = tk.StringVar(value="current")
        self.go_arch_target = tk.StringVar(value="current")
        self.go_static = tk.BooleanVar(value=False)
        self.go_trimpath = tk.BooleanVar(value=True)
        
        # Java compilation options
        self.java_source_file = tk.StringVar()
        self.java_output_name = tk.StringVar(value="Program")
        self.java_main_class = tk.StringVar()
        self.java_debug = tk.BooleanVar(value=False)
        self.java_deprecation = tk.BooleanVar(value=True)
        
        # C# compilation options
        self.cs_source_file = tk.StringVar()
        self.cs_output_name = tk.StringVar(value="program")
        self.cs_target = tk.StringVar(value="exe")
        self.cs_optimize = tk.BooleanVar(value=True)
        self.cs_debug = tk.BooleanVar(value=False)
        
        # Rust compilation options
        self.rust_source_file = tk.StringVar()
        self.rust_output_name = tk.StringVar(value="program")
        self.rust_release = tk.BooleanVar(value=False)
        self.rust_target_triple = tk.StringVar()
        
        # Create widgets
        self.create_widgets()
        
        # Load settings if available
        self.load_settings()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook for different languages
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Python tab
        self.create_python_tab(notebook)
        
        # C++ tab
        self.create_cpp_tab(notebook)
        
        # Go tab
        self.create_go_tab(notebook)
        
        # Java tab
        self.create_java_tab(notebook)
        
        # C# tab
        self.create_csharp_tab(notebook)
        
        # Rust tab
        self.create_rust_tab(notebook)
        
        # Status bar
        self.status_label = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(fill=tk.X, pady=(5, 0))

    def create_python_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Python")
        
        # File selection
        ttk.Label(tab, text="Python File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.target_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_python_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Icon selection
        ttk.Label(tab, text="Icon File (optional):", font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        icon_frame = ttk.Frame(tab)
        icon_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(icon_frame, textvariable=self.icon_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(icon_frame, text="Browse", command=self.browse_icon_file).pack(side=tk.LEFT)
        
        # UPX options
        ttk.Label(tab, text="UPX Directory (optional):", font=('Arial', 9, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=(5, 5))
        upx_frame = ttk.Frame(tab)
        upx_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(upx_frame, textvariable=self.upx_dir, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(upx_frame, text="Browse", command=self.browse_upx_dir).pack(side=tk.LEFT)
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Single executable (--onefile)", variable=self.onefile_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Windowed mode (--windowed)", variable=self.windowed_option).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Use embedded Python", variable=self.python_embed).pack(anchor=tk.W)
        
        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=9, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Compile Python", command=self.compile_python).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Encrypt Python", command=self.encrypt_python).pack(side=tk.LEFT, padx=5)
        
        tab.columnconfigure(0, weight=1)

    def create_cpp_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="C++")
        
        # File selection
        ttk.Label(tab, text="C++ Source File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.cpp_source_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_cpp_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.cpp_output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Compiler selection
        ttk.Label(tab, text="Compiler:", font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Combobox(tab, textvariable=self.cpp_compiler, 
                    values=["g++", "clang++", "cl", "mingw32-g++"]).grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        # Icon selection (Windows only)
        if sys.platform == 'win32':
            ttk.Label(tab, text="Icon File (optional):", font=('Arial', 9, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=(5, 5))
            icon_frame = ttk.Frame(tab)
            icon_frame.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
            ttk.Entry(icon_frame, textvariable=self.cpp_icon_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
            ttk.Button(icon_frame, text="Browse", command=self.browse_cpp_icon).pack(side=tk.LEFT)
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=8, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(options_frame, text="Optimization Level:").pack(anchor=tk.W)
        opt_frame = ttk.Frame(options_frame)
        opt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Radiobutton(opt_frame, text="O0", variable=self.cpp_optimize_level, value="0").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O1", variable=self.cpp_optimize_level, value="1").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O2", variable=self.cpp_optimize_level, value="2").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="O3", variable=self.cpp_optimize_level, value="3").pack(side=tk.LEFT)
        
        # Action button
        ttk.Button(tab, text="Compile C++", command=self.compile_cpp).grid(row=9, column=0, pady=(10, 0), sticky=tk.W)
        
        tab.columnconfigure(0, weight=1)

    def create_go_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Go")
        
        # File selection
        ttk.Label(tab, text="Go Source File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.go_source_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_go_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.go_output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Static linking", variable=self.go_static).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Trim path", variable=self.go_trimpath).pack(anchor=tk.W)
        
        # Cross-compilation options
        cross_frame = ttk.LabelFrame(tab, text=" Cross-Compilation ", padding=10)
        cross_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(cross_frame, text="Target OS:").grid(row=0, column=0, sticky=tk.W)
        ttk.Combobox(cross_frame, textvariable=self.go_os_target, 
                    values=["current", "windows", "linux", "darwin", "android"]).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(cross_frame, text="Target Arch:").grid(row=1, column=0, sticky=tk.W)
        ttk.Combobox(cross_frame, textvariable=self.go_arch_target, 
                    values=["current", "amd64", "386", "arm", "arm64"]).grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Action button
        ttk.Button(tab, text="Compile Go", command=self.compile_go).grid(row=6, column=0, pady=(10, 0), sticky=tk.W)
        
        tab.columnconfigure(0, weight=1)

    def create_java_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Java")
        
        # File selection
        ttk.Label(tab, text="Java Source File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.java_source_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_java_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.java_output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Main class options
        ttk.Label(tab, text="Main Class (optional):", font=('Arial', 9, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.java_main_class, width=30).grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=6, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Include debug info", variable=self.java_debug).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Show deprecation warnings", variable=self.java_deprecation).pack(anchor=tk.W)
        
        # Action buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=7, column=0, pady=(10, 0), sticky=tk.W)
        ttk.Button(btn_frame, text="Compile Java", command=self.compile_java).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Create JAR", command=self.create_java_jar).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Create EXE", command=self.create_java_exe).pack(side=tk.LEFT, padx=5)
        
        tab.columnconfigure(0, weight=1)

    def create_csharp_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="C#")
        
        # File selection
        ttk.Label(tab, text="C# Source File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.cs_source_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_csharp_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.cs_output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(options_frame, text="Output Type:").pack(anchor=tk.W)
        opt_frame = ttk.Frame(options_frame)
        opt_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Radiobutton(opt_frame, text="Executable", variable=self.cs_target, value="exe").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="Library", variable=self.cs_target, value="library").pack(side=tk.LEFT)
        ttk.Radiobutton(opt_frame, text="Module", variable=self.cs_target, value="module").pack(side=tk.LEFT)
        
        ttk.Checkbutton(options_frame, text="Optimize code", variable=self.cs_optimize).pack(anchor=tk.W)
        ttk.Checkbutton(options_frame, text="Include debug info", variable=self.cs_debug).pack(anchor=tk.W)
        
        # Action button
        ttk.Button(tab, text="Compile C#", command=self.compile_csharp).grid(row=5, column=0, pady=(10, 0), sticky=tk.W)
        
        tab.columnconfigure(0, weight=1)

    def create_rust_tab(self, notebook):
        tab = ttk.Frame(notebook)
        notebook.add(tab, text="Rust")
        
        # File selection
        ttk.Label(tab, text="Rust Source File:", font=('Arial', 9, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(5, 5))
        file_frame = ttk.Frame(tab)
        file_frame.grid(row=1, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        ttk.Entry(file_frame, textvariable=self.rust_source_file, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_frame, text="Browse", command=self.browse_rust_file).pack(side=tk.LEFT)
        
        # Output options
        ttk.Label(tab, text="Output Name:", font=('Arial', 9, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(5, 5))
        ttk.Entry(tab, textvariable=self.rust_output_name, width=30).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Compilation options
        options_frame = ttk.LabelFrame(tab, text=" Compilation Options ", padding=10)
        options_frame.grid(row=4, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Checkbutton(options_frame, text="Release mode", variable=self.rust_release).pack(anchor=tk.W)
        
        # Cross-compilation options
        cross_frame = ttk.LabelFrame(tab, text=" Cross-Compilation ", padding=10)
        cross_frame.grid(row=5, column=0, columnspan=2, sticky=tk.EW, pady=(0, 10))
        
        ttk.Label(cross_frame, text="Target Triple (optional):").pack(anchor=tk.W)
        ttk.Entry(cross_frame, textvariable=self.rust_target_triple, width=50).pack(fill=tk.X, pady=(5, 0))
        
        # Action button
        ttk.Button(tab, text="Compile Rust", command=self.compile_rust).grid(row=6, column=0, pady=(10, 0), sticky=tk.W)
        
        tab.columnconfigure(0, weight=1)

    # File browsing methods
    def browse_python_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Python File",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
        )
        if file_path:
            self.target_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name.set(base_name)
            self.update_status(f"Selected: {file_path}")

    def browse_icon_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")]
        )
        if file_path:
            self.icon_file.set(file_path)
            self.update_status(f"Selected icon: {file_path}")

    def browse_upx_dir(self):
        dir_path = filedialog.askdirectory(title="Select UPX Directory")
        if dir_path:
            self.upx_dir.set(dir_path)
            self.update_status(f"Selected UPX directory: {dir_path}")

    def browse_cpp_file(self):
        file_path = filedialog.askopenfilename(
            title="Select C++ Source File",
            filetypes=[("C++ Files", "*.cpp;*.c"), ("All Files", "*.*")]
        )
        if file_path:
            self.cpp_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.cpp_output_name.set(base_name)
            self.update_status(f"Selected C++ file: {file_path}")

    def browse_cpp_icon(self):
        file_path = filedialog.askopenfilename(
            title="Select Icon File",
            filetypes=[("Icon Files", "*.ico"), ("All Files", "*.*")]
        )
        if file_path:
            self.cpp_icon_file.set(file_path)
            self.update_status(f"Selected C++ icon: {file_path}")

    def browse_go_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Go Source File",
            filetypes=[("Go Files", "*.go"), ("All Files", "*.*")]
        )
        if file_path:
            self.go_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.go_output_name.set(base_name)
            self.update_status(f"Selected Go file: {file_path}")

    def browse_java_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Java File",
            filetypes=[("Java Files", "*.java"), ("All Files", "*.*")]
        )
        if file_path:
            self.java_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.java_output_name.set(base_name)
            self.update_status(f"Selected Java file: {file_path}")

    def browse_csharp_file(self):
        file_path = filedialog.askopenfilename(
            title="Select C# File",
            filetypes=[("C# Files", "*.cs"), ("All Files", "*.*")]
        )
        if file_path:
            self.cs_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.cs_output_name.set(base_name)
            self.update_status(f"Selected C# file: {file_path}")

    def browse_rust_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Rust File",
            filetypes=[("Rust Files", "*.rs"), ("All Files", "*.*")]
        )
        if file_path:
            self.rust_source_file.set(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.rust_output_name.set(base_name)
            self.update_status(f"Selected Rust file: {file_path}")

    # Compilation methods
    def compile_python(self):
        if not self.target_file.get():
            messagebox.showerror("Error", "Please select a Python file first")
            return
            
        try:
            self.update_status("Starting Python compilation...")
            cmd = ['pyinstaller', '--noconfirm']
            
            if self.onefile_option.get():
                cmd.append('--onefile')
                
            if self.windowed_option.get():
                cmd.append('--windowed')
                
            if self.icon_file.get():
                cmd.extend(['--icon', self.icon_file.get()])
                
            if self.upx_dir.get():
                cmd.extend(['--upx-dir', self.upx_dir.get()])
                
            if self.python_embed.get():
                cmd.append('--python-option=embed')
                
            cmd.extend(['--name', self.output_name.get(), self.target_file.get()])
            
            self.show_compilation_output(cmd, "Python")
            
        except Exception as e:
            self.update_status(f"Python compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile Python file: {str(e)}")

    def encrypt_python(self):
        if not self.target_file.get():
            messagebox.showerror("Error", "Please select a Python file first")
            return
            
        try:
            self.update_status("Encrypting Python file...")
            
            # Generate a key
            key = Fernet.generate_key()
            cipher = Fernet(key)
            
            # Read the source file
            with open(self.target_file.get(), 'rb') as f:
                content = f.read()
            
            # Encrypt the content
            encrypted = cipher.encrypt(content)
            
            # Create the loader script
            loader_script = f'''# -*- coding: utf-8 -*-
from cryptography.fernet import Fernet
import os
import sys

key = {key!r}
cipher = Fernet(key)
encrypted_data = {encrypted!r}

def main():
    try:
        # Decrypt and execute
        decrypted = cipher.decrypt(encrypted_data).decode('utf-8')
        exec(decrypted, {{'__name__': '__main__'}})
    except Exception as e:
        print(f"Error: {{e}}")
        if not getattr(sys, 'frozen', False):
            input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
            # Save the encrypted file
            output_path = filedialog.asksaveasfilename(
                title="Save Encrypted Python File",
                defaultextension=".py",
                initialfile=f"encrypted_{os.path.basename(self.target_file.get())}",
                filetypes=[("Python Files", "*.py"), ("All Files", "*.*")]
            )
            
            if output_path:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(loader_script)
                
                self.update_status(f"Python file encrypted: {output_path}")
                messagebox.showinfo("Success", f"Python file encrypted successfully!\nSaved as: {output_path}")
                
        except Exception as e:
            self.update_status(f"Python encryption failed: {str(e)}")
            messagebox.showerror("Error", f"Could not encrypt Python file: {str(e)}")

    def compile_cpp(self):
        if not self.cpp_source_file.get():
            messagebox.showerror("Error", "Please select a C++ file first")
            return
            
        try:
            self.update_status("Starting C++ compilation...")
            source_path = self.cpp_source_file.get()
            output_name = self.cpp_output_name.get()
            optimize_level = self.cpp_optimize_level.get()
            compiler = self.cpp_compiler.get()
            
            # Windows specific: handle icon
            extra_files = []
            if sys.platform == 'win32' and self.cpp_icon_file.get():
                rc_file = 'icon.rc'
                res_file = 'icon.res'
                
                # Create resource file
                with open(rc_file, 'w') as f:
                    f.write(f'1 ICON "{self.cpp_icon_file.get()}"')
                
                # Compile resource
                subprocess.run(['windres', rc_file, '-O', 'coff', '-o', res_file], check=True)
                extra_files.append(res_file)
            
            # Build compilation command
            cmd = [
                compiler,
                f'-O{optimize_level}',
                '-Wall',
                '-o',
                output_name + ('.exe' if sys.platform == 'win32' else ''),
                source_path
            ] + extra_files
            
            self.show_compilation_output(cmd, "C++")
            
            # Clean up temporary files
            if sys.platform == 'win32' and self.cpp_icon_file.get():
                try:
                    os.remove(rc_file)
                    os.remove(res_file)
                except:
                    pass
                
        except Exception as e:
            self.update_status(f"C++ compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile C++ file: {str(e)}")

    def compile_go(self):
        if not self.go_source_file.get():
            messagebox.showerror("Error", "Please select a Go file first")
            return
            
        try:
            self.update_status("Starting Go compilation...")
            source_path = self.go_source_file.get()
            output_name = self.go_output_name.get()
            
            # Set environment variables for cross-compilation
            env = os.environ.copy()
            if self.go_os_target.get() != "current":
                env["GOOS"] = self.go_os_target.get()
            if self.go_arch_target.get() != "current":
                env["GOARCH"] = self.go_arch_target.get()
            
            # Build compilation command
            cmd = ['go', 'build']
            
            if self.go_static.get():
                cmd.extend(['-ldflags', '-extldflags "-static"'])
                
            if self.go_trimpath.get():
                cmd.extend(['-trimpath'])
                
            cmd.extend(['-o', output_name + ('.exe' if sys.platform == 'win32' else ''), source_path])
            
            self.show_compilation_output(cmd, "Go", env=env)
            
        except Exception as e:
            self.update_status(f"Go compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile Go file: {str(e)}")

    def compile_java(self):
        if not self.java_source_file.get():
            messagebox.showerror("Error", "Please select a Java file first")
            return
            
        try:
            self.update_status("Starting Java compilation...")
            source_path = self.java_source_file.get()
            output_name = self.java_output_name.get()
            
            # Build compilation command
            cmd = ['javac']
            
            if self.java_debug.get():
                cmd.append('-g')
                
            if not self.java_deprecation.get():
                cmd.append('-nowarn')
                
            cmd.extend(['-d', '.', source_path])
            
            self.show_compilation_output(cmd, "Java")
            
        except Exception as e:
            self.update_status(f"Java compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile Java file: {str(e)}")

    def create_java_jar(self):
        if not self.java_source_file.get():
            messagebox.showerror("Error", "Please select a Java file first")
            return
            
        try:
            self.update_status("Creating JAR file...")
            source_path = self.java_source_file.get()
            output_name = self.java_output_name.get()
            main_class = self.java_main_class.get()
            
            # First compile the Java file
            compile_cmd = ['javac', source_path]
            subprocess.run(compile_cmd, check=True)
            
            # Get the class name if not specified
            if not main_class:
                main_class = os.path.splitext(os.path.basename(source_path))[0]
            
            # Create manifest file
            manifest_content = f"Main-Class: {main_class}\n"
            with open("MANIFEST.MF", "w") as f:
                f.write(manifest_content)
            
            # Build JAR command
            class_file = os.path.splitext(source_path)[0] + ".class"
            jar_cmd = ['jar', 'cvfm', f"{output_name}.jar", "MANIFEST.MF", class_file]
            
            self.show_compilation_output(jar_cmd, "Java JAR")
            
            # Clean up
            try:
                os.remove("MANIFEST.MF")
                os.remove(class_file)
            except:
                pass
                
        except Exception as e:
            self.update_status(f"JAR creation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not create JAR file: {str(e)}")

    def create_java_exe(self):
        if not self.java_source_file.get():
            messagebox.showerror("Error", "Please select a Java file first")
            return
            
        try:
            self.update_status("Creating Java EXE wrapper...")
            source_path = self.java_source_file.get()
            output_name = self.java_output_name.get()
            main_class = self.java_main_class.get()
            
            # First create the JAR file
            self.create_java_jar()
            
            # Create a batch file that runs the JAR
            batch_content = f'''@echo off
java -jar "{output_name}.jar" %*
'''
            batch_file = f"{output_name}.bat"
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # On Windows, we can convert the batch file to EXE using Bat To Exe Converter
            if sys.platform == 'win32':
                import win32api
                import win32con
                
                # Create a simple EXE that runs the batch file
                exe_content = f'''# -*- coding: utf-8 -*-
import os
import sys

def main():
    os.system('"{batch_file}" ' + ' '.join(sys.argv[1:]))

if __name__ == "__main__":
    main()
'''
                # Save the Python script
                py_file = f"{output_name}_wrapper.py"
                with open(py_file, 'w') as f:
                    f.write(exe_content)
                
                # Compile it to EXE
                self.target_file.set(py_file)
                self.output_name.set(output_name)
                self.compile_python()
                
                # Clean up
                try:
                    os.remove(py_file)
                    os.remove(batch_file)
                except:
                    pass
                
                self.update_status(f"Java EXE wrapper created: {output_name}.exe")
                messagebox.showinfo("Success", f"Java EXE wrapper created successfully!\nSaved as: {output_name}.exe")
            else:
                self.update_status(f"Java batch file created: {batch_file}")
                messagebox.showinfo("Success", f"Java batch file created (on Windows you can convert this to EXE)\nSaved as: {batch_file}")
                
        except Exception as e:
            self.update_status(f"Java EXE creation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not create Java EXE wrapper: {str(e)}")

    def compile_csharp(self):
        if not self.cs_source_file.get():
            messagebox.showerror("Error", "Please select a C# file first")
            return
            
        try:
            self.update_status("Starting C# compilation...")
            source_path = self.cs_source_file.get()
            output_name = self.cs_output_name.get()
            target = self.cs_target.get()
            
            # Build compilation command
            cmd = ['csc']
            
            if self.cs_optimize.get():
                cmd.append('/optimize')
                
            if self.cs_debug.get():
                cmd.append('/debug')
                
            cmd.extend([
                f'/out:{output_name}.{"exe" if target == "exe" else "dll"}',
                f'/target:{target}',
                source_path
            ])
            
            self.show_compilation_output(cmd, "C#")
            
        except Exception as e:
            self.update_status(f"C# compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile C# file: {str(e)}")

    def compile_rust(self):
        if not self.rust_source_file.get():
            messagebox.showerror("Error", "Please select a Rust file first")
            return
            
        try:
            self.update_status("Starting Rust compilation...")
            source_path = self.rust_source_file.get()
            output_name = self.rust_output_name.get()
            
            # Build compilation command
            cmd = ['rustc']
            
            if self.rust_release.get():
                cmd.append('--release')
                
            if self.rust_target_triple.get():
                cmd.extend(['--target', self.rust_target_triple.get()])
                
            cmd.extend(['-o', output_name + ('.exe' if sys.platform == 'win32' else ''), source_path])
            
            self.show_compilation_output(cmd, "Rust")
            
        except Exception as e:
            self.update_status(f"Rust compilation failed: {str(e)}")
            messagebox.showerror("Error", f"Could not compile Rust file: {str(e)}")

    def show_compilation_output(self, cmd, language, env=None):
        """Show compilation output in a new window"""
        output_window = tk.Toplevel(self.root)
        output_window.title(f"{language} Compilation Output")
        output_window.geometry("800x500")
        
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
            self.update_status(f"Executing: {' '.join(cmd)}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                universal_newlines=True,
                env=env
            )
            
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
                output_text.insert(tk.END, f"\n{language} compilation successful!\n")
                self.update_status(f"{language} compilation completed")
                
                ttk.Button(
                    output_window,
                    text="Open Output Folder",
                    command=self.open_output_folder
                ).pack(pady=5)
            else:
                output_text.insert(tk.END, f"\n{language} compilation failed with code {process.returncode}\n")
                self.update_status(f"{language} compilation failed")
            
            stop_button.config(text="Close", command=output_window.destroy)
            return process
        
        import threading
        process = threading.Thread(target=read_output, daemon=True)
        process.start()

    def stop_compilation(self, process, window):
        """Stop the compilation process"""
        try:
            if process.is_alive():
                # In this simplified version, we can't actually stop the process
                # In a real implementation, we would need to manage the subprocess
                pass
        except:
            pass
        window.destroy()

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        output_dir = os.getcwd()
        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', output_dir])
        else:
            subprocess.Popen(['xdg-open', output_dir])

    def update_status(self, message):
        """Update the status bar"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def load_settings(self):
        """Load settings from file"""
        try:
            if os.path.exists('compiler_settings.json'):
                with open('compiler_settings.json', 'r') as f:
                    settings = json.load(f)
                
                # Apply settings to variables
                for key, value in settings.items():
                    if hasattr(self, key):
                        var = getattr(self, key)
                        if isinstance(var, (tk.StringVar, tk.BooleanVar)):
                            var.set(value)
                
                self.update_status("Settings loaded")
        except:
            pass

    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'target_file': self.target_file.get(),
                'output_name': self.output_name.get(),
                'icon_file': self.icon_file.get(),
                'upx_dir': self.upx_dir.get(),
                'onefile_option': self.onefile_option.get(),
                'windowed_option': self.windowed_option.get(),
                'python_embed': self.python_embed.get(),
                'cpp_source_file': self.cpp_source_file.get(),
                'cpp_output_name': self.cpp_output_name.get(),
                'cpp_icon_file': self.cpp_icon_file.get(),
                'cpp_optimize_level': self.cpp_optimize_level.get(),
                'cpp_compiler': self.cpp_compiler.get(),
                'go_source_file': self.go_source_file.get(),
                'go_output_name': self.go_output_name.get(),
                'go_static': self.go_static.get(),
                'go_trimpath': self.go_trimpath.get(),
                'go_os_target': self.go_os_target.get(),
                'go_arch_target': self.go_arch_target.get(),
                'java_source_file': self.java_source_file.get(),
                'java_output_name': self.java_output_name.get(),
                'java_main_class': self.java_main_class.get(),
                'java_debug': self.java_debug.get(),
                'java_deprecation': self.java_deprecation.get(),
                'cs_source_file': self.cs_source_file.get(),
                'cs_output_name': self.cs_output_name.get(),
                'cs_target': self.cs_target.get(),
                'cs_optimize': self.cs_optimize.get(),
                'cs_debug': self.cs_debug.get(),
                'rust_source_file': self.rust_source_file.get(),
                'rust_output_name': self.rust_output_name.get(),
                'rust_release': self.rust_release.get(),
                'rust_target_triple': self.rust_target_triple.get()
            }
            
            with open('compiler_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.update_status("Settings saved")
        except Exception as e:
            self.update_status(f"Error saving settings: {str(e)}")

    def on_closing(self):
        """Handle window closing event"""
        self.save_settings()
        self.root.destroy()

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