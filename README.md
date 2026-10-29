<p align="center">
  <img src="banner.PNG" alt="Android TV Toolkit" width="1000" style="height:auto;">
</p>

[![Latest Release](https://img.shields.io/github/v/release/seun-novodev/android-tv-debloat-toolkit?style=for-the-badge)](https://github.com/seun-novodev/android-tv-debloat-toolkit/releases/latest)

# Android TV Toolkit

Lightweight desktop application (Windows and macOS) to debloat TCL/Google Android TV devices, install APKs, and customize the TV experience.

Built using Python and FreeSimpleGUI.

> **Maintenance status:** This project is not actively maintained. It works as described and issues are read, but updates and responses may be slow. Pull requests are welcome — see the source code, it's short and straightforward.

---

## Features
- Connect to Android TV over Wi-Fi (ADB Wireless)
- Pair & Connect for Android 11+ / Chromecast with Google TV (Wireless Debugging)
- Debloat TCL and Google bloatware (apps are disabled, not uninstalled — fully reversible)
- Disable Google TV Recommendations
- Re-enable any disabled app (undo)
- Install APKs remotely (FLauncher included)
- Disable the Google TV / Android TV launcher safely (refuses unless another launcher is installed)
- Reboot TV remotely

---

## ⚠️ Why Did Antivirus Flag This as a Trojan?

**Short answer: it was a false positive. There is no trojan, spyware, or malicious code in this project.**

Previous versions included a pre-built `run_toolkit.exe` file. This triggered antivirus warnings for three reasons — none of which involve actual malware:

1. **PyInstaller packaging** — The exe was built with PyInstaller, which bundles a Python runtime and unpacks itself into a temporary folder at launch. This self-extracting behaviour is identical to how some malware operates, so antivirus tools flag it heuristically even when the code inside is completely clean.
2. **Shell command execution** — The old code used `os.popen()` to run ADB commands, which passes commands through the Windows shell. Antivirus tools see a GUI program silently spawning shell processes and treat it as suspicious.
3. **Bundled ADB binaries** — Shipping `adb.exe` inside a zip alongside an unsigned executable is another common malware pattern that triggers heuristic detection.

**What changed in v1.2:**
- The pre-built `run_toolkit.exe` has been **removed from the repo entirely**. You run the toolkit directly from the Python source — no packaging, nothing to flag.
- All shell commands have been rewritten to use Python's `subprocess` module with explicit argument lists (no shell involvement), which is both safer and less suspicious to antivirus tools.
- Input validation was added so no user-supplied data is ever passed unsanitised to a system command.

You are encouraged to read the source code (`run_toolkit.py`) yourself — it is short, straightforward, and does exactly what it says.

---

## Requirements
- Windows 10 or 11, or macOS (Apple Silicon or Intel)
- **Python 3.8 or later** with Tk 8.6+ — [Download from python.org](https://www.python.org/downloads/)
- macOS only: ADB from Homebrew (`brew install --cask android-platform-tools`)
- TV must have Developer Options enabled
- ADB Debugging turned ON
- TV and PC must be on the same Wi-Fi network

---

## 🚀 Setup & Usage (v1.2+)

### Step 1 — Install Python

Download and install Python 3.8+ from [python.org](https://www.python.org/downloads/).  
- **Windows:** during installation, check **"Add Python to PATH"**.
- **macOS:** the python.org installer is recommended because it includes Tk, which the GUI needs. If you use Homebrew's Python instead, also run `brew install python-tk`. Don't use Apple's built-in `/usr/bin/python3` — its Tk 8.5 freezes on modern macOS.

### Step 2 — Download this project

Click the green **Code** button on this page → **Download ZIP**, then unzip it anywhere.

### Step 3 — Install the required library

**Windows:** open a Command Prompt in the project folder and run:

```
pip install -r requirements.txt
```

**macOS:** nothing to do here — the `run_toolkit.command` launcher in Step 5 sets everything up the first time you run it. (Prefer doing it by hand? See [Running from Terminal on macOS](#running-from-terminal-on-macos).)

> **Why FreeSimpleGUI?** PySimpleGUI v5+ became closed-source and requires a licence key. [FreeSimpleGUI](https://github.com/spyoungtech/FreeSimpleGUI) is the free, open-source (LGPL) fork with the same API, so there is no licence prompt.

**macOS only — install ADB:** the bundled `adb/` folder contains Windows binaries only. Install ADB with [Homebrew](https://brew.sh):

```
brew install --cask android-platform-tools
```

### Step 4 — Enable ADB on your TV

1. Go to **Settings → Device Preferences → About → Build Number** and click it 7 times to unlock Developer Options.
2. Go to **Settings → Device Preferences → Developer Options** and turn on **ADB Debugging**.

### Step 5 — Run the Toolkit

**Windows:** in a Command Prompt in the project folder, run:

```
python run_toolkit.py
```

Or double-click `run_toolkit.pyw` to start it without a console window.

**macOS:** double-click **`run_toolkit.command`** in Finder. The first launch takes a minute: it finds a suitable Python, creates a private environment in a `.venv` folder inside the project and installs the requirements. Later launches start straight away.

> **"cannot be opened because it is from an unidentified developer"?** macOS blocks downloaded scripts the first time. Right-click (or Control-click) `run_toolkit.command` → **Open** → **Open**. You only need to do this once. If Finder says the file isn't executable, run `chmod +x run_toolkit.command` in Terminal, or start it with `bash run_toolkit.command`.

#### Running from Terminal on macOS

```
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run_toolkit.py
```

### Step 6 — Connect and use

**Standard Android TV (TCL, Onn, Nvidia Shield):**
1. Click **Connect to TV** and enter your TV's IP address (find it under **Settings → Network → About**). If your TV uses a port other than 5555, enter it as `IP:port`.

**Android 11+ / Chromecast with Google TV:**
1. Enable **Wireless Debugging** in Developer Options (separate from ADB Debugging).
2. Click **Pair & Connect (Android 11+ / Chromecast)** and fill in the IP, Pairing Port, Pairing Code, and Debug Port shown on your TV's Wireless Debugging screen. The pairing port and the debug port are different, and both change each time — a TV restart also turns Wireless Debugging off.

Then choose a function:
- **Safe Debloat** — recommended first run; disables common bloatware. Apps that aren't on your TV are greyed out.
- **Advanced Debloat** — more options with risk ratings (✅ Safe / ⚠️ Caution / 🚫 Critical). Critical apps ask for confirmation.
- **Re-enable Apps** — lists every disabled app on the TV so you can turn any of them back on
- **Install APK** — install apps directly to your TV
- **Disable Google TV Launcher** — disables the Google TV (Chromecast) or Android TV home screen. It refuses unless another launcher such as FLauncher is installed, and asks before doing anything.
- **Reboot TV** — restarts the TV (asks first)

---

## Optional: FLauncher (Custom Launcher)

If you plan to disable the Google TV Launcher, install a backup launcher first so you don't get locked out.

1. Download the FLauncher APK from [APKPure](https://apkpure.com/flauncher/me.efesser.flauncher).
2. Use the **Install APK** button in the Toolkit to push it to your TV.
3. Open FLauncher from your TV's Apps list to confirm it works.
4. Then use **Disable Google TV Launcher** in the Toolkit.

✅ FLauncher is open-source, ad-free, and maintained by the community.

---

## 🧪 Running the Tests (for contributors)

The unit tests fake all adb calls, so no TV is needed:

```
pip install -r requirements-dev.txt
python -m pytest
```

On macOS, run these with your virtual environment's Python (`.venv/bin/python -m pip ...` and `.venv/bin/python -m pytest`).

GitHub Actions runs the same tests on Windows, macOS (Apple Silicon and Intel) and Linux for every pull request, opens every window for real (`ATV_GUI_TESTS=1`), and checks that the Windows `.exe` and macOS `.app` build and start.

---

## 🛠️ Troubleshooting: ADB Connection Issues

**"adb not found" error:**
The toolkit looks for ADB in this order: the `ADB_PATH` environment variable, the `adb/` folder next to the script, then your `PATH` plus the usual install locations (Homebrew's `/opt/homebrew/bin` and `/usr/local/bin`, and Android Studio's `platform-tools`).
- **Windows:** make sure you unzipped the full project (not just the `.py` file).
- **macOS:** run `brew install --cask android-platform-tools`, or set `ADB_PATH` to the full path of your `adb`.

**"This Python has no Tk" / "needs Tk 8.6" (macOS):**
Install Python from [python.org](https://www.python.org/downloads/), or with Homebrew run `brew install python-tk`. Then double-click `run_toolkit.command` again — it notices the broken environment and rebuilds it. (If you set it up by hand, delete the `.venv` folder and redo [Running from Terminal on macOS](#running-from-terminal-on-macos).)

**32-bit ADB / incompatible with 64-bit Windows:**
The bundled `adb.exe` may be 32-bit. Replace the files in the `adb/` folder with the latest 64-bit version:
- Download from [Google's official platform-tools](https://developer.android.com/studio/releases/platform-tools)
- Copy `adb.exe`, `AdbWinApi.dll`, and `AdbWinUsbApi.dll` into the `adb/` folder, replacing the existing files

**"Failed to connect" / "connection refused":**
- Make sure ADB Debugging is enabled on the TV
- Make sure the TV and PC are on the same Wi-Fi network
- If using a Chromecast or Android 11+ device, use the **Pair & Connect** button instead of **Connect to TV**

---

## 📖 FAQ

**Q: Do I need to install anything to run the Toolkit?**  
**A:** Yes — Python 3.8+ and the `FreeSimpleGUI` library (`pip install -r requirements.txt`); on macOS, also ADB via Homebrew. This replaced the old `.exe` approach to eliminate antivirus false positives.

**Q: Will this work on all Android TV devices?**  
**A:** The Toolkit is designed for devices that support ADB Debugging — TCL TVs, Onn 4K boxes, and Nvidia Shield TV. Chromecast with Google TV is supported via the Pair & Connect option. Start with Safe Debloat mode if you are unsure.

**Q: Is there a risk of disabling important apps?**  
**A:** Always start with **Safe Debloat**, which only removes known bloatware. The Advanced mode shows risk ratings for each app (✅ / ⚠️ / 🚫) so you can make informed choices.

**Q: Is the Toolkit free to use?**  
**A:** Yes — fully open-source under the MIT License.

**Q: The old `.exe` got flagged by my antivirus. Is this version safe?**  
**A:** Yes. See the [Why Did Antivirus Flag This?](#️-why-did-antivirus-flag-this-as-a-trojan) section above. Running from Python source removes every trigger that caused those false positives.

**Q: Is this project actively maintained?**  
**A:** Not actively. The toolkit works as described and issues are read, but updates may be infrequent. The source code is short and well-structured — contributions via pull request are welcome.

---

## What Changed in v1.2

| Area | Before | After |
|---|---|---|
| Distribution | Pre-built `run_toolkit.exe` (PyInstaller) | Run from Python source directly |
| Shell commands | `os.popen()` — passes through Windows shell | `subprocess.run()` with argument lists — no shell |
| Input validation | None — raw user input passed to commands | IP address validated before any ADB call |
| Error reporting | Fragile string matching on command output | Return codes checked; errors shown clearly |
| ADB target | Port hardcoded to 5555 in some places | Consistent `ip:port` target throughout |
| State management | Global variables | `TVConnection` class |
| Android 11+ / Chromecast | Not supported | New Pair & Connect flow |

---



## 🔨 Building Your Own Windows Executable (Optional)

Some people prefer to use a `.exe` file rather than running a Python script — it feels more like a normal Windows app. You can build one yourself from the source code. Because **you** built it on **your** machine, Windows will trust it.

> **Why not just download a pre-built exe?** A pre-built exe created by someone else will often trigger antivirus warnings — not because it contains malware, but because Windows is suspicious of executables from the internet that it hasn't seen before. Building it yourself avoids this entirely.

### What you need first

Make sure you have already completed Steps 1–3 from the Setup section above (Python installed, project downloaded, and FreeSimpleGUI installed).

### Step-by-step

**Step 1 — Install PyInstaller**

PyInstaller is a free tool that packages a Python script into a standalone `.exe`. Open a Command Prompt and run:

```
pip install pyinstaller
```

This downloads and installs PyInstaller automatically. You only need to do this once.

**Step 2 — Open a Command Prompt in the project folder**

Navigate to the folder where you unzipped this project. Click the address bar at the top of File Explorer, type `cmd`, and press Enter. This opens a Command Prompt already pointing at the right folder.

**Step 3 — Run the build command**

Type the following and press Enter:

```
pyinstaller --onefile --windowed --add-data "adb;adb" run_toolkit.py
```

What this does:
- `--onefile` packages everything into a single `.exe` file (easier to use)
- `--windowed` prevents a black console window from appearing when you run the app
- `--add-data "adb;adb"` puts the bundled `adb/` folder inside the exe, so it still finds ADB after you move it

This will take 30–60 seconds. You will see a lot of text scroll by — that is normal.

**Step 4 — Find your exe**

When it finishes, open the `dist` folder inside the project folder. Your `run_toolkit.exe` is in there. You can move it anywhere you like — your Desktop, for example.

> **Note:** This exe will work on your machine but may still trigger antivirus warnings if you send it to someone else. That is expected behaviour — see the [Why Did Antivirus Flag This?](#️-why-did-antivirus-flag-this-as-a-trojan) section. If you want to share the toolkit with someone, send them the Python source and point them to the Setup instructions instead.

---

## 🍎 Building a macOS App (Optional)

Double-clicking `run_toolkit.command` is the easiest way to run the toolkit on a Mac. If you'd rather have a normal app you can keep in Applications and the Dock, you can build one:

1. Run `run_toolkit.command` once, so the Python environment is set up.
2. In Terminal, in the project folder, run:

   ```
   ./build_macos_app.sh
   ```

3. Your app is at `dist/Android TV Toolkit.app`. Drag it to Applications.

Notes:
- The app is built for your Mac's chip (Apple Silicon or Intel).
- It isn't notarised by Apple (that needs a paid developer account), so it runs on the Mac that built it. If you copy it to another Mac, Gatekeeper will block it until you run `xattr -cr "/Applications/Android TV Toolkit.app"` on that Mac.
- ADB isn't included — install it with `brew install --cask android-platform-tools`. The app finds Homebrew's ADB even when started from Finder or the Dock.

---

## Credits

Inspired by the Reddit Android TV community.  
Built for the community to simplify TV customization.

---

![Open Source](https://img.shields.io/badge/Open%20Source-MIT%20License-brightgreen?style=for-the-badge)

## License
This project is licensed under the MIT License.