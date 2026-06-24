import json
import socket
from datetime import datetime


try:
    from seed_config import SEED_MULTIDEVICE_HUB_FILE
except Exception:
    SEED_MULTIDEVICE_HUB_FILE = "seed_multidevice_hub_v19.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def local_host_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        hostname = "unknown"
        local_ip = "127.0.0.1"
    return hostname, local_ip


def build_multidevice_hub():
    hostname, local_ip = local_host_info()

    hub = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Multi-Device Hub v19",
        "host": {
            "hostname": hostname,
            "local_ip_guess": local_ip,
            "control_plane_local": "http://127.0.0.1:8790"
        },
        "modes": {
            "mac_primary": True,
            "raspberry_pi_future": True,
            "phone_companion_future": True,
            "lan_dashboard_future": True
        },
        "policy": {
            "local_first": True,
            "no_open_lan_without_explicit_config": True,
            "no_remote_control_by_default": True
        }
    }

    with open(SEED_MULTIDEVICE_HUB_FILE, "w") as file:
        json.dump(hub, file, indent=4)

    return hub


def show_multidevice_hub():
    print("\n=== SEED MULTI-DEVICE HUB v19 ===")
    print(json.dumps(build_multidevice_hub(), indent=4))


if __name__ == "__main__":
    show_multidevice_hub()
