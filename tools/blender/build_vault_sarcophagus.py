"""
SOVEREIGN//77 — HERO ASSET: Vault Sarcophagus (ACT IV / BLACK VAULT).

The central data-coffin of a black-stone sanctuary. The most advanced place
looks the most quiet and classical: a long low obsidian monolith on a stepped
plinth, framed by a thin precise titanium baldachin, sealed with a machined lid.
It is a reliquary that WORSHIPS data, not a server. Its power is silence and
symmetry; the only living light is a single restrained cyan thread at the seam
and the sealed core glowing under the lid.

Parts kept as separate, named objects so the web runtime can animate them:
  Plinth, Sarcophagus, Lid (opens), SealedCore (revealed), Frame, Ritual, Fibers.

Run:  python3 tools/blender/build_vault_sarcophagus.py [--render]
Out:  public/assets/models/vault_sarcophagus.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector, Matrix  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/vault_sarcophagus.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/vault_sarcophagus.png")

S.reset()
col = S.collection("VAULT_SARCOPHAGUS")
m = S.mats()


# ---------------------------------------------------------------------------
# Local helpers.
# ---------------------------------------------------------------------------
def trough(name, size, wall, depth, loc, col):
    """A block with a rectangular cavity carved from its top face (a coffin)."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts)
    top = max(bm.faces, key=lambda f: f.calc_center_median().z)
    res = bmesh.ops.inset_individual(bm, faces=[top], thickness=wall, depth=0.0)
    ext = bmesh.ops.extrude_face_region(bm, geom=[top])
    vlist = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, vec=Vector((0, 0, -depth)), verts=vlist)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    obj.location = loc
    return obj


def fluted_column(name, R, height, flutes, seg_per_flute, z_segs, depth, loc, col):
    """A slender fluted column shaft (classical, high-poly, reads as machined)."""
    samples = flutes * seg_per_flute
    bm = bmesh.new()
    rings = []
    for zi in range(z_segs + 1):
        z = -height / 2 + height * zi / z_segs
        loop = []
        for k in range(samples):
            th = (k / samples) * math.tau
            r = R - depth * (0.5 + 0.5 * math.cos(flutes * th))
            loop.append(bm.verts.new((math.cos(th) * r, math.sin(th) * r, z)))
        rings.append(loop)
    for zi in range(z_segs):
        a, b = rings[zi], rings[zi + 1]
        for k in range(samples):
            bm.faces.new((a[k], a[(k + 1) % samples], b[(k + 1) % samples], b[k]))
    for loop, zc, flip in ((rings[0], -height / 2, True), (rings[-1], height / 2, False)):
        c = bm.verts.new((0, 0, zc))
        for k in range(samples):
            v1, v2 = loop[k], loop[(k + 1) % samples]
            bm.faces.new((c, v2, v1) if flip else (c, v1, v2))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = S.bm_to_obj(bm, name, col)
    o.location = loc
    return o


def dentils(name, span_x, span_y, z, block, gap, col, mat, height):
    """A classical dentil course: repeated small blocks around a rectangle."""
    bm = bmesh.new()
    step = block + gap
    def place(cx, cy, w, d):
        r = bmesh.ops.create_cube(bm, size=1.0)["verts"]
        bmesh.ops.scale(bm, vec=Vector((w, d, height)), verts=r)
        bmesh.ops.translate(bm, vec=Vector((cx, cy, 0)), verts=r)
    nx = int(span_x / step)
    ny = int(span_y / step)
    for i in range(nx + 1):
        x = -nx * step / 2 + i * step
        place(x, span_y / 2, block, block)
        place(x, -span_y / 2, block, block)
    for j in range(1, ny):
        y = -ny * step / 2 + j * step
        place(span_x / 2, y, block, block)
        place(-span_x / 2, y, block, block)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = S.bm_to_obj(bm, name, col)
    o.location = (0, 0, z)
    S.assign(o, mat)
    return o


# ---------------------------------------------------------------------------
# STEPPED PLINTH — classical, deliberately symmetric. Dark basalt going matte
# toward the floor, a machined obsidian top course. A dentil cornice reads as
# a temple base (reverent), not a machine housing.
# ---------------------------------------------------------------------------
plinth_parts = []
z = 0.0
steps = [
    ((4.30, 2.55, 0.26), m["obsidian_matte"]),
    ((3.78, 2.08, 0.22), m["obsidian_matte"]),
    ((3.34, 1.74, 0.22), m["obsidian"]),
]
for i, (sz, mat) in enumerate(steps):
    b = S.box(f"Plinth_Step_{i}", sz, (0, 0, z + sz[2] / 2), col)
    S.assign(b, mat); S.bevel(b, 0.012, 4); S.apply_modifiers(b)
    plinth_parts.append(b)
    # A thin machined reveal molding capping each step edge (classical profile).
    rv = S.box(f"Plinth_Reveal_{i}", (sz[0] + 0.03, sz[1] + 0.03, 0.03),
               (0, 0, z + sz[2] - 0.02), col)
    S.assign(rv, m["graphite"]); S.bevel(rv, 0.006, 3); S.apply_modifiers(rv)
    plinth_parts.append(rv)
    z += sz[2]
PLINTH_TOP = z    # top surface of the plinth

# A classical dentil cornice tucked under the top step's overhang (temple base).
# Square, evenly-spaced teeth read as reverent stonework, never as machine vents.
dent = dentils("Plinth_Dentils", 3.5, 1.9, PLINTH_TOP - 0.30, 0.055, 0.05,
               col, m["graphite"], 0.09)
plinth_parts.append(dent)

plinth = S.join_all(plinth_parts, "Plinth")
S.weighted_normal(plinth); S.shade_smooth(plinth)


# ---------------------------------------------------------------------------
# SARCOPHAGUS BODY — a long low obsidian monolith with a carved cavity. Classical
# proportions (~2.3 : 1). Machined bevels. A faint oxidized-brass band girdles
# it; thin brass inlays run its length. Symmetry throughout.
# ---------------------------------------------------------------------------
BODY = (2.72, 1.22, 0.82)
WALL, CAV_DEPTH = 0.13, 0.56
BODY_Z = PLINTH_TOP + BODY[2] / 2
body = trough("Sarcophagus", BODY, WALL, CAV_DEPTH, (0, 0, BODY_Z), col)
S.assign(body, m["obsidian"]); S.bevel(body, 0.018, 4)
S.shade_smooth(body); S.apply_modifiers(body)
body_parts = [body]

BODY_TOP = PLINTH_TOP + BODY[2]

# Oxidized-brass girdle band low on the body (ceremonial, restrained).
for zz in (BODY_Z - 0.20,):
    for sy in (1, -1):
        band = S.box("Body_BrassBand", (BODY[0] + 0.006, 0.028, 0.05),
                     (0, sy * (BODY[1] / 2 + 0.003), zz), col)
        S.assign(band, m["brass"]); S.bevel(band, 0.004, 2)
        S.apply_modifiers(band); body_parts.append(band)
    for sx in (1, -1):
        band = S.box("Body_BrassBand", (0.028, BODY[1] + 0.006, 0.05),
                     (sx * (BODY[0] / 2 + 0.003), 0, zz), col)
        S.assign(band, m["brass"]); S.bevel(band, 0.004, 2)
        S.apply_modifiers(band); body_parts.append(band)

# Dentil entablature under the lid overhang — a classical frieze that quietly
# crowns the coffin (and, being finely repeated, carries real machined density).
frieze = dentils("Body_Frieze", BODY[0] - 0.02, BODY[1] - 0.02, BODY_TOP - 0.07,
                 0.05, 0.045, col, m["graphite"], 0.06)
body_parts.append(frieze)

# Framed relief panels sunk into the long faces — classical, symmetric. A matte
# recessed field bordered by a thin titanium reveal (surgical joinery).
for sy in (1, -1):
    yface = sy * (BODY[1] / 2 + 0.002)
    field = S.box("Body_Panel", (BODY[0] - 0.62, 0.02, BODY[2] - 0.40),
                  (0, yface, BODY_Z - 0.02), col)
    S.assign(field, m["obsidian_matte"]); body_parts.append(field)
    fw, fh = BODY[0] - 0.54, BODY[2] - 0.32
    for (w, h, oz) in [(fw, 0.028, fh / 2), (fw, 0.028, -fh / 2)]:
        r = S.box("Body_PanelFrame", (w, 0.03, h),
                  (0, yface, BODY_Z - 0.02 + oz), col)
        S.assign(r, m["titanium"]); S.bevel(r, 0.003, 2)
        S.apply_modifiers(r); body_parts.append(r)
    for ox in (fw / 2, -fw / 2):
        r = S.box("Body_PanelFrame", (0.028, 0.03, fh),
                  (ox, yface, BODY_Z - 0.02), col)
        S.assign(r, m["titanium"]); S.bevel(r, 0.003, 2)
        S.apply_modifiers(r); body_parts.append(r)

# Engaged fluted colonnettes at the coffin's four vertical corners — a classical
# corner treatment (like a tomb's corner columns). Real, subsurf-smoothed stone,
# baked so it survives the join: it enriches the plain corners and carries mass.
COLN_H = BODY[2] - 0.04
for sx in (1, -1):
    for sy in (1, -1):
        cn = fluted_column("Body_Colonnette", 0.075, COLN_H, 14, 8, 8, 0.010,
                           (sx * (BODY[0] / 2 - 0.015), sy * (BODY[1] / 2 - 0.015),
                            BODY_Z), col)
        S.assign(cn, m["obsidian"]); S.shade_smooth(cn)
        S.subsurf(cn, 1, 1); S.apply_modifiers(cn)
        body_parts.append(cn)
        # A thin oxidized-brass ring astragal near the top of each colonnette.
        ring = S.tube("Body_ColRing", 0.088, 0.072, 0.03, 32,
                      (sx * (BODY[0] / 2 - 0.015), sy * (BODY[1] / 2 - 0.015),
                       BODY_Z + COLN_H / 2 - 0.06), col)
        S.assign(ring, m["brass"]); S.shade_smooth(ring)
        S.apply_modifiers(ring); body_parts.append(ring)

body = S.join_all(body_parts, "Sarcophagus")

# ---------------------------------------------------------------------------
# SEALED CORE — the cavity floor and a thin cyan data grid at its bottom. This
# is the reliquary's heart, sealed under the lid; the web reveals it on open.
# ---------------------------------------------------------------------------
core_parts = []
CAV_FLOOR_Z = BODY_TOP - CAV_DEPTH + 0.02
floor = S.box("SealedCore_Floor",
              (BODY[0] - 2 * WALL - 0.02, BODY[1] - 2 * WALL - 0.02, 0.03),
              (0, 0, CAV_FLOOR_Z), col)
S.assign(floor, m["obsidian_matte"]); S.bevel(floor, 0.004, 2)
core_parts.append(floor)
# A restrained cyan grid — few lines, dark data. Sealed, so it can be a grid.
gx = BODY[0] - 2 * WALL - 0.08
gy = BODY[1] - 2 * WALL - 0.08
for i in range(5):
    x = -gx / 2 + i * gx / 4
    ln = S.box(f"SealedCore_Lx_{i}", (0.012, gy, 0.012),
               (x, 0, CAV_FLOOR_Z + 0.022), col)
    S.assign(ln, m["data"]); core_parts.append(ln)
for j in range(3):
    y = -gy / 2 + j * gy / 2
    ln = S.box(f"SealedCore_Ly_{j}", (gx, 0.012, 0.012),
               (0, y, CAV_FLOOR_Z + 0.022), col)
    S.assign(ln, m["data"]); core_parts.append(ln)
sealed = S.join_all(core_parts, "SealedCore")
S.shade_smooth(sealed)

# A single restrained cyan seam thread in the rim gap under the lid overhang —
# a whisper of light from a sealed reliquary (data_soft, very thin, recessed).
seam_parts = []
for sy in (1, -1):
    br = S.box("Seam_bar", (BODY[0] - 0.16, 0.012, 0.014),
               (0, sy * (BODY[1] / 2 - 0.05), BODY_TOP - 0.002), col)
    S.assign(br, m["data_soft"]); seam_parts.append(br)
for sx in (1, -1):
    br = S.box("Seam_bar", (0.012, BODY[1] - 0.16, 0.014),
               (sx * (BODY[0] / 2 - 0.05), 0, BODY_TOP - 0.002), col)
    S.assign(br, m["data_soft"]); seam_parts.append(br)
seam = S.join_all(seam_parts, "Seam"); S.shade_smooth(seam)
sealed = S.join_all([sealed, seam], "SealedCore")


# ---------------------------------------------------------------------------
# LID — a separate machined obsidian slab (the web opens it). A recessed centre
# panel framed by oxidized brass; a small smoked-glass viewing port at the head
# through which the sealed core faintly reads. Deliberately symmetric.
# ---------------------------------------------------------------------------
LID = (BODY[0] - 0.10, BODY[1] - 0.10, 0.20)
LID_Z = BODY_TOP + 0.02 + LID[2] / 2
lid_parts = []
lid = S.box("Lid_Slab", LID, (0, 0, LID_Z), col)
S.assign(lid, m["obsidian"]); S.bevel(lid, 0.016, 4)
lid_parts.append(lid)

LID_TOP = LID_Z + LID[2] / 2

def brass_line(name, size, loc, mat=None):
    b = S.box(name, size, loc, col)
    S.assign(b, mat or m["brass"]); S.bevel(b, 0.0025, 2)
    return b

# A raised machined "table" gives the lid a stepped, classical silhouette.
TABLE = (LID[0] - 0.26, LID[1] - 0.22, 0.07)
table = S.box("Lid_Table", TABLE, (0, 0, LID_TOP + TABLE[2] / 2), col)
S.assign(table, m["obsidian"]); S.bevel(table, 0.012, 4)
lid_parts.append(table)
TABLE_TOP = LID_TOP + TABLE[2]

# A fine oxidized-brass lattice proud of the stone divides the table into a
# symmetric grid of coffers (the ribs read as the coffering). Reverent, quiet.
COF_NX, COF_NY = 5, 3
FMX, FMY = 0.14, 0.11
field_x, field_y = TABLE[0] - 2 * FMX, TABLE[1] - 2 * FMY
cw, ch = field_x / COF_NX, field_y / COF_NY
# Recessed coffer pockets (skip the centre — the reliquary port sits there).
for i in range(COF_NX):
    for j in range(COF_NY):
        if i == COF_NX // 2 and j == COF_NY // 2:
            continue
        cx = -field_x / 2 + (i + 0.5) * cw
        cy = -field_y / 2 + (j + 0.5) * ch
        pk = S.box(f"Lid_Coffer_{i}_{j}", (cw - 0.05, ch - 0.05, 0.04),
                   (cx, cy, TABLE_TOP - 0.024), col)
        S.assign(pk, m["obsidian_matte"]); S.bevel(pk, 0.006, 3)
        lid_parts.append(pk)
for i in range(COF_NX + 1):
    x = -field_x / 2 + i * cw
    lid_parts.append(brass_line("Lid_Brass", (0.018, field_y + 0.018, 0.02),
                                (x, 0, TABLE_TOP + 0.002)))
for j in range(COF_NY + 1):
    y = -field_y / 2 + j * ch
    lid_parts.append(brass_line("Lid_Brass", (field_x + 0.018, 0.018, 0.02),
                                (0, y, TABLE_TOP + 0.002)))

# Centred smoked-glass reliquary port with a machined titanium bezel (symmetric).
PORT = 0.30
bezel = S.tube("Lid_PortBezel", PORT / 2 + 0.035, PORT / 2 - 0.005, 0.05, 56,
               (0, 0, TABLE_TOP + 0.006), col)
S.assign(bezel, m["titanium_polish"]); S.bevel(bezel, 0.004, 2)
S.shade_smooth(bezel); lid_parts.append(bezel)
port = S.cyl("Lid_Port", PORT / 2, 0.05, 56, (0, 0, TABLE_TOP - 0.008), col)
S.assign(port, m["glass"]); S.shade_smooth(port); lid_parts.append(port)
# A faint cyan core reads up through the smoked glass — the sealed data, quietly
# worshipped through the reliquary window. The single restrained cyan focus.
core_glow = S.cyl("Lid_PortCore", PORT / 2 - 0.03, 0.02, 48,
                  (0, 0, TABLE_TOP - 0.045), col)
S.assign(core_glow, m["data_soft"]); S.shade_smooth(core_glow); lid_parts.append(core_glow)

lid = S.join_all(lid_parts, "Lid")
S.weighted_normal(lid); S.shade_smooth(lid)


# ---------------------------------------------------------------------------
# FRAME — a thin, precise titanium baldachin: four corner posts and a top rail
# frame. The "surgical technology" reading around the classical stone. Quiet.
# ---------------------------------------------------------------------------
frame_parts = []
PX, PY = 1.55, 0.96                     # column positions (corners, on the plinth)
COL_R = 0.095
SHAFT_H = 1.62
BASE_H, CAP_H = 0.14, 0.13
POST_Z0 = PLINTH_TOP
SHAFT_Z0 = POST_Z0 + BASE_H
for sx in (1, -1):
    for sy in (1, -1):
        cx, cy = sx * PX, sy * PY
        # Machined base (stepped) and shaft (fluted) and capital (stepped).
        base = S.box("Frame_Base", (0.26, 0.26, BASE_H),
                     (cx, cy, POST_Z0 + BASE_H / 2), col)
        S.assign(base, m["titanium"]); S.bevel(base, 0.008, 4)
        S.apply_modifiers(base); frame_parts.append(base)
        # Fluted shaft, smoothed with a subsurf for buttery machined metal, then
        # baked so the count survives the join intact (real, visible density).
        shaft = fluted_column("Frame_Column", COL_R, SHAFT_H, 22, 10, 12, 0.010,
                              (cx, cy, SHAFT_Z0 + SHAFT_H / 2), col)
        S.assign(shaft, m["titanium"]); S.shade_smooth(shaft)
        S.subsurf(shaft, 1, 1); S.apply_modifiers(shaft)
        frame_parts.append(shaft)
        cap = S.box("Frame_Capital", (0.28, 0.28, CAP_H),
                    (cx, cy, SHAFT_Z0 + SHAFT_H + CAP_H / 2), col)
        S.assign(cap, m["titanium"]); S.bevel(cap, 0.008, 3)
        S.apply_modifiers(cap); frame_parts.append(cap)
RAIL_Z = SHAFT_Z0 + SHAFT_H + CAP_H
# Architrave — a thin frame connecting the capitals.
for sy in (1, -1):
    r = S.box("Frame_Rail", (2 * PX + 0.28, 0.07, 0.10),
              (0, sy * PY, RAIL_Z + 0.05), col)
    S.assign(r, m["titanium"]); S.bevel(r, 0.006, 3); frame_parts.append(r)
for sx in (1, -1):
    r = S.box("Frame_Rail", (0.07, 2 * PY + 0.28, 0.10),
              (sx * PX, 0, RAIL_Z + 0.05), col)
    S.assign(r, m["titanium"]); S.bevel(r, 0.006, 3); frame_parts.append(r)
frame = S.join_all(frame_parts, "Frame")
S.weighted_normal(frame); S.shade_smooth(frame)


# ---------------------------------------------------------------------------
# RITUAL — white ceramic (authority). Machined finial caps crown the posts;
# two low ceramic offering discs sit symmetrically at the head and foot on the
# plinth. Reverent, sparse.
# ---------------------------------------------------------------------------
ritual_parts = []
ARCH_TOP = RAIL_Z + 0.10
for sx in (1, -1):
    for sy in (1, -1):
        # Two-step ceramic finial crowning each column (reverent).
        f0 = S.box("Ritual_Cap", (0.22, 0.22, 0.06),
                   (sx * PX, sy * PY, ARCH_TOP + 0.03), col)
        S.assign(f0, m["ceramic"]); S.bevel(f0, 0.006, 3)
        ritual_parts.append(f0)
        f1 = S.box("Ritual_Cap", (0.12, 0.12, 0.08),
                   (sx * PX, sy * PY, ARCH_TOP + 0.10), col)
        S.assign(f1, m["ceramic"]); S.bevel(f1, 0.006, 3)
        ritual_parts.append(f1)
for sx in (1, -1):
    disc = S.cyl("Ritual_Disc", 0.17, 0.06, 48,
                 (sx * (BODY[0] / 2 + 0.30), 0, PLINTH_TOP + 0.03), col)
    S.assign(disc, m["ceramic"]); S.bevel(disc, 0.006, 3); S.shade_smooth(disc)
    ritual_parts.append(disc)
    rim = S.tube("Ritual_DiscRim", 0.17, 0.145, 0.05, 48,
                 (sx * (BODY[0] / 2 + 0.30), 0, PLINTH_TOP + 0.055), col)
    S.assign(rim, m["ceramic_matte"]); S.shade_smooth(rim)
    ritual_parts.append(rim)
ritual = S.join_all(ritual_parts, "Ritual")
S.weighted_normal(ritual)


# ---------------------------------------------------------------------------
# FIBERS — a few very thin cyan data_soft threads running up the plinth face to
# the body, the reliquary's nerves. Extremely restrained.
# ---------------------------------------------------------------------------
fiber_parts = []
for sx in (1, -1):
    for i in range(3):
        yy = -0.4 + i * 0.4
        f = S.box(f"Fiber", (0.01, 0.01, PLINTH_TOP - 0.06),
                  (sx * (BODY[0] / 2 - 0.05), yy, (PLINTH_TOP) / 2 + 0.02), col)
        S.assign(f, m["data_soft"]); fiber_parts.append(f)
fibers = S.join_all(fiber_parts, "Fibers"); S.shade_smooth(fibers)


print("[vault_sarcophagus] objects:", len(col.objects))
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Cold neutral rim (not cyan): this scene's metal must read cold graphite/
    # titanium; the ONLY cyan is the sealed core and the seam thread.
    # Hero read: a reverent 3/4 from slightly above — read the length, the
    # stepped symmetry, the frame and the sealed lid at once.
    S.lookdev_render(REF, cam_loc=(3.9, -5.9, 2.75), target=(0, 0, 1.02),
                     lens=47, samples=96, res=(1000, 720),
                     rim_color=(0.42, 0.52, 0.62))
