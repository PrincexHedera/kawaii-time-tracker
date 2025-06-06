import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime, timedelta
from gif_animator import GIFAnimator
from tkextrafont import Font
import os
import tkinter.messagebox
import sqlite3
from collections import defaultdict
from computer_animator import ComputerAnimator

class TimeTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Kawaii Time Tracker")
        master.geometry("400x500")
        master.resizable(False, False)
        master.configure(bg="#FFB6C1")

        master.wm_attributes('-topmost', True)

        self.clock_in_time = None
        self.total_hours_worked = 0.0

        script_dir = os.path.dirname(__file__)
        self.db_file_path = os.path.join(script_dir, "study_sessions.db")

        self._init_database()
        self._load_data()

        # --- Load Custom Fonts ---
        self.minecraft_font_path = os.path.join(script_dir, "assets", "fonts", "Minecraft.ttf")
        self.minecraft_font_family_name = "Minecraft"

        self.pixel_font_path = os.path.join(script_dir, "assets", "fonts", "pixel.ttf")
        self.pixel_font_family_name = "Pixelify Sans Regular"

        self.title_font = ("Arial", 24, "bold") # Default fallback
        self.main_text_font = ("Arial", 16)   # Default fallback
        self.button_text_font = ("Arial", 16, "bold") # Default fallback
        self.small_button_font = ("Arial", 12) # Default fallback
        self.star_font = ("Arial", 12)       # Default fallback

        try:
            # Register fonts. tkextrafont will return the actual family name used.
            # We don't assign to self.font directly here, but verify registration.
            dummy_minecraft_font = Font(file=self.minecraft_font_path, family=self.minecraft_font_family_name, size=10)
            dummy_pixel_font = Font(file=self.pixel_font_path, family=self.pixel_font_family_name, size=10)

            # Assign actual font objects if registration was successful
            self.title_font = Font(family=self.minecraft_font_family_name, size=24, weight="bold")
            self.main_text_font = Font(family=self.minecraft_font_family_name, size=13)
            self.button_text_font = Font(family=self.minecraft_font_family_name, size=15)
            self.small_button_font = Font(family=self.minecraft_font_family_name, size=13)
            self.star_font = Font(family=self.pixel_font_family_name, size=12)

            # Check if the font family name returned by actual() matches the desired name
            if dummy_minecraft_font.actual('family') != self.minecraft_font_family_name:
                print(f"Font Error: Minecraft font registration failed. Expected '{self.minecraft_font_family_name}', but got '{dummy_minecraft_font.actual('family')}'. Falling back to system fonts for Minecraft-related fonts.")
                self.title_font = ("Arial", 24, "bold")
                self.main_text_font = ("Arial", 16)
                self.button_text_font = ("Arial", 16, "bold")
                self.small_button_font = ("Arial", 12)

            if dummy_pixel_font.actual('family') != self.pixel_font_family_name:
                print(f"Font Error: Pixelify Sans font registration failed. Expected '{self.pixel_font_family_name}', but got '{dummy_pixel_font.actual('family')}'. Falling back to system fonts for Pixelify Sans-related fonts.")
                self.star_font = ("Arial", 12)

        except Exception as e:
            print(f"Font Error: Could not load custom fonts. Error: {e}. Falling back to system fonts.")
            # If any exception occurs during font loading, ensure all fonts fallback to Arial
            self.title_font = ("Arial", 24, "bold")
            self.main_text_font = ("Arial", 16)
            self.button_text_font = ("Arial", 16, "bold")
            self.small_button_font = ("Arial", 12)
            self.star_font = ("Arial", 12)


        # --- Load and prepare background image ---
        self.background_image_path = os.path.join(script_dir, "assets", "images", "pink_background.jpg")
        self.background_photo = None

        app_width = 400
        app_height = 500
        self.canvas = tk.Canvas(master, width=app_width, height=app_height, highlightthickness=0, bg="#FFB6C1")
        self.canvas.pack(fill="both", expand=True)

        try:
            original_bg_img = Image.open(self.background_image_path)
            self.background_photo = ImageTk.PhotoImage(original_bg_img)
            self.canvas.create_image(0, 0, image=self.background_photo, anchor="nw")

        except FileNotFoundError:
            print(f"Background image not found: {self.background_image_path}. Using solid background color for canvas.")
            self.canvas.config(bg="#FFB6C1")
        except Exception as e:
            print(f"Error loading or processing background image: {e}. Using solid background color for canvas.")
            self.canvas.config(bg="#FFB6C1")

        # --- UI Elements as Canvas Items ---
        self.title_text_id = self.canvas.create_text(200, 30, text="LOCK IN CLOCK IN", font=self.title_font, fill="#80084A", anchor="n")

        gif_display_width = 220
        gif_display_height = 220
        self.animated_gif_item_id = self.canvas.create_image(200, 60, anchor="n") # Create placeholder for GIF

        self.gif_animator = GIFAnimator(self.master, self.canvas, self.animated_gif_item_id,
                                        os.path.join("assets", "images", "pink_computer.gif"), gif_display_width, gif_display_height)



        # --- Load button images ---
        self.use_image_buttons = False
        try:
            main_button_size = (150, 70)
            side_button_size = (80, 30)

            self.img_clock_in_normal = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "clock_in_normal.png")).resize(main_button_size, Image.Resampling.LANCZOS))
            self.img_clock_in_active = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "clock_in_active.png")).resize(main_button_size, Image.Resampling.LANCZOS))

            self.img_clock_out_normal = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "clock_out_normal.png")).resize(main_button_size, Image.Resampling.LANCZOS))
            self.img_clock_out_active = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "clock_out_active.png")).resize(main_button_size, Image.Resampling.LANCZOS))

            self.img_reset_normal = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "reset_normal.png")).resize(side_button_size, Image.Resampling.LANCZOS))
            self.img_reset_active = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "reset_active.png")).resize(side_button_size, Image.Resampling.LANCZOS))

            self.img_summary_normal = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "summary_normal.png")).resize(side_button_size, Image.Resampling.LANCZOS))
            self.img_summary_active = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "summary_active.png")).resize(side_button_size, Image.Resampling.LANCZOS))

            self.img_back_normal = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "back_normal.png")).resize(side_button_size, Image.Resampling.LANCZOS))
            self.img_back_active = ImageTk.PhotoImage(Image.open(os.path.join(script_dir, "assets", "images", "back_active.png")).resize(side_button_size, Image.Resampling.LANCZOS))

            self.use_image_buttons = True
        except FileNotFoundError as e:
            print(f"Image Error: Missing button image file: {e.filename}. Using text fallback for buttons.")
            self.use_image_buttons = False
        except Exception as e:
            print(f"Image Error: Could not load or resize button image: {e}. Using text fallback for buttons.")
            self.use_image_buttons = False

        # --- Create Buttons ---
        # Clock In Button
        self.clock_in_item = self.canvas.create_image(
            200 - main_button_size[0] // 2 - 5, 
            380,
            image=self.img_clock_in_normal if self.use_image_buttons else None,
            anchor="n", tags="clock_in_button_img"
        )
        self.clock_in_text_item = None
        if not self.use_image_buttons:
            self.clock_in_text_item = self.canvas.create_text(200 - main_button_size[0] // 2 - 5, 390 + main_button_size[1]//2, text="Clock In", font=self.button_text_font, fill="#80084A", anchor="center")
            self.canvas.tag_bind(self.clock_in_text_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.clock_in_text_item, None))
            self.canvas.tag_bind(self.clock_in_text_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.clock_in_text_item, "clock_in"))
        
        self.canvas.tag_bind(self.clock_in_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.clock_in_item, self.img_clock_in_active))
        self.canvas.tag_bind(self.clock_in_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.clock_in_item, "clock_in"))


        # Clock Out Button
        self.clock_out_item = self.canvas.create_image(
            200 + main_button_size[0] // 2 + 5, 
            380,
            image=self.img_clock_out_normal if self.use_image_buttons else None,
            anchor="n", tags="clock_out_button_img"
        )
        self.clock_out_text_item = None
        if not self.use_image_buttons:
            self.clock_out_text_item = self.canvas.create_text(200 + main_button_size[0] // 2 + 5, 390 + main_button_size[1]//2, text="Clock Out", font=self.button_text_font, fill="#80084A", anchor="center")
            self.canvas.tag_bind(self.clock_out_text_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.clock_out_text_item, None))
            self.canvas.tag_bind(self.clock_out_text_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.clock_out_text_item, "clock_out"))

        self.canvas.tag_bind(self.clock_out_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.clock_out_item, self.img_clock_out_active))
        self.canvas.tag_bind(self.clock_out_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.clock_out_item, "clock_out"))


        # Reset Button (initially hidden on main page)
        self.reset_item = self.canvas.create_image(
            200, 500, # Default hidden position, will be repositioned for summary
            image=self.img_reset_normal if self.use_image_buttons else None,
            anchor="n", tags="reset_button_img", state="hidden"
        )
        self.reset_text_item = None
        if not self.use_image_buttons:
            self.reset_text_item = self.canvas.create_text(200, 460 + side_button_size[1]//2, text="Reset", font=self.small_button_font, fill="#80084A", anchor="center", state="hidden")
            self.canvas.tag_bind(self.reset_text_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.reset_text_item, None))
            self.canvas.tag_bind(self.reset_text_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.reset_text_item, "reset"))

        self.canvas.tag_bind(self.reset_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.reset_item, self.img_reset_active))
        self.canvas.tag_bind(self.reset_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.reset_item, "reset"))


        # Summary/Back Button (initially Summary button)
        self.summary_button_item = self.canvas.create_image(
            200, 460, # Default main page position
            image=self.img_summary_normal if self.use_image_buttons else None,
            anchor="n", tags="summary_button_img"
        )
        self.summary_button_text_item = None
        if not self.use_image_buttons:
            self.summary_button_text_item = self.canvas.create_text(200, 490 + side_button_size[1]//2, text="Summary", font=self.small_button_font, fill="#80084A", anchor="center")
            self.canvas.tag_bind(self.summary_button_text_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.summary_button_text_item, None))
            self.canvas.tag_bind(self.summary_button_text_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.summary_button_text_item, "toggle_summary"))

        self.canvas.tag_bind(self.summary_button_item, "<ButtonPress-1>", lambda e: self._on_canvas_button_press(e, self.summary_button_item, self.img_summary_active if not self.summary_mode else self.img_back_active))
        self.canvas.tag_bind(self.summary_button_item, "<ButtonRelease-1>", lambda e: self._on_canvas_button_release(e, self.summary_button_item, "toggle_summary"))

        # Initialize ComputerAnimator ONLY if GIF is loadable
        self.computer_animator = None
        if self.gif_animator.is_loadable(): # Check if GIF was successfully loaded by gif_animator
            try:
                # Pass the actual initial coordinates of the GIF item to ComputerAnimator
                # (Assuming GIFAnimator sets the initial image, so coords should be valid)
                gif_initial_coords = self.canvas.coords(self.animated_gif_item_id)
                self.computer_animator = ComputerAnimator(
                    self.master,
                    self.canvas,
                    self.animated_gif_item_id,
                    [
                        os.path.join("assets", "images", "heart.png"),
                        os.path.join("assets", "images", "filled_heart.png")
                    ],
                    self.gif_animator,
                    gif_initial_coords
                )
                self.canvas.tag_bind(self.animated_gif_item_id, "<Button-1>", self.computer_animator._handle_computer_click)

            except Exception as e:
                print(f"Error initializing ComputerAnimator: {e}")
                self.computer_animator = None

        else: # If GIF not loadable, remove its canvas item
            print("GIF not loadable, removing GIF item from canvas.")
            self.canvas.delete(self.animated_gif_item_id)
            self.animated_gif_item_id = None # Invalidate ID if GIF not loaded


        self.status_text_id = self.canvas.create_text(200, 300, text="Not Clocked In", font=self.main_text_font, fill="#990000", anchor="n")
        self.active_session_text_id = self.canvas.create_text(200, 330, text="", font=self.main_text_font, fill="#277445", anchor="n")
        self.hours_display_text_id = self.canvas.create_text(200, 360, text=f"Total Hours: {self.hours_to_h_m_format(self.total_hours_worked)}", font=self.main_text_font, fill="#80084A", anchor="n")

        # Summary page elements (initially hidden)
        self.summary_title_id = self.canvas.create_text(200, 50, text="Weekly Study Summary", font=self.title_font, fill="#80084A", anchor="n", state="hidden")
        self.summary_text_display_id = self.canvas.create_text(200, 100, text="", font=self.main_text_font, fill="#277445", anchor="n", justify="left", state="hidden")

        self.summary_mode = False
        self._update_button_visuals() # Initial call to set correct button states


    def _init_database(self):
        try:
            self.conn = sqlite3.connect(self.db_file_path)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    clock_in TEXT NOT NULL,
                    clock_out TEXT NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    notes TEXT
                )
            ''')
            self.conn.commit()
            print(f"Database initialized at {self.db_file_path}")
        except sqlite3.Error as e:
            print(f"Database error during initialization: {e}")
            self.conn = None
            self.cursor = None

    def _load_data(self):
        self.total_hours_worked = 0.0
        if self.conn:
            try:
                self.cursor.execute("SELECT SUM(duration_minutes) FROM sessions")
                total_minutes = self.cursor.fetchone()[0]
                self.total_hours_worked = (total_minutes / 60.0) if total_minutes is not None else 0.0
            except sqlite3.Error as e:
                print(f"Error loading total hours from database: {e}")
                self.total_hours_worked = 0.0
        else:
            self.total_hours_worked = 0.0

    def record_session(self, clock_in_iso, clock_out_iso, duration_minutes, notes):
        if self.conn:
            try:
                self.cursor.execute("INSERT INTO sessions (clock_in, clock_out, duration_minutes, notes) VALUES (?, ?, ?, ?)",
                                    (clock_in_iso, clock_out_iso, duration_minutes, notes))
                self.conn.commit()
                print(f"Session recorded: {clock_in_iso} to {clock_out_iso}, {duration_minutes} minutes.")
                return True
            except sqlite3.Error as e:
                print(f"Error recording session to database: {e}")
                return False
        return False

    def clear_all_sessions(self):
        if self.conn:
            try:
                self.cursor.execute("DELETE FROM sessions")
                self.conn.commit()
                print("All sessions deleted from database.")
                return True
            except sqlite3.Error as e:
                print(f"Error deleting sessions from database: {e}")
                return False
        return False

    def get_all_sessions_for_summary(self):
        if self.conn:
            try:
                self.cursor.execute("SELECT clock_in, duration_minutes FROM sessions ORDER BY clock_in ASC")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error querying sessions from database for summary: {e}")
                return []
        return []

    def get_weekly_hours_summary(self):
        sessions = self.get_all_sessions_for_summary()
        weekly_hours = defaultdict(float)

        for clock_in_iso, duration_minutes in sessions:
            clock_in_dt = datetime.fromisoformat(clock_in_iso)
            week_key = clock_in_dt.strftime("%G-W%V")
            weekly_hours[week_key] += duration_minutes / 60.0

        return dict(sorted(weekly_hours.items()))

    def hours_to_h_m_format(self, total_hours):
        total_minutes = int(total_hours * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        parts = []
        if hours > 0: parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
        if minutes > 0 or (hours == 0 and minutes == 0): parts.append(f"{minutes} minute{'s' if minutes > 1 else ''}")
        return " ".join(parts) if parts else "0 minutes"

    # item_id_to_highlight is the actual canvas item ID that should change its image
    def _on_canvas_button_press(self, event, item_id_to_highlight, active_image):
        if self.use_image_buttons and active_image:
            self.canvas.itemconfig(item_id_to_highlight, image=active_image)
        elif not self.use_image_buttons:
            self.canvas.itemconfig(item_id_to_highlight, fill="#FF6600")

    def _on_canvas_button_release(self, event, item_id_to_reset, action_name):
        if action_name == "clock_in":
            self.clock_in()
        elif action_name == "clock_out":
            self.clock_out()
        elif action_name == "reset":
            self.reset_hours()
        elif action_name == "toggle_summary":
            self.toggle_summary_display()

        self._update_button_visuals()
        
        self._update_button_visuals() # Ensure all buttons reflect the overall app state

    def clock_in(self, *args):
        if self.clock_in_time is not None:
            self.canvas.itemconfig(self.status_text_id, text="You are already clocked in!")
            return

        self.clock_in_time = datetime.now()
        self.canvas.itemconfig(self.status_text_id, text=f"Clocked In at: {self.clock_in_time.strftime('%I:%M %p')}")
        self._update_active_session_display()
        self._update_button_visuals()

        if self.gif_animator.is_loadable():
            self.gif_animator.start_animation()

    def clock_out(self, *args):
        if self.clock_in_time is None:
            self.canvas.itemconfig(self.status_text_id, text="You need to clock in first!")
            return

        clock_out_time = datetime.now()
        time_worked = clock_out_time - self.clock_in_time
        hours_worked = time_worked.total_seconds() / 3600
        duration_minutes = round(hours_worked * 60)

        if self.record_session(self.clock_in_time.isoformat(), clock_out_time.isoformat(), duration_minutes, ""):
            self.total_hours_worked += hours_worked

        self.canvas.itemconfig(self.status_text_id, text="Clocked Out")
        self.canvas.itemconfig(self.hours_display_text_id, text=f"Total Hours: {self.hours_to_h_m_format(self.total_hours_worked)}")
        self.clock_in_time = None
        self._update_active_session_display()
        self._update_button_visuals()

        if self.gif_animator.is_loadable():
            self.gif_animator.stop_animation()

    def reset_hours(self, *args):
        if tkinter.messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all hours? This cannot be undone."):
            if self.clear_all_sessions():
                self.canvas.itemconfig(self.status_text_id, text="All hours reset!")
                self.total_hours_worked = 0.0
                self.canvas.itemconfig(self.hours_display_text_id, text=f"Total Hours: {self.hours_to_h_m_format(self.total_hours_worked)}")
                self.clock_in_time = None
                self._update_active_session_display()
                self._update_button_visuals()

                if self.gif_animator.is_loadable():
                    self.gif_animator.stop_animation()
                if self.computer_animator:
                    self.computer_animator.clear_hearts()
            else:
                self.canvas.itemconfig(self.status_text_id, text="Error resetting hours!")

    def _update_active_session_display(self):
        if self.clock_in_time:
            self.canvas.itemconfig(self.active_session_text_id, text=f"Active Session: {self.hours_to_h_m_format((datetime.now() - self.clock_in_time).total_seconds() / 3600)}")
            self.master.after(1000, self._update_active_session_display)
        else:
            self.canvas.itemconfig(self.active_session_text_id, text="")

    def _update_button_visuals(self):
            """Updates all button visuals based on app state."""
            def reset_button(item, normal_img, text_item):
                if self.use_image_buttons:
                    self.canvas.itemconfig(item, image=normal_img)
                elif text_item:
                    self.canvas.itemconfig(text_item, fill="#80084A")

            # Reset all buttons to normal
            reset_button(self.clock_in_item, self.img_clock_in_normal, self.clock_in_text_item)
            reset_button(self.clock_out_item, self.img_clock_out_normal, self.clock_out_text_item)
            reset_button(self.reset_item, self.img_reset_normal, self.reset_text_item)

            # Set summary/back button based on current mode
            if self.summary_mode:
                if self.use_image_buttons:
                    self.canvas.itemconfig(self.summary_button_item, image=self.img_back_normal)
                elif self.summary_button_text_item:
                    self.canvas.itemconfig(self.summary_button_text_item, text="Back", fill="#80084A")
            else:
                if self.use_image_buttons:
                    self.canvas.itemconfig(self.summary_button_item, image=self.img_summary_normal)
                elif self.summary_button_text_item:
                    self.canvas.itemconfig(self.summary_button_text_item, text="Summary", fill="#80084A")


    def _hide_main_page_elements(self):
        """Hides the main page UI elements."""
        self.canvas.itemconfig(self.title_text_id, state="hidden")
        if self.animated_gif_item_id is not None:
            self.canvas.itemconfig(self.animated_gif_item_id, state="hidden")
        self.canvas.itemconfig(self.status_text_id, state="hidden")
        self.canvas.itemconfig(self.active_session_text_id, state="hidden")
        self.canvas.itemconfig(self.hours_display_text_id, state="hidden")

        if self.use_image_buttons:
            self.canvas.itemconfig(self.clock_in_item, state="hidden")
            self.canvas.itemconfig(self.clock_out_item, state="hidden")
        else:
            if self.clock_in_text_item: self.canvas.itemconfig(self.clock_in_text_item, state="hidden")
            if self.clock_out_text_item: self.canvas.itemconfig(self.clock_out_text_item, state="hidden")
            # Reset button text is handled in _hide_summary_elements (as it's on summary page)


        if self.gif_animator.is_loadable():
            self.gif_animator.stop_animation()
        if self.computer_animator:
            self.computer_animator.stop_shake()
            self.computer_animator.clear_hearts()


    def _show_main_page_elements(self):
        """Shows the main page UI elements."""
        self.canvas.itemconfig(self.title_text_id, state="normal")
        if self.animated_gif_item_id is not None:
            self.canvas.itemconfig(self.animated_gif_item_id, state="normal")
        self.canvas.itemconfig(self.status_text_id, state="normal")
        self.canvas.itemconfig(self.active_session_text_id, state="normal")
        self.canvas.itemconfig(self.hours_display_text_id, state="normal")

        if self.use_image_buttons:
            self.canvas.itemconfig(self.clock_in_item, state="normal")
            self.canvas.itemconfig(self.clock_out_item, state="normal")
        else:
            if self.clock_in_text_item: self.canvas.itemconfig(self.clock_in_text_item, state="normal")
            if self.clock_out_text_item: self.canvas.itemconfig(self.clock_out_text_item, state="normal")
            # Reset button text is handled by _hide_summary_elements (as it's on summary page)

        if self.clock_in_time and self.gif_animator.is_loadable():
            self.gif_animator.start_animation()


    def _show_summary_elements(self):
        """Shows the weekly summary UI elements."""
        self.canvas.itemconfig(self.summary_title_id, state="normal")
        self.canvas.itemconfig(self.summary_text_display_id, state="normal")

        # Position and show Reset button on summary page
        side_button_size = (80, 30)
        button_y = 420 # Y coordinate for buttons on summary page
        reset_x = 200 # X coordinate for buttons on summary page
        self.canvas.coords(self.reset_item, reset_x, button_y)
        self.canvas.itemconfig(self.reset_item, state="normal") # Show Reset button
        if not self.use_image_buttons and self.reset_text_item:
            self.canvas.coords(self.reset_text_item, reset_x, button_y + side_button_size[1]//2)
            self.canvas.itemconfig(self.reset_text_item, state="normal")


    def _hide_summary_elements(self):
        """Hides the weekly summary UI elements."""
        self.canvas.itemconfig(self.summary_title_id, state="hidden")
        self.canvas.itemconfig(self.summary_text_display_id, state="hidden")
        self.canvas.itemconfig(self.reset_item, state="hidden") # Hide Reset button
        if not self.use_image_buttons and self.reset_text_item:
            self.canvas.itemconfig(self.reset_text_item, state="hidden")


    def display_weekly_summary(self):
        weekly_summary = self.get_weekly_hours_summary()

        summary_text = ""
        if not weekly_summary:
            summary_text = "Nothing's here..."
        else:
            sorted_weeks = sorted(weekly_summary.keys())
            for week_key in sorted_weeks:
                hours = weekly_summary[week_key]
                summary_text += f"{week_key}: {self.hours_to_h_m_format(hours)}\n"

        self.canvas.itemconfig(self.summary_text_display_id, text=summary_text)

    def toggle_summary_display(self, *args):
        self.summary_mode = not self.summary_mode

        if self.summary_mode:
            self._show_summary_elements()
            self._hide_main_page_elements()
            self.display_weekly_summary()
            if self.gif_animator.is_loadable():
                self.gif_animator.stop_animation()
            if self.computer_animator:
                self.computer_animator.clear_hearts()
        else:
            self._hide_summary_elements()
            self._show_main_page_elements()
            if self.clock_in_time and self.gif_animator.is_loadable():
                self.gif_animator.start_animation()
            elif self.gif_animator.is_loadable():
                self.gif_animator.stop_animation()

        self._update_button_visuals()

    def stop_all_animations(self):
        """Stops all active animations."""
        if self.gif_animator.is_loadable():
            self.gif_animator.stop_animation()
        if self.computer_animator:
            self.computer_animator.stop_shake()
            self.computer_animator.clear_hearts()


    def on_close(self):
        self.stop_all_animations()
        self.close_db_connection()
        self.master.destroy()