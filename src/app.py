import os
import sys
import tempfile
import customtkinter as ctk
from PIL import Image

from src.core.activity import ActivityEngine


class AntiIdleApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Assistente Anti-Idle")
        self.root.geometry("500x580")
        self.root.minsize(460, 500)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self._set_icon()

        self.engine = ActivityEngine()

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _set_icon(self):
        try:
            bundle_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            ico = os.path.join(bundle_dir, "resources", "app_icon.ico")
            if not os.path.exists(ico):
                ico = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resources", "app_icon.ico")
            if not os.path.exists(ico):
                return

            if os.name == "nt":
                self.root.iconbitmap(ico)
                return

            from tkinter import PhotoImage
            img = Image.open(ico).resize((32, 32), Image.Resampling.LANCZOS)
            tmp = os.path.join(tempfile.gettempdir(), "assist-anti-idle-icon.png")
            img.save(tmp, "PNG")
            self._icon_img = PhotoImage(file=tmp)
            self.root.tk.call('wm', 'iconphoto', self.root._w, '-default', self._icon_img)
        except Exception:
            pass

    def _build_ui(self):
        main = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            main, text="Assistente Anti-Idle",
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
        ).pack(fill="x", pady=(0, 6))

        self.status_label = ctk.CTkLabel(
            main, text="Status: Inativo", anchor="w",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.pack(fill="x", pady=(0, 15))

        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 15))

        self.start_btn = ctk.CTkButton(
            btn_frame, text="Iniciar", command=self.start_activity,
            width=150, height=32,
        )
        self.start_btn.pack(side="left", padx=(0, 10))

        self.stop_btn = ctk.CTkButton(
            btn_frame, text="Parar", command=self.stop_activity,
            width=150, height=32, state="disabled", fg_color="#555",
        )
        self.stop_btn.pack(side="left")

        self._build_config(main)

    def _build_config(self, parent):
        cfg = ctk.CTkFrame(parent)
        cfg.pack(fill="x")

        ctk.CTkLabel(
            cfg, text="Configurações",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(12, 10))

        interval_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        interval_frame.pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(interval_frame, text="Intervalo entre ações:").pack(side="left")
        self.interval_var = ctk.StringVar(value="60")
        ctk.CTkEntry(interval_frame, textvariable=self.interval_var, width=80).pack(side="left", padx=(12, 6))
        ctk.CTkLabel(interval_frame, text="segundos").pack(side="left")

        self.caps_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cfg, text="Alternar Caps Lock", variable=self.caps_var).pack(anchor="w", padx=18, pady=6)

        self.keys_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(cfg, text="Simular pressionamento de teclas", variable=self.keys_var).pack(anchor="w", padx=18, pady=6)

        keys_sub = ctk.CTkFrame(cfg, fg_color="transparent")
        keys_sub.pack(fill="x", padx=(40, 0))

        self.key_f15 = ctk.BooleanVar(value=True)
        self.key_shift = ctk.BooleanVar(value=True)
        self.key_alt = ctk.BooleanVar(value=True)
        self.key_ctrl = ctk.BooleanVar(value=False)

        ctk.CTkCheckBox(keys_sub, text="F15", variable=self.key_f15).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(keys_sub, text="Shift", variable=self.key_shift).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(keys_sub, text="Alt", variable=self.key_alt).pack(anchor="w", pady=3)
        ctk.CTkCheckBox(keys_sub, text="Ctrl", variable=self.key_ctrl).pack(anchor="w", pady=3)

        hold_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        hold_frame.pack(fill="x", padx=18, pady=10)
        ctk.CTkLabel(hold_frame, text="Tempo segurando tecla:").pack(side="left")
        self.hold_var = ctk.StringVar(value="0.1")
        ctk.CTkEntry(hold_frame, textvariable=self.hold_var, width=60).pack(side="left", padx=(12, 6))
        ctk.CTkLabel(hold_frame, text="segundos").pack(side="left")

        ctk.CTkFrame(cfg, fg_color="#333", height=1).pack(fill="x", padx=18, pady=12)

        self.mouse_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(cfg, text="Mouse jiggler (movimento sutil)", variable=self.mouse_var).pack(anchor="w", padx=18, pady=6)

        jiggle_amt_frame = ctk.CTkFrame(cfg, fg_color="transparent")
        jiggle_amt_frame.pack(fill="x", padx=18, pady=(2, 8))
        ctk.CTkLabel(jiggle_amt_frame, text="Intensidade do movimento:").pack(side="left")
        self.jiggle_amt_var = ctk.StringVar(value="3")
        ctk.CTkEntry(jiggle_amt_frame, textvariable=self.jiggle_amt_var, width=60).pack(side="left", padx=(12, 6))
        ctk.CTkLabel(jiggle_amt_frame, text="pixels").pack(side="left")

        ctk.CTkLabel(cfg, text="").pack(pady=(0, 12))

    def _collect_config(self) -> dict:
        try:
            interval = int(self.interval_var.get())
        except ValueError:
            interval = 60
        try:
            hold = float(self.hold_var.get())
        except ValueError:
            hold = 0.1
        try:
            jiggle_amt = int(self.jiggle_amt_var.get())
        except ValueError:
            jiggle_amt = 3

        return {
            "interval": interval,
            "caps_lock": self.caps_var.get(),
            "key_press": self.keys_var.get(),
            "keys": {
                "f15": self.key_f15.get(),
                "shift": self.key_shift.get(),
                "alt": self.key_alt.get(),
                "ctrl": self.key_ctrl.get(),
            },
            "hold_time": hold,
            "mouse_jiggle": self.mouse_var.get(),
            "jiggle_amount": jiggle_amt,
        }

    def _update_ui_state(self, running: bool):
        state = "disabled" if running else "normal"
        self.start_btn.configure(state=state)
        self.stop_btn.configure(state="normal" if running else "disabled",
                                fg_color="#c0392b" if running else "#555",
                                hover_color="#e74c3c" if running else "#666")
        self.status_label.configure(
            text=f"Status: {'Ativo' if running else 'Inativo'}",
            text_color=("#00c853" if running else "#ff5252"),
        )

    def start_activity(self):
        self.engine.start(self._collect_config())
        self._update_ui_state(True)

    def stop_activity(self):
        self.engine.stop()
        self._update_ui_state(False)

    def on_close(self):
        self.engine.stop()
        self.root.destroy()

    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.on_close()
