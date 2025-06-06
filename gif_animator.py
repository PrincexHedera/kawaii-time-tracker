# gif_animator.py (Corrected)
import tkinter as tk
from PIL import Image, ImageTk

class GIFAnimator:
    def __init__(self, master, canvas, item_id, gif_path, width, height):
        self.master = master
        self.canvas = canvas
        self.item_id = item_id
        self.gif_path = gif_path
        self.width = width
        self.height = height
        self.frames = []
        self.frame_index = 0
        self.animation_id = None
        self.is_playing = False
        self.original_gif_duration = 100

        try:
            original_gif = Image.open(gif_path)
            if 'duration' in original_gif.info:
                self.original_gif_duration = original_gif.info['duration']

            for i in range(original_gif.n_frames):
                original_gif.seek(i)
                frame = original_gif.convert('RGBA').resize((width, height), Image.Resampling.LANCZOS)
                self.frames.append(ImageTk.PhotoImage(frame))
            self.is_loadable_flag = True
        except FileNotFoundError:
            print(f"GIF file not found: {gif_path}")
            self.is_loadable_flag = False
        except Exception as e:
            print(f"Error loading GIF: {e}")
            self.is_loadable_flag = False

        if self.is_loadable_flag:
            self.canvas.itemconfig(self.item_id, image=self.frames[0])
        else:
            # --- FIX ---
            # Instead of deleting the item, we hide it.
            # This prevents a crash if other parts of the code (like ComputerAnimator)
            # try to reference this item_id.
            self.canvas.itemconfig(self.item_id, state="hidden")

    def is_loadable(self):
        return self.is_loadable_flag

    def start_animation(self):
        if self.is_loadable() and not self.is_playing:
            self.is_playing = True
            self._animate_gif()

    def stop_animation(self):
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None
        self.is_playing = False # Ensure this is always set

    def _animate_gif(self):
        if not self.is_playing:
            return

        frame = self.frames[self.frame_index]
        self.canvas.itemconfig(self.item_id, image=frame)

        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.animation_id = self.master.after(self.original_gif_duration, self._animate_gif)