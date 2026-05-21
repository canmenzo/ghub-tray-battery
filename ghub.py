import json
import uuid
import websocket

WS_URL = "ws://localhost:9010"


def get_battery():
    """Returns {"mouse": int|None, "headset": int|None} from G HUB local API."""
    ws = websocket.create_connection(WS_URL, timeout=5)
    try:
        msg_id = str(uuid.uuid4())
        ws.send(json.dumps({"msgid": msg_id, "verb": "GET", "path": "/devices/list"}))
        # API may push unsolicited messages first; loop until we get the right one
        for _ in range(10):
            raw = ws.recv()
            resp = json.loads(raw)
            if resp.get("msgid") == msg_id or resp.get("path") == "/devices/list":
                return _parse(resp)
    finally:
        ws.close()
    return {"mouse": None, "headset": None}


def _parse(resp):
    result = {"mouse": None, "headset": None}
    devices = (
        resp.get("payload", {}).get("deviceList", [])
        or resp.get("payload", {}).get("devices", [])
        or resp.get("devices", [])
    )
    for dev in devices:
        dtype = (dev.get("deviceType") or dev.get("type") or dev.get("category") or "").lower()
        battery = dev.get("batteryInfo") or dev.get("battery") or {}
        pct = battery.get("percentage") if isinstance(battery, dict) else None
        if pct is None:
            continue
        if "mouse" in dtype and result["mouse"] is None:
            result["mouse"] = int(pct)
        elif ("headset" in dtype or "audio" in dtype) and result["headset"] is None:
            result["headset"] = int(pct)
    return result
