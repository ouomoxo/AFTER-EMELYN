"""
SOVEREIGN//77 — MID ASSET: Cooling / Heat-Exchanger Unit (ACT I).

A vertical heat exchanger: a machined graphite plenum, a titanium finned
radiator core, a converging cowl, and a large slow axial fan in a bell-mouth
shroud. Thermal infrastructure, not data — so it is cyan-free: cold
titanium + graphite with a single sparse amber status. The rotor is a separate
`Fan` object (origin on its axis) so the web runtime can spin it.

Named parts:  Body, Fins, Fan

Run:  python3 tools/blender/build_cooling_unit.py [--render]
Out:  public/assets/models/cooling_unit.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector, Matrix  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/cooling_unit.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/cooling_unit.png")

S.reset()
col = S.collection("COOLING_UNIT")
m = S.mats()

FAN_Z = 1.30


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
# BODY — core duct, base plenum + intake louvers + feet, converging cowl,
# bell-mouth fan shroud, stator struts, one amber status.
# ===========================================================================
body_parts = []

# Central duct core (air path).
core = S.cyl("Cool_Core", 0.28, 1.12, 48, (0, 0, 0.56), col)
S.assign(core, m["graphite"])
body_parts.append(core)

# Base plenum housing.
base = S.cyl("Cool_Base", 0.45, 0.46, 48, (0, 0, 0.23), col)
S.assign(base, m["graphite_worn"])
body_parts.append(base)

# A machined collar capping the plenum (a crisp titanium band).
collar = S.tube("Cool_Collar", 0.455, 0.40, 0.04, 48, (0, 0, 0.46), col)
S.assign(collar, m["titanium"])
body_parts.append(collar)

# Intake louvers — a ring of vertical titanium slats around the plenum.
NL = 28
for i in range(NL):
    a = (i / NL) * math.tau
    x, y = math.cos(a) * 0.452, math.sin(a) * 0.452
    slat = S.box(f"Cool_Louver_{i}", (0.012, 0.03, 0.34), (x, y, 0.24), col)
    slat.rotation_euler = (0, 0, a)
    S.assign(slat, m["titanium"])
    body_parts.append(slat)

# Machined feet.
for i in range(3):
    a = (i / 3) * math.tau + math.radians(30)
    x, y = math.cos(a) * 0.40, math.sin(a) * 0.40
    foot = S.box(f"Cool_Foot_{i}", (0.10, 0.10, 0.05), (x, y, 0.025), col)
    S.assign(foot, m["graphite"])
    body_parts.append(foot)

# Converging cowl from radiator to fan shroud.
cowl = S.tube("Cool_Cowl", 0.455, 0.40, 0.08, 48, (0, 0, 1.10), col)
S.assign(cowl, m["graphite"])
body_parts.append(cowl)

# Bell-mouth fan shroud (short, so the rotor is exposed at the mouth) + lip.
shroud = S.tube("Cool_Shroud", 0.46, 0.405, 0.24, 56, (0, 0, 1.25), col)
S.assign(shroud, m["titanium"])
body_parts.append(shroud)
lip = S.torus("Cool_Lip", 0.44, 0.022, 56, 12, (0, 0, 1.37), col)
S.assign(lip, m["titanium_polish"])
body_parts.append(lip)

# Stator struts (below the rotor) hub->shroud, hold the motor.
for i in range(4):
    a = (i / 4) * math.tau + 0.3
    st = S.box(f"Cool_Stator_{i}", (0.34, 0.03, 0.03), (0, 0, FAN_Z - 0.075), col)
    st.rotation_euler = (0, 0, a)
    st.location = (math.cos(a) * 0.2, math.sin(a) * 0.2, FAN_Z - 0.075)
    S.assign(st, m["graphite_light"])
    body_parts.append(st)

# One sparse amber thermal status (caution grammar) low on the plenum.
amber = S.box("Cool_Status", (0.05, 0.014, 0.02), (0.14, -0.45, 0.34), col)
S.assign(amber, m["warning"])
body_parts.append(amber)

Body = S.join_all(body_parts, "Body")
S.bevel(Body, 0.004, 2)
S.weighted_normal(Body)
S.shade_smooth(Body)


# ===========================================================================
# FINS — the finned radiator: a dense stack of thin titanium disc fins around
# the core (heat-exchange surface). Arrayed vertically.
# ===========================================================================
fin = S.tube("Fin", 0.43, 0.285, 0.006, 40, (0, 0, 0.52), col)
S.assign(fin, m["titanium"])
S.shade_smooth(fin)
Fins = S.join_all([fin], "Fins")
S.array(Fins, 26, (0, 0, 0.021))


# ===========================================================================
# FAN — the slow axial rotor. Hub (first → sets origin on the spin axis) + a
# titanium cap + wide pitched blades. Separate object; web spins it about Z.
# ===========================================================================
def make_blade(name, R, pitch, blade_len, chord, thick):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((blade_len, chord, thick)), verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(pitch, 3, "X"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((R, 0, 0)))
    return S.bm_to_obj(bm, name, col)


fan_parts = []
hub = S.cyl("Fan_Hub", 0.10, 0.14, 28, (0, 0, FAN_Z), col)
S.assign(hub, m["obsidian"])
fan_parts.append(hub)
cap = S.cyl("Fan_Cap", 0.075, 0.06, 24, (0, 0, FAN_Z + 0.08), col)
S.assign(cap, m["titanium_polish"])
fan_parts.append(cap)
NB = 9
for i in range(NB):
    a = (i / NB) * math.tau
    # Bright titanium blades read as a machined rotor in the dark shroud mouth.
    bl = make_blade(f"Fan_Blade_{i}", 0.25, 0.6, 0.31, 0.17, 0.01)
    bl.rotation_euler = (0, 0, a)
    bl.location = (0, 0, FAN_Z)
    S.assign(bl, m["titanium"])
    fan_parts.append(bl)

Fan = S.join_all(fan_parts, "Fan")   # origin inherits the hub centre (spin axis)
S.bevel(Fan, 0.003, 2)
S.weighted_normal(Fan)
S.shade_smooth(Fan)

tris = count_tris()
print(f"[cooling_unit] objects: {len(col.objects)}  tris: {tris}")
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # 3/4 from front, slightly above to read the fan; cyan-free asset → neutral
    # rim so metal stays cold, amber status the only accent.
    S.lookdev_render(REF, cam_loc=(2.35, -2.95, 2.15), target=(0, 0, 0.72),
                     lens=48, samples=80, res=(820, 1000),
                     key_energy=760, rim_color=(0.11, 0.13, 0.15))
