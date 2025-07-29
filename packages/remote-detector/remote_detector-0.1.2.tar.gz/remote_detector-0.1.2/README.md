# Remote Detector

A Python CLI tool to detect remote access applications (like AnyDesk, TeamViewer, Getscreen, etc.) running on your system, log ERP login details, and push all logs to MongoDB for centralized monitoring.

---

## Features
- Detects remote access tools running on your system
- Prompts for IIITA ERP login and fetches academic details
- Logs detection events and ERP login info to DB
- Each log includes system username, ERP username, detected app name, and timestamp
- Automatically adds the package to your PATH during installation

---

## Installation

### One-Click Installation (Recommended)
```sh
# Using curl (Mac/Linux)
curl -sSL https://raw.githubusercontent.com/yourusername/remote-detector/main/easy_install.py | python3

# Using wget (Linux)
wget -qO- https://raw.githubusercontent.com/yourusername/remote-detector/main/easy_install.py | python3

# Or download and run the script
python3 easy_install.py
```
The one-click installer will:
- Install the remote-detector package
- Set up PATH automatically 
- Configure MongoDB connection URL
- Make the tool immediately usable

### Standard PyPI Installation
```sh
pip3 install remote-detector
```
The installer will automatically try to add the package to your PATH.

### From source
1. **Clone the repository or download the package**
2. **Install the package:**
   ```sh
   pip3 install --upgrade .
   ```
   The installer will attempt to automatically add the package to your PATH.

---

## Environment Setup

**Set your MongoDB connection string as an environment variable:**

```sh
export MONGO_URL=url
```

---

## Usage

Start the CLI tool:
```sh
remote-detector start --duration 0.1
```
- You will be prompted for your ERP username (UID), password, and batch.
- The tool will log ERP details and immediately detect and log any remote access applications running.
- All logs are pushed to your MongoDB collection (`remote_detector.logs`).

---

## Log Structure in MongoDB
Each detection log will look like:
```json
{
  "system_username": "<your system username>",
  "erp_username": "<ERP UID>",
  "app_name": "<name of application detected>",
  "timestamp": "<ISO timestamp of detection>"
}
```

---

## Troubleshooting
- If logs do not appear in MongoDB:
  - Ensure `pymongo` is installed
  - Check your MongoDB URI and network access (IP whitelisting)
  - Watch for error messages in your terminal
- If you see logs in `remote_detector.log` file but not in MongoDB, the logger is falling back to file logging due to a connection issue.
- If the `remote-detector` command is not found after installation:
  - The installer should automatically add it to your PATH
  - You may need to restart your terminal or run `source ~/.bashrc` or `source ~/.zshrc`
  - You can manually add the bin directory to your PATH: `export PATH="$HOME/Library/Python/3.x/bin:$PATH"` (replace 3.x with your Python version)

---

## License
MIT 