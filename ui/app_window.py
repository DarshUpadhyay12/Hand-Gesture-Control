import customtkinter as ctk
from PIL import Image, ImageTk
import cv2
import threading
import time
from loguru import logger

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AppWindow(ctk.CTk):
    def __init__(self, app_core):
        super().__init__()
        self.app_core = app_core
        
        self.title("Hand Gesture Control")
        self.geometry("900x600")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # UI Structure
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Gesture Control", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Mode Selection
        self.mode_var = ctk.StringVar(value="mouse")
        self.app_core.current_mode = "mouse"
        
        self.radio_mouse = ctk.CTkRadioButton(self.sidebar_frame, text="Mouse Mode", variable=self.mode_var, value="mouse", command=self.change_mode)
        self.radio_mouse.grid(row=1, column=0, pady=10, padx=20, sticky="w")
        
        self.radio_media = ctk.CTkRadioButton(self.sidebar_frame, text="Media Mode", variable=self.mode_var, value="media", command=self.change_mode)
        self.radio_media.grid(row=2, column=0, pady=10, padx=20, sticky="w")
        
        self.radio_presentation = ctk.CTkRadioButton(self.sidebar_frame, text="Presentation Mode", variable=self.mode_var, value="presentation", command=self.change_mode)
        self.radio_presentation.grid(row=3, column=0, pady=10, padx=20, sticky="w")
        
        self.radio_drawing = ctk.CTkRadioButton(self.sidebar_frame, text="Drawing Mode", variable=self.mode_var, value="drawing", command=self.change_mode)
        self.radio_drawing.grid(row=4, column=0, pady=10, padx=20, sticky="w")

        # Sensitivity
        self.sens_label = ctk.CTkLabel(self.sidebar_frame, text="Mouse Sensitivity:")
        self.sens_label.grid(row=7, column=0, padx=20, pady=(10,0), sticky="w")
        self.sens_slider = ctk.CTkSlider(self.sidebar_frame, from_=1, to=10, command=self.change_sensitivity)
        self.sens_slider.set(self.app_core.config.get("sensitivity", "mouse_smoothness"))
        self.sens_slider.grid(row=8, column=0, padx=20, pady=(0,20), sticky="w")

        # Main Frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = ctk.CTkLabel(self.main_frame, text="")
        self.video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Status Bar
        self.status_var = ctk.StringVar(value="Status: Ready | FPS: 0 | Detected: None")
        self.status_label = ctk.CTkLabel(self.main_frame, textvariable=self.status_var, font=ctk.CTkFont(size=12))
        self.status_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.running = True
        self.app_core.request_close_all = False
        self.update_video()

    def confirm_close_all(self):
        import tkinter.messagebox as messagebox
        response = messagebox.askyesno("Confirm Close", "Are you sure you want to close ALL applications?")
        if response:
            import threading
            threading.Thread(target=self.app_core.system.close_all_apps_gracefully, daemon=True).start()
        self.app_core.request_close_all = False

    def change_mode(self):
        mode = self.mode_var.get()
        self.app_core.config.set("general", "mode", mode)
        self.app_core.current_mode = mode
        logger.info(f"Mode changed to: {mode}")

    def change_sensitivity(self, value):
        self.app_core.config.set("sensitivity", "mouse_smoothness", int(value))
        self.app_core.mouse.smoothness = int(value)

    def update_video(self):
        if not self.running:
            return
            
        frame = self.app_core.get_processed_frame()
        if frame is not None:
            # Resize for UI
            frame_resized = cv2.resize(frame, (640, 480))
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ctk.CTkImage(light_image=img, dark_image=img, size=(640, 480))
            self.video_label.configure(image=imgtk)
            self.video_label.image = imgtk
            
            # Update status
            fps = self.app_core.current_fps
            gesture = self.app_core.current_gesture
            self.status_var.set(f"Status: Active | FPS: {fps:.1f} | Gesture: {gesture}")

        if hasattr(self.app_core, 'request_close_all') and self.app_core.request_close_all:
            self.confirm_close_all()

        self.after(30, self.update_video)

    def on_closing(self):
        self.running = False
        self.app_core.stop()
        self.destroy()
