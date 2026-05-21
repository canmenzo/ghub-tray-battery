import sys
import threading
import time
from PIL import Image, ImageDraw, ImageFont
import pystray
from ghub import get_battery

POLL_INTERVAL = 30  # seconds


def _color(pct):
    if pct is None:
        return (150, 150, 150)
    if pct <= 20:
        return (255, 80, 80)
    if pct <= 50:
        return (255, 190, 0)
    return (80, 220, 80)


def make_icon(mouse, headset):
    img = Image.new("RGBA", (64, 64), (28, 28, 28, 230))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("consola.ttf", 18)
    except Exception:
        font = ImageFont.load_default()

    m_text = f"M{mouse}" if mouse is not None else "M--"
    h_text = f"H{headset}" if headset is not None else "H--"

    draw.text((4, 6), m_text, fill=_color(mouse), font=font)
    draw.text((4, 34), h_text, fill=_color(headset), font=font)
    return img


def _title(mouse, headset):
    m = f"{mouse}%" if mouse is not None else "N/A"
    h = f"{headset}%" if headset is not None else "N/A"
    return f"Mouse: {m}  |  Headset: {h}"


class App:
    def __init__(self):
        self.mouse = None
        self.headset = None
        self.icon = None

    def refresh(self, _=None):
        try:
            data = get_battery()
            self.mouse = data["mouse"]
            self.headset = data["headset"]
        except Exception:
            pass
        if self.icon:
            self.icon.icon = make_icon(self.mouse, self.headset)
            self.icon.title = _title(self.mouse, self.headset)

    def _poll(self):
        while True:
            time.sleep(POLL_INTERVAL)
            self.refresh()

    def run(self):
        self.refresh()
        threading.Thread(target=self._poll, daemon=True).start()

        menu = pystray.Menu(
            pystray.MenuItem(
                lambda _: f"Mouse: {self.mouse}%" if self.mouse is not None else "Mouse: N/A",
                None, enabled=False,
            ),
            pystray.MenuItem(
                lambda _: f"Headset: {self.headset}%" if self.headset is not None else "Headset: N/A",
                None, enabled=False,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Refresh", self.refresh),
            pystray.MenuItem("Quit", lambda _: self.icon.stop()),
        )

        self.icon = pystray.Icon(
            "ghub-battery",
            make_icon(self.mouse, self.headset),
            _title(self.mouse, self.headset),
            menu=menu,
        )
        self.icon.run()


if __name__ == "__main__":
    App().run()
