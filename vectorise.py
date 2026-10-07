"""Core logic: raster -> SVG, then measure how good the SVG is."""
import os, re, tempfile
import numpy as np
import vtracer, resvg_py
from io import BytesIO
from PIL import Image
from skimage.metrics import structural_similarity as ssim

MAX_SIDE = 512  # resize before tracing: keeps it fast and node counts comparable

def load_rgb_on_white(img: Image.Image) -> Image.Image:
    """Flatten transparency onto white, cap size."""
    img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    img = Image.alpha_composite(bg, img).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    return img

def trace(img: Image.Image, color_precision=6, filter_speckle=4,
          corner_threshold=60, mode="spline") -> str:
    """Run VTracer and return the SVG string."""
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in.png"), os.path.join(d, "out.svg")
        img.save(src)
        vtracer.convert_image_to_svg_py(
            src, dst, colormode="color", hierarchical="stacked", mode=mode,
            filter_speckle=filter_speckle, color_precision=color_precision,
            corner_threshold=corner_threshold)
        return open(dst, encoding="utf-8").read()

def render(svg: str, size) -> Image.Image:
    """Render SVG to a PIL image with resvg (pure pip wheel, works on Windows)."""
    png = bytes(resvg_py.svg_to_bytes(svg_string=svg, width=size[0],
                                      height=size[1], background="#ffffff"))
    return Image.open(BytesIO(png)).convert("RGB")

def svg_stats(svg: str) -> dict:
    """How editable is this for a designer? Fewer paths/nodes = easier."""
    paths = len(re.findall(r"<path", svg))
    # every drawing command letter in a path 'd' attribute ~ one node
    nodes = sum(len(re.findall(r"[MmLlCcQqSsHhVvAa]", d))
                for d in re.findall(r'\sd="([^"]+)"', svg))
    colors = len(set(re.findall(r'fill="(#[0-9a-fA-F]{3,8})"', svg)))
    return {"paths": paths, "nodes": nodes, "colors": colors,
            "svg_kb": round(len(svg.encode()) / 1024, 1)}

def evaluate(original: Image.Image, svg: str) -> dict:
    rendered = render(svg, original.size)
    a, b = np.asarray(original), np.asarray(rendered)
    score = ssim(a, b, channel_axis=2)
    mae = float(np.abs(a.astype(float) - b.astype(float)).mean())
    return {"ssim": round(float(score), 4), "mean_abs_err": round(mae, 2),
            **svg_stats(svg)}, rendered
