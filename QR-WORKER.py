# ignore
import io
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
from pyzbar.pyzbar import decode
import qrcode


def _apply_dark_titlebar(window: tk.Tk):
    if sys.platform != "win32":
        return

    try:
        window.update_idletasks()  # ensure the window handle exists
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())

        DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # value for Win10 20H1+/Win11
        value = ctypes.c_int(1)  # 1 = dark, 0 = light
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value),
        )
    except Exception:
        pass

# still ignore
BG = "#1e1e1e"
BG_PANEL = "#2b2b2b"
FG = "#e0e0e0"
FG_MUTED = "#9a9a9a"
ACCENT = "#3a7bd5"
ACCENT_HOVER = "#4f8ee0"
BORDER = "#3a3a3a"


class QRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR-WORKER")
        self.root.geometry("560x640")
        self.root.minsize(420, 480)
        self.root.configure(bg=BG)

        try:
            icon_img = tk.PhotoImage(file="logo.png")
            self.root.iconphoto(False, icon_img)
        except Exception:
            pass

        _apply_dark_titlebar(self.root)
        self._setup_dark_style()

        notebook = ttk.Notebook(root, style="Dark.TNotebook")
        notebook.pack(fill="both", expand=True)

        self.read_tab = tk.Frame(notebook, bg=BG)
        self.create_tab = tk.Frame(notebook, bg=BG)
        notebook.add(self.read_tab, text="Read")
        notebook.add(self.create_tab, text="Create")

        self._build_read_tab()
        self._build_create_tab()

        self.notebook = notebook
        self.root.bind_all("<Control-v>", self._on_ctrl_v)

    #also ignore, it's for the app to be dark themed
    def _setup_dark_style(self):
        style = ttk.Style()
        # "clam" theme is required as a base for reliable color overrides
        style.theme_use("clam")

        style.configure(
            "Dark.TNotebook",
            background=BG,
            borderwidth=0,
        )
        style.configure(
            "Dark.TNotebook.Tab",
            background=BG_PANEL,
            foreground=FG,
            padding=(14, 6),
            borderwidth=0,
        )
        style.map(
            "Dark.TNotebook.Tab",
            background=[("selected", ACCENT)],
            foreground=[("selected", "#ffffff")],
        )

    def _make_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=ACCENT,
            fg="#ffffff",
            activebackground=ACCENT_HOVER,
            activeforeground="#ffffff",
            relief="flat",
            padx=10,
            pady=4,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )

    def _make_label(self, parent, text, muted=False):
        return tk.Label(
            parent,
            text=text,
            bg=BG,
            fg=FG_MUTED if muted else FG,
        )
    # Read
    def _build_read_tab(self):
        tab = self.read_tab
        self.current_image = None

        top_frame = tk.Frame(tab, bg=BG, pady=8)
        top_frame.pack(fill="x")

        self._make_button(
            top_frame, "Select from file", self.choose_file
        ).pack(side="left", padx=8)

        self._make_label(
            top_frame, "Use ctrl+v to insert screenshot", muted=True
        ).pack(side="left", padx=8)

        self.preview_label = tk.Label(
            tab,
            text="No image here,\n(Select file, or paste a screenshot using ctrl+v)",
            bg=BG_PANEL,
            fg=FG_MUTED,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.preview_label.pack(fill="both", expand=True, padx=10, pady=10)

        result_frame = tk.Frame(tab, bg=BG, pady=6)
        result_frame.pack(fill="x")

        self._make_label(result_frame, "Read value:").pack(anchor="w", padx=10)

        self.result_text = tk.Text(
            result_frame,
            height=5,
            wrap="word",
            bg=BG_PANEL,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.result_text.pack(fill="x", padx=10, pady=(2, 6))

        self._make_button(
            result_frame, "->Copy outcome<-", self.copy_result
        ).pack(padx=10, pady=(0, 8), anchor="w")

    def choose_file(self):
        path = filedialog.askopenfilename(
            title="Select image/screenshot",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.bmp *.gif *.webp"),
                ("All", "*.*"),
            ],
        )
        if not path:
            return
        try:
            image = Image.open(path)
            self.load_image(image)
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't create a file :[ \n{e}")

    def load_image(self, image: Image.Image):
        self.current_image = image.convert("RGB")
        self.show_preview(self.current_image)
        self.decode_qr(self.current_image)

    def show_preview(self, image: Image.Image):
        preview = image.copy()
        preview.thumbnail((480, 320))
        photo = ImageTk.PhotoImage(preview)
        self.preview_label.configure(image=photo, text="")
        self.preview_label.image = photo

    def decode_qr(self, image: Image.Image):
        self.result_text.delete("1.0", "end")
        results = decode(image)

        if not results:
            self.result_text.insert(
                "1.0",
                "No QR found on the image.\n"
                "Please, if possible, take a clearer picture/screenshot :]",
            )
            return

        lines = []
        for i, r in enumerate(results, start=1):
            content = r.data.decode("utf-8", errors="replace")
            lines.append(f"[{i}] typ: {r.type}\n{content}")

        self.result_text.insert("1.0", "\n\n".join(lines))

    def copy_result(self):
        text = self.result_text.get("1.0", "end").strip()
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "The result copied to clipboard :]")

    # Create
    def _build_create_tab(self):
        tab = self.create_tab
        self.generated_qr_image = None

        input_frame = tk.Frame(tab, bg=BG, pady=8)
        input_frame.pack(fill="x")

        self._make_label(input_frame, "Type in/paste here:").pack(anchor="w", padx=10)

        self.qr_input = tk.Text(
            input_frame,
            height=4,
            wrap="word",
            bg=BG_PANEL,
            fg=FG,
            insertbackground=FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor=ACCENT,
        )
        self.qr_input.pack(fill="x", padx=10, pady=(2, 6))

        self._make_button(
            input_frame, "Generate the QR", self.generate_qr
        ).pack(padx=10, anchor="w")

        self.qr_preview_label = tk.Label(
            tab,
            text="QR code will be found here",
            bg=BG_PANEL,
            fg=FG_MUTED,
            relief="flat",
            highlightthickness=1,
            highlightbackground=BORDER,
        )
        self.qr_preview_label.pack(fill="both", expand=True, padx=10, pady=10)

        bottom_frame = tk.Frame(tab, bg=BG, pady=6)
        bottom_frame.pack(fill="x")

        self._make_button(
            bottom_frame, "Save as PNG file", self.save_qr
        ).pack(side="left", padx=10)

        self._make_button(
            bottom_frame, "Copy the image", self.copy_qr_image
        ).pack(side="left", padx=10)

    def generate_qr(self):
        text = self.qr_input.get("1.0", "end").strip()
        if not text:
            messagebox.showinfo("Nothing here", "Paste/type something here :]")
            return

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white").convert("RGB")

        self.generated_qr_image = image
        preview = image.copy()
        preview.thumbnail((400, 400))
        photo = ImageTk.PhotoImage(preview)
        self.qr_preview_label.configure(image=photo, text="")
        self.qr_preview_label.image = photo

    def save_qr(self):
        if self.generated_qr_image is None:
            messagebox.showinfo("No QR here?", "Generate QR first :]")
            return

        path = filedialog.asksaveasfilename(
            title="Save QR as",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
        )
        if not path:
            return

        try:
            self.generated_qr_image.save(path)
            messagebox.showinfo("Saved", f"QR saved as \n{path}")
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't save qr :[ \n{e}")

    def copy_qr_image(self):
        if self.generated_qr_image is None:
            messagebox.showinfo("No QR", "Generate QR first :]")
            return
        try:
            output = io.BytesIO()
            self.generated_qr_image.save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()

            import win32clipboard
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            messagebox.showinfo("Copied", "Qr saved to clipboard :]")
        except ImportError:
            messagebox.showwarning(
                "Error",
                "Requires 'pywin32'.\n"
                "Install using:\n\npip install pywin32\n\n"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't copy image :[ \n{e}")

    def _on_ctrl_v(self, event=None):
        current = self.notebook.select()
        if current == str(self.read_tab):
            self._paste_image_from_clipboard()

    def _paste_image_from_clipboard(self):
        try:
            image = ImageGrab.grabclipboard()
        except Exception as e:
            messagebox.showerror("Something crashed", f"Couldn't read the clipboard :[ :\n{e}")
            return

        if image is None:
            messagebox.showinfo(
                "No image",
                "The clipboard is empty, or does not contain an image.\n"
            )
            return

        if isinstance(image, list):
            if not image:
                return
            try:
                image = Image.open(image[0])
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't load the image :[ \n{e}")
                return

        self.load_image(image)


if __name__ == "__main__":
    root = tk.Tk()
    app = QRApp(root)
    root.mainloop()