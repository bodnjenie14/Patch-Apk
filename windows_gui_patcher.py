import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import shutil

def download_file(url, dest):
    """Download a file from the specified URL to the destination path."""
    try:
        subprocess.run(["curl", "-Lo", dest, url], check=True)
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download {url}: {e}")
        sys.exit(1)

def check_dependencies():
    """Check if all required dependencies are installed."""
    missing = []

    if not shutil.which("curl"):
        missing.append("cURL")
    if not shutil.which("java"):
        missing.append("Java (OpenJDK)")
    if not shutil.which("python3"):
        missing.append("Python3")
    if not shutil.which("r2"):
        missing.append("radare2")

    if missing:
        # Inform the user about missing dependencies
        response = messagebox.askyesno(
            "Missing Dependencies",
            "The following dependencies are missing:\n" +
            "\n".join(missing) +
            "\n\nWould you like to attempt to install them now?"
        )
        if response:  # If the user clicks "Yes"
            try:
                install_dependencies()
                messagebox.showinfo("Dependencies Installed", "Dependencies have been installed successfully.")
            except Exception as e:
                messagebox.showerror("Installation Error", f"Failed to install dependencies: {e}")
        else:
            messagebox.showwarning("Dependencies Required", "Please install the missing dependencies to proceed.")
    else:
        messagebox.showinfo("Dependencies", "All dependencies are installed.")

def install_dependencies():
    """Install all necessary dependencies for the APK patching process."""
    # Check for Python (should already be running with Python)
    if not shutil.which("python3"):
        messagebox.showerror("Dependency Error", "Python is not installed. Please install it and re-run the application.")
        sys.exit(1)

    # Ensure cURL is available
    if not shutil.which("curl"):
        messagebox.showinfo("Dependency Info", "Installing cURL (Linux only)...")
        if sys.platform == "win32":
            messagebox.showerror("Dependency Error", "cURL is not available. Please install it manually.")
            sys.exit(1)
        else:
            subprocess.run(["sudo", "apt-get", "install", "-y", "curl"], check=True)

    # Install OpenJDK
    if not shutil.which("java"):
        if sys.platform == "win32":
            messagebox.showinfo("Dependency Info", "Please install OpenJDK 11+ manually and ensure it's in your PATH.")
            sys.exit(1)
        else:
            subprocess.run(["sudo", "apt-get", "install", "-y", "openjdk-11-jre"], check=True)

    # Download apktool
    apktool_jar = "apktool_2.10.0.jar"
    apktool_script = "apktool"
    if not os.path.isfile(apktool_jar):
        download_file("https://github.com/iBotPeaches/Apktool/releases/download/v2.10.0/apktool_2.10.0.jar", apktool_jar)
    if not shutil.which(apktool_script):
        wrapper_url = "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool" if sys.platform != "win32" else "https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/windows/apktool.bat"
        wrapper_dest = apktool_script if sys.platform != "win32" else "apktool.bat"
        download_file(wrapper_url, wrapper_dest)
        os.chmod(wrapper_dest, 0o755)

    # Download Android SDK tools
    sdk_tools_url = "https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip" if sys.platform == "win32" else \
                    "https://dl.google.com/android/repository/commandlinetools-linux-9477386_latest.zip"
    sdk_tools_zip = "cmdline-tools.zip"
    sdk_tools_dir = "android-sdk"
    if not os.path.isdir(sdk_tools_dir):
        download_file(sdk_tools_url, sdk_tools_zip)
        shutil.unpack_archive(sdk_tools_zip, sdk_tools_dir)
        os.remove(sdk_tools_zip)

    # Install platform tools
    platform_tools_url = "https://dl.google.com/android/repository/platform-tools_r34.0.4-windows.zip" if sys.platform == "win32" else \
                         "https://dl.google.com/android/repository/platform-tools_r34.0.4-linux.zip"
    platform_tools_zip = "platform-tools.zip"
    platform_tools_dir = "platform-tools"
    if not os.path.isdir(platform_tools_dir):
        download_file(platform_tools_url, platform_tools_zip)
        shutil.unpack_archive(platform_tools_zip, platform_tools_dir)
        os.remove(platform_tools_zip)

    # Create and activate a Python virtual environment
    pip_path = "venv\\Scripts\\pip" if sys.platform == "win32" else "venv/bin/pip"
    if not os.path.isdir("venv"):
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    # Install Python dependencies
    #subprocess.run([pip_path, "install", "--upgrade", "pip"], check=True) this seems to need admin roles

    subprocess.run([pip_path, "install", "buildapp"], check=True)
    subprocess.run([pip_path, "install", "r2pipe"], check=True)
    buildapp_fetch_tools = "venv\\Scripts\\buildapp_fetch_tools" if sys.platform == "win32" else "venv/bin/buildapp_fetch_tools"
    subprocess.run([buildapp_fetch_tools], check=True)

def configure_r2():
    """Download and install radare2."""
    if not shutil.which("r2"):
        try:
            if sys.platform != "win32":
                subprocess.run(["sudo", "apt-get", "install", "-y", "radare2"], check=True)
            else:
                messagebox.showinfo("Dependency Info", "Please install radare2 manually on Windows.")
                sys.exit(1)
        except Exception as e:
            messagebox.showerror("Install Error", f"Failed to install radare2: {e}")
            sys.exit(1)
            


def decompile_app(input_filename):
    """Decompile the APK file."""
    subprocess.run([
        "java", "-jar", "apktool_2.10.0.jar", "d", input_filename, "-o", "tappedout"
    ], check=True)

import os

def replace_and_log_urls(new_gameserver_url, new_dlcserver_url):
    """Replace server URLs in the decompiled APK and log only the replacements."""
    
    replacements = {
        "https://prod.simpsons-ea.com": new_gameserver_url,
        "https://syn-dir.sn.eamobile.com": new_gameserver_url,
        "https://oct2018-4-35-0-uam5h44a.tstodlc.eamobile.com/netstorage/gameasset/direct/simpsons/": new_dlcserver_url
    }

    log = []  # Store logs of replacements

    for root, _, files in os.walk("./tappedout/"):
        for file in files:
            file_path = os.path.join(root, file)
            
            # Only process text files
            if file_path.endswith((".xml", ".smali", ".txt")):
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                except Exception as e:
                    print(f"Failed to read file: {file_path}, Error: {e}")
                    continue

                modified = False
                for original, replacement in replacements.items():
                    if original in content:
                        # Log the replacement
                        log.append(f"Replaced '{original}' with '{replacement}' in {file_path}")
                        # Replace the URL
                        content = content.replace(original, replacement)
                        modified = True

                if modified:
                    try:
                        with open(file_path, "w", encoding="utf-8", errors="ignore") as f:
                            f.write(content)
                    except Exception as e:
                        print(f"Failed to write to file: {file_path}, Error: {e}")

    # Print the log
    print("\n".join(log))


def recompile_app(input_filename):
    """Recompile the patched APK."""
    buildapp_path = "venv\\Scripts\\buildapp" if sys.platform == "win32" else "venv/bin/buildapp"
    output_filename = f"{os.path.splitext(os.path.basename(input_filename))[0]}-patched.apk"
    subprocess.run([
        buildapp_path, "-d", "tappedout", "-o", output_filename
    ], check=True)
    return output_filename

def process_apk(input_filename, new_gameserver_url, new_dlcserver_url):
    try:
        progress_bar.start()
        install_dependencies()  # Install all necessary dependencies
        decompile_app(input_filename)  # Decompile the APK
        replace_and_log_urls(new_gameserver_url, new_dlcserver_url)  # Replace URLs and log them
        output_filename = recompile_app(input_filename)  # Recompile APK
        messagebox.showinfo("Success", f"Patched APK created: {output_filename}")
    except FileNotFoundError as e:
        messagebox.showerror("Dependency Error", str(e))
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        progress_bar.stop()


def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("APK files", "*.apk")])
    apk_entry.delete(0, tk.END)
    apk_entry.insert(0, file_path)

def run_script():
    input_filename = apk_entry.get()
    new_gameserver_url = gameserver_entry.get()
    new_dlcserver_url = dlcserver_entry.get()

    if not input_filename or not new_gameserver_url or not new_dlcserver_url:
        messagebox.showerror("Error", "All fields are required!")
        return

    process_apk(input_filename, new_gameserver_url, new_dlcserver_url)

# Create GUI
root = tk.Tk()
root.title("APK Patcher")

# Enable dark mode
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#2e2e2e", foreground="#ffffff")
style.configure("TButton", background="#4a4a4a", foreground="#ffffff")
style.configure("TEntry", fieldbackground="#4a4a4a", foreground="#ffffff")
style.configure("TFrame", background="#2e2e2e")

# Input fields
frame = ttk.Frame(root, padding="10")
frame.pack(fill="both", expand=True)

apk_label = ttk.Label(frame, text="APK File:")
apk_label.grid(row=0, column=0, sticky="w")

apk_entry = ttk.Entry(frame, width=50)
apk_entry.grid(row=0, column=1, padx=5)

browse_button = ttk.Button(frame, text="Browse", command=browse_file)
browse_button.grid(row=0, column=2, padx=5)

gameserver_label = ttk.Label(frame, text="New Gameserver URL:")
gameserver_label.grid(row=1, column=0, sticky="w")

gameserver_entry = ttk.Entry(frame, width=50)
gameserver_entry.grid(row=1, column=1, columnspan=2, pady=5)

dlcserver_label = ttk.Label(frame, text="New DLC Server URL:")
dlcserver_label.grid(row=2, column=0, sticky="w")

dlcserver_entry = ttk.Entry(frame, width=50)
dlcserver_entry.grid(row=2, column=1, columnspan=2, pady=5)

# Progress bar
progress_bar = ttk.Progressbar(frame, orient="horizontal", mode="determinate")
progress_bar.grid(row=3, column=0, columnspan=3, pady=10, sticky="ew")

# Buttons
run_button = ttk.Button(frame, text="Patch APK", command=run_script)
run_button.grid(row=4, column=0, columnspan=3, pady=5)

check_button = ttk.Button(frame, text="Check Dependencies", command=check_dependencies)
check_button.grid(row=5, column=0, columnspan=3, pady=5)

footer_label = ttk.Label(root, text="Bodnjenie™", background="#2e2e2e", foreground="#ffffff", anchor="e")
footer_label.pack(side="bottom", fill="x", padx=10, pady=5)

root.mainloop()

#coded by @bodnjenie