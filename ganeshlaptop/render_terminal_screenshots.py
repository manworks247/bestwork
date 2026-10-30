#!/usr/bin/env python3
"""Render saved run logs as legible black-background terminal transcript images."""
from __future__ import annotations

from pathlib import Path
import re
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
LOG_DIR = ROOT / "outputs" / "logs"
SHOT_DIR = ROOT / "outputs" / "screenshots"
FONT_DIRS = [Path("/usr/share/fonts/truetype/dejavu"), Path("/usr/share/fonts/truetype/liberation2")]

SCREENS = [
    ("00_environment.log", "Runtime and compute availability", "ganesh@ganeshlaptop:~/ganeshlaptop$", "python environment_check.py", "01_runtime.png"),
    ("00_fixture_generation.log", "Synthetic fixture preparation", "ganesh@ganeshlaptop:~/ganeshlaptop$", "python prepare_fixtures.py", "00_fixture_generation.png"),
    ("01_dataset_access.log", "Dataset access check", "user@bestwork:~/bestwork$", "curl -I -L ModelNet40 and ModelNet10 archive endpoints", "02_dataset_access.png"),
    ("02_full_pointnet_attempt.log", "PointNet++ full-run attempt (dataset missing)", "user@pointnet2:/tmp/pointnet-upstream$", "python train_classification.py --model pointnet2_cls_ssg --log_dir pointnet2_modelnet40 --num_category 40 --epoch 200 --batch_size 24 --use_cpu", "03_full_pointnet_attempt.png"),
    ("03_pointnet_smoke.log", "PointNet++ official-code CPU smoke run", "user@pointnet2:/tmp/pointnet-upstream$", "python train_classification.py --model pointnet2_cls_ssg --log_dir pointnet2_synthetic_smoke --num_category 40 --epoch 1 --batch_size 2 --num_point 512 --use_cpu", "04_pointnet_smoke.png"),
    ("04_voxel_demo.log", "Mesh-to-voxel and 3D CNN forward pass", "ganesh@ganeshlaptop:~/ganeshlaptop$", "python run_voxel_demo.py --grid-size 32", "05_voxel_demo.png"),
    ("05_meshcnn_smoke.log", "MeshCNN edge-network smoke run", "ganesh@ganeshlaptop:~/ganeshlaptop$", "python run_meshcnn_smoke.py --meshcnn-root /tmp/meshcnn-upstream", "06_meshcnn_smoke.png"),
    ("06_conversions.log", "Mesh / point cloud / voxel conversions", "ganesh@ganeshlaptop:~/ganeshlaptop$", "python run_conversions.py --grid-size 32", "07_conversions.png"),
]


def load_font(size: int, bold: bool = False):
    candidates = []
    for directory in FONT_DIRS:
        candidates += [directory / ("DejaVuSansMono-Bold.ttf" if bold else "DejaVuSansMono.ttf"),
                       directory / ("LiberationMono-Bold.ttf" if bold else "LiberationMono-Regular.ttf")]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def clean_lines(text: str) -> list[str]:
    text = re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", text)
    text = text.replace("\r", "\n").replace("\x00", "")
    lines = []
    for line in text.splitlines():
        line = line.rstrip()
        if not line:
            continue
        if line.startswith("Script started on") or line.startswith("Script done on"):
            continue
        if line.startswith("---") and len(line) > 110:
            continue
        # Keep true log content, but avoid a screenshot consisting only of a progress bar.
        if re.search(r"\d+%\|[█▉▊▋▌▍▎▏ ]+\|", line):
            if not lines or "100%" not in line:
                continue
            line = re.sub(r"\s+", " ", line)
        lines.append(line)
    return lines


def wrapped(lines: list[str], width: int) -> list[str]:
    out = []
    for line in lines:
        if len(line) <= width:
            out.append(line)
        else:
            out.extend(textwrap.wrap(line, width=width, subsequent_indent="    ",
                                      replace_whitespace=False, drop_whitespace=True))
    return out


def render(filename: str, title: str, prompt: str, command: str, output_name: str) -> None:
    path = LOG_DIR / filename
    if not path.exists():
        return
    lines = clean_lines(path.read_text(errors="replace"))
    lines = wrapped(lines, 112)
    width, line_height, margin = 1680, 30, 35
    max_body_lines = 28
    if len(lines) > max_body_lines:
        # Preserve the command, most informative head, and the final results/error.
        keep_head = 10
        keep_tail = max_body_lines - keep_head - 1
        lines = lines[:keep_head] + ["... (see the complete raw transcript in outputs/logs/) ..."] + lines[-keep_tail:]
    height = 162 + line_height * max(len(lines), 3) + 38
    image = Image.new("RGB", (width, height), "#080b10")
    draw = ImageDraw.Draw(image)
    regular = load_font(22)
    small = load_font(17)
    bold = load_font(20, bold=True)
    # Terminal title bar.
    draw.rounded_rectangle((16, 15, width - 16, height - 15), radius=17,
                           fill="#0b0f14", outline="#263240", width=2)
    draw.rounded_rectangle((17, 16, width - 17, 59), radius=16, fill="#171d26")
    draw.rectangle((17, 41, width - 17, 60), fill="#171d26")
    for x, color in ((43, "#ff5f56"), (69, "#ffbd2e"), (95, "#27c93f")):
        draw.ellipse((x, 30, x + 13, 43), fill=color)
    draw.text((width // 2, 38), title, font=bold, fill="#dbe7f3", anchor="mm")
    y = 78
    draw.text((margin, y), prompt, font=regular, fill="#67d391")
    cmd_x = margin + int(draw.textlength(prompt + " ", font=regular))
    command_lines = textwrap.wrap(command, width=78, subsequent_indent="") or [""]
    draw.text((cmd_x, y), command_lines[0], font=regular, fill="#e7edf5")
    y += 29
    for command_line in command_lines[1:]:
        draw.text((margin + 22, y), command_line, font=regular, fill="#e7edf5")
        y += 29
    y += 2
    draw.line((margin, y, width - margin, y), fill="#202b38", width=1)
    y += 12
    for line in lines:
        text_color = "#e6edf3"
        if any(word in line.upper() for word in ("STATUS: PASS", "SUCCESSFULLY", "PASS —", "PASS -")):
            text_color = "#69d391"
        elif any(word in line.upper() for word in ("WARNING", "NOT INSTALLED", "BLOCKED", "CUDA AVAILABLE: FALSE")):
            text_color = "#f0c674"
        elif any(word in line for word in ("Traceback", "FileNotFoundError", "curl: (")):
            text_color = "#ff7b72"
        draw.text((margin, y), line, font=regular, fill=text_color)
        y += line_height
    draw.text((width - margin, height - 37), "Saved stdout transcript · black terminal theme", font=small,
              fill="#728196", anchor="ra")
    target = SHOT_DIR / output_name
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target, quality=94)


def main() -> None:
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    for entry in SCREENS:
        render(*entry)
    print(f"Rendered {len(list(SHOT_DIR.glob('*.png')))} terminal transcript screenshots to {SHOT_DIR}")


if __name__ == "__main__":
    main()
