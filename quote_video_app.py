"""
Traders Never Settle - Quote Video Generator (Desktop GUI)

A simple standalone Python app (no browser, no environment variables).
Enter your API key, pick a reference image, type a quote, and generate
a narrated video clip using Gemini Omni Flash.

Setup (run once):
    pip install google-genai pillow

Run:
    python quote_video_app.py
"""

import base64
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

try:
    from google import genai
except ImportError:
    genai = None


class QuoteVideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Traders Never Settle - Quote Video Generator")
        self.root.geometry("560x760")
        self.root.resizable(False, False)

        self.image_path = None
        self.output_path = None

        pad = {"padx": 12, "pady": 6}

        # ---- API key ----
        ttk.Label(root, text="1. Gemini API key", font=("Segoe UI", 10, "bold")).pack(anchor="w", **pad)
        key_frame = ttk.Frame(root)
        key_frame.pack(fill="x", **pad)
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(key_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.pack(side="left", fill="x", expand=True)
        self.show_key_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            key_frame, text="Show", variable=self.show_key_var, command=self.toggle_key_visibility
        ).pack(side="left", padx=(6, 0))
        ttk.Label(
            root,
            text="Get a key at aistudio.google.com. It is only kept in memory for this session, never saved to disk.",
            foreground="#666",
            wraplength=520,
        ).pack(anchor="w", padx=12)

        # ---- Reference image ----
        ttk.Label(root, text="2. Reference image", font=("Segoe UI", 10, "bold")).pack(anchor="w", **pad)
        ttk.Button(root, text="Choose image...", command=self.choose_image).pack(anchor="w", padx=12)
        self.image_label = ttk.Label(root, text="No image selected")
        self.image_label.pack(anchor="w", padx=12, pady=(4, 0))
        self.preview_canvas = tk.Label(root)
        self.preview_canvas.pack(pady=8)

        # ---- Quote ----
        ttk.Label(root, text="3. Quote to narrate", font=("Segoe UI", 10, "bold")).pack(anchor="w", **pad)
        self.quote_text = tk.Text(root, height=3, width=60, wrap="word")
        self.quote_text.pack(padx=12)

        # ---- Extra direction ----
        ttk.Label(root, text="4. Optional extra direction", font=("Segoe UI", 10, "bold")).pack(anchor="w", **pad)
        self.direction_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.direction_var, width=60).pack(padx=12)

        # ---- Options ----
        opts_frame = ttk.Frame(root)
        opts_frame.pack(fill="x", **pad)

        ttk.Label(opts_frame, text="Aspect ratio:").grid(row=0, column=0, sticky="w")
        self.aspect_var = tk.StringVar(value="16:9")
        ttk.Combobox(
            opts_frame, textvariable=self.aspect_var, values=["16:9", "9:16"], width=10, state="readonly"
        ).grid(row=0, column=1, padx=(6, 24))

        ttk.Label(opts_frame, text="Resolution:").grid(row=0, column=2, sticky="w")
        self.resolution_var = tk.StringVar(value="720p")
        self.resolution_box = ttk.Combobox(
            opts_frame, textvariable=self.resolution_var, values=["720p", "1080p", "4k"], width=10, state="readonly"
        )
        self.resolution_box.grid(row=0, column=3, padx=(6, 0))
        self.resolution_box.bind("<<ComboboxSelected>>", lambda e: self.update_cost_label())

        self.cost_label = ttk.Label(root, foreground="#666")
        self.cost_label.pack(anchor="w", padx=12)
        self.update_cost_label()

        # ---- Generate ----
        self.generate_btn = ttk.Button(root, text="Generate video", command=self.on_generate_clicked)
        self.generate_btn.pack(pady=14)

        self.status_label = ttk.Label(root, text="", foreground="#333", wraplength=520)
        self.status_label.pack(padx=12)

        self.progress = ttk.Progressbar(root, mode="indeterminate", length=400)

    # ---- UI helpers ----
    def toggle_key_visibility(self):
        self.api_key_entry.config(show="" if self.show_key_var.get() else "*")

    def update_cost_label(self):
        res = self.resolution_var.get()
        if res == "720p":
            text = "Estimated cost: ~$0.60-$0.90 for a short clip (~$0.10/sec at 720p)."
        elif res == "1080p":
            text = "Estimated cost: higher than 720p due to upscaling - test at 720p first."
        else:
            text = "Estimated cost: 4K is the priciest tier - validate at 720p before using this."
        self.cost_label.config(text=text)

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Choose reference image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.webp")],
        )
        if not path:
            return
        self.image_path = path
        self.image_label.config(text=os.path.basename(path))
        try:
            img = Image.open(path)
            img.thumbnail((260, 260))
            self.tk_img = ImageTk.PhotoImage(img)
            self.preview_canvas.config(image=self.tk_img)
        except Exception as e:
            messagebox.showerror("Image error", f"Could not preview image:\n{e}")

    # ---- Generation ----
    def on_generate_clicked(self):
        api_key = self.api_key_var.get().strip()
        quote = self.quote_text.get("1.0", "end").strip()

        if genai is None:
            messagebox.showerror(
                "Missing dependency",
                "The google-genai package is not installed.\nRun: pip install google-genai",
            )
            return
        if not api_key:
            messagebox.showwarning("Missing API key", "Please enter your Gemini API key.")
            return
        if not self.image_path:
            messagebox.showwarning("Missing image", "Please choose a reference image.")
            return
        if not quote:
            messagebox.showwarning("Missing quote", "Please type a quote to narrate.")
            return

        if self.resolution_var.get() in ("1080p", "4k"):
            if not messagebox.askyesno(
                "Confirm generation",
                f"You're about to generate at {self.resolution_var.get()}, which costs more than 720p.\n\nContinue?",
            ):
                return

        self.generate_btn.config(state="disabled")
        self.status_label.config(text="Generating video... this can take a minute or two.")
        self.progress.pack(pady=(0, 10))
        self.progress.start(10)

        thread = threading.Thread(
            target=self._generate_video,
            args=(api_key, self.image_path, quote, self.direction_var.get().strip(),
                  self.aspect_var.get(), self.resolution_var.get()),
            daemon=True,
        )
        thread.start()

    def _generate_video(self, api_key, image_path, quote, extra_direction, aspect_ratio, resolution):
        try:
            client = genai.Client(api_key=api_key)

            with open(image_path, "rb") as f:
                image_bytes = f.read()
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")

            ext = os.path.splitext(image_path)[1].lower()
            mime_type = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(
                ext.replace(".", ""), "image/jpeg"
            )

            prompt_text = (
                f'In a single continuous shot, no scene cuts: the character in the '
                f'reference image looks at the camera and says, in character: "{quote}" '
            )
            if extra_direction:
                prompt_text += f" Direction: {extra_direction}."
            prompt_text += (
                " Natural lip sync matching the character's voice and personality. "
                " Keep the clip short and tight, just long enough for the line. No extra dialogue."
            )

            interaction = client.interactions.create(
                model="gemini-omni-1.1-flash",
                input=[
                    {"type": "image", "data": image_b64, "mime_type": mime_type},
                    {"type": "text", "text": prompt_text},
                ],
                generation_config={"video_config": {"task": "image_to_video"}},
                response_format={
                    "type": "video",
                    "aspect_ratio": aspect_ratio,
                    "resolution": resolution,
                },
            )

            video_bytes = base64.b64decode(interaction.output_video.data)
            self.root.after(0, lambda: self._on_generation_done(video_bytes))

        except Exception as e:
            err = str(e)
            self.root.after(0, lambda: self._on_generation_error(err))

    def _on_generation_done(self, video_bytes):
        self.progress.stop()
        self.progress.pack_forget()
        self.generate_btn.config(state="normal")

        save_path = filedialog.asksaveasfilename(
            title="Save video as...",
            defaultextension=".mp4",
            filetypes=[("MP4 video", "*.mp4")],
            initialfile="quote_clip.mp4",
        )
        if save_path:
            with open(save_path, "wb") as f:
                f.write(video_bytes)
            self.status_label.config(text=f"Saved to {save_path}")
            messagebox.showinfo("Done", f"Video saved to:\n{save_path}")
        else:
            self.status_label.config(text="Generation finished, but no save location was chosen.")

    def _on_generation_error(self, error_message):
        self.progress.stop()
        self.progress.pack_forget()
        self.generate_btn.config(state="normal")
        self.status_label.config(text="Generation failed - see error popup for details.")
        messagebox.showerror("Generation failed", error_message)


if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteVideoApp(root)
    root.mainloop()
