# Advanced Download Manager (مدير التحميل المتقدم)

A modern, multi-threaded download manager built with Python and Tkinter, featuring browser integration, download scheduling, and speed limiting.

<!-- يمكنك رفع لقطة شاشة للمشروع على GitHub وإضافة رابطها هنا -->
<!-- ![Screenshot](link-to-your-screenshot.png) -->

## ✨ Features (الميزات)

- **Multi-threaded Downloading**: Splits files into parts to download them faster.
- **Browser Integration**: Automatically intercepts downloads from Chrome and Edge.
- **Download Queue**: Manages multiple downloads concurrently.
- **Pause & Resume**: Pause and resume downloads at any time.
- **Speed Limiter**: Control the maximum download speed.
- **Scheduling**: Schedule downloads to start at a specific time.
- **Theming**: Supports multiple themes for the user interface.
- **Multi-language Support**: Available in Arabic, English, French, and Spanish.

## 🚀 Installation (التثبيت)

1.  Go to the [Releases page](https://github.com/legionr4/-Advanced-Download-Manager/releases).
2.  Download the latest `AdvancedDownloader-Setup.exe`.
3.  Run the installer and follow the on-screen instructions.
4.  Restart your browser (Chrome/Edge) and enable the new extension when prompted.

## 🔧 Building from Source (البناء من المصدر)

If you want to build the project yourself, follow these steps:

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/legionr4/-Advanced-Download-Manager.git
    cd Advanced-Download-Manager
    ```

2.  **Install dependencies:**
    Run the `install_requirements.py` script to install all required packages.

3.  **Run the application:**
    ```sh
    python idm.py
    ```

4.  **Build the executable and installer:**
    You will need `PyInstaller` and `Inno Setup`.
    - **Package the app with PyInstaller:** Use the command provided in the documentation or previous conversations.
    - **Build the installer with Inno Setup:** Open `installer.iss` in Inno Setup and click `Build` -> `Compile`.