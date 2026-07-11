"""
SOVEREIGN//77 — HERO-ish ASSET: Maintenance / Surveillance Drone (ACT I).

Not a toy quadcopter. A surgical instrument that flies: a machined, tapered
graphite fuselage (chamfered flanks, sensor prow), a gimbaled sensor "eye" (one
small restrained cyan lens), two thin booms carrying four *ducted* fans
(shrouded rotors read premium, never a bare prop), a cold titanium spine.

Named parts the web runtime can pose/animate:
  Body, Eye, Arm_L, Arm_R

Run:  python3 tools/blender/build_maintenance_drone.py [--render]
Out:  public/assets/models/maintenance_drone.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector, Matrix  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/maintenance_drone.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/maintenance_drone.png")

S.reset()
col = S.collection("DRONE")
m = S.mats()


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


# --- shaping helpers: chamfered machined volumes, never plain slabs ----------
def fuselage(name, dx_bot, dx_top, dy, dz, loc):
    """Box with a narrower top → chamfered flanks (a machined fuselage)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= (dx_bot if v.co.z < 0 else dx_top)
        v.co.y *= dy
        v.co.z *= dz
    o = S.bm_to_obj(bm, name, col)
    o.location = loc
    return o


def prow(name, dx, dy, dz, tip_x, tip_z, loc, front=-1):
    """Box tapering to a smaller face toward `front` in Y (a sensor prow)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        tip = (v.co.y < 0) if front < 0 else (v.co.y > 0)
        v.co.x *= dx * (tip_x if tip else 1.0)
        v.co.z *= dz * (tip_z if tip else 1.0)
        v.co.y *= dy
    o = S.bm_to_obj(bm, name, col)
    o.location = loc
    return o


# ===========================================================================
# BODY — machined fuselage pod. Chamfered flanks, sensor prow, titanium spine,
# side sensor cheeks, rear vent grille. Long axis Y, nose at -Y (forward).
# ===========================================================================
body_parts = []

# Main volumes are near-black obsidian: off-key faces stay black (not a teal
# mirror), and only edges catch a restrained cyan/white kiss — the hero look.
hull = fuselage("Body_Hull", 0.21, 0.125, 0.50, 0.13, (0, 0, 0))
S.assign(hull, m["obsidian"])
body_parts.append(hull)

# Sensor prow — tapers to a smaller forward face; carries the eye mount.
nose = prow("Body_Nose", 0.17, 0.145, 0.12, 0.42, 0.62, (0, -0.295, -0.006), front=-1)
S.assign(nose, m["obsidian"])
body_parts.append(nose)

# Rear taper.
tail = prow("Body_Tail", 0.16, 0.115, 0.11, 0.5, 0.66, (0, 0.29, -0.002), front=1)
S.assign(tail, m["obsidian"])
body_parts.append(tail)

# Shoulder steps flanking the spine — break the top plane, machined graphite.
for sgn in (-1, 1):
    sh = S.box(f"Body_Shoulder_{sgn}", (0.045, 0.42, 0.02),
               (sgn * 0.05, -0.01, 0.058), col)
    S.assign(sh, m["graphite"])
    body_parts.append(sh)

# Dorsal spine — cold machined keel (graphite, not mirror-bright).
spine = S.box("Body_Spine", (0.05, 0.42, 0.028), (0, -0.01, 0.072), col)
S.assign(spine, m["graphite_light"])
body_parts.append(spine)

# Narrow ceramic sensor strip inset in the spine (surgical white, restrained).
inlay = S.box("Body_Inlay", (0.02, 0.2, 0.012), (0, -0.04, 0.084), col)
S.assign(inlay, m["ceramic"])
body_parts.append(inlay)

# Side sensor cheeks — faceted obsidian pods (short cylinders along X).
for sgn in (-1, 1):
    pod = S.cyl(f"Body_Cheek_{sgn}", 0.048, 0.05, 20,
                (sgn * 0.10, -0.11, -0.012), col)
    pod.rotation_euler = (0, math.radians(90), 0)
    S.assign(pod, m["obsidian"])
    body_parts.append(pod)

# Rear vent grille — thin titanium slats (machined heat exit, cold).
for i in range(4):
    slat = S.box(f"Body_Vent_{i}", (0.10, 0.006, 0.045),
                 (0, 0.33, -0.028 + i * 0.02), col)
    S.assign(slat, m["titanium"])
    body_parts.append(slat)

# Dorsal comms/sensor housing (a small machined module) + a sensor mast.
dorsal = S.box("Body_Dorsal", (0.07, 0.09, 0.028), (0, 0.135, 0.088), col)
S.assign(dorsal, m["graphite"])
body_parts.append(dorsal)
dorsal_ring = S.tube("Body_DorsalRing", 0.026, 0.018, 0.012, 20, (0, 0.135, 0.102), col)
S.assign(dorsal_ring, m["titanium_polish"])
body_parts.append(dorsal_ring)
mast = S.cyl("Body_Mast", 0.005, 0.08, 8, (0, 0.235, 0.11), col)
S.assign(mast, m["titanium"])
body_parts.append(mast)

# Side intake vents — fine machined slats on each flank.
for sgn in (-1, 1):
    for i in range(3):
        iv = S.box(f"Body_Intake_{sgn}_{i}", (0.006, 0.11, 0.03),
                   (sgn * 0.10, -0.02 + i * 0.05, 0.02), col)
        S.assign(iv, m["titanium"])
        body_parts.append(iv)

# One restrained cyan data sightline near the sensor (small, soft).
data_strip = S.box("Body_Data", (0.01, 0.075, 0.005), (0.032, 0.11, 0.086), col)
S.assign(data_strip, m["data_soft"])
body_parts.append(data_strip)

# One sparse amber status tick, asymmetric (caution grammar).
tick = S.box("Body_Warn", (0.026, 0.01, 0.006), (-0.06, -0.14, 0.03), col)
S.assign(tick, m["warning"])
body_parts.append(tick)

Body = S.join_all(body_parts, "Body")
S.bevel(Body, 0.006, 3)
S.weighted_normal(Body)
S.shade_smooth(Body)


# ===========================================================================
# EYE — a gimbaled surgical sensor slung under the prow. Machined lens barrel in
# a yoke, tilted down-forward. The cyan lens is the drone's single bright data
# element (small, recessed, restrained).
# ===========================================================================
eye_parts = []
EYE_C = Vector((0, -0.25, -0.10))
PITCH = math.radians(20)
FWD = Vector((0, -math.cos(PITCH), -math.sin(PITCH)))   # barrel forward vector

yoke_hub = S.cyl("Eye_YokeHub", 0.022, 0.13, 20,
                 (EYE_C.x, EYE_C.y + 0.03, EYE_C.z + 0.05), col)
yoke_hub.rotation_euler = (0, math.radians(90), 0)
S.assign(yoke_hub, m["titanium"])
eye_parts.append(yoke_hub)
for sgn in (-1, 1):
    cheek = S.box(f"Eye_Cheek_{sgn}", (0.013, 0.07, 0.10),
                  (sgn * 0.058, EYE_C.y + 0.015, EYE_C.z + 0.015), col)
    S.assign(cheek, m["graphite"])
    eye_parts.append(cheek)

barrel = S.cyl("Eye_Barrel", 0.048, 0.10, 32, (0, 0, 0), col)
barrel.rotation_euler = (math.radians(90) + PITCH, 0, 0)
barrel.location = EYE_C + Vector((0, -0.01, 0))
S.assign(barrel, m["graphite_light"])
eye_parts.append(barrel)


def eye_front(d):
    return EYE_C + Vector((0, -0.01, 0)) + FWD * d


bez = S.tube("Eye_Bezel", 0.05, 0.036, 0.02, 40, (0, 0, 0), col)
bez.rotation_euler = (math.radians(90) + PITCH, 0, 0)
bez.location = eye_front(0.052)
S.assign(bez, m["titanium_polish"])
eye_parts.append(bez)

bez2 = S.tube("Eye_BezelC", 0.036, 0.029, 0.016, 40, (0, 0, 0), col)
bez2.rotation_euler = (math.radians(90) + PITCH, 0, 0)
bez2.location = eye_front(0.056)
S.assign(bez2, m["ceramic"])
eye_parts.append(bez2)

lens = S.cyl("Eye_Lens", 0.027, 0.012, 32, (0, 0, 0), col)
lens.rotation_euler = (math.radians(90) + PITCH, 0, 0)
lens.location = eye_front(0.05)
S.assign(lens, m["data"])
eye_parts.append(lens)

Eye = S.join_all(eye_parts, "Eye")
S.bevel(Eye, 0.0022, 2)
S.weighted_normal(Eye)
S.shade_smooth(Eye)


# ===========================================================================
# DUCTED FAN — shroud + rim lip + hub + pitched blades + stators. Axis = Z.
# ===========================================================================
def make_blade(name, R, pitch, blade_len, chord, thick):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((blade_len, chord, thick)), verts=bm.verts)
    bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0),
                     matrix=Matrix.Rotation(pitch, 3, "X"))
    bmesh.ops.translate(bm, verts=bm.verts, vec=Vector((R, 0, 0)))
    return S.bm_to_obj(bm, name, col)


def ducted_fan(tag, center):
    parts = []
    cx, cy, cz = center
    shroud = S.tube(f"Fan_{tag}_Shroud", 0.104, 0.086, 0.06, 48, (cx, cy, cz), col)
    S.assign(shroud, m["graphite_worn"])   # rougher/darker → no teal mirror ring
    parts.append(shroud)
    lip = S.torus(f"Fan_{tag}_Lip", 0.097, 0.009, 48, 10, (cx, cy, cz + 0.03), col)
    S.assign(lip, m["graphite"])
    parts.append(lip)
    # Machined motor-mount ring under the hub (engineered joinery).
    mring = S.tube(f"Fan_{tag}_Motor", 0.036, 0.024, 0.02, 24, (cx, cy, cz - 0.018), col)
    S.assign(mring, m["titanium"])
    parts.append(mring)
    hub = S.cyl(f"Fan_{tag}_Hub", 0.02, 0.05, 20, (cx, cy, cz), col)
    S.assign(hub, m["obsidian"])
    parts.append(hub)
    cap = S.cyl(f"Fan_{tag}_HubCap", 0.013, 0.02, 16, (cx, cy, cz + 0.026), col)
    S.assign(cap, m["titanium_polish"])
    parts.append(cap)
    # Hub fasteners.
    for i in range(5):
        a = (i / 5) * math.tau
        blt = S.cyl(f"Fan_{tag}_Bolt_{i}", 0.004, 0.014, 6,
                    (cx + math.cos(a) * 0.03, cy + math.sin(a) * 0.03, cz + 0.006), col)
        S.assign(blt, m["titanium"])
        parts.append(blt)
    NB = 9
    for i in range(NB):
        a = (i / NB) * math.tau
        # Blades raised near the rim so the key light catches them → reads as a
        # rotor, not a solid disc.
        bl = make_blade(f"Fan_{tag}_Blade_{i}", 0.05, 0.5, 0.066, 0.026, 0.005)
        bl.rotation_euler = (0, 0, a)
        bl.location = (cx, cy, cz + 0.02)
        S.assign(bl, m["graphite_light"])
        parts.append(bl)
    for i in range(3):
        a = (i / 3) * math.tau + 0.4
        st = S.box(f"Fan_{tag}_Stator_{i}", (0.066, 0.008, 0.008), (0, 0, 0), col)
        st.rotation_euler = (0, 0, a)
        st.location = (cx + math.cos(a) * 0.055, cy + math.sin(a) * 0.055, cz - 0.024)
        S.assign(st, m["graphite"])
        parts.append(st)
    return parts


# ===========================================================================
# ARMS — H-frame booms at x=±0.225, each with two ducted fans + a body strut.
# ===========================================================================
def make_arm(name, sgn):
    parts = []
    bx = sgn * 0.225
    boom = S.box(f"{name}_Boom", (0.03, 0.50, 0.028), (bx, 0.0, 0.014), col)
    S.assign(boom, m["graphite"])
    parts.append(boom)
    strut = S.box(f"{name}_Strut", (0.14, 0.048, 0.026), (sgn * 0.145, 0.0, 0.01), col)
    S.assign(strut, m["graphite_worn"])
    parts.append(strut)
    for fy in (-0.225, 0.225):
        nac = S.box(f"{name}_Nac", (0.05, 0.05, 0.04), (bx, fy, 0.016), col)
        S.assign(nac, m["obsidian"])
        parts.append(nac)
    parts += ducted_fan(f"{name}F", (bx, -0.225, 0.052))
    parts += ducted_fan(f"{name}R", (bx, 0.225, 0.052))
    arm = S.join_all(parts, name)
    S.bevel(arm, 0.002, 2)
    S.weighted_normal(arm)
    S.shade_smooth(arm)
    return arm

Arm_L = make_arm("Arm_L", -1)
Arm_R = make_arm("Arm_R", +1)

tris = count_tris()
print(f"[drone] objects: {len(col.objects)}  tris: {tris}")
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Low, frontal hero 3/4 — reads the prow, gimbal eye, and fan depth. The
    # default cyan rim is tuned for the 5 m hero door; on a 0.5 m drone it
    # floods, so restrain it and let the neutral key define the cold metal.
    S.lookdev_render(REF, cam_loc=(1.24, -1.78, 0.7), target=(0, -0.05, 0.02),
                     lens=76, samples=90, res=(1000, 720),
                     key_energy=720, rim_color=(0.11, 0.13, 0.15))
