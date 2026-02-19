# Vibecoded – Wallpaper Policy Setter (Windows)

Ein kleines Windows-Tool (Python + Tkinter), das ein Desktop-Hintergrundbild **per Registry-Policy** setzt und anschließend **sofort** anwendet.

> Registry-Pfad: `HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System`

---

## ✨ Features
- GUI zum Auswählen einer Bilddatei (JPG/PNG/BMP/GIF/…)
- Wallpaper-Styles: **Center, Tile, Stretch, Fit, Fill, Span (multi-monitor)**
- Schreibt Policy-Werte in **HKCU Policies\\System**:
  - `Wallpaper` (Pfad)
  - `WallpaperStyle` (Style)
  - `TileWallpaper` (Tile-Flag)
- Kompatibilitäts-Fix: schreibt in **64‑bit UND 32‑bit Registry-View** (WOW64)
- Wendet das Wallpaper direkt via **SystemParametersInfoW** an (ohne `rundll32`).

---

## 📁 Dateien
- `wallpaper.py` – Hauptskript (GUI + Registry/Apply)
- `executesysadmin.cmd.txt` – CMD-Launcher, der `wallpaper.py` **elevated** startet (UAC)

> Tipp: Benenne `executesysadmin.cmd.txt` um in z. B. **`Run-Wallpaper-Admin.cmd`** und lege die Datei in denselben Ordner wie `wallpaper.py`.

---

## ✅ Voraussetzungen
- Windows
- Python 3 (Tkinter ist bei Standard-Windows-Python i. d. R. enthalten)

---

## 🚀 Nutzung

### Variante A: Normal starten

```powershell
py -3 wallpaper.py
# oder
python wallpaper.py
```

### Variante B: Mit Admin-Rechten (UAC)

Doppelklick auf **`Run-Wallpaper-Admin.cmd`** (umbenannte `executesysadmin.cmd.txt`).  
Der Launcher startet Python im Script-Ordner und fordert Admin-Rechte an.

---

## 🛠 Troubleshooting

- **Unsupported OS**: Das Tool läuft nur unter Windows.
- **Permission denied** beim Registry-Write:
  - Nutze den Admin-Launcher (UAC) bzw. starte eine Konsole **als Admin**.
- Wenn das Wallpaper nicht sofort wechselt:
  - Die Policy-Werte wurden gesetzt; ab-/anmelden oder Explorer neu starten kann helfen.

---

## 📜 Lizenz (MIT)

MIT ist gesetzt ✅ — bitte lege eine Datei **`LICENSE`** mit dem MIT-Lizenztext ins Repo und ergänze darin die Copyright-Zeile.

---

## 🤝 Contributing

Issues und Pull Requests sind willkommen. Bitte beschreibe:
- Windows-Version
- Python-Version (`python --version`)
- Repro-Schritte

---

## 📌 Hinweis

Dieses Tool schreibt in eine Policy-Registry-Location. Nutze es verantwortungsvoll, besonders in verwalteten Umgebungen.
