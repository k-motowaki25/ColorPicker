import tkinter as tk
from PIL import Image, ImageTk
import mss
import pyautogui
import colorsys


class ColorPickerApp:
    def __init__(self, screenshot_size=10, magnification=20, refresh_rate=10):
        self.screenshot_size = screenshot_size
        self.magnification = magnification
        self.refresh_rate = refresh_rate
        self.window = tk.Tk()
        self.sct = mss.mss()
        self.locked_position = None
        self.tk_screenshot = None

        self.canvas, self.label_rgb, self.label_hsb, self.label_hex, self.hex_color = self._initialize_widgets()
        self._bind_events()

    def _initialize_widgets(self):
        canvas = self._create_canvas()
        label_rgb, label_hsb, label_hex, hex_color = self._create_labels()
        self._create_copy_button()

        return canvas, label_rgb, label_hsb, label_hex, hex_color

    def _create_canvas(self):
        canvas = tk.Canvas(
            self.window,
            width=self.screenshot_size * self.magnification,
            height=self.screenshot_size * self.magnification
        )
        canvas.pack()

        return canvas

    def _create_labels(self):
        label_rgb = tk.Label(self.window)
        label_rgb.pack()

        label_hsb = tk.Label(self.window)
        label_hsb.pack()

        hex_color = tk.StringVar()
        label_hex = tk.Label(self.window, textvariable=hex_color)
        label_hex.pack()

        return label_rgb, label_hsb, label_hex, hex_color

    def _create_copy_button(self):
        tk.Button(self.window, text="Copy", command=self.copy_hex_color_to_clipboard).pack()

    def _bind_events(self):
        self.window.bind("<space>", self.toggle_lock_position)
        self.window.after(self.refresh_rate, self.update_display)

    def copy_hex_color_to_clipboard(self):
        self.window.clipboard_clear()
        self.window.clipboard_append(self.hex_color.get())

    def toggle_lock_position(self, event):
        self.locked_position = pyautogui.position() if self.locked_position is None else None

    def update_display(self):
        x, y = self.locked_position or pyautogui.position()
        screenshot = self._get_screenshot(x, y, self.screenshot_size)
        self._display_screenshot(screenshot)

        r, g, b = self._get_rgb_from_screenshot(self._get_screenshot(x, y, 1))
        h, s, v = self._get_hsv_from_rgb(r, g, b)

        self._update_color_labels(r, g, b, h, s, v)
        self._set_hex_color(r, g, b)

        self.window.after(self.refresh_rate, self.update_display)

    def _get_screenshot(self, x, y, size):
        screenshot = self.sct.grab({
            "left": x - size // 2,
            "top": y - size // 2,
            "width": size,
            "height": size,
        })
        screenshot = Image.frombytes("RGB", screenshot.size, screenshot.rgb, "raw", "RGB")
        screenshot = screenshot.resize((size * self.magnification, size * self.magnification), Image.NEAREST)

        return screenshot

    def _display_screenshot(self, screenshot):
        self.tk_screenshot = ImageTk.PhotoImage(screenshot)
        self.canvas.delete("all")
        self.canvas.create_image(
            self.screenshot_size * self.magnification // 2,
            self.screenshot_size * self.magnification // 2,
            image=self.tk_screenshot
        )
        self.canvas.create_rectangle(
            self.screenshot_size * self.magnification // 2,
            self.screenshot_size * self.magnification // 2,
            self.screenshot_size * self.magnification // 2 + 1 * self.screenshot_size,
            self.screenshot_size * self.magnification // 2 + 1 * self.screenshot_size,
            outline="red"
        )

    def _get_rgb_from_screenshot(self, screenshot):
        return screenshot.getpixel((0, 0))

    def _get_hsv_from_rgb(self, r, g, b):
        return colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)

    def _update_color_labels(self, r, g, b, h, s, v):
        self.label_rgb["text"] = f"RGB: ({r}, {g}, {b})"
        self.label_hsb["text"] = f"HSV: ({h:.2f}, {s:.2f}, {v:.2f})"

    def _set_hex_color(self, r, g, b):
        self.hex_color.set(f"#{r:02X}{g:02X}{b:02X}")


if __name__ == "__main__":
    app = ColorPickerApp()
    app.window.mainloop()
