import subprocess
import sys
import os

def install(package):
    """Installs a package using the current Python interpreter's pip."""
    # sys.executable هو المسار الدقيق لمفسر بايثون الذي يشغل هذا السكربت
    # نستخدمه لضمان تثبيت الحزمة في البيئة الصحيحة.
    try:
        print(f"Attempting to install '{package}' for Python at: {sys.executable}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"Successfully installed '{package}'.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install '{package}'.")
        print(f"Please try running this command manually in your terminal:")
        print(f'"{sys.executable}" -m pip install {package}')
        print(f"Error details: {e}")
        # الخروج مع رمز خطأ لإعلام المستخدم بوجود مشكلة.
        sys.exit(1)
    except FileNotFoundError:
        print(f"ERROR: Could not find 'pip'. Make sure pip is installed for your Python environment.")
        print(f"Python path: {sys.executable}")
        sys.exit(1)

if __name__ == "__main__":
    required_packages = [
        "tkinterdnd2",
        "cloudscraper",
        "Pillow",
        "win10toast-persist",
        "pystray",
        "ttkthemes"
    ]
    
    print("--- Checking and installing required libraries ---")
    for pkg in required_packages:
        install(pkg)
    
    print("\n--- All required libraries have been processed. ---")
    print("You can now try running the application again.")
    # إيقاف مؤقت في النهاية حتى يتمكن المستخدم من رؤية المخرجات.
    os.system("pause")