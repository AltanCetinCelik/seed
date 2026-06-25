import json
import socket
from datetime import datetime
from pathlib import Path


HUB_FILE = Path("seed_multidevice_hub_max_v43.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ip_guess():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def build_multidevice_max():
    ip = ip_guess()
    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "mac_primary": True,
        "control_plane_local": "http://127.0.0.1:8790",
        "control_plane_lan_candidate": f"http://{ip}:8790",
        "phone_dashboard_future": True,
        "raspberry_pi_node_future": True,
        "pairing_model": ["local-only first", "explicit LAN enable", "QR pairing later"],
        "remote_control_default": False
    }
    HUB_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_multidevice_max():
    print("\n=== SEED MULTI-DEVICE HUB MAX v43 ===")
    print(json.dumps(build_multidevice_max(), indent=4))


if __name__ == "__main__":
    show_multidevice_max()
