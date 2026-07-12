"""
SOVEREIGN//77 — HERO ASSET: Cybernetic Spine Module (ACT II / HUMAN REVISION).

Not a robot. Not armor. A surgical-grade spinal augmentation where medical
device, military hardware, and luxury industrial design converge — authored to
survive close 65–85mm inspection. It separates like an exploded medical diagram
into SIX named parts the web animates:

    Spinal_Interface    articulated machined vertebrae + hydraulic actuators
    Neural_Conductor    the cyan nervous system, branching to every segment
    Muscle_Layer        braided artificial musculature under tension
    Dermal_Shell_L/R    paneled ceramic covers (vent on L, service hatch on R)
    Memory_Coprocessor  the finned "brain" heatsink with a glass-windowed core

Every vertebra is a real anatomical machine: centrum, endplate facets, pedicles,
a posterior arch enclosing the neural foramen, a tapered spinous blade, transverse
arms ending in actuator clevises, and asymmetric medical hardware (sensor pods on
odd segments, connector stubs on even). The narrative anomaly lives in the DATA
(VOLUNTARY 41% / OVERRIDE 59%), never in the geometry.

Run:  python3 tools/blender/build_cybernetic_module.py [--render]
Out:  public/assets/models/cybernetic_module.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S
import sovereign_kit as K

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/cybernetic_module.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/cybernetic_module.png")

S.reset()
col = S.collection("CYBERNETIC")
m = S.mats()

# ---------------------------------------------------------------------------
# Spinal axis — a subtle anatomical S-curve along +Z (thoracic kyphosis +
# lumbar lordosis, dialed right down so the module still reads as engineered).
# ---------------------------------------------------------------------------
Z0, Z1, NV = 0.20, 1.52, 13

def spine_at(t):
    z = Z0 + (Z1 - Z0) * t
    y = 0.06 * math.sin(t * math.pi * 1.15) - 0.022 * math.sin(t * math.pi * 2.3)
    return Vector((0.0, y, z))

def tangent_at(t):
    a = spine_at(max(0.0, t - 0.02))
    b = spine_at(min(1.0, t + 0.02))
    return (b - a).normalized()

X = Vector((1, 0, 0))   # lateral (left / right)


# ===========================================================================
# LAYER — SPINAL INTERFACE : articulated vertebrae + hydraulic actuation
# ===========================================================================
spine_parts = []
clevis_pts = []   # (left, right) actuator anchor per vertebra, for the actuators

def spinous_blade(name, root, length, col, mat):
    """A tapered posterior blade pointing -Y and angling down, with a lightening
    slot implied by the bevel. Constant-section boxes read as toy; this tapers."""
    bm = bmesh.new()
    tip = root + Vector((0, -length, -length * 0.35))
    wb, wt = 0.020, 0.007     # half-width base / tip
    hb, ht = 0.030, 0.014     # half-height base / tip
    ring_b = [root + Vector((sx * wb, 0, sz * hb)) for sx, sz in
              ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    ring_t = [tip + Vector((sx * wt, 0, sz * ht)) for sx, sz in
              ((-1, -1), (1, -1), (1, 1), (-1, 1))]
    vb = [bm.verts.new(p) for p in ring_b]
    vt = [bm.verts.new(p) for p in ring_t]
    for k in range(4):
        bm.faces.new((vb[k], vb[(k + 1) % 4], vt[(k + 1) % 4], vt[k]))
    bm.faces.new(vb[::-1]); bm.faces.new(vt)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    S.assign(obj, mat); S.bevel(obj, 0.003, 2); S.shade_smooth(obj)
    return obj

for i in range(NV):
    t = i / (NV - 1)
    p = spine_at(t)
    tan = tangent_at(t)
    taper = 1.0 - 0.24 * t
    R = 0.055 * taper

    # --- centrum: a machined drum with a recessed circumferential groove ---
    body = S.cyl(f"Vbody{i}", R, 0.058, 48, tuple(p), col)
    body.rotation_euler = tan.to_track_quat("Z", "Y").to_euler()
    S.assign(body, m["titanium_polish"]); S.bevel(body, 0.004, 2)
    spine_parts.append(body)
    groove = S.tube(f"Vgrv{i}", R * 0.98, R * 0.86, 0.014, 48, tuple(p), col)
    groove.rotation_euler = body.rotation_euler
    S.assign(groove, m["obsidian_matte"])
    spine_parts.append(groove)
    # a bright bearing race seated in the groove (machined density)
    bearing = S.tube(f"Vbr{i}", R * 0.90, R * 0.84, 0.020, 48, tuple(p), col)
    bearing.rotation_euler = body.rotation_euler
    S.assign(bearing, m["titanium"]); S.bevel(bearing, 0.0016, 1)
    spine_parts.append(bearing)

    # --- endplate facets: ceramic articulation pads above & below, each ringed
    #     by a mounting flange + a bolt circle (mechanical density) ---
    for sz, tag in ((1, "sup"), (-1, "inf")):
        fp = p + tan * (sz * 0.032)
        facet = S.cyl(f"Vfac{i}{tag}", R * 1.06, 0.010, 48, tuple(fp), col)
        facet.rotation_euler = body.rotation_euler
        S.assign(facet, m["ceramic"]); S.bevel(facet, 0.003, 1)
        spine_parts.append(facet)
        flange = S.cyl(f"Vflg{i}{tag}", R * 1.16, 0.007, 48, tuple(fp + tan * (sz * 0.006)), col)
        flange.rotation_euler = body.rotation_euler
        S.assign(flange, m["graphite_light"]); S.bevel(flange, 0.0016, 1)
        spine_parts.append(flange)
        spine_parts += K.bolt_ring(f"Vfb{i}{tag}", tuple(fp + tan * (sz * 0.010)),
                                   tuple(tan * sz), R * 1.10, 10, col, m, r=0.004, head_h=0.004)

    # --- pedicles + posterior arch enclosing the neural foramen ---
    arch_c = p + Vector((0, -R * 1.7, 0))
    for s in (-1, 1):
        ped = K.oriented_box(f"Vped{i}_{s}", (0.014 * taper, 0.016),
                             p + Vector((s * R * 0.6, -R * 0.2, 0)),
                             arch_c + Vector((s * R * 0.55, 0, 0)), col, m["graphite"])
        S.bevel(ped, 0.003, 1)
        spine_parts.append(ped)
    # arch: a swept bar arcing around the back between the two pedicle tops
    arc = []
    for k in range(9):
        a = math.pi * (0.15 + 0.7 * (k / 8))   # sweep across the -Y rear
        arc.append(p + Vector((math.cos(a) * R * 0.95, -abs(math.sin(a)) * R * 1.9 - R * 0.1, 0)))
    arch = K.sweep_tube(f"Varch{i}", arc, 0.013 * taper, col, m["graphite_worn"], segs=8)
    if arch:
        spine_parts.append(arch)

    # --- spinous blade + its clamp bolt ---
    blade = spinous_blade(f"Vspin{i}", arch_c + Vector((0, -R * 0.2, 0)),
                          0.085 * taper, col, m["graphite"])
    spine_parts.append(blade)
    spine_parts += K.socket_cap(f"Vspb{i}", arch_c + Vector((0, -R * 0.15, 0.028)),
                                col, m, r=0.008, axis=(0, 0, 1))

    # --- transverse arms ending in actuator clevis pads (±X) ---
    lr = []
    for s in (-1, 1):
        end = p + Vector((s * R * 2.0, -R * 0.3, 0))
        arm = K.oriented_box(f"Vtrv{i}_{s}", (0.016 * taper, 0.020),
                            p + Vector((s * R * 0.7, -R * 0.2, 0)), end, col, m["graphite_worn"])
        S.bevel(arm, 0.003, 1)
        spine_parts.append(arm)
        clev = S.cyl(f"Vclv{i}_{s}", 0.014, 0.026, 12, tuple(end), col)
        clev.rotation_euler = X.to_track_quat("Z", "Y").to_euler()
        S.assign(clev, m["titanium"]); S.bevel(clev, 0.003, 1)
        spine_parts.append(clev)
        lr.append(end)
    clevis_pts.append((lr[0], lr[1]))

    # --- anterior fixation screws (+Y face) ---
    for s in (-1, 1):
        spine_parts += K.socket_cap(f"Vasc{i}_{s}", p + Vector((s * R * 0.5, R * 0.98, 0)),
                                    col, m, r=0.006, axis=(0, 1, 0))

    # --- posterolateral servo housing: machined box + mini heatsink + micro-bolts
    #     + a data connector. Alternating side; the biggest per-vertebra density. ---
    ss = 1 if i % 2 == 0 else -1
    sv = p + Vector((ss * R * 1.5, -R * 1.15, 0.028))
    sbox = S.box(f"Vsv{i}", (0.052, 0.040, 0.030), tuple(sv), col)
    S.assign(sbox, m["graphite"]); S.bevel(sbox, 0.003, 2)
    spine_parts.append(sbox)
    spine_parts += K.fin_stack(f"Vsvf{i}", sv + Vector((0, 0, 0.018)), X, Vector((0, 1, 0)),
                               7, 0.046, 0.012, 0.0022, 0.032, col, m["graphite_worn"])
    for bx in (-1, 1):
        for by in (-1, 1):
            spine_parts += K.hex_bolt(f"Vsvb{i}{bx}{by}",
                                      tuple(sv + Vector((bx * 0.022, by * 0.017, 0.016))),
                                      col, m, r=0.0032, head_h=0.0032, washer=False, axis=(0, 0, 1))
    spine_parts += K.connector_port(f"Vsvc{i}", tuple(sv + Vector((0, -0.024, 0.0))),
                                    col, m, r=0.013, depth=0.012, axis=(0, -1, 0), pins=5)

    # --- asymmetric medical hardware: sensor pod (odd) / connector stub (even) ---
    if i % 2 == 1:
        pod = p + Vector((R * 2.05, -R * 0.3, 0.03))
        dome = S.cyl(f"Vpod{i}", 0.018, 0.02, 16, tuple(pod), col)
        dome.rotation_euler = X.to_track_quat("Z", "Y").to_euler()
        S.assign(dome, m["obsidian"]); S.bevel(dome, 0.003, 2)
        lens = S.cyl(f"Vpodl{i}", 0.010, 0.006, 16, tuple(pod + X * 0.012), col)
        lens.rotation_euler = dome.rotation_euler
        S.assign(lens, m["data"])
        spine_parts += [dome, lens]
    else:
        spine_parts += K.connector_port(f"Vcon{i}", p + Vector((-R * 2.0, -R * 0.3, 0)),
                                        col, m, r=0.02, depth=0.016, axis=(-1, 0, 0), pins=5)

# --- hydraulic actuators zig-zagging between segments (biological asymmetry) ---
for i in range(NV - 1):
    a_lr = clevis_pts[i]
    b_lr = clevis_pts[i + 1]
    side = i % 2                      # alternate L/R down the column
    spine_parts += K.actuator(f"Act{i}", a_lr[side], b_lr[side], col, m, r=0.015)
    # a short rigid tie-rod on the opposite side keeps both flanks mechanical
    other = 1 - side
    rod = K.oriented_cyl(f"Tie{i}", 0.008, a_lr[other], b_lr[other], col, verts=10,
                        mat=m["titanium_polish"])
    spine_parts.append(rod)

# --- armored central conduit threading every foramen ---
conduit_pts = [spine_at(i / 44) for i in range(45)]
conduit = K.sweep_tube("Conduit", conduit_pts, 0.024, col, m["titanium"], segs=14)
if conduit:
    spine_parts.append(conduit)
# segmented armor rings on the conduit
for k in range(10):
    t = 0.04 + 0.92 * (k / 9)
    ring = S.tube(f"Carm{k}", 0.030, 0.024, 0.016, 20, tuple(spine_at(t)), col)
    ring.rotation_euler = tangent_at(t).to_track_quat("Z", "Y").to_euler()
    S.assign(ring, m["graphite_light"]); S.bevel(ring, 0.002, 1)
    spine_parts.append(ring)

# --- base mount: an anchored machined flange with a real bolt circle ---
base_p = spine_at(0.0) + Vector((0, 0, -0.05))
flange = S.cyl("Base_Flange", 0.17, 0.045, 40, tuple(base_p), col)
S.assign(flange, m["graphite"]); S.bevel(flange, 0.006, 2); S.shade_smooth(flange)
spine_parts.append(flange)
hub = S.cyl("Base_Hub", 0.10, 0.07, 32, tuple(base_p + Vector((0, 0, 0.03))), col)
S.assign(hub, m["titanium"]); S.bevel(hub, 0.005, 2)
spine_parts.append(hub)
for k in range(8):
    a = (k / 8) * math.tau
    bp = base_p + Vector((math.cos(a) * 0.14, math.sin(a) * 0.14, 0.024))
    spine_parts += K.hex_bolt(f"Basebolt{k}", tuple(bp), col, m, r=0.011, axis=(0, 0, 1))

# --- asymmetric medical interface cluster (upper +X flank) ---
cl_p = spine_at(0.72) + Vector((0.14, -0.02, 0))
for k, (dz, ang) in enumerate([(0.06, 0.0), (0.0, 0.25), (-0.06, -0.2)]):
    cp = cl_p + Vector((0, 0, dz))
    ax = (X * math.cos(ang) + Vector((0, 0, 1)) * math.sin(ang))
    spine_parts += K.connector_port(f"Med{k}", tuple(cp), col, m, r=0.026, depth=0.02,
                                    axis=tuple(ax), pins=7, live=(k == 1))
mount = K.oriented_box("MedMount", (0.05, 0.10), tuple(cl_p + Vector((-0.03, 0, 0.08))),
                      tuple(cl_p + Vector((-0.03, 0, -0.08))), col, m["graphite_light"])
S.bevel(mount, 0.004, 2)
spine_parts.append(mount)

spinal_interface = S.join_all(spine_parts, "Spinal_Interface")
S.weighted_normal(spinal_interface); S.shade_smooth(spinal_interface)


# ===========================================================================
# LAYER — NEURAL CONDUCTOR : cyan nervous system, branching to every segment
# ===========================================================================
neural_parts = []
core_line = K.sweep_tube("NeuralCore", [spine_at(i / 44) for i in range(45)],
                         0.011, col, m["data_soft"], segs=10)
if core_line:
    neural_parts.append(core_line)

# a branch from the core out to each vertebra's flank, ending in a node
for i in range(NV):
    t = i / (NV - 1)
    p = spine_at(t)
    s = 1 if i % 2 == 1 else -1
    br = [p + Vector((0, 0, 0)),
          p + Vector((s * 0.03, -0.01, 0.005)),
          p + Vector((s * 0.075, -0.015, 0.004)),
          p + Vector((s * R * 0 + s * 0.10, -0.02, 0.0))]
    branch = K.sweep_tube(f"Nbr{i}", br, lambda k, tt: 0.006 * (1 - 0.4 * tt),
                          col, m["data_soft"], segs=7)
    if branch:
        neural_parts.append(branch)
    node = S.cyl(f"Nnode{i}", 0.012, 0.010, 12, tuple(br[-1]), col)
    node.rotation_euler = X.to_track_quat("Z", "Y").to_euler()
    S.assign(node, m["data"])
    neural_parts.append(node)

# DENSE cyan cable harnesses running each flank — a woven bundle of many thin
# fibres with machined clamp collars, not a single fat filament.
for s in (-1, 1):
    def flank(tt, s=s):
        return spine_at(tt * 0.9 + 0.05) + Vector((s * 0.055, -0.03, 0))
    neural_parts += K.cable_bundle(f"Nbun{s}", flank, col, m, count=13, r=0.0032,
                                   spread=0.016, samples=34, mat=m["data_soft"], collars=6)

neural_conductor = S.join_all(neural_parts, "Neural_Conductor")
S.shade_smooth(neural_conductor)


# ===========================================================================
# LAYER — MUSCLE : braided artificial musculature under tension
# ===========================================================================
muscle_parts = []
NM = 6
for j in range(NM):
    ang0 = (j / NM) * math.tau
    def path(tt, ang0=ang0):
        cp = spine_at(tt * 0.9 + 0.05)
        # a slow spiral so strands cross like real fascicles
        ang = ang0 + tt * 0.9
        bulge = 0.125 + 0.028 * math.sin(tt * math.pi)
        return cp + Vector((math.cos(ang) * bulge, math.sin(ang) * bulge, 0))
    muscle_parts += K.braided_strand(f"Mus{j}", path, col, m, n_ply=3,
                                     ply_r=0.006, bundle_r=0.022, twist=5.0, samples=30)

# machined retaining clamps (band + two bolt tabs) at intervals
for bi, t in enumerate([0.20, 0.44, 0.68, 0.90]):
    p = spine_at(t)
    band = S.tube(f"Clamp{bi}", 0.158, 0.146, 0.026, 44, tuple(p), col)
    band.rotation_euler = tangent_at(t).to_track_quat("Z", "Y").to_euler()
    S.assign(band, m["graphite_light"]); S.bevel(band, 0.002, 1)
    muscle_parts.append(band)
    for s in (-1, 1):
        tab = S.box(f"Ctab{bi}_{s}", (0.02, 0.012, 0.03),
                    (p.x + s * 0.155, p.y, p.z), col)
        S.assign(tab, m["titanium"]); S.bevel(tab, 0.002, 1)
        muscle_parts.append(tab)
        muscle_parts += K.hex_bolt(f"Cbolt{bi}_{s}", (p.x + s * 0.168, p.y, p.z),
                                   col, m, r=0.007, axis=(s, 0, 0), washer=False)

# two pneumatic feed lines running the length, tucked posterolateral
for s in (-1, 1):
    pts = [spine_at(i / 24) + Vector((s * 0.10, -0.06, 0)) for i in range(25)]
    line = K.sweep_tube(f"Pneu_{s}", pts, 0.008, col, m["brass"], segs=8)
    if line:
        muscle_parts.append(line)

muscle_layer = S.join_all(muscle_parts, "Muscle_Layer")
S.weighted_normal(muscle_layer); S.shade_smooth(muscle_layer)


# ===========================================================================
# LAYER — DERMAL SHELL : paneled ceramic covers (3 panels/side, vent L / hatch R)
# ===========================================================================
def shell_panel(name, sign, z_lo, z_hi, mat):
    """One curved ceramic panel spanning ~140° on one flank, between z_lo..z_hi
    of the spine parameter, with bevelled edges."""
    bm = bmesh.new()
    R_out, R_in = 0.202, 0.188
    span = math.radians(140)
    base_ang = (math.pi / 2) if sign > 0 else (-math.pi / 2)
    segs, rows_n = 16, 12
    rows = []
    for idx in range(rows_n + 1):
        t = z_lo + (z_hi - z_lo) * (idx / rows_n)
        cp = spine_at(t)
        ro, ri = [], []
        for k in range(segs + 1):
            a = base_ang - span / 2 + span * (k / segs)
            ro.append(bm.verts.new((cp.x + math.cos(a) * R_out, cp.y + math.sin(a) * R_out, cp.z)))
            ri.append(bm.verts.new((cp.x + math.cos(a) * R_in, cp.y + math.sin(a) * R_in, cp.z)))
        rows.append((ro, ri))
    for idx in range(rows_n):
        (o0, i0), (o1, i1) = rows[idx], rows[idx + 1]
        for k in range(segs):
            bm.faces.new((o0[k], o0[k + 1], o1[k + 1], o1[k]))
            bm.faces.new((i0[k + 1], i0[k], i1[k], i1[k + 1]))
        bm.faces.new((o0[0], i0[0], i1[0], o1[0]))
        bm.faces.new((o0[segs], o1[segs], i1[segs], i0[segs]))
    (o0, i0) = rows[0]; (oe, ie) = rows[-1]
    for k in range(segs):
        bm.faces.new((o0[k], i0[k], i0[k + 1], o0[k + 1]))
        bm.faces.new((oe[k + 1], ie[k + 1], ie[k], oe[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    S.assign(obj, mat); S.bevel(obj, 0.004, 2); S.shade_smooth(obj)
    return obj

def shell_bolts(prefix, sign, zl, zh, mats, n=6):
    """A full ROW of countersunk fasteners down each of a panel's two vertical
    seam edges — dense, engineered joinery rather than a token pair."""
    out = []
    span = math.radians(140)
    base_ang = (math.pi / 2) if sign > 0 else (-math.pi / 2)
    for edge in (-1, 1):
        a = base_ang + edge * span / 2 * 0.93
        nrm = (math.cos(a), math.sin(a), 0)
        for j in range(n):
            t = zl + (zh - zl) * (j + 0.5) / n
            cp = spine_at(t)
            pos = (cp.x + math.cos(a) * 0.203, cp.y + math.sin(a) * 0.203, cp.z)
            out += K.hex_bolt(f"{prefix}_{edge}_{j}", pos, col, mats, r=0.005,
                              head_h=0.005, axis=nrm, washer=False)
    return out

def shell_on_surface_axes(sign, t):
    """Return (center, u_tangent, v_up, normal) on the shell surface at flank
    centre for placing vents/hatches flush to the curve."""
    base_ang = (math.pi / 2) if sign > 0 else (-math.pi / 2)
    cp = spine_at(t)
    n = Vector((math.cos(base_ang), math.sin(base_ang), 0))
    center = cp + n * 0.202
    u = Vector((-math.sin(base_ang), math.cos(base_ang), 0))
    v = Vector((0, 0, 1))
    return center, u, v, n

# --- LEFT shell (+X): 3 panels + a louvered vent in the mid panel ---
shellL_parts = []
zbands = [(0.06, 0.36), (0.37, 0.66), (0.67, 0.95)]
mat_variants = [m["ceramic"], m["ceramic_matte"], m["ceramic"]]
for pi, (zl, zh) in enumerate(zbands):
    shellL_parts.append(shell_panel(f"ShL_p{pi}", +1, zl, zh, mat_variants[pi]))
    shellL_parts += shell_bolts(f"ShLb{pi}", +1, zl, zh, m)
cV, uV, vV, nV = shell_on_surface_axes(+1, 0.5)
shellL_parts += K.vent_louvers("ShL_vent", cV, uV, vV, 0.10, 0.14, col, m, slats=6, tilt=0.5)
shell_L = S.join_all(shellL_parts, "Dermal_Shell_L")
S.weighted_normal(shell_L)

# --- RIGHT shell (−X): 3 panels + a recessed service hatch with a latch ---
shellR_parts = []
for pi, (zl, zh) in enumerate(zbands):
    shellR_parts.append(shell_panel(f"ShR_p{pi}", -1, zl, zh, mat_variants[(pi + 1) % 3]))
    shellR_parts += shell_bolts(f"ShRb{pi}", -1, zl, zh, m)
cH, uH, vH, nH = shell_on_surface_axes(-1, 0.5)
hatch = K._plate("ShR_hatch", cH + nH * 0.002, uH, vH, 0.11, 0.15, 0.012, col, m["graphite_light"])
shellR_parts.append(hatch)
latch = K._plate("ShR_latch", cH + nH * 0.012, uH, vH, 0.03, 0.02, 0.01, col, m["titanium"])
shellR_parts.append(latch)
for e in (-1, 1):
    shellR_parts += K.hex_bolt(f"ShR_hb{e}", tuple(cH + nH * 0.004 + vH * (e * 0.06)),
                               col, m, r=0.006, axis=tuple(nH), washer=False)
shell_R = S.join_all(shellR_parts, "Dermal_Shell_R")
S.weighted_normal(shell_R)


# ===========================================================================
# LAYER — MEMORY CO-PROCESSOR : finned heatsink + glass-windowed data core
# ===========================================================================
crown = spine_at(1.0)
mem_parts = []
# mounting collar to the crown
collar = S.tube("Mem_Collar", 0.11, 0.086, 0.05, 40, tuple(crown + Vector((0, 0, 0.05))), col)
S.assign(collar, m["titanium_polish"]); S.bevel(collar, 0.005, 2)
mem_parts.append(collar)
# machined housing with a recessed front bay
house_c = crown + Vector((0, -0.01, 0.20))
house = S.box("Mem_House", (0.20, 0.15, 0.15), tuple(house_c), col)
S.assign(house, m["titanium"]); S.bevel(house, 0.006, 2)
mem_parts.append(house)
# a graphite backplate the fins mount to
backplate = S.box("Mem_Back", (0.19, 0.02, 0.14), tuple(house_c + Vector((0, 0.085, 0))), col)
S.assign(backplate, m["graphite"]); S.bevel(backplate, 0.003, 1)
mem_parts.append(backplate)
# dense finned heatsink (28 fins) on the +Y crown, split into two combs
mem_parts += K.fin_stack("Mem_finA", house_c + Vector((0, 0.115, 0)), Vector((0, 0, 1)),
                         X, 28, 0.13, 0.05, 0.0022, 0.185, col, m["graphite_worn"], taper=0.15)
# a machined comb base + tie-bars over the fins
combbase = S.box("Mem_combbase", (0.185, 0.014, 0.14), tuple(house_c + Vector((0, 0.088, 0))), col)
S.assign(combbase, m["graphite"]); S.bevel(combbase, 0.003, 1)
mem_parts.append(combbase)
for tb in (-1, 1):
    bar = S.box(f"Mem_tie{tb}", (0.185, 0.008, 0.010), tuple(house_c + Vector((0, 0.16, tb * 0.055))), col)
    S.assign(bar, m["titanium"]); S.bevel(bar, 0.002, 1)
    mem_parts.append(bar)
# heat-pipe loops emerging from the sink
for hp in (-1, 1):
    pts = [house_c + Vector((hp * 0.06, 0.088, 0.05)), house_c + Vector((hp * 0.09, 0.15, 0.03)),
           house_c + Vector((hp * 0.07, 0.17, -0.02)), house_c + Vector((hp * 0.03, 0.15, -0.05))]
    pipe = K.sweep_tube(f"Mem_hp{hp}", pts, 0.006, col, m["titanium_polish"], segs=10)
    if pipe:
        mem_parts.append(pipe)
# A live emissive DISPLAY behind a machined bezel and a thin clear cover. (Deep
# smoked-glass-over-a-core went dead in AgX — an emissive screen reads in every
# renderer, and clear cover glass never filters the glow.)
ZAX = Vector((0, 0, 1))
bay = K._plate("Mem_Bay", house_c + Vector((0, -0.066, 0)), X, ZAX,
               0.15, 0.11, 0.004, col, m["obsidian_matte"])
mem_parts.append(bay)
# SMD detail on the bay floor, reading around the screen edges
for gx in range(5):
    for gz in range(3):
        sx = -0.058 + gx * 0.029
        sz = -0.034 + gz * 0.034
        smd = S.box(f"Mem_smd{gx}{gz}", (0.009, 0.006, 0.007),
                    tuple(house_c + Vector((sx, -0.069, sz))), col)
        S.assign(smd, m["brass"] if (gx + gz) % 2 else m["graphite_light"])
        mem_parts.append(smd)
core_bright = S.material("M_DataCore", S.PAL["cyan"], 0.0, 0.4,
                         emission=S.PAL["cyan"], emission_strength=5.0)
screen = K._plate("Mem_Screen", house_c + Vector((0, -0.072, 0)), X, ZAX,
                  0.126, 0.086, 0.003, col, core_bright)
mem_parts.append(screen)
# dark data traces across the screen so it reads as a display, not a lamp
for ti, tz in enumerate((-2, -1, 1, 2)):
    tr = S.box(f"Mem_tr{ti}", (0.11, 0.004, 0.0025),
               tuple(house_c + Vector((0, -0.074, tz * 0.018))), col)
    S.assign(tr, m["obsidian_matte"])
    mem_parts.append(tr)
# machined bezel frame around the screen
bez = [((0, 0.049), (0.15, 0.010)), ((0, -0.049), (0.15, 0.010)),
       ((0.070, 0), (0.012, 0.11)), ((-0.070, 0), (0.012, 0.11))]
for bi, ((ox, oz), (bw, bh)) in enumerate(bez):
    bz = K._plate(f"Mem_bez{bi}", house_c + Vector((ox, -0.078, oz)), X, ZAX,
                  bw, bh, 0.006, col, m["titanium"])
    mem_parts.append(bz)
# thin clear cover glass (sealed device) — near-clear so it never kills emission
clear_glass = S.material("M_ClearGlass", (0.85, 0.9, 0.9), 0.0, 0.03,
                         transmission=0.96, ior=1.5)
cover = K._plate("Mem_Cover", house_c + Vector((0, -0.081, 0)), X, ZAX,
                 0.148, 0.108, 0.002, col, clear_glass)
mem_parts.append(cover)
# side connector ports + corner fasteners
for s in (-1, 1):
    mem_parts += K.connector_port(f"Mem_port{s}", tuple(house_c + Vector((s * 0.10, -0.02, 0.03))),
                                  col, m, r=0.02, depth=0.016, axis=(s, 0, 0), pins=5)
for cxx in (-1, 1):
    for czz in (-1, 1):
        mem_parts += K.socket_cap(f"Mem_b{cxx}{czz}",
                                  tuple(house_c + Vector((cxx * 0.088, -0.078, czz * 0.06))),
                                  col, m, r=0.007, axis=(0, -1, 0))
memory = S.join_all(mem_parts, "Memory_Coprocessor")
S.weighted_normal(memory); S.shade_smooth(memory)


# ---------------------------------------------------------------------------
print("[cybernetic] parts:", [o.name for o in col.objects])
def tri_count():
    tot = 0
    for o in col.objects:
        d = o.data
        d.calc_loop_triangles()
        tot += len(d.loop_triangles)
    return tot
print("[cybernetic] triangles (post-join, pre-export):", tri_count())

size = S.export_glb(OUT, draco=True)   # exported in ASSEMBLED state
S.report(OUT, size)

if RENDER:
    offsets = {
        "Dermal_Shell_L": Vector((0.60, 0, 0)),
        "Dermal_Shell_R": Vector((-0.60, 0, 0)),
        "Muscle_Layer": Vector((0, -0.40, 0)),
        "Neural_Conductor": Vector((0, 0.22, 0)),
        "Memory_Coprocessor": Vector((0, 0, 0.42)),
    }
    for nm, off in offsets.items():
        o = bpy.data.objects.get(nm)
        if o:
            o.location = o.location + off
    # Cold-steel rim (not saturated cyan) so the render reads the METAL, not an
    # anodized cast — the scene supplies the real cyan data light at runtime.
    S.lookdev_render(REF, cam_loc=(1.9, -2.3, 1.15), target=(0, 0.0, 0.8),
                     lens=60, samples=100, res=(900, 1050),
                     rim_color=(0.34, 0.48, 0.52))
