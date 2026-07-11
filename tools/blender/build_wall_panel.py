"""
SOVEREIGN//77 — BACKGROUND / MODULAR ASSET: Wall Panel (all acts).

A machined architecture panel that tiles edge-to-edge: raised graphite lands
separated by recessed machined seams, a central service channel holding a
subtle ceramic inlay and two thin cyan fiber runs, four machined bolts. The
outer margin is flush and the fibers run the full height, so panels butt in a
grid and the fiber runs stay continuous across stacked panels.

Named parts:  Panel, Inlay, Fiber, Bolts

Run:  python3 tools/blender/build_wall_panel.py [--render]
Out:  public/assets/models/wall_panel.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/wall_panel.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/wall_panel.png")

S.reset()
col = S.collection("WALL_PANEL")
m = S.mats()

W, TH, Hh = 1.20, 0.10, 1.20     # panel width (X), thickness (Y), height (Z)
FY = -TH / 2                     # front face plane (-Y toward room)


def count_tris():
    deps = bpy.context.evaluated_depsgraph_get()
    total = 0
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH":
            continue
        ev = obj.evaluated_get(deps)
        me = ev.to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        ev.to_mesh_clear()
    return total


# ===========================================================================
# PANEL — base slab + raised machined lands (the gaps between lands are the
# recessed seam lines) + a recessed central service channel.
# ===========================================================================
panel_parts = []

slab = S.box("WP_Slab", (W, TH, Hh), (0, 0, 0), col)
S.assign(slab, m["graphite"])
panel_parts.append(slab)

# Recessed central channel — a darker inset the inlay & fibers sit inside.
chan = S.box("WP_Channel", (0.30, 0.02, Hh - 0.10), (0, FY + 0.028, 0), col)
S.assign(chan, m["obsidian_matte"])
panel_parts.append(chan)

# Raised lands — 2 columns x 2 rows per side field (8 lands), fine seams.
land_defs = []
for fx in (-0.345, 0.345):                 # two side fields
    for lx in (-0.10, 0.10):               # two columns within a field
        for lz in (-0.285, 0.285):         # two rows
            land_defs.append((fx + lx, lz))
for i, (cx, cz) in enumerate(land_defs):
    land = S.box(f"WP_Land_{i}", (0.185, 0.022, 0.50), (cx, FY - 0.011, cz), col)
    S.assign(land, m["graphite_worn"])
    panel_parts.append(land)

# A thin machined border rail inside the flush margin (framed-panel read).
for (sx, sy, w, h) in [(0, 0.565, W - 0.10, 0.02), (0, -0.565, W - 0.10, 0.02),
                       (0.565, 0, 0.02, Hh - 0.10), (-0.565, 0, 0.02, Hh - 0.10)]:
    rail = S.box("WP_Rail", (w, 0.02, h), (sx, FY - 0.006, sy), col)
    S.assign(rail, m["graphite_light"])
    panel_parts.append(rail)

Panel = S.join_all(panel_parts, "Panel")
S.bevel(Panel, 0.006, 2)
S.weighted_normal(Panel)
S.shade_smooth(Panel)


# ===========================================================================
# INLAY — a subtle matte-ceramic strip down the service channel (restrained).
# ===========================================================================
inlay = S.box("Inlay", (0.028, 0.018, Hh - 0.16), (0, FY + 0.008, 0), col)
S.assign(inlay, m["ceramic_matte"])
Inlay = S.join_all([inlay], "Inlay")
S.bevel(Inlay, 0.003, 2)
S.shade_smooth(Inlay)


# ===========================================================================
# FIBER — two thin cyan fiber runs flanking the inlay, FULL height so stacked
# panels form continuous vertical fiber lines. Restrained (data_soft).
# ===========================================================================
fiber_parts = []
for sx in (-1, 1):
    fb = S.box(f"Fiber_{sx}", (0.012, 0.016, Hh), (sx * 0.095, FY + 0.004, 0), col)
    S.assign(fb, m["data_soft"])
    fiber_parts.append(fb)
Fiber = S.join_all(fiber_parts, "Fiber")
S.shade_smooth(Fiber)


# ===========================================================================
# BOLTS — four machined titanium fasteners at the field corners (joinery).
# ===========================================================================
bolt_parts = []
for bx in (-0.50, 0.50):
    for bz in (-0.50, 0.50):
        # A recessed socket ring + a proud fastener head → reads as machined.
        ring = S.tube(f"BoltRing_{bx}_{bz}", 0.045, 0.036, 0.02, 20,
                      (bx, FY - 0.002, bz), col)
        ring.rotation_euler = (math.radians(90), 0, 0)
        S.assign(ring, m["graphite_light"])
        bolt_parts.append(ring)
        b = S.cyl(f"Bolt_{bx}_{bz}", 0.03, 0.032, 14, (bx, FY - 0.012, bz), col)
        b.rotation_euler = (math.radians(90), 0, 0)
        S.assign(b, m["titanium_polish"])
        bolt_parts.append(b)
Bolts = S.join_all(bolt_parts, "Bolts")
S.bevel(Bolts, 0.002, 1)
S.shade_smooth(Bolts)

tris = count_tris()
print(f"[wall_panel] objects: {len(col.objects)}  tris: {tris}")
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Prove tiling: clone the single exported panel into a 2x2 grid (render
    # only — the GLB stays one panel), then frame the wall at a raking angle
    # so the machined seams read.
    base = list(col.objects)
    for (dx, dz) in [(W, 0), (0, Hh), (W, Hh)]:
        for o in base:
            d = o.copy()
            d.data = o.data
            d.location = (o.location.x + dx, o.location.y, o.location.z + dz)
            col.objects.link(d)
    S.lookdev_render(REF, cam_loc=(1.95, -3.6, 1.2), target=(0.58, 0, 0.6),
                     lens=44, samples=80, res=(1000, 900),
                     key_energy=760, rim_color=(0.06, 0.15, 0.16))
