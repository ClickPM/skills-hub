"""
Example: Generate an architecture diagram using ExcalidrawBuilder.

Demonstrates all major features:
  - box(): rectangle with centered text
  - group_bg(): dashed background group
  - label(): standalone text label
  - arrow(): arrow with label text
  - Color conventions for different element types

Run:
    python .claude/skills/diagram/scripts/example_architecture.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from excalidraw_builder import ExcalidrawBuilder

b = ExcalidrawBuilder(seed=42)

# ── Title ─────────────────────────────────────────────
b.text("title", 300, 20, 400, 40, "System Architecture Example",
       font_size=24, text_align="center", v_align="top", stroke_color="#1e1e1e")

# ── Group 1: Frontend (blue group) ────────────────────
b.group_bg("bg_fe", 50, 80, 400, 200, "#1971c2", bg="#d0ebff")
b.label("fe", 60, 88, "Frontend", font_size=14, stroke_color="#1971c2")

b.box("web",   70, 120, 170, 60, "Web App\n(React)", "#74c0fc", "#1971c2")
b.box("mobile", 260, 120, 170, 60, "Mobile App\n(React Native)", "#74c0fc", "#1971c2")

# ── Group 2: Backend (green group) ────────────────────
b.group_bg("bg_be", 50, 340, 400, 200, "#2f9e44", bg="#ebfbee")
b.label("be", 60, 348, "Backend", font_size=14, stroke_color="#2f9e44")

b.box("api",   70, 380, 170, 60, "API Server\n(Rust/Rocket)", "#b2f2bb", "#2f9e44")
b.box("worker", 260, 380, 170, 60, "Worker\n(Python)", "#b2f2bb", "#2f9e44")

# ── Group 3: Data (purple group) ──────────────────────
b.group_bg("bg_data", 520, 80, 280, 460, "#7048e8", bg="#f3f0ff")
b.label("data", 530, 88, "Data Layer", font_size=14, stroke_color="#7048e8")

b.box("db",    540, 130, 240, 60, "PostgreSQL", "#b197fc", "#7048e8")
b.box("cache", 540, 210, 240, 60, "Redis Cache", "#b197fc", "#7048e8")
b.box("queue", 540, 290, 240, 60, "Message Queue\n(RabbitMQ)", "#b197fc", "#7048e8")
b.box("s3",    540, 370, 240, 60, "Object Storage\n(S3/MinIO)", "#b197fc", "#7048e8")

# ── Arrows ────────────────────────────────────────────
b.arrow("fe_api", 250, 180, 155, 380, "#1971c2", label_text="REST API")
b.arrow("api_db", 240, 410, 540, 160, "#2f9e44", label_text="Query")
b.arrow("api_cache", 240, 400, 540, 240, "#2f9e44", label_text="Cache R/W")
b.arrow("worker_q", 345, 380, 540, 320, "#2f9e44", label_text="Consume")

# ── Save ──────────────────────────────────────────────
output = os.path.join(os.path.dirname(__file__), "example_output.excalidraw.md")
b.save(output)
print(f"Open in Obsidian Excalidraw plugin to view.")
