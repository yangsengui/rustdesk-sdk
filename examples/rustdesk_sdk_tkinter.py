import ctypes
import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# Default to the release DLL path under this repo
DEFAULT_DLL = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    "..",
    "target",
    "release",
    "rustdesk_sdk.dll",
))

class RustDeskSdk:
    def __init__(self, dll_path):
        self._dll = None
        self._dll_path = dll_path

    def load(self):
        if not os.path.exists(self._dll_path):
            raise FileNotFoundError(self._dll_path)
        self._dll = ctypes.CDLL(self._dll_path)

        # bool rd_global_init()
        self._dll.rd_global_init.restype = ctypes.c_bool

        # bool rd_is_cm()
        self._dll.rd_is_cm.restype = ctypes.c_bool

        # bool rd_start_server(bool is_server, bool no_server)
        self._dll.rd_start_server.argtypes = [ctypes.c_bool, ctypes.c_bool]
        self._dll.rd_start_server.restype = ctypes.c_bool

        # bool rd_start_server_safe()
        self._dll.rd_start_server_safe.restype = ctypes.c_bool

        # bool rd_stop_server()
        self._dll.rd_stop_server.restype = ctypes.c_bool

        # bool rd_is_server_running()
        self._dll.rd_is_server_running.restype = ctypes.c_bool

        # char* rd_get_id()
        self._dll.rd_get_id.restype = ctypes.c_void_p

        # char* rd_get_temporary_password()
        self._dll.rd_get_temporary_password.restype = ctypes.c_void_p

        # void rd_free_c_string(char* s)
        self._dll.rd_free_c_string.argtypes = [ctypes.c_void_p]
        self._dll.rd_free_c_string.restype = None

    def _read_c_string(self, ptr):
        if not ptr:
            return ""
        s = ctypes.c_char_p(ptr).value
        try:
            return s.decode("utf-8") if s else ""
        finally:
            self._dll.rd_free_c_string(ptr)

    def global_init(self):
        return self._dll.rd_global_init()

    def is_cm(self):
        return self._dll.rd_is_cm()

    def start_server(self, is_server, no_server):
        return self._dll.rd_start_server(is_server, no_server)

    def start_server_safe(self):
        return self._dll.rd_start_server_safe()

    def stop_server(self):
        return self._dll.rd_stop_server()

    def is_server_running(self):
        return self._dll.rd_is_server_running()

    def get_id(self):
        return self._read_c_string(self._dll.rd_get_id())

    def get_temp_password(self):
        return self._read_c_string(self._dll.rd_get_temporary_password())

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RustDesk SDK (DLL) Tkinter Test")
        self.geometry("560x420")
        self.resizable(False, False)

        self.sdk = None
        self.dll_path = tk.StringVar(value=DEFAULT_DLL)
        self.status = tk.StringVar(value="Not loaded")
        self.server_status = tk.StringVar(value="Unknown")
        self.id_value = tk.StringVar(value="")
        self.pw_value = tk.StringVar(value="")

        self._build_ui()

    def _build_ui(self):
        frm = tk.Frame(self, padx=12, pady=12)
        frm.pack(fill=tk.BOTH, expand=True)
        frm.columnconfigure(0, weight=1)

        dll_box = tk.LabelFrame(frm, text="DLL", padx=10, pady=8)
        dll_box.grid(row=0, column=0, sticky="ew")
        dll_box.columnconfigure(1, weight=1)

        tk.Label(dll_box, text="Path").grid(row=0, column=0, sticky="w")
        tk.Entry(dll_box, textvariable=self.dll_path, width=56).grid(row=0, column=1, sticky="ew")
        tk.Button(dll_box, text="Browse", command=self.on_browse).grid(row=0, column=2, padx=6)

        tk.Button(dll_box, text="Load DLL", command=self.on_load).grid(row=1, column=0, pady=6, sticky="w")
        tk.Label(dll_box, textvariable=self.status, fg="#1a7f37").grid(row=1, column=1, sticky="w")

        core_box = tk.LabelFrame(frm, text="Core", padx=10, pady=8)
        core_box.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        core_box.columnconfigure(0, weight=1)
        core_box.columnconfigure(1, weight=1)

        tk.Button(core_box, text="Global Init", command=self.on_global_init).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        tk.Button(core_box, text="Is CM?", command=self.on_is_cm).grid(row=0, column=1, sticky="ew", pady=4)

        server_box = tk.LabelFrame(frm, text="Server", padx=10, pady=8)
        server_box.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        server_box.columnconfigure(0, weight=1)
        server_box.columnconfigure(1, weight=1)
        server_box.columnconfigure(2, weight=1)

        tk.Button(
            server_box,
            text="Start (Safe)",
            command=self.on_start_server_safe,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6), pady=4)
        tk.Button(
            server_box,
            text="Start (Force is_server=true)",
            command=self.on_start_server_force,
        ).grid(row=0, column=1, sticky="ew", padx=(0, 6), pady=4)
        tk.Button(
            server_box,
            text="Stop",
            command=self.on_stop_server,
        ).grid(row=0, column=2, sticky="ew", pady=4)

        tk.Button(
            server_box,
            text="Check Running",
            command=self.on_check_server_running,
        ).grid(row=1, column=0, sticky="ew", padx=(0, 6), pady=4)
        tk.Label(server_box, text="Running:").grid(row=1, column=1, sticky="e")
        tk.Label(server_box, textvariable=self.server_status).grid(row=1, column=2, sticky="w")

        info_box = tk.LabelFrame(frm, text="Info", padx=10, pady=8)
        info_box.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        info_box.columnconfigure(1, weight=1)

        tk.Button(info_box, text="Get ID", command=self.on_get_id).grid(row=0, column=0, sticky="w", pady=4)
        tk.Entry(info_box, textvariable=self.id_value, width=56).grid(row=0, column=1, sticky="ew")

        tk.Button(info_box, text="Get Temp Password", command=self.on_get_pw).grid(row=1, column=0, sticky="w", pady=4)
        tk.Entry(info_box, textvariable=self.pw_value, width=56).grid(row=1, column=1, sticky="ew")

        note = tk.Label(frm, text="Note: Run in same architecture as DLL (x64).", fg="#555")
        note.grid(row=4, column=0, sticky="w", pady=(10, 0))

    def on_browse(self):
        path = filedialog.askopenfilename(title="Select rustdesk_sdk.dll", filetypes=[("DLL", "*.dll")])
        if path:
            self.dll_path.set(path)

    def on_load(self):
        try:
            self.sdk = RustDeskSdk(self.dll_path.get())
            self.sdk.load()
            self.status.set("Loaded")
        except Exception as e:
            messagebox.showerror("Load failed", str(e))
            self.status.set("Not loaded")
            self.sdk = None

    def _require_sdk(self):
        if not self.sdk:
            messagebox.showwarning("Not loaded", "Please load the DLL first.")
            return False
        return True

    def on_global_init(self):
        if not self._require_sdk():
            return
        ok = self.sdk.global_init()
        messagebox.showinfo("Global Init", f"global_init => {ok}")

    def on_is_cm(self):
        if not self._require_sdk():
            return
        ok = self.sdk.is_cm()
        messagebox.showinfo("Is CM", f"is_cm => {ok}")

    def on_start_server_safe(self):
        if not self._require_sdk():
            return
        # Call in a worker to keep UI responsive
        threading.Thread(target=lambda: self.sdk.start_server_safe(), daemon=True).start()
        messagebox.showinfo("Start Server", "start_server_safe() dispatched")
        self.server_status.set("Starting...")

    def on_start_server_force(self):
        if not self._require_sdk():
            return
        threading.Thread(target=lambda: self.sdk.start_server(True, False), daemon=True).start()
        messagebox.showinfo("Start Server", "start_server(true, false) dispatched")
        self.server_status.set("Starting...")

    def on_stop_server(self):
        if not self._require_sdk():
            return
        ok = self.sdk.stop_server()
        self.server_status.set("Stopped" if ok else "Unknown")

    def on_check_server_running(self):
        if not self._require_sdk():
            return
        self.server_status.set("Yes" if self.sdk.is_server_running() else "No")

    def on_get_id(self):
        if not self._require_sdk():
            return
        self.id_value.set(self.sdk.get_id())

    def on_get_pw(self):
        if not self._require_sdk():
            return
        self.pw_value.set(self.sdk.get_temp_password())

if __name__ == "__main__":
    if sys.platform != "win32":
        print("This example is intended for Windows.")
    App().mainloop()
