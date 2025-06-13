**🎞️ YouVideoDownloader**
YouVideoDownloader is a sleek and powerful cross-platform video downloader built using Python, Pyside6, and yt-dlp. It supports modern features like theme switching, animated dialogs, format conversion, and real-time download progress—all packaged as a Linux AppImage for easy installation.

**📦 Features**

- Elegant Pyside6 interface

- Light and Dark themes

- Real-time download speed, ETA, and quality selector

- Animated confirmation and spinner

- Automatic audio merging using FFmpeg

- AppImage packaging for one-click execution on Linux

**🛠️ Setup Instructions**
✅ Prerequisites

- Python 3.10+
- pip,
- virtualenv,
- ffmpeg

# Linux environment for AppImage packaging

**🔢 Step-by-Step Guide**

- Step 1: Clone the Repository

```bash

git clone https://github.com/yourusername/YouVideoDownloader.git
cd YouVideoDownloader
```

- Step 2: Create and Activate a Virtual Environment

```bash

python3 -m venv .venv
source .venv/bin/activate
```

- Step 3: Install Python Dependencies

```bash

pip install -r requirements.txt
```

- Step 4: Ensure FFmpeg is Installed

```bash

# Ubuntu/Debian
sudo apt install ffmpeg

# Arch
sudo pacman -S ffmpeg

# Fedora
sudo dnf install ffmpeg
```

- Step 5: Run the App (for testing)

```bash

python main.py
```

- 🧩 Step 6: Package the App Using PyInstaller

```bash

pyinstaller YouVideoDownloader.spec
```

> Make sure your .spec includes all required asset folders like assets/, downloader/, ui/.

- 📦 Step 7: Create AppImage
  Install appimagetool:

```bash

sudo apt install libfuse2
wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
```

Build the AppDir structure:

```bash
mkdir -p AppDir/usr/bin
cp -r dist/YouVideoDownloader AppDir/usr/bin/
cp YouVideoDownloader.desktop AppDir/
cp assets/icons/appicon.png AppDir/YouVideoDownloader.png
```

Create AppImage:

```bash

./appimagetool-x86_64.AppImage AppDir
```

> This will generate a file like YouVideoDownloader-x86_64.AppImage.

- ✅ Step 8: Launch Your AppImage

```bash
chmod +x YouVideoDownloader-x86_64.AppImage
./YouVideoDownloader-x86_64.AppImage
```

- 🖼️ Fix Missing Taskbar Icon (Linux)
  > Make sure your .desktop file looks like this:

```bash
[Desktop Entry]
Type=Application
Name=YouVideoDownloader
Exec=YouVideoDownloader
Icon=YouVideoDownloader
Categories=Utility;
And YouVideoDownloader.png is placed in the same directory or in AppDir.
```

**📁 Project Structure**

```bash
YouVideoDownloader/
├── assets/
│   ├── icons/
│   ├── qss/
│   └── screenshot/
├── downloader/
├── ui/
├── main.py
├── requirements.txt
├── YouVideoDownloader.spec
├── YouVideoDownloader.desktop
```

# 📦 Windows Packaging Instructions

**✅ Requirements**

> Make sure you are on Windows and using a virtual environment (recommended).

**🛠️ Step 1: Install Required Packages**

```bash

pip install pyinstaller
```

**📁 Step 2: Organize Project Structure**
Place all required files in a clean directory:

```BASH
your-project/
│
├── main.py
├── assets/
│   ├── icons/
│   │   └── appicon.ico
│   └── qss/
│       ├── dark.qss
│       ├── light.qss
│       └── welcome.qss
├── ui/
│   └── *.py or *.ui files
├── downloader/
│   └── *.py files
```

> Use .ico format for Windows icon in assets/icons/appicon.ico.

**📝 Step 3: Create Spec File**
Generate a basic .spec file:

```bash

pyi-makespec main.py --noconfirm --name YouVideoDownloader --windowed --icon=assets/icons/appicon.ico
```

Then, open the generated YouVideoDownloader.spec and edit the datas section like this:

```python

datas=[
    ('assets/qss/dark.qss', 'assets/qss'),
    ('assets/qss/light.qss', 'assets/qss'),
    ('assets/qss/welcome.qss', 'assets/qss'),
    ('assets/icons/appicon.ico', 'assets/icons'),
    ('downloader', 'downloader'),
    ('ui', 'ui'),
],
```

**⚙️ Step 4: Build the .exe File**

```bash

pyinstaller YouVideoDownloader.spec
```

> Output .exe will be located inside the dist/YouVideoDownloader/ folder.

Double-click YouVideoDownloader.exe to run your app.

**🖼️ Step 5: Fix Taskbar Icon (Optional)**
To ensure the taskbar icon shows:

```python

import ctypes
myappid = 'com.yourcompany.youvideodownloader.1.0'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
```

> Place this at the top of your main.py before creating the QApplication.

**📁 Step 6: Bundle with Dependencies (Optional)**
Use tools like Inno Setup or NSIS to bundle your app into an installer for easier distribution.

**🔍 Step 7: Test on Another Windows System**
Ensure:

- ffmpeg is bundled or downloaded dynamically.

- .dll dependencies (if any) are not missing.

- Use a clean VM or friend’s PC to verify.

**📤 Step 8: Publish**
Distribute via:

- GitHub Releases

- Your Website

- USB/Email, etc.

- 📄 License
  [MIT License](LICENSE) – free for personal and commercial use.
