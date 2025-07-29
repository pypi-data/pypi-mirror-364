import datetime
import time
import psutil
import os  # Add for path handling
import platform  # Add for platform detection

from .logger import get_logger

def detect_remote_tools():
    logger = get_logger()  # Instantiate logger here
    system = platform.system().lower()
    is_windows = 'windows' in system
    is_macos = 'darwin' in system

    known_processes = [
        'anydesk', 'anydesk.exe',
        'teamviewer', 'teamviewer.exe',
        'ultraviewer', 'ultraviewer_desktop.exe',
        'getscreen', 'getscreen.exe'  # Adjust based on actual process names
    ]
    known_ports = [
        5938,  # TeamViewer
        7070,  # AnyDesk
        21115, # UltraViewer (assumed, verify)
        # Add for Getscreen if known
    ]

    # Platform-specific patterns
    known_path_patterns = {
        'anydesk': ['anydesk'] + (['\\anydesk'] if is_windows else ['/Applications/AnyDesk.app'] if is_macos else []),
        'teamviewer': ['teamviewer'] + (['\\teamviewer'] if is_windows else ['/Applications/TeamViewer.app'] if is_macos else []),
        'ultraviewer': ['ultraviewer'] + (['\\ultraviewer'] if is_windows else []),  # UltraViewer is Windows-only
        'getscreen': ['getscreen'] + (['\\getscreen'] if is_windows else []),  # Assuming Windows, adjust if macOS version exists
    }
    known_cmdline_patterns = {
        'anydesk': ['anydesk'],
        'teamviewer': ['teamviewer'],
        'ultraviewer': ['ultraviewer'],
        'getscreen': ['getscreen']
    }

    detected = []

    # Process check with stricter matching
    for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline', 'username']):
        name = proc.info['name'].lower() if proc.info['name'] else ''
        exe = proc.info['exe'].lower() if proc.info['exe'] else ''
        cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
        path = os.path.dirname(exe) if exe else ''

        is_suspicious = False
        tool_type = None

        # Check name
        for tool, patterns in known_path_patterns.items():
            if any(p in name for p in patterns):
                is_suspicious = True
                tool_type = tool
                break

        # If not by name, check path and cmdline
        if not is_suspicious:
            for tool, patterns in known_path_patterns.items():
                if any(p in path for p in patterns):
                    is_suspicious = True
                    tool_type = tool
                    break
            if not is_suspicious:
                for tool, patterns in known_cmdline_patterns.items():
                    if any(p in cmdline for p in patterns):
                        is_suspicious = True
                        tool_type = tool
                        break

        if is_suspicious:
            detected.append({
                'type': 'process',
                'tool': tool_type,
                'details': proc.info
            })

    # Port check with process inspection
    try:
        connections = psutil.net_connections(kind='tcp')
    except psutil.AccessDenied:
        logger.warning({"event": "permission_warning", "message": "Access denied for net_connections. Port-based detection skipped. Run with elevated privileges (sudo) for full functionality."})
        connections = []

    for conn in connections:
        if conn.laddr and conn.laddr.port in known_ports and conn.status == psutil.CONN_LISTEN:
            if conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    proc_info = proc.as_dict(attrs=['pid', 'name', 'exe', 'cmdline', 'username'])
                    exe = proc_info['exe'].lower() if proc_info['exe'] else ''
                    cmdline = ' '.join(proc_info['cmdline']).lower() if proc_info['cmdline'] else ''
                    path = os.path.dirname(exe) if exe else ''

                    is_confirmed = False
                    tool_type = None

                    # Confirm by checking path or cmdline
                    for tool, patterns in known_path_patterns.items():
                        if any(p in path or p in cmdline or p in proc_info['name'].lower() for p in patterns):
                            is_confirmed = True
                            tool_type = tool
                            break

                    if is_confirmed:
                        detected.append({
                            'type': 'port',
                            'port': conn.laddr.port,
                            'tool': tool_type,
                            'details': proc_info
                        })
                except psutil.NoSuchProcess:
                    pass

    return detected

def run_detection(duration_hours=3):
    logger = get_logger()
    start_time = datetime.datetime.now()
    end_time = start_time + datetime.timedelta(hours=duration_hours)
    logger.info({"event": "session_start", "start_time": start_time.isoformat(), "duration_hours": duration_hours})

    last_heartbeat = time.time()
    while datetime.datetime.now() < end_time:
        detected = detect_remote_tools()
        for d in detected:
            logger.info({"event": "detection", "timestamp": datetime.datetime.now().isoformat(), "details": d})
        if time.time() - last_heartbeat > 600:  # 10 minutes
            logger.info({"event": "heartbeat", "timestamp": datetime.datetime.now().isoformat()})
            last_heartbeat = time.time()
        time.sleep(60)  # Check every minute

    logger.info({"event": "session_end", "end_time": datetime.datetime.now().isoformat()}) 