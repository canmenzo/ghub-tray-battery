# ghub-tray-battery

Windows system tray app that shows Logitech wireless device battery levels by querying G HUB's local WebSocket API.

**Shows:** Mouse % and Headset % — color-coded green / yellow / red.  
**Updates:** Every 30 seconds. Right-click → Refresh to update on demand.

## Requirements

- Python 3.9+
- Logitech G HUB running in the background

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Auto-start with Windows

1. Press `Win + R` → type `shell:startup` → Enter
2. Create a shortcut to `run.vbs` in that folder

`run.vbs` launches the app via `pythonw` (no console window).

## Troubleshooting

If both values show `N/A`, G HUB's local API (`ws://localhost:9010`) may use a different message format for your version. Open an issue with the raw WebSocket response from G HUB and I'll update the parser.
