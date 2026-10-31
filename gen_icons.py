#!/usr/bin/env python3
"""
產生「韓味屋」PWA 所需的各尺寸圖示（PNG）。

使用方式：
    pip install pillow
    python gen_icons.py

會在同一層的 icons/ 資料夾輸出：
    icon-72x72 ~ icon-512x512.png   （一般圖示，圓角）
    maskable-192x192 / 512x512.png  （Maskable，滿版背景，主體在安全區內）
    apple-touch-icon.png (180x180)  （iOS 主畫面圖示）
    favicon-32x32.png
"""
from pathlib import Path
from PIL import Image, ImageDraw

RED = (229, 62, 62, 255)        # koreanRed #E53E3E
DARK = (26, 32, 44, 255)        # koreanDark #1A202C
GOLD = (214, 158, 46, 255)      # koreanGold #D69E2E
WHITE = (255, 255, 255, 255)

SS = 4  # 超取樣倍率，讓邊緣更平滑

OUT_DIR = Path(__file__).resolve().parent / "icons"
SIZES = [72, 96, 128, 144, 152, 192, 384, 512]


def draw_bowl(draw: ImageDraw.ImageDraw, size: int, scale: float = 1.0):
    """在 size x size 的畫布中央畫一個韓式石鍋碗 + 蒸氣 + 筷子。
    scale 用來縮小主體（maskable 需要保留安全區）。"""
    cx = size / 2
    unit = size * scale

    # 碗身（半圓）
    bowl_w = unit * 0.56
    bowl_h = unit * 0.28
    top = size / 2 + unit * 0.02
    draw.pieslice(
        [cx - bowl_w / 2, top - bowl_h, cx + bowl_w / 2, top + bowl_h],
        start=0, end=180, fill=WHITE,
    )
    # 碗口橫條
    rim_h = unit * 0.045
    draw.rounded_rectangle(
        [cx - bowl_w / 2 - unit * 0.02, top - rim_h / 2,
         cx + bowl_w / 2 + unit * 0.02, top + rim_h / 2],
        radius=rim_h / 2, fill=WHITE,
    )
    # 碗底座
    base_w = unit * 0.24
    base_h = unit * 0.05
    draw.rounded_rectangle(
        [cx - base_w / 2, top + bowl_h - base_h * 0.2,
         cx + base_w / 2, top + bowl_h + base_h],
        radius=base_h / 2, fill=WHITE,
    )
    # 碗內金色裝飾條
    stripe_y = top + bowl_h * 0.35
    draw.arc(
        [cx - bowl_w * 0.36, stripe_y - bowl_h * 0.55, cx + bowl_w * 0.36, stripe_y + bowl_h * 0.55],
        start=15, end=165, fill=GOLD, width=max(2, int(unit * 0.025)),
    )

    # 蒸氣（三條波浪線，用多段弧線近似）
    steam_w = max(2, int(unit * 0.03))
    import math
    for dx in (-0.12, 0.0, 0.12):
        x = cx + unit * dx
        y_start = top - unit * 0.32
        y_end = top - unit * 0.10
        pts = []
        steps = 40
        for k in range(steps + 1):
            t = k / steps
            y = y_start + (y_end - y_start) * t
            px = x + math.sin(t * math.pi * 2) * unit * 0.025
            pts.append((px, y))
        draw.line(pts, fill=WHITE, width=steam_w, joint="curve")
        r = steam_w / 2
        for (px, py) in (pts[0], pts[-1]):
            draw.ellipse([px - r, py - r, px + r, py + r], fill=WHITE)

    # 筷子（斜放兩根）
    chop_w = max(2, int(unit * 0.022))
    draw.line(
        [cx + unit * 0.05, top - unit * 0.02, cx + unit * 0.30, top - unit * 0.24],
        fill=GOLD, width=chop_w,
    )
    draw.line(
        [cx + unit * 0.10, top - unit * 0.02, cx + unit * 0.34, top - unit * 0.20],
        fill=GOLD, width=chop_w,
    )


def make_icon(size: int, maskable: bool = False) -> Image.Image:
    big = size * SS
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    if maskable:
        # 滿版背景；主體縮到 ~60%，落在中心 80% 安全區內
        d.rectangle([0, 0, big, big], fill=RED)
        draw_bowl(d, big, scale=0.78)
    else:
        radius = int(big * 0.22)
        d.rounded_rectangle([0, 0, big - 1, big - 1], radius=radius, fill=RED)
        # 上方柔和高光
        glow = Image.new("RGBA", (big, big), (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.ellipse([-big * 0.2, -big * 0.6, big * 1.2, big * 0.45], fill=(255, 255, 255, 28))
        mask = Image.new("L", (big, big), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, big - 1, big - 1], radius=radius, fill=255)
        img = Image.composite(Image.alpha_composite(img, glow), img, mask)
        d = ImageDraw.Draw(img)
        draw_bowl(d, big, scale=1.0)

    return img.resize((size, size), Image.LANCZOS)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for s in SIZES:
        make_icon(s).save(OUT_DIR / f"icon-{s}x{s}.png", optimize=True)
        print(f"✔ icons/icon-{s}x{s}.png")

    for s in (192, 512):
        make_icon(s, maskable=True).save(OUT_DIR / f"maskable-{s}x{s}.png", optimize=True)
        print(f"✔ icons/maskable-{s}x{s}.png")

    # iOS 主畫面圖示：不透明、不需圓角（iOS 會自行裁切）
    apple = make_icon(180, maskable=True)
    apple.save(OUT_DIR / "apple-touch-icon.png", optimize=True)
    print("✔ icons/apple-touch-icon.png")

    make_icon(32).save(OUT_DIR / "favicon-32x32.png", optimize=True)
    print("✔ icons/favicon-32x32.png")

    print("\n完成！圖示已輸出到:", OUT_DIR)


if __name__ == "__main__":
    main()
