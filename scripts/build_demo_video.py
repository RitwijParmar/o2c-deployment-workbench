from __future__ import annotations

import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
SLIDES = DEMO / "slides"
SLIDES.mkdir(parents=True, exist_ok=True)
WIDTH, HEIGHT = 1280, 720
NAVY, BLUE, CYAN, PAPER, INK, MUTED, AMBER, GREEN = "#0B1F33", "#1769AA", "#30B6C9", "#F4F7FA", "#17212B", "#617181", "#B56A00", "#177A55"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"


def font(size: int, bold: bool = False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def wrapped(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], size: int, color: str = INK, bold: bool = False, spacing: int = 10):
    x1, y1, x2, _ = box
    words, lines, line = text.split(), [], ""
    face = font(size, bold)
    for word in words:
        candidate = f"{line} {word}".strip()
        if draw.textbbox((0, 0), candidate, font=face)[2] <= x2 - x1:
            line = candidate
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    y = y1
    for item in lines:
        draw.text((x1, y), item, font=face, fill=color)
        y += size + spacing
    return y


def base(title: str, kicker: str, number: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGB", (WIDTH, HEIGHT), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, WIDTH, 132), fill=NAVY)
    draw.text((68, 28), kicker.upper(), font=font(17, True), fill=CYAN)
    draw.text((68, 58), title, font=font(38, True), fill="white")
    draw.text((1170, 46), f"0{number}", font=font(42, True), fill="#315570")
    draw.text((68, 682), "SYNTHETIC ERP EXPORTS · CONTROLLED IMPLEMENTATION BENCHMARK · NOT CUSTOMER IMPACT", font=font(13, True), fill=MUTED)
    return image, draw


slides = [
    ("A customer implementation, not an ETL demo", "O2C Deployment Workbench", ["Three incompatible source styles", "Seven canonical receivables entities", "Controls, UAT, cutover and hypercare"]),
    ("Configuration is the product layer", "Customer setup", ["Source-field mappings", "Payment tolerances and deduction limits", "Collection weights, exception owners and KPI targets"]),
    ("Difficult cash is the main event", "Cash application", ["Partial, overpay, one-to-many and many-to-one", "Missing remittance and cross-currency tolerance", "Duplicates, deduction short-pays and true unmatched cash"]),
    ("Controlled benchmark, visible gaps", "Current vs future", ["Auto-match: 10.0% → 80.7%", "Manual review: 90.3% → 21.9%", "Unapplied cash: $2.19M → $550K"]),
    ("Dashboard and operating queues", "Implementation evidence", []),
    ("MCP exposes narrow evidence tools", "Agent platform", ["4 structured tools", "3 resources and 2 prompts", "stdio locally; Streamable HTTP when deployed"]),
    ("Specialists advise; people control money", "Multi-agent governance", ["Supervisor → Cash Application / Data Quality / Collections", "Go Live Monitor evaluates controls and targets", "Post, refund, write-off and master-data changes require approval"]),
    ("Observable from ingestion to handoff", "Agent observability", ["OpenTelemetry pipeline, agent, tool and handoff spans", "GenAI-aligned workflow and agent attributes", "Sensitive record content capture disabled"]),
    ("Conditional go, with a real hypercare plan", "Deployment decision", ["1,908 records · 0 validation errors · 18 routed warnings", "3 KPI targets met · 4 stretch targets still open", "Complete consulting pack and 28 UAT scenarios"]),
]

for index, (title_text, kicker, bullets) in enumerate(slides, start=1):
    canvas, draw = base(title_text, kicker, index)
    if index == 5:
        dashboard = Image.open(DEMO / "dashboard.png").convert("RGB")
        dashboard.thumbnail((1120, 500))
        x = (WIDTH - dashboard.width) // 2
        canvas.paste(dashboard, (x, 155))
    else:
        y = 185
        for bullet in bullets:
            draw.rounded_rectangle((78, y, 1202, y + 115), radius=18, fill="white", outline="#D8E2EA", width=2)
            draw.ellipse((108, y + 39, 138, y + 69), fill=CYAN if index not in {4, 9} else (GREEN if "met" in bullet.lower() else AMBER))
            wrapped(draw, bullet, (165, y + 27, 1160, y + 100), 27, INK, True)
            y += 135
    canvas.save(SLIDES / f"slide-{index:02d}.png")

script = (DEMO / "demo_script.md").read_text(encoding="utf-8")
narration = "\n".join(line for line in script.splitlines() if line.strip() and not line.startswith("#"))
narration = re.sub(r"[*`]+", "", narration).replace("O2C", "O 2 C").replace("MCP", "M C P").replace("KPI", "K P I")
narration_path = DEMO / "narration.txt"
narration_path.write_text(narration, encoding="utf-8")
audio_path = DEMO / "narration.aiff"
subprocess.run(["/usr/bin/say", "-r", "120", "-f", str(narration_path), "-o", str(audio_path)], check=True)

concat_path = DEMO / "slides.ffconcat"
duration_each = 300 / len(slides)
concat_lines = ["ffconcat version 1.0"]
for index in range(1, len(slides) + 1):
    concat_lines.extend([f"file '{(SLIDES / f'slide-{index:02d}.png').as_posix()}'", f"duration {duration_each:.6f}"])
concat_lines.append(f"file '{(SLIDES / f'slide-{len(slides):02d}.png').as_posix()}'")
concat_path.write_text("\n".join(concat_lines) + "\n", encoding="utf-8")

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
probe = subprocess.run([ffmpeg, "-i", str(audio_path)], text=True, capture_output=True)
match = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", probe.stderr)
if not match:
    raise RuntimeError("Could not determine narration duration")
hours, minutes, seconds = match.groups()
audio_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
atempo = audio_seconds / 300

video_path = DEMO / "o2c_implementation_demo.mp4"
subprocess.run(
    [
        ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_path), "-i", str(audio_path),
        "-filter:a", f"atempo={atempo:.6f}", "-t", "300", "-r", "30", "-c:v", "libx264", "-preset", "medium",
        "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(video_path),
    ],
    check=True,
)
print(f"{video_path}\nsource narration: {audio_seconds:.2f}s; final target: 300.00s")

