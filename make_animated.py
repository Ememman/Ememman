#!/usr/bin/env python3
"""
Turns assets/luffy.png and assets/piccolo.png into animated SVGs that
GitHub will animate inside a README (<img src="assets/xxx-animated.svg">).

Usage (from your repo root, Python 3, no dependencies):
    python make_animated.py

Tip: keep each PNG under ~500 KB, since it gets embedded as base64.
"""
import base64
import struct
from pathlib import Path

ASSETS = Path("assets")


def png_size(data: bytes):
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG file")
    return struct.unpack(">II", data[16:24])


def build_svg(png_path: Path, style: str) -> str:
    data = png_path.read_bytes()
    w, h = png_size(data)
    b64 = base64.b64encode(data).decode()

    pad_top = int(h * 0.12)
    pad_bottom = int(h * 0.12)
    total_h = h + pad_top + pad_bottom
    amp = int(h * 0.05)  # movement amplitude

    if style == "bounce":  # Luffy: energetic rubbery bounce
        css = f"""
        .shadow {{ transform-box: fill-box; transform-origin: center; animation: shadow 1.2s ease-in-out infinite; }}
        .hero   {{ transform-box: fill-box; transform-origin: 50% 100%; animation: bounce 1.2s ease-in-out infinite; }}
        @keyframes bounce {{
          0%,100% {{ transform: translateY(0) scale(1.03, 0.97); }}
          50%     {{ transform: translateY(-{amp * 2}px) scale(0.98, 1.03); }}
        }}
        @keyframes shadow {{
          0%,100% {{ transform: scale(1);   opacity: .35; }}
          50%     {{ transform: scale(.7);  opacity: .15; }}
        }}"""
        aura = ""
    else:  # Piccolo: calm levitation + pulsing aura
        css = f"""
        .shadow {{ transform-box: fill-box; transform-origin: center; animation: shadow 4s ease-in-out infinite; }}
        .hero   {{ transform-box: fill-box; transform-origin: center; animation: float 4s ease-in-out infinite; }}
        .aura   {{ transform-box: fill-box; transform-origin: center; animation: aura 4s ease-in-out infinite; }}
        @keyframes float {{
          0%,100% {{ transform: translateY(0) rotate(-1deg); }}
          50%     {{ transform: translateY(-{amp * 2}px) rotate(1deg); }}
        }}
        @keyframes shadow {{
          0%,100% {{ transform: scale(1);   opacity: .35; }}
          50%     {{ transform: scale(.75); opacity: .15; }}
        }}
        @keyframes aura {{
          0%,100% {{ opacity: .15; transform: scale(.95); }}
          50%     {{ opacity: .45; transform: scale(1.08); }}
        }}"""
        aura = (
            f'<ellipse class="aura" cx="{w/2}" cy="{pad_top + h/2}" '
            f'rx="{w*0.48}" ry="{h*0.48}" fill="url(#glow)"/>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="0 0 {w} {total_h}" width="{w}" height="{total_h}">
  <defs>
    <radialGradient id="glow">
      <stop offset="0%"  stop-color="#7CFC8A" stop-opacity="0.9"/>
      <stop offset="100%" stop-color="#7CFC8A" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <style>{css}
  </style>
  {aura}
  <ellipse class="shadow" cx="{w/2}" cy="{total_h - pad_bottom/2}" rx="{w*0.3}" ry="{pad_bottom*0.25}" fill="#000"/>
  <image class="hero" x="0" y="{pad_top}" width="{w}" height="{h}"
         href="data:image/png;base64,{b64}"
         xlink:href="data:image/png;base64,{b64}"/>
</svg>
"""


def main():
    jobs = [("luffy", "bounce"), ("piccolo", "float")]
    for name, style in jobs:
        src = ASSETS / f"{name}.png"
        if not src.exists():
            print(f"Skipping {name}: {src} not found")
            continue
        out = ASSETS / f"{name}-animated.svg"
        out.write_text(build_svg(src, style), encoding="utf-8")
        print(f"Created {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
