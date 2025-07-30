"""
Advanced system check utilities for ShadowSeal package.

Provides platform detection, hardware binding, expiry lock, and environment checks.
"""

import platform
import hashlib
import uuid
import time
import os
import subprocess
import sys
import socket
import psutil

def get_platform() -> str:
    """Get the current platform name."""
    return platform.system()

def get_machine_id() -> str:
    """Generate a hardware binding ID using MAC address and other system info."""
    try:
        mac = uuid.getnode()
        mac_hash = hashlib.sha256(str(mac).encode()).hexdigest()
    except Exception:
        mac_hash = None

    try:
        # Additional system info for binding
        uname = platform.uname()
        sys_info = f"{uname.system}-{uname.node}-{uname.release}-{uname.version}-{uname.machine}"
        sys_hash = hashlib.sha256(sys_info.encode()).hexdigest()
    except Exception:
        sys_hash = None

    # Get CPU info
    try:
        cpu_info = platform.processor()
        cpu_hash = hashlib.sha256(cpu_info.encode()).hexdigest()
    except Exception:
        cpu_hash = None

    # Get disk serial
    try:
        if platform.system() == "Windows":
            cmd = "wmic diskdrive get serialnumber"
            result = subprocess.check_output(cmd, shell=True).decode()
            disk_serial = hashlib.sha256(result.encode()).hexdigest()
        else:
            cmd = "lsblk -o SERIAL -n"
            result = subprocess.check_output(cmd, shell=True).decode()
            disk_serial = hashlib.sha256(result.encode()).hexdigest()
    except Exception:
        disk_serial = None

    # Combine all hardware identifiers
    combined = (mac_hash or '') + (sys_hash or '') + (cpu_hash or '') + (disk_serial or '')
    return hashlib.sha256(combined.encode()).hexdigest()

def check_expiry(expiry_timestamp: int) -> bool:
    """Check if the current time is before the expiry timestamp."""
    current = int(time.time())
    return current <= expiry_timestamp

def check_root() -> bool:
    """Check if running as root/administrator."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        # Windows fallback
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False

def check_virtual_env() -> bool:
    """Check if running inside a virtual environment."""
    return (
        hasattr(sys, 'real_prefix') or
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )

def check_debugger_processes() -> bool:
    """Check for common debugger processes running."""
    debuggers = [
        'gdb', 'lldb', 'strace', 'ltrace', 'ida', 'ollydbg',
        'x64dbg', 'windbg', 'radare2', 'hopper', 'binaryninja',
        'frida', 'mitmproxy', 'burpsuite', 'wireshark', 'pycharm',
        'vscode', 'code', 'atom', 'sublime_text'
    ]
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                proc_name = proc.info['name'].lower()
                cmdline = ' '.join(proc.info['cmdline'] or []).lower()
                
                for dbg in debuggers:
                    if dbg.lower() in proc_name or dbg.lower() in cmdline:
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass
    return False

def check_network_connection() -> bool:
    """Check if network connection is available."""
    try:
        # Try to connect to Google's DNS
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def check_system_resources() -> dict:
    """Check system resources."""
    return {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': time.time() - psutil.boot_time(),
    }

def check_python_version() -> str:
    """Check Python version."""
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def check_system_architecture() -> str:
    """Check system architecture."""
    return platform.machine()

def check_environment_safety() -> dict:
    """Check if environment is safe for execution."""
    return {
        'is_root': check_root(),
        'is_virtual_env': check_virtual_env(),
        'has_debugger': check_debugger_processes(),
        'has_network': check_network_connection(),
        'platform': get_platform(),
        'python_version': check_python_version(),
        'architecture': check_system_architecture(),
    }

def generate_system_fingerprint() -> str:
    """Generate a unique system fingerprint."""
    try:
        # Get system information
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': sys.version,
            'hostname': socket.gethostname(),
            'username': os.getlogin(),
        }
        
        # Convert to string and hash
        info_str = str(sorted(system_info.items()))
        return hashlib.sha256(info_str.encode()).hexdigest()
    except Exception:
        return "unknown"

def check_system_compatibility() -> bool:
    """Check if system is compatible with ShadowSeal."""
    min_python_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < min_python_version:
        return False
    
    # Check for required modules
    required_modules = ['cryptography', 'psutil']
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            return False
    
    return True

def get_system_info() -> dict:
    """Get comprehensive system information."""
    return {
        'platform': get_platform(),
        'machine_id': get_machine_id(),
        'python_version': check_python_version(),
        'architecture': check_system_architecture(),
        'is_root': check_root(),
        'is_virtual_env': check_virtual_env(),
        'has_network': check_network_connection(),
        'resources': check_system_resources(),
        'fingerprint': generate_system_fingerprint(),
        'compatible': check_system_compatibility(),
    }

# Example usage
if __name__ == "__main__":
    info = get_system_info()
    for key, value in info.items():
        print(f"{key}: {value}")
