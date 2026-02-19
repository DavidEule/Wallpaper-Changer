import os
import sys
import struct
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

try:
    import winreg
    import ctypes
    from ctypes import wintypes
except ImportError:
    winreg = None
    ctypes = None

REG_PATH = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"

# Policy styles (REG_SZ)
WALLPAPER_STYLES = {
    "Center": ("0", "0"),
    "Tile": ("1", "1"),
    "Stretch": ("2", "0"),
    "Fit": ("6", "0"),
    "Fill": ("10", "0"),
    "Span (multi-monitor)": ("22", "0"),
}

SPI_SETDESKWALLPAPER = 20
SPIF_UPDATEINIFILE = 0x01
SPIF_SENDCHANGE = 0x02


def is_windows() -> bool:
    return sys.platform.startswith("win")


def python_bitness() -> int:
    # 32 or 64
    return struct.calcsize("P") * 8


def normalize_path(path: str) -> str:
    path = os.path.expandvars(path)
    path = os.path.expanduser(path)
    return os.path.abspath(path)


def browse_wallpaper():
    file_path = filedialog.askopenfilename(
        title="Select Wallpaper",
        filetypes=[
            ("Image Files", "*.jpg *.jpeg *.png *.bmp *.gif"),
            ("All Files", "*.*"),
        ],
    )
    if file_path:
        wallpaper_var.set(normalize_path(file_path))
        status_var.set("Wallpaper selected. Choose a style and click Apply.")


def apply_wallpaper_now(path: str) -> tuple[bool, str]:
    """Apply wallpaper immediately using SystemParametersInfoW (no rundll32)."""
    try:
        user32 = ctypes.windll.user32
        SystemParametersInfoW = user32.SystemParametersInfoW
        SystemParametersInfoW.argtypes = [wintypes.UINT, wintypes.UINT, wintypes.LPCWSTR, wintypes.UINT]
        SystemParametersInfoW.restype = wintypes.BOOL

        ok = SystemParametersInfoW(
            SPI_SETDESKWALLPAPER,
            0,
            path,
            SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        if not ok:
            return False, "SystemParametersInfoW returned failure."
        return True, "Applied immediately via SystemParametersInfoW."
    except Exception as e:
        return False, f"Immediate apply failed: {e}"


def write_policy_values(view_flag: int, wallpaper: str, style: str, tile: str) -> dict:
    """
    Write values to a specific registry view (32-bit or 64-bit) using WOW64 flags.
    Returns the values read back for verification.
    """
    access = winreg.KEY_SET_VALUE | winreg.KEY_QUERY_VALUE | view_flag
    key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, REG_PATH, 0, access)

    # Required keys
    winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, wallpaper)
    winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, style)

    # Often needed for Tile mode; harmless otherwise
    winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, tile)

    # Read back to prove the write happened
    result = {}
    for name in ("Wallpaper", "WallpaperStyle", "TileWallpaper"):
        try:
            result[name] = winreg.QueryValueEx(key, name)[0]
        except FileNotFoundError:
            result[name] = None

    winreg.CloseKey(key)
    return result


def set_wallpaper():
    if not is_windows() or winreg is None or ctypes is None:
        messagebox.showerror("Unsupported OS", "This script only works on Windows.")
        return

    wallpaper = wallpaper_var.get().strip()
    style_name = style_var.get().strip()

    if not wallpaper:
        messagebox.showerror("Error", "Please select a wallpaper file.")
        return

    wallpaper = normalize_path(wallpaper)
    wallpaper_var.set(wallpaper)

    if not os.path.isfile(wallpaper):
        messagebox.showerror("Error", f"Wallpaper file not found:\n{wallpaper}")
        return

    if style_name not in WALLPAPER_STYLES:
        messagebox.showerror("Error", "Please select a wallpaper style.")
        return

    style_value, tile_value = WALLPAPER_STYLES[style_name]

    try:
        # Write to 64-bit view (this is the key fix for 32-bit Python issues)
        written_64 = write_policy_values(winreg.KEY_WOW64_64KEY, wallpaper, style_value, tile_value)

        # Also write to 32-bit view for completeness (optional, but safe)
        written_32 = write_policy_values(winreg.KEY_WOW64_32KEY, wallpaper, style_value, tile_value)

    except PermissionError:
        messagebox.showerror(
            "Permission denied",
            "Registry write failed due to permissions.\n"
            "Try running from an elevated terminal (Admin) under the SAME user session."
        )
        return
    except Exception as e:
        messagebox.showerror("Registry error", f"Failed to write registry values:\n{e}")
        return

    # Apply immediately
    ok, msg = apply_wallpaper_now(wallpaper)

    # Show verification info so you can confirm it actually wrote where Windows reads
    bitness = python_bitness()
    verification = (
        f"Python bitness: {bitness}-bit\n\n"
        f"64-bit view readback:\n"
        f"  Wallpaper      = {written_64.get('Wallpaper')}\n"
        f"  WallpaperStyle = {written_64.get('WallpaperStyle')}\n"
        f"  TileWallpaper  = {written_64.get('TileWallpaper')}\n\n"
        f"32-bit view readback:\n"
        f"  Wallpaper      = {written_32.get('Wallpaper')}\n"
        f"  WallpaperStyle = {written_32.get('WallpaperStyle')}\n"
        f"  TileWallpaper  = {written_32.get('TileWallpaper')}\n\n"
        f"Apply result: {msg}"
    )

    status_var.set(msg)

    if ok:
        messagebox.showinfo("Success", f"Policy values set and wallpaper applied.\n\n{verification}")
    else:
        messagebox.showwarning("Policy set (apply uncertain)", f"Values were set.\n\n{verification}")


# ---------------- GUI ----------------

root = tk.Tk()
root.title("Wallpaper Policy Setter (HKCU Policies\\System)")
root.resizable(False, False)
root.configure(padx=10, pady=10)

wallpaper_var = tk.StringVar()
style_var = tk.StringVar(value="Stretch")
status_var = tk.StringVar(value="Select a wallpaper file to begin.")

tk.Label(root, text="Wallpaper File:").grid(row=0, column=0, sticky="w", pady=(0, 6))
tk.Entry(root, textvariable=wallpaper_var, width=52).grid(row=0, column=1, padx=(6, 6), pady=(0, 6), sticky="w")
tk.Button(root, text="Browse...", command=browse_wallpaper).grid(row=0, column=2, pady=(0, 6))

tk.Label(root, text="Wallpaper Style:").grid(row=1, column=0, sticky="w", pady=(0, 6))
style_dropdown = ttk.Combobox(
    root,
    textvariable=style_var,
    values=list(WALLPAPER_STYLES.keys()),
    state="readonly",
    width=49,
)
style_dropdown.grid(row=1, column=1, columnspan=2, padx=(6, 0), pady=(0, 6), sticky="w")
style_dropdown.set("Stretch")

tk.Button(root, text="Apply Wallpaper", command=set_wallpaper, width=20).grid(
    row=2, column=0, columnspan=3, pady=(6, 6)
)

tk.Label(root, textvariable=status_var, fg="#444").grid(row=3, column=0, columnspan=3, sticky="w")

if not is_windows():
    messagebox.showerror("Unsupported OS", "This script only works on Windows.")
    root.destroy()
else:
    root.mainloop()
