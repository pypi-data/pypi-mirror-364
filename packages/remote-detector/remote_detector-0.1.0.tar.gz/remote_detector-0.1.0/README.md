# Remote Detector

A Python CLI tool to detect remote access applications (like AnyDesk, TeamViewer, Getscreen, etc.) running on your system, log ERP login details, and push all logs to MongoDB for centralized monitoring.

---

## Features
- Detects remote access tools running on your system
- Prompts for IIITA ERP login and fetches academic details
- Logs detection events and ERP login info to DB
- Each log includes system username, ERP username, detected app name, and timestamp

---

## Installation

1. **Clone the repository or download the package**
2. **Create and activate a virtual environment:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies and the package:**
   ```sh
   pip install --upgrade .
   pip install pymongo
   ```

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

---


## License
MIT 