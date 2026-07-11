"""
SOVEREIGN//77 — BACKGROUND ASSET: Fiber-Optic Junction Box / Conduit Node (ACT I).

A machined junction enclosure (bolted lid, titanium frame, cable glands) from
which bundled thin cyan fiber lines emerge and route away — the "nerves" of the
city machine. One dark protective conduit gives material contrast so the cyan
stays a read of *data*, not decoration. Fibers are beveled bezier curves
converted to mesh so they route organically.

Named parts:  Box, Fibers, Data

Run:  python3 tools/blender/build_fiber_box.py [--render]
Out:  public/assets/models/fiber_box.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/fiber_box.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/fiber_box.png")

S.reset()
col = S.collection("FIBER_BOX")
m = S.mats()

BW, BD, BH = 0.48, 0.26, 0.60       # box width, depth, height
FRONT = -BD / 2                     # lid faces -Y
BOTTOM = -BH / 2


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


def curve_tube(name, pts, radius, res_u=6):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = radius
    cu.bevel_resolution = 1
    cu.resolution_u = res_u
    sp = cu.splines.new("BEZIER")
    sp.bezier_points.add(len(pts) - 1)
    for i, p in enumerate(pts):
        bp = sp.bezier_points[i]
        bp.co = Vector(p)
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    obj = bpy.data.objects.new(name, cu)
    col.objects.link(obj)
    return obj


# ===========================================================================
# BOX — enclosure, bolted lid + titanium frame, hinges, cable glands.
# ===========================================================================
box_parts = []

body = S.box("FB_Body", (BW, BD, BH), (0, 0, 0), col)
S.assign(body, m["graphite"])
box_parts.append(body)

# Recessed machined lid (proud panel) + titanium frame border.
lid = S.box("FB_Lid", (BW - 0.10, 0.03, BH - 0.10), (0, FRONT - 0.012, 0), col)
S.assign(lid, m["graphite_worn"])
box_parts.append(lid)
for (sx, sz, w, h) in [(0, BH / 2 - 0.06, BW - 0.08, 0.022),
                       (0, -BH / 2 + 0.06, BW - 0.08, 0.022),
                       (BW / 2 - 0.055, 0, 0.022, BH - 0.10),
                       (-BW / 2 + 0.055, 0, 0.022, BH - 0.10)]:
    fr = S.box("FB_Frame", (w, 0.024, h), (sx, FRONT - 0.006, sz), col)
    S.assign(fr, m["titanium"])
    box_parts.append(fr)

# Lid bolts (socket ring + polished head) at the four corners.
for bx in (-0.17, 0.17):
    for bz in (-0.21, 0.21):
        ring = S.tube(f"FB_BoltRing_{bx}_{bz}", 0.03, 0.022, 0.016, 16,
                      (bx, FRONT - 0.004, bz), col)
        ring.rotation_euler = (math.radians(90), 0, 0)
        S.assign(ring, m["graphite_light"])
        box_parts.append(ring)
        head = S.cyl(f"FB_Bolt_{bx}_{bz}", 0.018, 0.024, 12,
                     (bx, FRONT - 0.014, bz), col)
        head.rotation_euler = (math.radians(90), 0, 0)
        S.assign(head, m["titanium_polish"])
        box_parts.append(head)

# Ceramic label plate (blank, matte, restrained) on the lid.
label = S.box("FB_Label", (0.13, 0.014, 0.05), (0, FRONT - 0.022, 0.02), col)
S.assign(label, m["ceramic_matte"])
box_parts.append(label)

# Two hinges on the +X side.
for hz in (-0.18, 0.18):
    hg = S.cyl(f"FB_Hinge_{hz}", 0.02, 0.08, 14, (BW / 2 + 0.01, FRONT + 0.02, hz), col)
    hg.rotation_euler = (0, 0, 0)
    S.assign(hg, m["titanium"])
    box_parts.append(hg)

# Cable glands on the bottom face — machined fittings the fibers emerge from.
GLANDS = [(-0.15, 0.0), (0.0, 0.02), (0.15, 0.0), (0.0, -0.06)]
for i, (gx, gy) in enumerate(GLANDS):
    collar = S.cyl(f"FB_GlandCollar_{i}", 0.042, 0.03, 18, (gx, gy, BOTTOM - 0.012), col)
    S.assign(collar, m["titanium"])
    box_parts.append(collar)
    nut = S.cyl(f"FB_GlandNut_{i}", 0.032, 0.05, 18, (gx, gy, BOTTOM - 0.045), col)
    S.assign(nut, m["graphite_light"])
    box_parts.append(nut)

Box = S.join_all(box_parts, "Box")
S.bevel(Box, 0.004, 2)
S.weighted_normal(Box)
S.shade_smooth(Box)


# ===========================================================================
# DATA — a small cyan status slot on the lid (restrained; the box is "live").
# ===========================================================================
slot = S.box("Data_Slot", (0.10, 0.014, 0.016), (0, FRONT - 0.024, -0.12), col)
S.assign(slot, m["data_soft"])
Data = S.join_all([slot], "Data")
S.bevel(Data, 0.003, 1)
S.shade_smooth(Data)


# ===========================================================================
# FIBERS — bundled thin cyan lines emerging from the glands and routing down &
# out (the nerves). One dark conduit per side for contrast (folded into Box's
# material family via rubber). Bezier tubes → mesh.
# ===========================================================================
fiber_objs = []
conduit_objs = []


def bundle(tag, gx, gy, direction, n=7, drop=0.42, spread=0.22):
    gz = BOTTOM - 0.07
    for i in range(n):
        t = (i / (n - 1)) - 0.5                     # -0.5 .. 0.5
        yd = (i % 3 - 1) * 0.06                      # Y depth → 3D bundle volume
        ex = gx + direction * spread * 0.55 + t * spread
        ey = gy + 0.02 + yd + abs(t) * 0.03
        ez = gz - (drop + (i % 2) * 0.07) - abs(t) * 0.05   # varied lengths
        mx = gx + direction * spread * 0.22 + t * spread * 0.35
        mz = gz - drop * 0.4
        pts = [(gx + t * 0.018, gy + yd * 0.25, gz + 0.02),
               (mx, gy + 0.02 + yd * 0.5, mz),
               (ex, ey, ez)]
        # ~1 strand in 4 is a dark, inactive fiber → cyan reads as *live* data.
        if i % 4 == 2:
            f = curve_tube(f"FBdark_{tag}_{i}", pts, 0.006)
            S.assign(f, m["rubber"])
            conduit_objs.append(f)
        else:
            f = curve_tube(f"Fiber_{tag}_{i}", pts, 0.0055)
            S.assign(f, m["data_soft"])
            fiber_objs.append(f)


bundle("L", -0.15, 0.0, -1.0, n=7, drop=0.44, spread=0.20)
bundle("C", 0.0, 0.02, 0.0, n=8, drop=0.54, spread=0.17)
bundle("R", 0.15, 0.0, 1.0, n=7, drop=0.44, spread=0.20)

# Two thick dark protective conduits drooping wide (material contrast, mass).
for k, (dirn, off) in enumerate([(-1.0, -0.02), (1.0, 0.02)]):
    gz = BOTTOM - 0.09
    pts = [(0.0 + off, -0.06, gz + 0.02),
           (dirn * 0.15, -0.05, gz - 0.22),
           (dirn * 0.32, 0.05, gz - 0.42)]
    cd = curve_tube(f"FB_Conduit_{k}", pts, 0.022, res_u=6)
    S.assign(cd, m["rubber"])
    conduit_objs.append(cd)

# Convert all curve tubes to mesh, then join.
bpy.context.view_layer.update()
bpy.ops.object.select_all(action="DESELECT")
for f in fiber_objs + conduit_objs:
    f.select_set(True)
bpy.context.view_layer.objects.active = fiber_objs[0]
bpy.ops.object.convert(target="MESH")

Fibers = S.join_all(fiber_objs, "Fibers")
S.shade_smooth(Fibers)
Conduit = S.join_all(conduit_objs, "Conduit")
S.shade_smooth(Conduit)

tris = count_tris()
print(f"[fiber_box] objects: {len(col.objects)}  tris: {tris}")
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Front 3/4, framed to read the enclosure and the fiber fan descending;
    # neutral rim (metal cold), the fibers/status carry the restrained cyan.
    S.lookdev_render(REF, cam_loc=(1.25, -1.75, 0.28), target=(0, 0, -0.28),
                     lens=52, samples=84, res=(860, 1000),
                     key_energy=760, rim_color=(0.06, 0.15, 0.16))
