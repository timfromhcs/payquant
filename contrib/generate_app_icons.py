#!/usr/bin/env python3
"""
PayQuant (PQN) Executable & App Icon Generator
Generates high-resolution multi-size .ico icon files for all PayQuant GUI applications.
"""

import os
import sys
from PIL import Image, ImageDraw

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIXMAPS_DIR = os.path.join(BASE_DIR, "share", "pixmaps")
os.makedirs(PIXMAPS_DIR, exist_ok=True)

SIZES = [(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)]

def create_base_canvas(size, bg_color):
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    w, h = size
    r = int(w * 0.18)
    # Rounded rect background
    draw.rounded_rectangle([2, 2, w-3, h-3], radius=r, fill=bg_color, outline=(0, 212, 255, 180), width=max(1, int(w/64)))
    return img, draw

def draw_main_brand(size):
    img, draw = create_base_canvas(size, (6, 8, 20, 255))
    w, h = size
    cx, cy = w / 2, h / 2
    r = w * 0.32
    # Diamond
    points = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
    draw.polygon(points, fill=(0, 212, 255, 230), outline=(0, 255, 170, 255))
    # Inner diamond
    r2 = r * 0.5
    points2 = [(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)]
    draw.polygon(points2, fill=(123, 47, 190, 240), outline=(255, 255, 255, 200))
    return img

def draw_node_icon(size):
    img, draw = create_base_canvas(size, (11, 10, 38, 255))
    w, h = size
    cx, cy = w / 2, h / 2
    r = w * 0.28
    # Center node
    draw.ellipse([cx-r*0.4, cy-r*0.4, cx+r*0.4, cy+r*0.4], fill=(0, 212, 255, 255), outline=(0, 255, 170, 255), width=max(1, int(w/64)))
    # Satellite nodes
    satellites = [(cx-r, cy-r), (cx+r, cy-r), (cx-r, cy+r), (cx+r, cy+r)]
    for sx, sy in satellites:
        draw.line([(cx, cy), (sx, sy)], fill=(0, 255, 170, 200), width=max(1, int(w/64)))
        draw.ellipse([sx-r*0.25, sy-r*0.25, sx+r*0.25, sy+r*0.25], fill=(123, 47, 190, 255), outline=(0, 212, 255, 255))
    return img

def draw_miner_icon(size):
    img, draw = create_base_canvas(size, (20, 13, 4, 255))
    w, h = size
    cx, cy = w / 2, h / 2
    r = w * 0.35
    # Energy flame / Pickaxe diamond
    draw.ellipse([cx-r*0.65, cy-r*0.65, cx+r*0.65, cy+r*0.65], fill=(255, 170, 0, 255), outline=(255, 51, 0, 255), width=max(1, int(w/64)))
    # Lightning spark / pick handle
    draw.line([(cx-r*0.5, cy+r*0.5), (cx+r*0.5, cy-r*0.5)], fill=(255, 255, 255, 240), width=max(2, int(w/32)))
    draw.polygon([(cx, cy-r*0.6), (cx+r*0.4, cy-r*0.2), (cx-r*0.2, cy+r*0.4)], fill=(255, 51, 0, 230))
    return img

def draw_node_miner_icon(size):
    img, draw = create_base_canvas(size, (18, 8, 38, 255))
    w, h = size
    cx, cy = w / 2, h / 2
    r = w * 0.32
    # Dual rings: left node purple, right miner amber
    draw.ellipse([cx-r*0.8, cy-r*0.5, cx, cy+r*0.5], fill=(123, 47, 190, 200), outline=(0, 212, 255, 255), width=max(1, int(w/64)))
    draw.ellipse([cx, cy-r*0.5, cx+r*0.8, cy+r*0.5], fill=(255, 170, 0, 200), outline=(255, 255, 255, 255), width=max(1, int(w/64)))
    draw.ellipse([cx-r*0.3, cy-r*0.3, cx+r*0.3, cy+r*0.3], fill=(0, 255, 170, 240))
    return img

def draw_explorer_icon(size):
    img, draw = create_base_canvas(size, (4, 20, 16, 255))
    w, h = size
    cx, cy = w / 2 - w * 0.05, h / 2 - h * 0.05
    r = w * 0.26
    # Magnifying glass circle
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline=(0, 255, 170, 255), fill=(0, 212, 255, 100), width=max(2, int(w/32)))
    # Handle
    draw.line([(cx+r*0.7, cy+r*0.7), (cx+r*1.6, cy+r*1.6)], fill=(0, 255, 170, 255), width=max(3, int(w/20)))
    # Grid lines inside lens
    draw.line([(cx-r*0.6, cy), (cx+r*0.6, cy)], fill=(255, 255, 255, 200), width=max(1, int(w/64)))
    draw.line([(cx, cy-r*0.6), (cx, cy+r*0.6)], fill=(255, 255, 255, 200), width=max(1, int(w/64)))
    return img

def draw_wallet_icon(size):
    img, draw = create_base_canvas(size, (4, 10, 24, 255))
    w, h = size
    cx, cy = w / 2, h / 2
    r = w * 0.34
    # Shield outline
    points = [(cx, cy-r), (cx+r*0.8, cy-r*0.6), (cx+r*0.7, cy+r*0.4), (cx, cy+r), (cx-r*0.7, cy+r*0.4), (cx-r*0.8, cy-r*0.6)]
    draw.polygon(points, fill=(0, 255, 170, 220), outline=(0, 212, 255, 255))
    # Keyhole
    draw.ellipse([cx-r*0.2, cy-r*0.3, cx+r*0.2, cy+r*0.1], fill=(6, 8, 20, 255))
    draw.polygon([(cx-r*0.15, cy), (cx+r*0.15, cy), (cx+r*0.22, cy+r*0.4), (cx-r*0.22, cy+r*0.4)], fill=(6, 8, 20, 255))
    return img

TARGETS = {
    "payquant.ico": draw_main_brand,
    "payquant-node.ico": draw_node_icon,
    "payquant-miner.ico": draw_miner_icon,
    "payquant-node-miner.ico": draw_node_miner_icon,
    "payquant-explorer.ico": draw_explorer_icon,
    "payquant-wallet.ico": draw_wallet_icon,
}

def generate_all():
    for name, func in TARGETS.items():
        imgs = [func(sz) for sz in SIZES]
        filepath = os.path.join(PIXMAPS_DIR, name)
        imgs[0].save(filepath, format="ICO", sizes=SIZES)
        print(f"Generated {filepath} ({os.path.getsize(filepath)} bytes)")

if __name__ == "__main__":
    generate_all()
