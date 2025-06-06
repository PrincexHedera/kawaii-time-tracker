import tkinter as tk
from PIL import Image, ImageTk
import os
import random
import math
import time

class ComputerAnimator:
    def __init__(self, master, canvas, item_id, heart_image_path_list, gif_animator_instance, gif_coords):
        self.master = master
        self.canvas = canvas
        self.item_id = item_id
        self.gif_animator = gif_animator_instance
        self.original_x, self.original_y = gif_coords

        self.img_heart = None
        self.img_filled_heart = None
        self.img_clover = None
        self.star_images = []  # To keep references to PhotoImages
        self.star_base_images = []  # Store multiple star base images
        self._load_heart_images(heart_image_path_list)

        self.canvas.tag_bind(self.item_id, "<Button-1>", self._handle_computer_click)

        self.shake_animation_active = False
        self.shake_id = None

    def _load_heart_images(self, image_paths):
        script_dir = os.path.dirname(__file__)
        heart_size = (40, 40)
        star_size = (60, 60)
        try:
            self.img_heart = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "heart.png")).resize(heart_size, Image.Resampling.LANCZOS))
            self.img_filled_heart = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "filled_heart.png")).resize(heart_size, Image.Resampling.LANCZOS))
            self.img_clover = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "clover.png")).resize((40, 40), Image.Resampling.LANCZOS))
            star_filenames = ["stars.png", "stars1.png", "stars2.png", "stars3.png"]
            for filename in star_filenames:
                image = Image.open(os.path.join(script_dir, "assets", "images", filename)).resize(star_size, Image.Resampling.LANCZOS)
                self.star_base_images.append(image)
            self.star_size = star_size
        except Exception as e:
            print(f"Error loading heart/stars images: {e}")

    def _handle_computer_click(self, event):
        if self.gif_animator.is_playing:
            if not self.shake_animation_active:
                self._start_shake()
            self._create_hearts(event.x, event.y, num_hearts=random.randint(3, 7))
            self._create_star_effect(event.x, event.y - 20)
        else:
            print("Computer is sleeping... Clock in to wake it up!")

    def _start_shake(self):
        self.shake_animation_active = True
        self._shake_computer()

    def stop_shake(self):
        if self.shake_id:
            self.master.after_cancel(self.shake_id)
        self.shake_animation_active = False
        self.canvas.coords(self.item_id, self.original_x, self.original_y)

    def _shake_computer(self, count=0):
        if not self.shake_animation_active:
            self.canvas.coords(self.item_id, self.original_x, self.original_y)
            return
        if count < 5:
            x_offset = random.randint(-10, 10)
            y_offset = random.randint(-5, 5)
            self.canvas.coords(self.item_id, self.original_x + x_offset, self.original_y + y_offset)
            self.shake_id = self.master.after(50, self._shake_computer, count + 1)
        else:
            self.shake_animation_active = False
            self.canvas.coords(self.item_id, self.original_x, self.original_y)

    def _create_hearts(self, center_x, center_y, num_hearts=random.randint(1, 3)):
        start_y = center_y + 20
        for _ in range(num_hearts):
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)

            roll = random.randint(1, 1000)
            if roll == 1 and self.img_clover:
                heart_img = self.img_clover
            else:
                heart_img = random.choice([self.img_heart, self.img_filled_heart])

            heart_id = self.canvas.create_image(center_x + offset_x, start_y + offset_y, image=heart_img)
            self._animate_heart(heart_id)

    def _animate_heart(self, heart_id, speed=2, gravity=0.4):
        angle = random.uniform(-math.pi / 2 - math.pi / 8, -math.pi / 2 + math.pi / 4)
        velocity_x = speed * math.cos(angle) * random.uniform(0.8, 2)
        velocity_y = speed * math.sin(angle) * random.uniform(0.8, 2)
        fade_start = time.time()
        floor_y = self.canvas.winfo_height() - 10

        def update():
            nonlocal velocity_y, velocity_x
            coords = self.canvas.coords(heart_id)
            if not coords:
                return
            x, y = coords
            velocity_y += gravity
            new_x = x + velocity_x
            new_y = y + velocity_y
            if new_y >= floor_y:
                new_y = floor_y
                velocity_y *= -0.6
                velocity_x *= 0.8
            self.canvas.coords(heart_id, new_x, new_y)
            if time.time() - fade_start >= 20:
                self.canvas.delete(heart_id)
            else:
                self.master.after(20, update)

        update()

    def _create_star_effect(self, center_x, center_y):
        if not self.star_base_images:
            return

        base_image = random.choice(self.star_base_images)
        angle = random.randint(0, 360)
        rotated_image = base_image.rotate(angle, expand=True)
        star_photoimage = ImageTk.PhotoImage(rotated_image)
        self.star_images.append(star_photoimage)

        star_id = self.canvas.create_image(center_x, center_y, image=star_photoimage)
        fade_start = time.time()

        def fade():
            if time.time() - fade_start >= 1:
                self.canvas.delete(star_id)
            else:
                self.master.after(30, fade)

        fade()

    def clear_hearts(self):
        pass
