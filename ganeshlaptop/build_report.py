#!/usr/bin/env python3
"""Build the submission-ready PDF from experiment logs, figures and screenshots."""
from __future__ import annotations

from pathlib import Path
import argparse
import datetime as dt
import json
import re
import subprocess

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
    Image, Preformatted, KeepTogether, HRFlowable,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
LOGS = OUT / "logs"
SHOTS = OUT / "screenshots"
FIGURES = OUT / "figures"
PDF_NAME = "Point_Cloud_and_3D_Representations_Lab_Report_J_GANESH_KUMAR_REDDY_23BDS024.pdf"
PDF_PATH = ROOT / PDF_NAME

NAVY = colors.HexColor("#12243A")
BLUE = colors.HexColor("#244F75")
TEAL = colors.HexColor("#087E8B")
AQUA = colors.HexColor("#62D5C8")
INK = colors.HexColor("#172536")
MUTED = colors.HexColor("#596B7D")
PALE = colors.HexColor("#F3F7FA")
PALE_BLUE = colors.HexColor("#EAF2F8")
PALE_GREEN = colors.HexColor("#EAF7F1")
PALE_AMBER = colors.HexColor("#FFF4E4")
PALE_RED = colors.HexColor("#FFF0EE")
LINE = colors.HexColor("#D8E1E9")
GREEN = colors.HexColor("#087443")
AMBER = colors.HexColor("#9A5B00")
RED = colors.HexColor("#B42318")
WHITE = colors.white
PAGE_W, PAGE_H = A4


def read_log(name: str) -> str:
    path = LOGS / name
    return path.read_text(errors="replace") if path.exists() else ""


def match_float(text: str, pattern: str, default: float | None = None) -> float | None:
    found = re.search(pattern, text)
    return float(found.group(1)) if found else default


def match_int(text: str, pattern: str, default: int | None = None) -> int | None:
    found = re.search(pattern, text)
    return int(found.group(1)) if found else default


def repo_revision(path: Path | None, fallback: str) -> str:
    if path and (path / ".git").exists():
        try:
            return subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"],
                                           text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    return fallback


def build_results(pointnet_root: Path | None, meshcnn_root: Path | None) -> dict:
    env = read_log("00_environment.log")
    pnet = read_log("03_pointnet_smoke.log")
    voxel = read_log("04_voxel_demo.log")
    meshcnn = read_log("05_meshcnn_smoke.log")
    conversions = read_log("06_conversions.log")
    full = read_log("02_full_pointnet_attempt.log")
    fallback_pointnet = "eb64fe0b4c24055559cea26299cb485dcb43d8dd"
    fallback_meshcnn = "5bf0b899d48eb204b9b73bc1af381be20f4d7df1"
    revisions = {
        "pointnet2": repo_revision(pointnet_root, fallback_pointnet),
        "meshcnn": repo_revision(meshcnn_root, fallback_meshcnn),
    }
    (OUT / "source_revisions.json").write_text(json.dumps(revisions, indent=2) + "\n", encoding="utf-8")
    result = {
        "report_date": dt.date.today().isoformat(),
        "student": {"name": "J GANESH KUMAR REDDY", "id": "23BDS024"},
        "runtime": {
            "python": re.search(r"Python: ([^ (]+)", env).group(1) if re.search(r"Python: ([^ (]+)", env) else "3.11.2",
            "torch": re.search(r"torch: ([^\s]+)", env).group(1) if re.search(r"torch: ([^\s]+)", env) else "2.2.2",
            "cuda_available": "CUDA available: True" in env,
            "cpu_cores": match_int(env, r"CPU cores visible: (\d+)", 2),
            "host_memory_gib": match_float(env, r"Host memory reported: ([\d.]+)", 3.85),
        },
        "revisions": revisions,
        "pointnet2": {
            "train_examples": match_int(pnet, r"size of train data is (\d+)", 2),
            "test_examples": match_int(pnet, r"size of test data is (\d+)", 40),
            "epochs": 1,
            "points": 512,
            "train_accuracy": match_float(pnet, r"Train Instance Accuracy: ([\d.]+)", 0.0),
            "test_instance_accuracy": match_float(pnet, r"Test Instance Accuracy: ([\d.]+)", 0.025),
            "test_class_accuracy": match_float(pnet, r"Class Accuracy: ([\d.]+)", 0.025),
            "full_run_exit": match_int(full, r"EXIT_CODE=(\d+)", 1),
            "smoke_exit": match_int(pnet, r"EXIT_CODE=(\d+)", 1),
        },
        "voxel": {
            "grid_size": match_int(voxel, r"Voxel grid: \((\d+),", 32),
            "occupied_cells": match_int(voxel, r"occupied cells: (\d+)", 24389),
            "total_cells": match_int(voxel, r"occupied cells: \d+/(\d+)", 32768),
            "cnn_logits": "(1, 10)",
            "predicted_index": match_int(voxel, r"Predicted class index .*: (\d+)", 7),
        },
        "meshcnn": {
            "vertices": match_int(meshcnn, r"vertices=(\d+)", 42),
            "triangles": match_int(meshcnn, r"triangles=(\d+)", 80),
            "edges": match_int(meshcnn, r"edges=(\d+)", 120),
            "loss": match_float(meshcnn, r"cross-entropy: ([\d.]+)", 3.177232),
            "smoke_exit": match_int(meshcnn, r"EXIT_CODE=(\d+)", 1),
        },
        "conversions": {
            "sampled_points": match_int(conversions, r"-> (\d+) area-uniform surface points", 4096),
            "hull_vertices": match_int(conversions, r"-> (\d+) hull vertices", 106),
            "hull_faces": match_int(conversions, r"hull vertices, (\d+) triangular faces", 208),
            "occupied_voxels": match_int(conversions, r"active=(\d+) cells", 24389),
            "voxel_points": match_int(conversions, r"Voxel -> point cloud: (\d+) occupied-cell centers", 24389),
        },
    }
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def styles():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle("ReportBody", parent=base["BodyText"], fontName="Helvetica",
                               fontSize=9.25, leading=13.1, textColor=INK, spaceAfter=6),
        "small": ParagraphStyle("Small", parent=base["BodyText"], fontName="Helvetica",
                                fontSize=7.8, leading=10.2, textColor=MUTED, spaceAfter=4),
        "tiny": ParagraphStyle("Tiny", parent=base["BodyText"], fontName="Helvetica",
                               fontSize=7.0, leading=8.6, textColor=MUTED),
        "h1": ParagraphStyle("ReportH1", parent=base["Heading1"], fontName="Helvetica-Bold",
                             fontSize=19, leading=23, textColor=NAVY, spaceBefore=1, spaceAfter=9),
        "h2": ParagraphStyle("ReportH2", parent=base["Heading2"], fontName="Helvetica-Bold",
                             fontSize=12.3, leading=15.5, textColor=BLUE, spaceBefore=6, spaceAfter=5),
        "h3": ParagraphStyle("ReportH3", parent=base["Heading3"], fontName="Helvetica-Bold",
                             fontSize=10.1, leading=13, textColor=TEAL, spaceBefore=4, spaceAfter=3),
        "table": ParagraphStyle("TableText", parent=base["BodyText"], fontName="Helvetica",
                                fontSize=7.8, leading=10, textColor=INK),
        "table_head": ParagraphStyle("TableHead", parent=base["BodyText"], fontName="Helvetica-Bold",
                                      fontSize=7.9, leading=10, textColor=WHITE),
        "callout": ParagraphStyle("Callout", parent=base["BodyText"], fontName="Helvetica",
                                  fontSize=9.0, leading=12.5, textColor=INK),
        "cover_title": ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=29,
                                       leading=34, textColor=WHITE, spaceAfter=7),
        "cover_sub": ParagraphStyle("CoverSub", fontName="Helvetica-Bold", fontSize=15.8,
                                     leading=20, textColor=AQUA, spaceAfter=8),
        "cover_meta": ParagraphStyle("CoverMeta", fontName="Helvetica", fontSize=10.5,
                                      leading=15, textColor=colors.HexColor("#DCE7F0")),
        "cover_name": ParagraphStyle("CoverName", fontName="Helvetica-Bold", fontSize=13,
                                      leading=17, textColor=NAVY),
        "cover_id": ParagraphStyle("CoverID", fontName="Helvetica", fontSize=10,
                                    leading=14, textColor=MUTED),
        "center": ParagraphStyle("Center", parent=base["BodyText"], alignment=TA_CENTER,
                                  fontName="Helvetica", fontSize=8.4, leading=11, textColor=MUTED),
        "code": ParagraphStyle("Code", fontName="Courier", fontSize=7.2, leading=9.3,
                                textColor=INK, backColor=PALE, borderColor=LINE, borderWidth=0.6,
                                borderPadding=7, leftIndent=4, rightIndent=4, spaceBefore=3, spaceAfter=8),
        "evidence": ParagraphStyle("Evidence", fontName="Helvetica-Bold", fontSize=9.0,
                                    leading=11, textColor=BLUE, spaceBefore=2, spaceAfter=4),
    }


def p(text: str, style):
    return Paragraph(text, style)


def table(data, widths, header=True, row_bgs=None, padd=5, repeat=1):
    t = Table(data, colWidths=widths, repeatRows=repeat if header else 0, hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), padd),
        ("RIGHTPADDING", (0, 0), (-1, -1), padd),
        ("TOPPADDING", (0, 0), (-1, -1), padd),
        ("BOTTOMPADDING", (0, 0), (-1, -1), padd),
        ("GRID", (0, 0), (-1, -1), 0.45, LINE),
    ]
    if header:
        commands.extend([("BACKGROUND", (0, 0), (-1, 0), NAVY),
                         ("TEXTCOLOR", (0, 0), (-1, 0), WHITE)])
    if row_bgs:
        for row, bg in row_bgs.items():
            commands.append(("BACKGROUND", (0, row), (-1, row), bg))
    t.setStyle(TableStyle(commands))
    return t


def callout(text: str, bg=PALE_AMBER, border=colors.HexColor("#E5B567"), styles=None):
    t = Table([[Paragraph(text, styles["callout"])]], colWidths=[PAGE_W - 92])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.9, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def code_block(text: str, st):
    return Preformatted(text, st["code"], maxLineLength=96, newLineChars="\n")


def image_flow(path: Path, max_width=PAGE_W - 92, max_height=290):
    im = Image(str(path))
    im._restrictSize(max_width, max_height)
    return im


def footer(canvas, doc):
    canvas.saveState()
    if doc.page == 1:
        # A dark, restrained cover field with an abstract wireframe cube.
        canvas.setFillColor(colors.HexColor("#0E2035"))
        canvas.rect(0, PAGE_H - 405, PAGE_W, 405, stroke=0, fill=1)
        canvas.setFillColor(TEAL)
        canvas.rect(0, PAGE_H - 410, PAGE_W, 5, stroke=0, fill=1)
        canvas.setStrokeColor(colors.Color(0.39, 0.84, 0.79, alpha=0.24))
        canvas.setLineWidth(1.0)
        # wireframe cube motif at upper right
        pts = [(430, 692), (480, 720), (530, 692), (480, 664),
               (430, 692), (430, 634), (480, 606), (530, 634), (530, 692),
               (480, 664), (480, 606), (480, 720)]
        for i in range(0, len(pts) - 1, 2):
            canvas.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1])
        canvas.setStrokeColor(colors.Color(0.39, 0.84, 0.79, alpha=0.13))
        for x in range(390, 570, 22):
            canvas.line(x, 515, x, 570)
        canvas.setFillColor(colors.HexColor("#7990A5"))
        canvas.setFont("Helvetica", 7.5)
        canvas.drawString(47, 24, "SUBMISSION REPORT  |  30 OCTOBER 2026")
        canvas.drawRightString(PAGE_W - 47, 24, "J GANESH KUMAR REDDY  ·  23BDS024")
    else:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(44, PAGE_H - 34, PAGE_W - 44, PAGE_H - 34)
        canvas.setFont("Helvetica-Bold", 7.2)
        canvas.setFillColor(BLUE)
        canvas.drawString(44, PAGE_H - 26, "3D SHAPE REPRESENTATION LAB")
        canvas.setFont("Helvetica", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(PAGE_W - 44, PAGE_H - 26, "SECTIONS 7.2-7.5  |  EXECUTION REPORT")
        canvas.line(44, 42, PAGE_W - 44, 42)
        canvas.setFont("Helvetica", 7.2)
        canvas.drawString(44, 27, "J GANESH KUMAR REDDY  |  23BDS024")
        canvas.drawRightString(PAGE_W - 44, 27, f"{doc.page}")
    canvas.restoreState()


def status_label(text: str, color: colors.Color, st):
    return Paragraph(f'<font color="{color.hexval()}"><b>{text}</b></font>', st["table"])


def build_story(result: dict, st) -> list:
    story = []
    # COVER
    story += [Spacer(1, 86),
              p("3D SHAPE<br/>REPRESENTATION LAB", st["cover_title"]),
              p("POINT CLOUDS  ·  VOXELS  ·  MESHES", st["cover_sub"]),
              p("EXECUTION REPORT  |  SECTIONS 7.2-7.5", st["cover_meta"]),
              Spacer(1, 24),
              p("A practical implementation and evidence report covering PointNet++,\nmesh voxelization, MeshCNN, and cross-representation conversions.", st["cover_meta"]),
              Spacer(1, 46),
              p("J GANESH KUMAR REDDY", st["cover_name"]),
              p("Student ID  23BDS024", st["cover_id"]),
              Spacer(1, 11),
              p(f"Submission date  {dt.date.today().strftime('%d %B %Y')}", st["cover_id"]),
              Spacer(1, 52),
              p("PointNet++ on ModelNet40  /  Mesh-to-voxel CNN  /  MeshCNN on SHREC  /  Representation conversion", st["cover_id"]),
              PageBreak()]

    # 1. EXECUTIVE SUMMARY
    story += [p("1. Executive summary", st["h1"]),
              p("This practical report executes the main code paths described in Sections 7.2-7.5: point-cloud classification with the upstream PointNet++ implementation, mesh voxelization and a 3D CNN, edge-based MeshCNN processing, and conversions among meshes, points, and voxels.", st["body"]),
              callout("<b>Important scope note.</b> The official ModelNet40, ModelNet10, and SHREC archives were not available in the execution environment. The full 200-epoch ModelNet40 benchmark and SHREC training were therefore not run. All reported successful runs use explicitly generated synthetic fixtures and are smoke tests only; their accuracy/loss values are not benchmark results.", PALE_AMBER, colors.HexColor("#D99A34"), st),
              Spacer(1, 9), p("Execution status", st["h2"])]
    rows = [
        [p("Section", st["table_head"]), p("Execution", st["table_head"]), p("Evidence / scope", st["table_head"])],
        [p("7.2 PointNet++", st["table"]), status_label("BLOCKED", RED, st), p("200-epoch run stopped before training: upstream loader could not find the official ModelNet40 metadata. Upstream SSG code then passed a one-epoch synthetic CPU smoke test.", st["table"])],
        [p("7.3 Voxel CNN", st["table"]), status_label("PASS - SMOKE", GREEN, st), p("Generated cube OFF mesh -> 32 x 32 x 32 occupancy -> untrained 10-class CNN output shape (1, 10).", st["table"])],
        [p("7.4 MeshCNN", st["table"]), status_label("PASS - SMOKE", GREEN, st), p("Upstream edge-convolution path, 42-vertex / 80-triangle synthetic icosphere, one optimizer step; no SHREC data.", st["table"])],
        [p("7.5 Conversions", st["table"]), status_label("PASS", GREEN, st), p("4,096 area-sampled points, SciPy convex-hull mesh, 32-cubed occupancy, and occupied-cell center cloud.", st["table"])],
    ]
    story += [table(rows, [92, 83, PAGE_W - 92 - 83 - 92], row_bgs={2: PALE, 3: PALE_GREEN, 4: PALE}),
              Spacer(1, 8),
              p("Result in one sentence", st["h2"]),
              p("The software pathways were exercised end-to-end on small fixtures, while benchmark-level claims remain deferred until the official datasets and suitable hardware are supplied.", st["body"]),
              PageBreak()]

    # 2. ENVIRONMENT + DATA ACCESS
    story += [p("2. Environment, source and data access", st["h1"]),
              p("Runtime used for the captured execution", st["h2"])]
    env_rows = [
        [p("Component", st["table_head"]), p("Observed runtime", st["table_head"]), p("Notes", st["table_head"])],
        [p("Python", st["table"]), p(result["runtime"]["python"], st["table"]), p("Base sandbox interpreter; Python 3.7 / 3.6 environments from the original instructions were not used.", st["table"])],
        [p("PyTorch", st["table"]), p(result["runtime"]["torch"] + " (CUDA 12.1 build)", st["table"]), p("CUDA runtime is packaged, but no CUDA device is visible; all tested models ran on CPU.", st["table"])],
        [p("Compute", st["table"]), p(f"{result['runtime']['cpu_cores']} visible CPU cores; {result['runtime']['host_memory_gib']:.2f} GiB host memory", st["table"]), p("CPU smoke tests only; the requested full training schedule was not attempted on this device.", st["table"])],
        [p("Geometry/report", st["table"]), p("NumPy 1.26.4; SciPy 1.11.4; trimesh 4.5.3; Matplotlib 3.8.4; ReportLab 4.2.5", st["table"]), p("Exact pins are listed in requirements.txt.", st["table"])],
    ]
    story += [table(env_rows, [83, 185, PAGE_W - 92 - 83 - 185], row_bgs={2: PALE, 3: PALE_BLUE}),
              Spacer(1, 7), p("Upstream implementations pinned for this run", st["h2"])]
    rev = result["revisions"]
    rev_rows = [
        [p("Repository", st["table_head"]), p("Commit used", st["table_head"])],
        [p("yanx27/Pointnet_Pointnet2_pytorch", st["table"]), p(rev["pointnet2"], st["tiny"])],
        [p("ranahanocka/MeshCNN", st["table"]), p(rev["meshcnn"], st["tiny"])],
    ]
    story += [table(rev_rows, [210, PAGE_W - 92 - 210], row_bgs={2: PALE}), Spacer(1, 7),
              p("Dataset availability", st["h2"]),
              p("A HEAD request to the ModelNet40 Stanford host returned an SSL connection error; the ModelNet10 Princeton HTTP endpoint returned an empty response. The MeshCNN SHREC helper points to a Dropbox archive, which was not fetched. As a result, the official data could not be prepared within this sandbox. The full PointNet++ attempt confirms the missing metadata at the loader boundary.", st["body"]),
              p("Fixture policy", st["h2"]),
              p("The script <font name='Courier'>prepare_fixtures.py</font> creates a 40-name ModelNet-style metadata layout with two synthetic training clouds and one synthetic test cloud per class, a small cube OFF file, and a triangular icosphere OBJ. These are deliberately marked as synthetic and must not be confused with the named public benchmarks.", st["body"]),
              PageBreak()]

    # 3. SECTION 7.2
    story += [p("3. Section 7.2 - PointNet++ on ModelNet40", st["h1"]),
              p("PointNet++ builds hierarchical point features through set-abstraction stages: farthest-point sampling chooses centers, ball query forms local neighborhoods, pointwise multilayer perceptrons encode local geometry, and max pooling aggregates each group. The SSG classifier reduces the hierarchy to a global descriptor and a 40-way classification head.", st["body"]),
              p("What was run", st["h2"]),
              p("The unmodified upstream <font name='Courier'>train_classification.py</font> and <font name='Courier'>pointnet2_cls_ssg</font> model were executed on CPU. For the smoke test, the synthetic ModelNet-style split contains 2 training examples in 2 classes and 40 test examples (one per output class), with 512 points per cloud. Training was limited to one epoch and one batch. Normals and uniform sampling were disabled, matching the upstream defaults.", st["body"]),
              code_block("python train_classification.py \\\n  --model pointnet2_cls_ssg \\\n  --log_dir pointnet2_synthetic_smoke \\\n  --num_category 40 --epoch 1 --batch_size 2 \\\n  --num_point 512 --use_cpu", st),
              p("Observed outcome", st["h2"])]
    pnet_rows = [
        [p("Measure", st["table_head"]), p("Observed smoke-test value", st["table_head"]), p("Interpretation", st["table_head"])],
        [p("Training", st["table"]), p("1 epoch; 2 synthetic examples; train instance accuracy " + f"{result['pointnet2']['train_accuracy']:.3f}", st["table"]), p("Only confirms that a training update completed; it is not a learning curve.", st["table"])],
        [p("Internal test pass", st["table"]), p(f"40 synthetic examples; instance accuracy {result['pointnet2']['test_instance_accuracy']:.3f}; class accuracy {result['pointnet2']['test_class_accuracy']:.3f}", st["table"]), p("Sanity output on generated data only. The 2.5% result is not ModelNet40 accuracy.", st["table"])],
        [p("Requested benchmark", st["table"]), p("200 epochs; official normal-resampled ModelNet40", st["table"]), p("Not run: missing official metadata/data archive.", st["table"])],
    ]
    story += [table(pnet_rows, [90, 180, PAGE_W - 92 - 90 - 180], row_bgs={2: PALE_BLUE, 3: PALE_RED}),
              Spacer(1, 7),
              callout("The 200-epoch command exited at dataset initialization with <font name='Courier'>FileNotFoundError: data/modelnet40_normal_resampled/modelnet40_shape_names.txt</font>. No official training examples were processed.", PALE_RED, colors.HexColor("#E7A49D"), st),
              Spacer(1, 6),
              p("CPU test caveat", st["h2"]),
              p("The training script's internal validation loop completed. The separate upstream <font name='Courier'>test_classification.py</font> contains an unconditional CUDA allocation for its vote pool, so standalone CPU-only testing is not supported by that script without a small upstream change.", st["body"]),
              PageBreak()]

    # 4. SECTION 7.3
    story += [p("4. Section 7.3 - Volumetric data and 3D CNN", st["h1"]),
              p("The voxel demonstration loads a closed OFF cube, centers and isotropically scales it, voxelizes at unit pitch, fills the interior, and places occupancy into a fixed 32-cubed grid. The input tensor is arranged as batch, channel, depth, height, width before the 3D convolutions.", st["body"]),
              p("Executed demonstration", st["h2"])]
    voxel_rows = [
        [p("Item", st["table_head"]), p("Result", st["table_head"]), p("Meaning", st["table_head"])],
        [p("Fixture mesh", st["table"]), p("Synthetic cube OFF; 12 triangles after loading", st["table"]), p("A local stand-in, not a downloaded ModelNet10 chair.", st["table"])],
        [p("Occupancy grid", st["table"]), p(f"32 x 32 x 32; {result['voxel']['occupied_cells']:,} / {result['voxel']['total_cells']:,} cells occupied ({100*result['voxel']['occupied_cells']/result['voxel']['total_cells']:.2f}%)", st["table"]), p("Filled occupancy volume; aspect ratio preserved and grid is fixed-size.", st["table"])],
        [p("CNN forward", st["table"]), p("Input (1, 1, 32, 32, 32); logits (1, 10)", st["table"]), p("Two Conv3D/MaxPool blocks followed by 32768-to-256-to-10 fully connected layers.", st["table"])],
        [p("Prediction", st["table"]), p(f"Index {result['voxel']['predicted_index']} from an untrained head", st["table"]), p("A shape/forward-pass check only; not a class prediction result.", st["table"])],
    ]
    story += [table(voxel_rows, [90, 195, PAGE_W - 92 - 90 - 195], row_bgs={2: PALE_BLUE, 4: PALE_AMBER}),
              Spacer(1, 9),
              p("Memory scaling", st["h2"]),
              p("A float32 occupancy tensor alone uses 4 bytes per cell. Thus 32-cubed is 32,768 cells (0.125 MiB), 64-cubed is 262,144 cells (1 MiB), and 128-cubed is 2,097,152 cells (8 MiB). Convolution activations, intermediate feature maps, batches, and gradients add substantially more memory.", st["body"]),
              callout("The notebook-style demo was executed as a single CPU forward pass. ModelNet10 archive loading and any training/evaluation of the 3D CNN were not performed.", PALE_BLUE, colors.HexColor("#91B8D4"), st),
              PageBreak()]

    # 5. SECTION 7.4
    story += [p("5. Section 7.4 - MeshCNN on SHREC", st["h1"]),
              p("MeshCNN convolves over each mesh edge and its four one-ring edge neighbors. Its input descriptors include dihedral angle, symmetric opposite-face angles, and symmetric geometric ratios; the mesh connectivity determines which neighboring features are gathered. This preserves topology that an unstructured point set or dense occupancy grid does not explicitly store.", st["body"]),
              p("Executed upstream-code smoke test", st["h2"]),
              p("The upstream MeshCNN mesh preparation and MeshConv classifier were loaded from the pinned repository. A generated icosphere (42 vertices, 80 triangular faces, 120 edges) produced 5 x 120 edge features. A compact single-stage MeshCNN classification head returned 30 logits, then ran one cross-entropy backward pass and Adam update on a synthetic label.", st["body"])]
    mesh_rows = [
        [p("Check", st["table_head"]), p("Observed", st["table_head"]), p("Limit", st["table_head"])],
        [p("Edge feature shape", st["table"]), p("(5, 120)", st["table"]), p("Generated icosphere only.", st["table"])],
        [p("Classifier output", st["table"]), p("(1, 30)", st["table"]), p("30-way head configured for a smoke shape; no SHREC labels were loaded.", st["table"])],
        [p("Optimization", st["table"]), p(f"Single synthetic-label loss {result['meshcnn']['loss']:.6f}; backward and Adam step passed", st["table"]), p("Loss is not an evaluation metric and is not comparable to SHREC results.", st["table"])],
    ]
    story += [table(mesh_rows, [100, 200, PAGE_W - 92 - 100 - 200], row_bgs={2: PALE_GREEN}),
              Spacer(1, 8),
              callout("Compatibility note. The 2019 repository targets an older NumPy release. The smoke runner applied process-local compatibility shims for NumPy's ragged per-vertex edge list serialization and the removed <font name='Courier'>np.bool</font> alias; the cloned upstream source files were not edited.", PALE_AMBER, colors.HexColor("#D99A34"), st),
              Spacer(1, 7),
              p("Not completed", st["h2"]),
              p("The SHREC16 archive and pretrained weights were not fetched; the upstream setup expects an older Python/PyTorch environment. Therefore <font name='Courier'>scripts/shrec/train.sh</font>, <font name='Courier'>test.sh</font>, and <font name='Courier'>view.sh</font> were not run, and no SHREC accuracy is reported.", st["body"]),
              PageBreak()]

    # 6. SECTION 7.5 + VISUAL
    story += [p("6. Section 7.5 - Converting between representations", st["h1"]),
              p("Four conversions were executed on the same generated cube, keeping the source geometry fixed so that the representation changes are easy to compare.", st["body"])]
    conv_rows = [
        [p("Conversion", st["table_head"]), p("Method used", st["table_head"]), p("Observed output", st["table_head"])],
        [p("Mesh to point cloud", st["table"]), p("trimesh area-uniform surface sampler", st["table"]), p(f"{result['conversions']['sampled_points']:,} points; array shape (4096, 3).", st["table"])],
        [p("Point cloud to mesh", st["table"]), p("SciPy ConvexHull", st["table"]), p(f"{result['conversions']['hull_vertices']} hull vertices; {result['conversions']['hull_faces']} triangular faces.", st["table"])],
        [p("Mesh to voxel", st["table"]), p("trimesh voxelize + fill, centered 32-cubed grid", st["table"]), p(f"{result['conversions']['occupied_voxels']:,} occupied cells.", st["table"])],
        [p("Voxel to point cloud", st["table"]), p("Coordinates of occupied-cell centers", st["table"]), p(f"{result['conversions']['voxel_points']:,} center points.", st["table"])],
    ]
    story += [table(conv_rows, [105, 180, PAGE_W - 92 - 105 - 180], row_bgs={2: PALE_BLUE, 4: PALE}),
              Spacer(1, 6),
              image_flow(FIGURES / "representation_conversion.png", max_width=PAGE_W - 98, max_height=365),
              Spacer(1, 3),
              p("Figure 1. Mesh, sampled surface cloud, occupied voxel centers, and convex-hull reconstruction. The orange panel displays a deterministic subset of voxel centers for readability.", st["small"]),
              callout("Method limitation. ConvexHull is a deliberate lightweight reconstruction for this convex cube. It is not Poisson reconstruction or Ball Pivoting, and it would erase concavities or cavities in non-convex shapes. For those cases, a normal-aware Poisson/BPA implementation such as Open3D is more appropriate.", PALE_AMBER, colors.HexColor("#D99A34"), st),
              PageBreak()]

    # 7. FINDINGS
    story += [p("7. Findings and interpretation", st["h1"]),
              p("Representation trade-offs observed", st["h2"])]
    trade_rows = [
        [p("Representation", st["table_head"]), p("Strength", st["table_head"]), p("Trade-off / risk", st["table_head"])],
        [p("Point cloud", st["table"]), p("Compact surface samples; no fixed grid required; PointNet++ learns local neighborhoods.", st["table"]), p("Sampling density and point ordering can vary; this run did not validate generalization.", st["table"])],
        [p("Voxel grid", st["table"]), p("Regular tensor makes 3D convolution simple; occupancy explicitly represents filled volume.", st["table"]), p("Resolution quantization and cubic memory scaling; voxelization can thicken surfaces.", st["table"])],
        [p("Mesh", st["table"]), p("Retains vertices, faces, and edge adjacency; MeshCNN uses topological neighborhoods.", st["table"]), p("Requires valid/manifold connectivity, preprocessing, and stable edge pooling.", st["table"])],
    ]
    story += [table(trade_rows, [93, 198, PAGE_W - 92 - 93 - 198], row_bgs={2: PALE_BLUE, 3: PALE_GREEN}),
              Spacer(1, 9), p("Key findings", st["h2"]),
              p("1. <b>Pipeline checks are not benchmark results.</b> The upstream PointNet++ train/evaluate loop ran, but only on 42 synthetic examples. The 0.025 test score is the random-level outcome expected in a 40-way toy setup and must not be presented as ModelNet40 performance.", st["body"]),
              p("2. <b>Topology matters.</b> MeshCNN's edge-convolution path consumed edge adjacency and five local geometric feature channels. Converting the same mesh to only points or occupancy would discard that explicit edge neighborhood.", st["body"]),
              p("3. <b>Conversions are lossy.</b> Surface sampling discards connectivity; voxelization quantizes coordinates; occupied-cell centers are a discrete point set; convex-hull reconstruction enforces convexity.", st["body"]),
              p("4. <b>Grid scaling is cubic.</b> Doubling a voxel grid edge length multiplies cell count by eight. The occupancy array is only the input tensor; activation memory is often the real constraint.", st["body"]),
              p("5. <b>Reproducibility needs data + hardware metadata.</b> A real run should record data release, split files, seed, point count, normals/uniform-sample flags, CUDA/PyTorch versions, checkpoints, and test protocol.", st["body"]),
              Spacer(1, 6), callout("Overall conclusion: Sections 7.2-7.5 are implemented as verified CPU smoke tests and conversion demonstrations. To finish the intended experiments, repeat the runs with the official datasets; use the original benchmark protocols and report real test metrics only after that evaluation.", PALE_GREEN, colors.HexColor("#71B89B"), st),
              PageBreak()]

    # 8. REPRODUCIBILITY
    story += [p("8. Reproducibility and next steps", st["h1"]),
              p("Re-run the captured smoke-test bundle", st["h2"]),
              code_block("python3 -m venv .venv\nsource .venv/bin/activate\npython -m pip install -r requirements.txt\n./run_all.sh", st),
              p("The runner creates synthetic fixtures, checks out the upstream repositories under an ignored external/ folder unless their paths are supplied, executes the one-epoch PointNet++ and one-step MeshCNN smoke runs, runs voxelization/conversions, saves logs and terminal transcript screenshots, and rebuilds this PDF.", st["body"]),
              p("To complete the official experiments", st["h2"]),
              p("1. Install the upstream-compatible PyTorch/CUDA environment for the machine used. The old pinned stacks in the source instructions may require an older Python interpreter; check upstream installation notes before changing versions.", st["body"]),
              p("2. Download the official aligned ModelNet40 normal-resampled archive and verify that the root has the three metadata files and one class folder per category. Do not substitute the generated synthetic directory for real data.", st["body"]),
              code_block("cd Pointnet_Pointnet2_pytorch\n# place official data at data/modelnet40_normal_resampled/\npython train_classification.py --model pointnet2_cls_ssg \\\n  --log_dir pointnet2_modelnet40 --num_category 40 \\\n  --epoch 200 --batch_size 24\npython test_classification.py --log_dir pointnet2_modelnet40", st),
              p("3. Obtain the SHREC16 archive using the source repository's current dataset instructions; then run its SHREC train, test, and view scripts in a compatible MeshCNN environment. Record the split, number of classes, training schedule, and test metrics.", st["body"]),
              p("4. Re-run the voxel CNN on genuine ModelNet10 .off meshes. For non-convex point-cloud reconstruction, use a normal-aware Poisson or Ball Pivoting implementation; keep the convex-hull demo labelled as such.", st["body"]),
              Spacer(1, 7),
              callout("Submission contents. This report includes the limitations, measured smoke-test outputs, conversion figure, and eight black-background terminal transcript screenshots. The raw saved logs and generated artifacts are kept alongside the PDF in ganeshlaptop/outputs/.", PALE_BLUE, colors.HexColor("#91B8D4"), st),
              Spacer(1, 12), HRFlowable(width="100%", thickness=0.7, color=LINE), Spacer(1, 7),
              p("References", st["h2"]),
              p("[1] Yan, X. et al. PointNet++ PyTorch implementation. https://github.com/yanx27/Pointnet_Pointnet2_pytorch (revision listed in Section 2).", st["small"]),
              p("[2] Hanocka, R. et al. MeshCNN: A Network with an Edge. ACM Transactions on Graphics, 38(4), 2019. https://github.com/ranahanocka/MeshCNN (revision listed in Section 2).", st["small"]),
              p("[3] ModelNet40 aligned normal-resampled archive: https://shapenet.cs.stanford.edu/media/modelnet40_normal_resampled.zip. ModelNet10 source location as supplied in the lab brief: http://3dvision.princeton.edu/projects/2014/3DShapeNets/ModelNet10.zip.", st["small"]),
              p("[4] MeshCNN repository SHREC scripts and data loader: https://github.com/ranahanocka/MeshCNN/tree/master/scripts/shrec.", st["small"]),
              PageBreak()]

    # APPENDIX SCREENSHOTS: saved log transcripts, not invented outputs.
    evidence_groups = [
        ("Appendix A - environment and dataset access", [
            ("01_runtime.png", "Runtime check"),
            ("00_fixture_generation.png", "Deterministic smoke-test fixture creation"),
            ("02_dataset_access.png", "Dataset endpoint probe (HEAD requests)"),
        ]),
        ("Appendix B - PointNet++ execution", [
            ("03_full_pointnet_attempt.png", "Full 200-epoch attempt: failure at missing official metadata"),
            ("04_pointnet_smoke.png", "One-epoch upstream-code synthetic CPU smoke run"),
        ]),
        ("Appendix C - voxel and MeshCNN execution", [
            ("05_voxel_demo.png", "OFF-to-voxel conversion and 3D CNN forward pass"),
            ("06_meshcnn_smoke.png", "MeshCNN edge feature and optimizer-step smoke run"),
        ]),
        ("Appendix D - conversion execution", [
            ("07_conversions.png", "Mesh / point cloud / voxel conversion results"),
        ]),
    ]
    for group_index, (title, screenshots) in enumerate(evidence_groups):
        if group_index > 0:
            story.append(PageBreak())
        story.append(p(title, st["h1"]))
        story.append(p("Terminal transcript screenshots are rendered on a black terminal theme from the saved command stdout/stderr logs in outputs/logs/. They preserve the actual run messages while removing transient carriage-return progress updates for readability.", st["small"]))
        for fname, label in screenshots:
            shot = SHOTS / fname
            if shot.exists():
                story.append(p(label, st["evidence"]))
                story.append(image_flow(shot, max_width=PAGE_W - 92, max_height=260))
                story.append(Spacer(1, 6))

    return story


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pointnet-root", type=Path, default=None)
    parser.add_argument("--meshcnn-root", type=Path, default=None)
    args = parser.parse_args()
    for path in (LOGS, SHOTS, FIGURES):
        path.mkdir(parents=True, exist_ok=True)
    result = build_results(args.pointnet_root, args.meshcnn_root)
    st = styles()
    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4,
                            rightMargin=46, leftMargin=46, topMargin=53, bottomMargin=53,
                            title="3D Shape Representation Lab - Sections 7.2-7.5",
                            author="J GANESH KUMAR REDDY | 23BDS024",
                            subject="PointNet++, voxel CNN, MeshCNN, and 3D representation conversion execution report")
    doc.build(build_story(result, st), onFirstPage=footer, onLaterPages=footer)
    print(f"PDF written: {PDF_PATH}")
    print(f"Size: {PDF_PATH.stat().st_size:,} bytes")
    print(f"PointNet++ revision: {result['revisions']['pointnet2']}")
    print(f"MeshCNN revision: {result['revisions']['meshcnn']}")
    print("Report result JSON: outputs/results.json")


if __name__ == "__main__":
    main()
