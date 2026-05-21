import os
import threading
import time
from PIL import Image, ImageDraw, ImageFont
import pystray
from ghub import get_battery

POLL_INTERVAL = 30

FONTS = [
    r"C:\Windows\Fonts\arialbd.ttf",
    r"C:\Windows\Fonts\arial.ttf",
    r"C:\Windows\Fonts\calibrib.ttf",
    r"C:\Windows\Fonts\segoeui.ttf",
]


def _font(size):
    for path in FONTS:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def _color(pct):
    if pct is None:
        return (90, 90, 90, 220)
    if pct <= 20:
        return (210, 50, 50, 230)
    if pct <= 50:
        return (200, 140, 0, 230)
    return (40, 165, 40, 230)


def make_icon(pct, circle=True):
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    if circle:
        draw.ellipse([2, 2, 62, 62], fill=_color(pct))
    else:
        draw.rounded_rectangle([2, 2, 62, 62], radius=10, fill=_color(pct))

    text = str(pct) if pct is not None else "?"
    font = _font(30 if len(text) <= 2 else 24)
    draw.text((32, 32), text, fill=(255, 255, 255), anchor="mm", font=font)

    return img


class App:
    def __init__(self):
        self.mouse = None
        self.headset = None
        self.mouse_icon = None
        self.headset_icon = None

    def refresh(self, _=None):
        try:
            data = get_battery()
            self.mouse = data["mouse"]
            self.headset = data["headset"]
        except Exception:
            pass
        if self.mouse_icon:
            self.mouse_icon.icon = make_icon(self.mouse, circle=True)
            self.mouse_icon.title = f"Mouse: {self.mouse}%" if self.mouse is not None else "Mouse: N/A"
        if self.headset_icon:
            self.headset_icon.icon = make_icon(self.headset, circle=False)
            self.headset_icon.title = f"Headset: {self.headset}%" if self.headset is not None else "Headset: N/A"

    def _poll(self):
        while True:
            time.sleep(POLL_INTERVAL)
            self.refresh()

    def _quit(self, _=None):
        if self.mouse_icon:
            self.mouse_icon.stop()
        if self.headset_icon:
            self.headset_icon.stop()

    def run(self):
        self.refresh()
        threading.Thread(target=self._poll, daemon=True).start()

        menu = pystray.Menu(
            pystray.MenuItem("Refresh", self.refresh),
            pystray.MenuItem("Quit", self._quit),
        )

        self.mouse_icon = pystray.Icon(
            "ghub-mouse",
            make_icon(self.mouse, circle=True),
            f"Mouse: {self.mouse}%" if self.mouse is not None else "Mouse: N/A",
            menu=menu,
        )
        self.headset_icon = pystray.Icon(
            "ghub-headset",
            make_icon(self.headset, circle=False),
            f"Headset: {self.headset}%" if self.headset is not None else "Headset: N/A",
            menu=menu,
        )

        self.mouse_icon.run_detached()
        self.headset_icon.run()


if __name__ == "__main__":
    App().run()
