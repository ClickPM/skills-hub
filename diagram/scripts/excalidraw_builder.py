"""
Excalidraw Scene Builder — reusable library for generating Excalidraw files.

Usage:
    from excalidraw_builder import ExcalidrawBuilder

    b = ExcalidrawBuilder()
    b.box("my_box", 100, 200, 300, 80, "Hello\\nWorld", bg="#ffd43b", stroke="#e67700")
    b.label("my_label", 100, 180, "Section Title", font_size=14)
    b.arrow("a1", 250, 280, 250, 400, color="#1971c2")
    b.group_bg("bg1", 80, 170, 340, 130, stroke="#e67700")
    b.save("output.excalidraw.md")   # Preferred: native Obsidian format
    b.save("output.excalidraw")      # Legacy: pure JSON (auto-converted by plugin)

Output formats:
    .excalidraw.md — Obsidian-native markdown with embedded drawing data.
        Supports backlinks, search indexing, frontmatter metadata, and the
        "back of the note" feature. Recommended for all Obsidian vault usage.
    .excalidraw — Pure JSON, compatible with excalidraw.com. The Obsidian
        plugin auto-converts to .excalidraw.md on first save.

Key design decisions:
    1. Use roughness=0 for clean, professional diagrams.
    2. Use fontFamily=3 (monospace) for consistent CJK character rendering.
    3. Background rectangles (group_bg) must be added BEFORE content elements
       to ensure correct z-order (backgrounds behind content).
    4. All text elements include rawText and hasTextLink fields for plugin
       compatibility — prevents duplicate text rendering on format conversion.
    5. Container rectangles include customData for proper text wrapping.
"""
import json
import random


# Fractional index alphabet: 0-9, A-Z, a-z (62 chars)
_INDEX_CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def _make_index(n):
    """Generate a fractional index string for element ordering.

    Produces values like 'a0', 'a1', ..., 'a9', 'aA', ..., 'aZ', 'aa', ..., 'az',
    'b0', 'b1', ... matching the Excalidraw plugin's fractional indexing scheme.
    """
    prefix_idx = n // 62
    suffix_idx = n % 62
    prefix = _INDEX_CHARS[10 + prefix_idx]  # start at 'A' to avoid leading digits
    suffix = _INDEX_CHARS[suffix_idx]
    return f"{prefix}{suffix}"


class ExcalidrawBuilder:
    """Builder for Excalidraw scene files."""

    def __init__(self, seed=42):
        """Initialize with optional random seed for reproducible output."""
        random.seed(seed)
        self._bg_elements = []     # Background rectangles (rendered first / bottom z-layer)
        self._content_elements = [] # Content elements (rendered on top)
        self._arrow_elements = []   # Arrows (rendered last / top z-layer)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _seed(self):
        return random.randint(100000, 9999999)

    def _base_props(self, eid, etype, x, y, w, h, stroke, bg,
                    stroke_style="solid", roughness=0, opacity=100):
        """Common properties shared by all element types."""
        return {
            "id": eid, "type": etype,
            "x": x, "y": y, "width": w, "height": h,
            "angle": 0,
            "strokeColor": stroke,
            "backgroundColor": bg,
            "fillStyle": "solid",
            "strokeWidth": 2,
            "strokeStyle": stroke_style,
            "roughness": roughness,
            "opacity": opacity,
            "groupIds": [],
            "frameId": None,
            "roundness": {"type": 3} if etype == "rectangle" else
                         {"type": 2} if etype == "arrow" else None,
            "seed": self._seed(),
            "version": 2,
            "versionNonce": self._seed(),
            "isDeleted": False,
            "boundElements": None,
            "updated": 1710100000000,
            "link": None,
            "locked": False,
        }

    # ------------------------------------------------------------------
    # Public API — primitives
    # ------------------------------------------------------------------
    def rect(self, rid, x, y, w, h, bg, stroke,
             stroke_style="solid", opacity=100, bound_text_id=None):
        """Add a rectangle. Returns the element dict."""
        el = self._base_props(rid, "rectangle", x, y, w, h, stroke, bg,
                              stroke_style=stroke_style, opacity=opacity)
        el["boundElements"] = [{"id": bound_text_id, "type": "text"}] if bound_text_id else []
        if bound_text_id:
            el["customData"] = {"legacyTextWrap": True}
        el["hasTextLink"] = False
        self._content_elements.append(el)
        return el

    def text(self, tid, x, y, w, h, content, *,
             container_id=None, font_size=16, text_align="center",
             v_align="middle", stroke_color="#1e1e1e", font_family=3):
        """Add a text element. If container_id is set, it's bound text inside a rect."""
        el = self._base_props(tid, "text", x, y, w, h, stroke_color, "transparent")
        el["strokeWidth"] = 1
        el["roundness"] = None
        el.update({
            "text": content,
            "fontSize": font_size,
            "fontFamily": font_family,
            "textAlign": text_align,
            "verticalAlign": v_align,
            "containerId": container_id,
            "originalText": content,
            "autoResize": True,
            "lineHeight": 1.2,
            "hasTextLink": False,
            "rawText": content,
        })
        self._content_elements.append(el)
        return el

    def arrow_element(self, aid, x1, y1, x2, y2, color,
                      stroke_style="solid", start_arrow=None, end_arrow="arrow"):
        """Add an arrow from (x1,y1) to (x2,y2). Returns the element dict."""
        dx, dy = x2 - x1, y2 - y1
        el = self._base_props(aid, "arrow", x1, y1, abs(dx), abs(dy),
                              color, "transparent", stroke_style=stroke_style)
        el.update({
            "points": [[0, 0], [dx, dy]],
            "lastCommittedPoint": None,
            "startBinding": None,
            "endBinding": None,
            "startArrowhead": start_arrow,
            "endArrowhead": end_arrow,
            "hasTextLink": False,
        })
        self._arrow_elements.append(el)
        return el

    # ------------------------------------------------------------------
    # Public API — compound helpers
    # ------------------------------------------------------------------
    def box(self, prefix, x, y, w, h, content, bg, stroke, *,
            font_size=16, text_align="center", stroke_color="#1e1e1e",
            stroke_style="solid", font_family=3):
        """Add a rectangle with centered text inside (most common pattern).

        Creates two elements: rect_{prefix} and text_{prefix}.
        """
        rid = f"rect_{prefix}"
        tid = f"text_{prefix}"
        self.rect(rid, x, y, w, h, bg, stroke,
                  stroke_style=stroke_style, bound_text_id=tid)
        # Calculate vertical centering
        lines = content.count('\n') + 1
        line_h = font_size * 1.2
        th = lines * line_h
        ty = y + (h - th) / 2
        self.text(tid, x + 10, ty, w - 20, th, content,
                  container_id=rid, font_size=font_size,
                  text_align=text_align, stroke_color=stroke_color,
                  font_family=font_family)

    def label(self, prefix, x, y, content, *,
              font_size=15, stroke_color="#1e1e1e"):
        """Add a standalone text label (not bound to any rectangle)."""
        tid = f"lbl_{prefix}"
        w = len(content) * font_size * 0.7
        h = font_size * 1.3
        self.text(tid, x, y, w, h, content,
                  container_id=None, font_size=font_size,
                  text_align="left", v_align="top",
                  stroke_color=stroke_color)

    def group_bg(self, gid, x, y, w, h, stroke, *,
                 bg=None, stroke_style="dashed", opacity=30):
        """Add a background group rectangle (dashed border, low opacity).

        These are rendered BEHIND all content elements (bottom z-layer).
        If bg is None, a light tint is auto-derived from the stroke color.
        """
        if bg is None:
            bg = stroke  # fallback; caller should provide a light tint
        el = self._base_props(gid, "rectangle", x, y, w, h, stroke, bg,
                              stroke_style=stroke_style, opacity=opacity)
        el["boundElements"] = []
        el["hasTextLink"] = False
        self._bg_elements.append(el)
        return el

    def arrow(self, prefix, x1, y1, x2, y2, color, *,
              label_text=None, label_font_size=13,
              stroke_style="solid", start_arrow=None, bidirectional=False):
        """Add an arrow with optional label text near midpoint.

        If bidirectional=True, both ends get arrowheads.
        """
        start = "arrow" if bidirectional else start_arrow
        self.arrow_element(f"arr_{prefix}", x1, y1, x2, y2, color,
                           stroke_style=stroke_style,
                           start_arrow=start)
        if label_text:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2 - 15  # slightly above midpoint
            self.label(f"arr_{prefix}", mx, my, label_text,
                       font_size=label_font_size, stroke_color=color)

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def build_scene(self):
        """Build the complete Excalidraw scene dict.

        Element order determines z-layer: backgrounds first, content next, arrows last.
        Assigns fractional index to each element for proper ordering.
        """
        all_elements = self._bg_elements + self._content_elements + self._arrow_elements
        # Assign fractional indices for z-ordering
        for i, el in enumerate(all_elements):
            el["index"] = _make_index(i)
        return {
            "type": "excalidraw",
            "version": 2,
            "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin",
            "elements": all_elements,
            "appState": {
                "theme": "light",
                "viewBackgroundColor": "#ffffff",
                "gridSize": None,
            },
            "files": {},
        }

    def save(self, path, compress=False):
        """Save the scene. Format is auto-detected from file extension.

        .excalidraw.md — Obsidian-native markdown (recommended)
        .excalidraw     — Pure JSON (legacy, auto-converted by plugin on save)

        Args:
            compress: For .excalidraw.md only. If True, use LZ-String compression.
                      Default False for maximum compatibility.
        """
        if path.endswith(".excalidraw.md"):
            return self._save_md(path, compress=compress)
        return self._save_json(path)

    def _save_json(self, path):
        """Save as .excalidraw file (pure JSON)."""
        scene = self.build_scene()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(scene, f, ensure_ascii=False, indent=2)
        total = len(scene["elements"])
        print(f"Saved {total} elements to {path}")
        return total

    def _save_md(self, path, compress=False):
        """Save as .excalidraw.md file (Obsidian-native format).

        Structure: YAML frontmatter → warning text → Excalidraw Data heading →
        %% comment block containing Text Elements (empty) and Drawing JSON.

        The Text Elements section is left empty inside %%. The plugin auto-fills
        it on first save. Placing it outside %% causes visible ^id markers.

        Args:
            compress: If True, use LZ-String compression (requires lzstring).
                      If False (default), store raw JSON.
        """
        scene = self.build_scene()
        elements = scene.get("elements", [])
        scene_json = json.dumps(scene, ensure_ascii=False, indent="\t")

        if compress:
            try:
                from lzstring import LZString
                compact_json = json.dumps(scene, ensure_ascii=False, separators=(",", ":"))
                drawing_data = LZString.compressToBase64(compact_json)
                code_lang = "compressed-json"
            except ImportError:
                drawing_data = scene_json
                code_lang = "json"
        else:
            drawing_data = scene_json
            code_lang = "json"

        # Assemble the .excalidraw.md file
        # Both Text Elements and Drawing are inside %% comment block.
        # The plugin reads data from inside %%, while Obsidian won't render
        # the ^id block references as visible content.
        md_content = f"""---

excalidraw-plugin: parsed
tags: [excalidraw]

---
==\u26a0  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. \u26a0==


# Excalidraw Data

%%
## Text Elements

## Drawing
```{code_lang}
{drawing_data}
```
%%"""

        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)
        total = len(elements)
        print(f"Saved {total} elements to {path}")
        return total
