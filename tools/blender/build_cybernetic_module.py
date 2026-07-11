"""
SOVEREIGN//77 — HERO ASSET: Cybernetic Spine Module (ACT II / HUMAN REVISION).

Not a robot. Not armor. A surgical-grade spinal augmentation module where
medical device, military hardware, and luxury industrial design converge. It
separates — like an exploded medical diagram — into FIVE named layers the web
animates outward:

    Dermal_Shell        outer ceramic covers (open first)
    Muscle_Layer        synthetic musculature strands
    Neural_Conductor    the cyan nervous system (restrained glow)
    Spinal_Interface    the machined vertebral core
    Memory_Coprocessor  the "brain" heatsink unit at the crown

The narrative anomaly lives in the data, not the model:
    VOLUNTARY CONTROL 41% / PREDICTIVE OVERRIDE 59%.

Run:  python3 tools/blender/build_cybernetic_module.py [--render]
Out:  public/assets/models/cybernetic_module.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/cybernetic_module.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/cybernetic_module.png")

S.reset()
col = S.collection("CYBERNETIC")
m = S.mats()

# --- Spine path: a subtle anatomical S-curve along +Z. ---
Z0, Z1, NV = 0.22, 1.46, 14
def spine_at(t):
    """t in [0,1] -> Vector on the spinal axis."""
    z = Z0 + (Z1 - Z0) * t
    # gentle double curve (thoracic kyphosis + lumbar lordosis, dialed way down)
    y = 0.05 * math.sin(t * math.pi * 1.15) - 0.02 * math.sin(t * math.pi * 2.2)
    return Vector((0.0, y, z))

# ===========================================================================
# LAYER 4 — SPINAL INTERFACE (the machined vertebral core)
# ===========================================================================
spine_parts = []
for i in range(NV):
    t = i / (NV - 1)
    p = spine_at(t)
    taper = 1.0 - 0.28 * t           # vertebrae shrink toward the crown
    # central hub (load-bearing, polished titanium)
    hub = S.cyl(f"Vh{i}", 0.052 * taper, 0.052, 24, tuple(p), col)
    S.assign(hub, m["titanium_polish"]); S.bevel(hub, 0.004, 2)
    spine_parts.append(hub)
    # ceramic flange disc (surgical white authority)
    fl = S.cyl(f"Vf{i}", 0.092 * taper, 0.016, 32, (p.x, p.y, p.z), col)
    S.assign(fl, m["ceramic"]); S.bevel(fl, 0.004, 2)
    spine_parts.append(fl)
    # posterior spinous process (points -Y)
    sp = S.box(f"Vp{i}", (0.03, 0.10 * taper, 0.03),
               (p.x, p.y - 0.075 * taper, p.z), col)
    S.assign(sp, m["graphite"]); S.bevel(sp, 0.004, 2)
    spine_parts.append(sp)
    # lateral transverse processes (±X) with small port ends
    for s in (-1, 1):
        tp = S.box(f"Vt{i}_{s}", (0.09 * taper, 0.028, 0.028),
                   (p.x + s * 0.075 * taper, p.y, p.z), col)
        S.assign(tp, m["graphite_worn"]); S.bevel(tp, 0.003, 2)
        spine_parts.append(tp)
    # intervertebral disc (dark, between segments)
    if i < NV - 1:
        pn = spine_at((i + 0.5) / (NV - 1))
        disc = S.cyl(f"Vd{i}", 0.058 * taper, 0.026, 24, tuple(pn), col)
        S.assign(disc, m["rubber"])
        spine_parts.append(disc)

# central conduit tube threading every vertebra
conduit_pts = [spine_at(i / 40) for i in range(41)]
bm = bmesh.new()
prev_ring = None
for idx, cp in enumerate(conduit_pts):
    ring = []
    for k in range(12):
        a = (k / 12) * math.tau
        ring.append(bm.verts.new((cp.x + math.cos(a) * 0.026,
                                  cp.y + math.sin(a) * 0.026, cp.z)))
    if prev_ring:
        for k in range(12):
            bm.faces.new((prev_ring[k], prev_ring[(k + 1) % 12],
                          ring[(k + 1) % 12], ring[k]))
    prev_ring = ring
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
conduit = S.bm_to_obj(bm, "Conduit", col)
S.assign(conduit, m["titanium"]); S.shade_smooth(conduit)
spine_parts.append(conduit)

base = S.cyl("Base_Mount", 0.16, 0.05, 48, (0, spine_at(0).y, Z0 - 0.06), col)
S.assign(base, m["graphite"]); S.bevel(base, 0.008, 2); S.shade_smooth(base)
spine_parts.append(base)

spinal_interface = S.join_all(spine_parts, "Spinal_Interface")
S.weighted_normal(spinal_interface); S.shade_smooth(spinal_interface)

# ===========================================================================
# LAYER 3 — NEURAL CONDUCTOR (the cyan nervous system; restrained)
# ===========================================================================
neural_parts = []
# central cyan filament inside the conduit
bm = bmesh.new()
prev = None
for idx, cp in enumerate(conduit_pts):
    ring = []
    for k in range(8):
        a = (k / 8) * math.tau
        ring.append(bm.verts.new((cp.x + math.cos(a) * 0.012,
                                  cp.y + math.sin(a) * 0.012, cp.z)))
    if prev:
        for k in range(8):
            bm.faces.new((prev[k], prev[(k + 1) % 8], ring[(k + 1) % 8], ring[k]))
    prev = ring
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
core_line = S.bm_to_obj(bm, "NeuralCore", col)
S.assign(core_line, m["data_soft"]); S.shade_smooth(core_line)
neural_parts.append(core_line)

# external filaments running along the spine with nodes at each vertebra
for s in (-1, 1):
    bm = bmesh.new(); prev = None
    for idx in range(41):
        t = idx / 40
        cp = spine_at(t)
        off = Vector((s * 0.058, -0.02, 0))
        c = cp + off
        ring = []
        for k in range(6):
            a = (k / 6) * math.tau
            ring.append(bm.verts.new((c.x + math.cos(a) * 0.007,
                                      c.y + math.sin(a) * 0.007, c.z)))
        if prev:
            for k in range(6):
                bm.faces.new((prev[k], prev[(k + 1) % 6], ring[(k + 1) % 6], ring[k]))
        prev = ring
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    fil = S.bm_to_obj(bm, f"NeuralFil_{s}", col)
    S.assign(fil, m["data_soft"]); S.shade_smooth(fil)
    neural_parts.append(fil)

for i in range(NV):
    t = i / (NV - 1); p = spine_at(t)
    node = S.cyl(f"Nn{i}", 0.014, 0.012, 10, (p.x, p.y - 0.02, p.z), col)
    S.assign(node, m["data"])
    neural_parts.append(node)

neural_conductor = S.join_all(neural_parts, "Neural_Conductor")
S.shade_smooth(neural_conductor)

# ===========================================================================
# LAYER 2 — MUSCLE LAYER (synthetic musculature strands)
# ===========================================================================
muscle_parts = []
NM = 7
for j in range(NM):
    ang = (j / NM) * math.tau
    bm = bmesh.new(); prev = None
    for idx in range(31):
        t = idx / 30
        cp = spine_at(t)
        # strand bulges mid-length like real muscle
        bulge = 0.135 + 0.03 * math.sin(t * math.pi)
        c = cp + Vector((math.cos(ang) * bulge, math.sin(ang) * bulge, 0))
        r = 0.016 + 0.010 * math.sin(t * math.pi)
        ring = []
        for k in range(8):
            a = (k / 8) * math.tau
            ring.append(bm.verts.new((c.x + math.cos(a) * r,
                                      c.y + math.sin(a) * r, c.z)))
        if prev:
            for k in range(8):
                bm.faces.new((prev[k], prev[(k + 1) % 8], ring[(k + 1) % 8], ring[k]))
        prev = ring
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    strand = S.bm_to_obj(bm, f"Muscle_{j}", col)
    S.assign(strand, m["rubber"]); S.shade_smooth(strand)
    muscle_parts.append(strand)

# retaining bands wrapping the muscle bundle at intervals
for bi, t in enumerate([0.18, 0.42, 0.66, 0.88]):
    p = spine_at(t)
    band = S.tube(f"Band_{bi}", 0.165, 0.150, 0.03, 40, (p.x, p.y, p.z), col)
    S.assign(band, m["graphite_light"]); S.shade_smooth(band)
    muscle_parts.append(band)

muscle_layer = S.join_all(muscle_parts, "Muscle_Layer")
S.weighted_normal(muscle_layer); S.shade_smooth(muscle_layer)

# ===========================================================================
# LAYER 1 — DERMAL SHELL (outer ceramic covers, two halves)
# ===========================================================================
def shell_half(name, sign):
    """A curved ceramic plate spanning ~150° on one side of the spine."""
    bm = bmesh.new()
    R_out, R_in = 0.205, 0.190
    span = math.radians(150)
    base_ang = (math.pi / 2) if sign > 0 else (-math.pi / 2)
    segs = 18
    rows = []
    for idx in range(29):
        t = idx / 28
        cp = spine_at(t * 0.92 + 0.04)
        row_out, row_in = [], []
        for k in range(segs + 1):
            a = base_ang - span / 2 + span * (k / segs)
            row_out.append(bm.verts.new((cp.x + math.cos(a) * R_out,
                                         cp.y + math.sin(a) * R_out, cp.z)))
            row_in.append(bm.verts.new((cp.x + math.cos(a) * R_in,
                                        cp.y + math.sin(a) * R_in, cp.z)))
        rows.append((row_out, row_in))
    for idx in range(28):
        (o0, i0), (o1, i1) = rows[idx], rows[idx + 1]
        for k in range(segs):
            bm.faces.new((o0[k], o0[k + 1], o1[k + 1], o1[k]))       # outer
            bm.faces.new((i0[k + 1], i0[k], i1[k], i1[k + 1]))       # inner
        # side rims
        bm.faces.new((o0[0], i0[0], i1[0], o1[0]))
        bm.faces.new((o0[segs], o1[segs], i1[segs], i0[segs]))
    # cap the ends
    (o0, i0) = rows[0]; (oe, ie) = rows[-1]
    for k in range(segs):
        bm.faces.new((o0[k], i0[k], i0[k + 1], o0[k + 1]))
        bm.faces.new((oe[k + 1], ie[k + 1], ie[k], oe[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    S.assign(obj, m["ceramic"]); S.bevel(obj, 0.004, 2); S.shade_smooth(obj)
    return obj

# Kept as two SEPARATE named halves so the web can split them open (L→+X, R→−X).
shell_L = shell_half("Dermal_Shell_L", +1)
S.weighted_normal(shell_L)
shell_R = shell_half("Dermal_Shell_R", -1)
S.weighted_normal(shell_R)

# ===========================================================================
# LAYER 5 — MEMORY CO-PROCESSOR (the "brain" heatsink at the crown)
# ===========================================================================
crown = spine_at(1.0)
mem_parts = []
# cranial mounting collar
collar = S.tube("Cranial_Collar", 0.11, 0.085, 0.05, 40,
                (crown.x, crown.y, crown.z + 0.06), col)
S.assign(collar, m["titanium_polish"]); S.bevel(collar, 0.005, 2)
mem_parts.append(collar)
# housing
house = S.box("MemHouse", (0.17, 0.13, 0.14), (crown.x, crown.y - 0.02, crown.z + 0.20), col)
S.assign(house, m["titanium"]); S.bevel(house, 0.006, 2)
mem_parts.append(house)
# heatsink fins on top
for fi in range(9):
    fin = S.box(f"Fin_{fi}", (0.15, 0.008, 0.05),
                (crown.x, crown.y - 0.06 + fi * 0.015, crown.z + 0.30), col)
    S.assign(fin, m["graphite_worn"])
    mem_parts.append(fin)
# smoked glass window (front) + inner data core
win = S.box("MemWindow", (0.12, 0.008, 0.09), (crown.x, crown.y - 0.088, crown.z + 0.19), col)
S.assign(win, m["glass"])
mem_parts.append(win)
core = S.box("MemCore", (0.09, 0.03, 0.06), (crown.x, crown.y - 0.03, crown.z + 0.19), col)
S.assign(core, m["data"])
mem_parts.append(core)
memory = S.join_all(mem_parts, "Memory_Coprocessor")
S.weighted_normal(memory); S.shade_smooth(memory)

print("[cybernetic] objects:", len(col.objects),
      "->", [o.name for o in col.objects])
size = S.export_glb(OUT, draco=True)   # exported in ASSEMBLED state
S.report(OUT, size)

if RENDER:
    # Reference frame shows the EXPLODED layers so interior craft is verifiable.
    # (Export already happened above, so moving objects here is render-only.)
    offsets = {
        "Dermal_Shell_L": Vector((0.55, 0, 0)),
        "Dermal_Shell_R": Vector((-0.55, 0, 0)),
        "Muscle_Layer": Vector((0, -0.34, 0)),
        "Neural_Conductor": Vector((0, 0.20, 0)),
        "Memory_Coprocessor": Vector((0, 0, 0.34)),
    }
    for nm, off in offsets.items():
        o = bpy.data.objects.get(nm)
        if o:
            o.location = o.location + off
    S.lookdev_render(REF, cam_loc=(1.9, -2.3, 1.2), target=(0, 0.0, 0.8),
                     lens=58, samples=90, res=(900, 1000))
