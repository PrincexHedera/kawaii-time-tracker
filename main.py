import tkinter as tk
from app_module import TimeTrackerApp

if __name__ == "__main__":
    root = tk.Tk()
    app = TimeTrackerApp(root)

    # Ensure all animations are stopped when the window is closed
    root.protocol("WM_DELETE_WINDOW", lambda: [app.stop_all_animations(), root.destroy()])

    root.mainloop()