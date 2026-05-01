# Breathing Pet 🐾

> A quiet little pet that sits in the corner of your desktop and breathes at your pace.
> It won't remind you, won't pop up, won't interrupt — it just breathes, keeping you company while you work.

![demo](assets/demo.gif)

## Why this exists

There's a phenomenon called **Screen Apnea** — when staring at screens, our breathing involuntarily becomes shallow, rapid, and sometimes stops entirely. About 80% of computer workers have this, but most don't notice.

I noticed it in myself — coding, in meetings, reviewing designs — moments where I'd suddenly realize my chest was tight, shoulders locked, breath shallow and quick. I wanted something **that wouldn't interrupt me, but would gently remind me to breathe**.

So I made this little pet. It lives in the corner of your screen, breathing once every 5 seconds (2s inhale, 3s exhale). Watching it breathe, your own breath naturally syncs up — passive, gentle entrainment.

When you need active practice, triple-click to enter a guided 4-4-6-2 breathing session.

## Features

- 🌿 **Natural breathing rhythm** — 2s inhale (ease-in) + 3s exhale (ease-out), asymmetric easing mimics real breathing
- 🧘 **Guided training mode** — Triple-click to enter: 4s inhale → 4s hold → 6s exhale → 2s pause, 6 cycles
- 🎨 **15 emoji pets + 8 Morandi color tones** — Auto-rotate or manually switch
- 👻 **Fully passive** — No popups, no notifications, no interruptions
- 🐧 **Cross-platform** — Windows / macOS / Linux
- 🪶 **Zero dependencies** — Python standard library only

## Requirements

- Python 3.8+
- Linux users need tkinter: `sudo apt install python3-tk` (built-in on macOS / Windows)

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/breathing-pet.git
cd breathing-pet
python breathing_pet.py
```

Or use the launcher scripts:

- **macOS / Linux**: `./breathing_pet.sh`
- **Windows**: double-click `breathing_pet.bat`

On first run, a `config.json` is auto-generated in the same directory. Edit it and restart to customize.

## Controls

| Action | Effect |
|--------|--------|
| Drag | Move the pet (position is remembered) |
| Double-click | Switch to next pet |
| Triple-click | Enter / exit breathing training mode |
| Right-click | Open menu (change pet / color / quit) |

## Configuration

Edit `config.json`:

```json
{
  "pet": {
    "skin_type": "emoji",
    "emoji_list": ["🐱", "🐶", "🐼", "🦄", "🐧"],
    "skin_rotate_minutes": 30,
    "window_size": [120, 120],
    "emoji_font_size": 64,
    "breath_inhale_ms": 2000,
    "breath_exhale_ms": 3000,
    "pet_color": "莫兰迪粉",
    "position": [100, 100]
  },
  "bubble": {
    "duration_seconds": 8,
    "font_size": 11,
    "max_width": 200
  }
}
```

### Available colors

| Key | Description |
|-----|-------------|
| `纯白` | Pure white |
| `莫兰迪灰` | Morandi gray |
| `莫兰迪粉` | Morandi pink |
| `鼠尾草绿` | Sage green |
| `薰衣草紫` | Lavender |
| `雾蓝` | Misty blue |
| `奶油黄` | Cream yellow |
| `淡灰绿` | Pale gray-green |

### Adjust breathing rhythm

Research shows **exhales longer than inhales** activate the parasympathetic nervous system, reducing anxiety:

| Purpose | Inhale | Exhale | Rate |
|---------|--------|--------|------|
| Default companion | 2s | 3s | 12 / min |
| Light relaxation | 4s | 6s | 6 / min |
| Deep relaxation | 5s | 7s | 5 / min |

Modify `breath_inhale_ms` and `breath_exhale_ms` in `config.json`.

## Training Mode

Triple-click the pet to enter:

```
  Inhale 4s ──→ Hold 4s ──→ Exhale 6s ──→ Pause 2s
  100%→140%    stay 140%   140%→100%    stay 100%
   light blue  light blue   normal       normal

                  × 6 cycles (~96 seconds)
```

Click the pet again during training to exit early. Returns to normal companion mode after.

## Roadmap

- [ ] System tray icon, minimize to tray
- [ ] Custom training rhythm presets (4-7-8, Box Breathing, etc.)
- [ ] Auto-hide when fullscreen apps detected
- [ ] Custom image skins (beyond emoji)
- [ ] macOS / Windows installers
- [ ] Multi-language support (English / 日本語)

Suggestions and contributions welcome via issues.

## Contributing

This is a 100% open-source, forever-free project.

Whether it's:

- Filing an issue to report bugs
- Sharing your use case in discussions
- Submitting a PR for new features
- Translating copy
- Designing new emoji lists / color palettes

All contributions are warmly welcomed.

## License

[MIT License](LICENSE) — free to use, modify, and distribute. Please retain the copyright notice.

## Read in other languages

- [简体中文](README.md)

---

If you also have those moments where you suddenly realize you can't breathe properly, share your story in the issues. I'd love to hear it.
