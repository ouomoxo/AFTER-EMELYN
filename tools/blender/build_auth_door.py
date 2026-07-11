"""
SOVEREIGN//77 — HERO ASSET: Authentication Door + Iris (PROLOGUE / HANDSHAKE).

The "black screen" of the prologue is revealed to be this: a monolithic vault
door whose center is a surgical iris — the eye of the system. The user presses
and holds the core to authenticate; the two leaves then part and the camera is
pulled through.

Parts are kept as separate, named objects so the web runtime can animate them:
  Frame, Leaf_L, Leaf_R, Iris_Bezel, Iris_Ring_*, Blade_*, Core, CoreGroove.

Run:  python3 tools/blender/build_auth_door.py [--render]
Out:  public/assets/models/auth_door.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/auth_door.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/auth_door.png")

S.reset()
col = S.collection("AUTH_DOOR")
m = S.mats()

# --- Dimensions (metres). A vault door that dwarfs the subject. ---
W, H, T = 3.9, 5.4, 0.42          # single leaf
SEAM = 0.012                       # centre gap between leaves
IRIS_R = 0.92                      # iris outer radius

# ---------------------------------------------------------------------------
# Door leaves — machined slabs with concentric recessed detail toward centre.
# ---------------------------------------------------------------------------
def make_leaf(name, sign):
    """sign = -1 (left) / +1 (right). Centre edge sits at x = sign*SEAM/2."""
    parts = []
    # Main slab
    slab = S.box(f"{name}_Slab", (W, H, T), (sign * (W / 2 + SEAM / 2), 0, 0), col)
    S.assign(slab, m["graphite"])
    S.bevel(slab, 0.018, 2)
    parts.append(slab)

    # Deep face frame (recessed border) — inset rectangle rails
    rail_t = 0.16
    for (sx, sy, w, h) in [
        (0, H / 2 - 0.5, W - 0.7, rail_t),      # top rail
        (0, -H / 2 + 0.5, W - 0.7, rail_t),     # bottom rail
    ]:
        r = S.box(f"{name}_Rail", (w, h, 0.06),
                  (sign * (W / 2 + SEAM / 2) + sx, sy, T / 2), col)
        S.assign(r, m["graphite_worn"]); S.bevel(r, 0.006, 2)
        parts.append(r)

    # Vertical machined ribs (surgical repetition, not decoration)
    for i in range(4):
        rx = 0.55 + i * 0.62
        rib = S.box(f"{name}_Rib", (0.05, H - 1.6, 0.05),
                    (sign * (W / 2 + SEAM / 2) + sign * rx, 0, T / 2 + 0.01), col)
        S.assign(rib, m["titanium"]); S.bevel(rib, 0.004, 2)
        parts.append(rib)

    return parts

left = make_leaf("Leaf_L", -1)
right = make_leaf("Leaf_R", +1)

# Merge each leaf into one named object (web animates two leaves).
leaf_L = S.join_all(left, "Leaf_L")
S.weighted_normal(leaf_L); S.shade_smooth(leaf_L)
leaf_R = S.join_all(right, "Leaf_R")
S.weighted_normal(leaf_R); S.shade_smooth(leaf_R)

# ---------------------------------------------------------------------------
# Concentric recessed rings crossing the face, centred on the iris.
# These read as the "targeting" of the system — everything converges to centre.
# Split by the seam on purpose, reinforcing the two-leaf reading.
# ---------------------------------------------------------------------------
ring_objs = []
for i, rr in enumerate([1.35, 1.75, 2.2, 2.75]):
    ring = S.tube(f"FaceRing_{i}", rr, rr - 0.04, 0.05, 96, (0, 0, T / 2 + 0.005), col)
    S.assign(ring, m["titanium"] if i % 2 else m["graphite_worn"])
    S.shade_smooth(ring)
    ring_objs.append(ring)
face_rings = S.join_all(ring_objs, "FaceRings")

# ---------------------------------------------------------------------------
# THE IRIS — surgical aperture. The single center of the whole prologue.
# ---------------------------------------------------------------------------
iris_parts = []

# Outer bezel (heavy machined ring)
bezel = S.tube("Iris_Bezel", IRIS_R + 0.14, IRIS_R - 0.02, 0.22, 128,
               (0, 0, T / 2 + 0.02), col)
S.assign(bezel, m["titanium_polish"]); S.bevel(bezel, 0.01, 2); S.shade_smooth(bezel)
iris_parts.append(bezel)

# Concentric inner rings (digital-religion "altar" rings)
for i, rr in enumerate([IRIS_R - 0.06, IRIS_R - 0.16, IRIS_R - 0.24]):
    ir = S.tube(f"Iris_Ring_{i}", rr, rr - 0.03, 0.10 - i * 0.015, 96,
                (0, 0, T / 2 + 0.03), col)
    S.assign(ir, m["ceramic"] if i == 1 else m["graphite"])
    S.shade_smooth(ir)
    iris_parts.append(ir)

# A thin cyan data ring inset in the bezel (the only bright element)
data_ring = S.tube("Iris_DataRing", IRIS_R - 0.02, IRIS_R - 0.06, 0.03, 128,
                   (0, 0, T / 2 + 0.075), col)
S.assign(data_ring, m["data"]); S.shade_smooth(data_ring)

# Aperture blades — 8 overlapping wedges forming a closed surgical iris.
blades = []
NB = 8
for i in range(NB):
    ang = (i / NB) * math.tau
    bm = bmesh.new()
    # a thin curved-ish wedge blade
    verts = [
        bm.verts.new((-0.06, 0.0, 0)), bm.verts.new((0.06, 0.02, 0)),
        bm.verts.new((0.18, IRIS_R - 0.28, 0)), bm.verts.new((-0.14, IRIS_R - 0.30, 0)),
        bm.verts.new((-0.06, 0.0, 0.03)), bm.verts.new((0.06, 0.02, 0.03)),
        bm.verts.new((0.18, IRIS_R - 0.28, 0.03)), bm.verts.new((-0.14, IRIS_R - 0.30, 0.03)),
    ]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for f in faces:
        bm.faces.new([verts[k] for k in f])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    blade = S.bm_to_obj(bm, f"Blade_{i}", col)
    blade.rotation_euler = (0, 0, ang + 0.35)  # slight closed offset
    blade.location = (0, 0, T / 2 + 0.05)
    S.assign(blade, m["graphite_light"]); S.bevel(blade, 0.004, 2); S.shade_smooth(blade)
    blades.append(blade)
iris_blades = S.join_all(blades, "Iris_Blades")

# Core — recessed cyan disc, the press target. Kept as its own node ("Core").
core = S.cyl("Core", 0.30, 0.05, 64, (0, 0, T / 2 + 0.02), col)
S.assign(core, m["data"]); S.shade_smooth(core)
core_groove = S.tube("CoreGroove", 0.34, 0.30, 0.06, 64, (0, 0, T / 2 + 0.03), col)
S.assign(core_groove, m["obsidian_matte"]); S.shade_smooth(core_groove)

# Bolt ring around the bezel — surgical fasteners.
bolts = []
NBolt = 24
for i in range(NBolt):
    a = (i / NBolt) * math.tau
    bx, by = math.cos(a) * (IRIS_R + 0.24), math.sin(a) * (IRIS_R + 0.24)
    bolt = S.cyl(f"Bolt_{i}", 0.028, 0.06, 8, (bx, by, T / 2 + 0.02), col)
    S.assign(bolt, m["titanium"])
    bolts.append(bolt)
bolt_ring = S.join_all(bolts, "BoltRing"); S.shade_smooth(bolt_ring)

# Two small amber warning ticks (caution grammar — sparse, asymmetric).
for i, a in enumerate([math.radians(200), math.radians(340)]):
    tx, ty = math.cos(a) * (IRIS_R + 0.4), math.sin(a) * (IRIS_R + 0.4)
    tick = S.box(f"Warn_{i}", (0.14, 0.02, 0.01), (tx, ty, T / 2 + 0.03), col)
    S.assign(tick, m["warning"]); tick.rotation_euler = (0, 0, a)

print("[auth_door] objects:", len(col.objects))
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Face points +Z; view it near head-on from front-above for the hero read.
    S.lookdev_render(REF, cam_loc=(0.6, -3.4, 4.6), target=(0, 0, 0.2),
                     lens=55, samples=80, res=(1000, 660))
