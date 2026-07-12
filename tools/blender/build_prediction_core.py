"""
SOVEREIGN//77 — HERO ASSET: Prediction Core (ACT III / PREDICTION ENGINE).

A floating computation core at the centre of a huge circular hall. An
abnormally-precise faceted jewel — smoked-glass shell over a soft emissive
data-core — cradled inside counter-rotating gyroscopic rings (an armillary
sphere for a digital religion). A machined titanium cradle below suggests the
whole thing is suspended, not held.

Parts kept as separate, named objects so the web runtime can animate them:
  Core, CoreShell, CoreCage, Gyro_0, Gyro_1, Gyro_2, Cradle, Conduits, HallRing.
Web counter-rotates Gyro_0/1/2 and slow-spins Core inside the still glass.

Run:  python3 tools/blender/build_prediction_core.py [--render]
Out:  public/assets/models/prediction_core.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector, Matrix  # type: ignore
import sovereign_bpy as S
import sovereign_kit as K

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/prediction_core.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/prediction_core.png")

S.reset()
col = S.collection("PREDICTION_CORE")
m = S.mats()


# ---------------------------------------------------------------------------
# Local helpers (kept out of the shared library — asset-specific geometry).
# ---------------------------------------------------------------------------
def icosphere(name, radius, subdiv, col, flat=True):
    """A precise faceted polyhedron. flat=True keeps crisp jewel facets."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    if not flat:
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def strut(name, p0, p1, radius, verts, col):
    """A machined cylinder spanning two points (cradle arms / conduits)."""
    p0 = Vector(p0); p1 = Vector(p1)
    d = p1 - p0
    obj = S.cyl(name, radius, d.length, verts, (0, 0, 0), col)
    obj.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    obj.location = (p0 + p1) / 2
    return obj


# ---------------------------------------------------------------------------
# THE CORE — a precise faceted polyhedron (the jewel-heart) suspended inside a
# smooth smoked-glass sphere. The glass attenuates the soft emission so it
# reads as a contained inner light, not a flood. "Precise polyhedron /
# transparent sphere": the polyhedron is the core, the sphere is the glass.
# ---------------------------------------------------------------------------
CORE_R = 0.26         # inner emissive polyhedron (a crisp icosahedron)
SHELL_R = 0.76        # smoked-glass sphere

# Inner jewel: a clean icosahedron (20 facets) so it reads as an abnormally
# precise polyhedron, not a lava ball. Kept small so most of the sphere reads
# as dark smoked glass and the cyan stays restrained (a contained heart, ~7%).
core = icosphere("Core", CORE_R, 1, col, flat=True)
S.assign(core, m["data_soft"])

# A tiny data point at the exact centre — the "seed" of the prediction.
seed = icosphere("Core_Seed", 0.075, 1, col, flat=True)
S.assign(seed, m["data_soft"])

# A thin titanium equatorial index band around the jewel (instrument grammar).
core_band = S.tube("Core_Band", CORE_R + 0.025, CORE_R - 0.02, 0.04, 64,
                   (0, 0, 0), col)
S.assign(core_band, m["titanium_polish"]); S.shade_smooth(core_band)
core = S.join_all([core, core_band], "Core")

# Outer shell: a smooth precise transparent sphere. Smoked glass; the dark
# tint keeps the interior reading as depth, not a flat green ball.
shell = icosphere("CoreShell", SHELL_R, 4, col, flat=False)   # 1280 -> subsurf
S.assign(shell, m["glass"])
S.subsurf(shell, 2, 2)                                          # buttery dielectric
S.shade_smooth(shell)


# ---------------------------------------------------------------------------
# GYROSCOPIC RINGS — three orthogonal gimbal hoops (a true armillary / 3-axis
# gyroscope). Named Gyro_0/1/2 so the web counter-rotates them independently.
# Each hoop = a thin machined band (tube) + two pivot bosses on its gimbal axis.
# The equatorial hoop carries fine graduation ticks (instrument / digital-relic).
# ---------------------------------------------------------------------------
def ring_ticks(name, radius, count, length, width, thick, col, mat):
    """One mesh of `count` radial ticks around a circle in the XY plane."""
    bm = bmesh.new()
    for i in range(count):
        a = (i / count) * math.tau
        res = bmesh.ops.create_cube(bm, size=1.0)
        vs = res["verts"]
        bmesh.ops.scale(bm, vec=Vector((width, length, thick)), verts=vs)
        bmesh.ops.translate(bm, vec=Vector((0, radius, 0)), verts=vs)
        bmesh.ops.rotate(bm, cent=Vector((0, 0, 0)),
                         matrix=Matrix.Rotation(a, 3, "Z"), verts=vs)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = S.bm_to_obj(bm, name, col)
    S.assign(o, mat)
    return o


def gyro(idx, r, depth, wall, tilt, mat, verts=248, ticks=0):
    # Band gets bevel + a light subsurf for a smooth machined hoop, then it is
    # BAKED so the crisp ticks/bosses joined after it don't inherit the subsurf
    # (that would balloon the tri-count and round the ticks into blobs).
    band = S.tube(f"{idx}_band", r, r - wall, depth, verts, (0, 0, 0), col)
    S.assign(band, mat); S.bevel(band, 0.005, 2); S.subsurf(band, 1, 1)
    S.shade_smooth(band); S.apply_modifiers(band)
    parts = [band]
    if ticks:
        tk = ring_ticks(f"{idx}_ticks", r - wall - 0.006, ticks,
                        0.024, 0.006, depth * 0.42, col, m["titanium_polish"])
        parts.append(tk)
    # Gimbal bearing HOUSINGS on the pivot axis (±X of the untilted ring): a
    # machined bearing box + bolt ring + a shaft boss + a data connector. This
    # is the biggest density add — real gimbal joints, not bare stubs.
    for sx in (-1, 1):
        px = sx * (r - wall / 2)
        boss = S.cyl(f"{idx}_pivot{sx}", 0.045, depth + 0.10, 24, (px, 0, 0), col)
        boss.rotation_euler = (0, math.pi / 2, 0)
        S.assign(boss, m["titanium_polish"]); S.shade_smooth(boss)
        parts.append(boss)
        hx = sx * (r + 0.02)
        house = S.box(f"{idx}_gh{sx}", (0.10, 0.11, depth + 0.08), (hx, 0, 0), col)
        S.assign(house, m["graphite"]); S.bevel(house, 0.004, 2)
        parts.append(house)
        parts += K.bolt_ring(f"{idx}_ghb{sx}", (sx * (r + 0.07), 0, 0), (sx, 0, 0),
                             0.065, 6, col, m, r=0.007, head_h=0.007)
        parts += K.connector_port(f"{idx}_ghc{sx}", (hx, 0.062, 0), col, m,
                                  r=0.026, depth=0.02, axis=(0, 1, 0), pins=5)
    g = S.join_all(parts, f"Gyro_{idx}")
    g.rotation_euler = tilt
    return g

# Three mutually-perpendicular hoops, nested by radius so they never intersect.
gyro(0, 1.14, 0.11, 0.026, (0.0, 0.0, 0.0), m["titanium"], ticks=144)     # equator
gyro(1, 1.32, 0.12, 0.026, (math.pi / 2, 0.0, 0.0), m["graphite_light"],
     ticks=144)                                                           # meridian
gyro(2, 1.50, 0.12, 0.024, (0.0, math.pi / 2, 0.0), m["titanium"], ticks=132)  # meridian


# ---------------------------------------------------------------------------
# CRADLE — machined titanium base ring + three struts reaching up toward the
# core but stopping short: it is suspended, not held. A thin cyan levitation
# emitter caps each strut (restrained data grammar).
# ---------------------------------------------------------------------------
cradle_parts = []
BASE_Z = -1.95
base_ring = S.tube("Cradle_Base", 0.98, 0.80, 0.14, 128, (0, 0, BASE_Z), col)
S.assign(base_ring, m["titanium"]); S.bevel(base_ring, 0.01, 2)
S.shade_smooth(base_ring)
cradle_parts.append(base_ring)

# Lower machined plinth disc the ring sits on.
plinth = S.cyl("Cradle_Plinth", 1.12, 0.10, 128, (0, 0, BASE_Z - 0.10), col)
S.assign(plinth, m["graphite"]); S.bevel(plinth, 0.014, 2); S.shade_smooth(plinth)
cradle_parts.append(plinth)

# Bolt ring around the base — surgical fasteners (machined detail + credibility).
NBolt = 20
for i in range(NBolt):
    a = (i / NBolt) * math.tau
    bx, by = math.cos(a) * 0.90, math.sin(a) * 0.90
    bolt = S.cyl(f"Cradle_Bolt_{i}", 0.022, 0.05, 8, (bx, by, BASE_Z + 0.075), col)
    S.assign(bolt, m["titanium_polish"])
    cradle_parts.append(bolt)

# Instrument pods around the base ring — machined gauge housings + data
# connectors + a bolt ring each (the base reads as a real instrument deck).
for i in range(6):
    a = (i / 6) * math.tau + math.radians(30)
    px, py = math.cos(a) * 0.95, math.sin(a) * 0.95
    pod = S.box(f"Cradle_Inst{i}", (0.15, 0.11, 0.10), (px, py, BASE_Z + 0.11), col)
    pod.rotation_euler = (0, 0, a)
    S.assign(pod, m["graphite"]); S.bevel(pod, 0.004, 2)
    cradle_parts.append(pod)
    cradle_parts += K.connector_port(f"Cradle_InstC{i}", (px, py, BASE_Z + 0.17),
                                     col, m, r=0.026, depth=0.02, axis=(0, 0, 1), pins=7)
    cradle_parts += K.bolt_ring(f"Cradle_InstB{i}", (px, py, BASE_Z + 0.165),
                                (0, 0, 1), 0.075, 6, col, m, r=0.006, head_h=0.006)

# A single machined central column rises to a cradle cup; the sphere hovers
# above it with a clean suspension gap. Quieter and more monolithic than a
# splayed tripod — a reliquary pedestal, not a lab stand.
CUP_Z = -0.90
col_top, col_bot = CUP_Z - 0.04, BASE_Z + 0.05
column = S.cyl("Cradle_Column", 0.15, col_top - col_bot, 48,
               (0, 0, (col_top + col_bot) / 2), col)
S.assign(column, m["titanium"]); S.bevel(column, 0.006, 2); S.shade_smooth(column)
cradle_parts.append(column)
# Machined collars banding the column (surgical repetition).
for cz in (col_bot + 0.18, (col_top + col_bot) / 2, col_top - 0.14):
    collar = S.tube(f"Cradle_Collar", 0.175, 0.15, 0.03, 48, (0, 0, cz), col)
    S.assign(collar, m["graphite_light"]); S.bevel(collar, 0.004, 2)
    S.shade_smooth(collar)
    cradle_parts.append(collar)

# Machined cup ring the sphere hovers over (concave landing).
cup = S.tube("Cradle_Cup", 0.34, 0.235, 0.075, 96, (0, 0, CUP_Z), col)
S.assign(cup, m["titanium_polish"]); S.bevel(cup, 0.006, 2); S.shade_smooth(cup)
cradle_parts.append(cup)

cradle = S.join_all(cradle_parts, "Cradle")
S.weighted_normal(cradle)

# A single thin cyan levitation ring in the suspension gap (the maglev field).
emitters = []
lev = S.tube("Emitter_Lev", 0.30, 0.27, 0.014, 96, (0, 0, CUP_Z + 0.055), col)
S.assign(lev, m["data_soft"]); S.shade_smooth(lev)
emitters.append(lev)

# ---------------------------------------------------------------------------
# CONDUITS — fine cyan data lines feeding the cradle from the hall floor.
# Restrained: thin, dark-cyan (data_soft), a single inlaid base ring + radials.
# ---------------------------------------------------------------------------
conduit_parts = []
# Feed-lines lying across the plinth floor, running in toward the base ring.
FZ = BASE_Z - 0.045
for i in range(3):
    a = (i / 3) * math.tau + math.radians(90)
    p0 = (math.cos(a) * 1.10, math.sin(a) * 1.10, FZ)
    p1 = (math.cos(a) * 0.86, math.sin(a) * 0.86, FZ)
    line = strut(f"Conduit_{i}", p0, p1, 0.009, 8, col)
    S.assign(line, m["data_soft"]); S.shade_smooth(line)
    conduit_parts.append(line)
conduits = S.join_all(conduit_parts, "Conduits")

# All cyan on one animatable node (levitation ring + conduits).
conduits = S.join_all(emitters + [conduits], "Conduits")

# ---------------------------------------------------------------------------
# HALL — two faint concentric floor rings implying the huge circular hall.
# Dark graphite, low, subordinate: they give scale without stealing the eye.
# ---------------------------------------------------------------------------
hall_parts = []
for i, (ro, ri) in enumerate([(3.0, 2.72), (4.4, 4.28)]):
    hr = S.tube(f"HallRing_{i}", ro, ri, 0.06 if i == 0 else 0.04, 176,
                (0, 0, BASE_Z - 0.14), col)
    S.assign(hr, m["graphite_worn"] if i == 0 else m["obsidian_matte"])
    S.bevel(hr, 0.01, 2); S.shade_smooth(hr)
    hall_parts.append(hr)
hall = S.join_all(hall_parts, "HallRing")

print("[prediction_core] objects:", len(col.objects))
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Hero read: pulled back and near eye level so the whole armillary, the
    # floating jewel and the cradle below all read — a reliquary in a great hall.
    S.lookdev_render(REF, cam_loc=(4.0, -5.0, 0.35), target=(0, 0, -0.05),
                     lens=47, samples=112, res=(1000, 760))
