"""
SOVEREIGN//77 — MID ASSET: Server / Data Spine Column (ACT I).

A tall modular server spine — stacked machined blade-bays framed by cold
titanium corner posts, thin restrained cyan data slots (one per bay), side
cable channels with bundled conduit, fine vent slats. Reads as an internal
organ of the city machine, not a generic server room.

Tileable vertically: geometry spans z=0..H with flush top/bottom and a bay
pitch that continues seamlessly, so racks stack (place at z = k*H).

Named parts:  Column, Bays, Data, Cables

Run:  python3 tools/blender/build_server_rack.py [--render]
Out:  public/assets/models/server_rack.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/server_rack.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/server_rack.png")

S.reset()
col = S.collection("SERVER_RACK")
m = S.mats()

# --- dimensions (metres) ----------------------------------------------------
WX, DY = 0.60, 0.50          # column footprint
BAY_H = 0.26                 # bay pitch (tileable)
N_BAY = 9
H = BAY_H * N_BAY            # 2.34 m total
FRONT = -DY / 2              # front face plane (-Y toward viewer)


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
# COLUMN — core mass + cold titanium corner posts + flush caps.
# ===========================================================================
column_parts = []

core = S.box("Rack_Core", (WX, DY, H), (0, 0, H / 2), col)
S.assign(core, m["graphite"])
column_parts.append(core)

# Four corner posts run the full height (the machined spine frame).
for sx in (-1, 1):
    for sy in (-1, 1):
        post = S.box(f"Rack_Post_{sx}_{sy}", (0.05, 0.05, H),
                     (sx * (WX / 2 - 0.005), sy * (DY / 2 - 0.005), H / 2), col)
        S.assign(post, m["titanium"])
        column_parts.append(post)

# Flush top and bottom rails (thin) — keep the tiling seam crisp.
for z in (0.014, H - 0.014):
    rail = S.box("Rack_Rail", (WX - 0.02, DY - 0.02, 0.024), (0, 0, z), col)
    S.assign(rail, m["graphite_light"])
    column_parts.append(rail)

# One sparse amber status block, low and asymmetric (caution grammar).
amber = S.box("Rack_Status", (0.05, 0.012, 0.018), (0.16, FRONT - 0.028, 0.30), col)
S.assign(amber, m["warning"])
column_parts.append(amber)

Column = S.join_all(column_parts, "Column")
S.bevel(Column, 0.005, 2)
S.weighted_normal(Column)
S.shade_smooth(Column)


# ===========================================================================
# BAYS — one machined blade-bay, arrayed up the column. Front plate + vent
# slats + a handle rail. (Cyan lives in the separate "Data" object.)
# ===========================================================================
bay_parts = []
bz = BAY_H / 2               # centre of the bottom bay
plate_y = FRONT - 0.02

# Front plate (recessed machined panel, proud of the core).
plate = S.box("Bay_Plate", (WX - 0.10, BAY_H - 0.03, 0.04),
              (0, plate_y, bz), col)
S.assign(plate, m["graphite_worn"])
bay_parts.append(plate)

# Machined sill lip along the bottom of each bay (the blade seam / ledge).
sill = S.box("Bay_Sill", (WX - 0.10, 0.018, 0.055), (0, plate_y - 0.01, bz - 0.108), col)
S.assign(sill, m["graphite_light"])
bay_parts.append(sill)

# Vent slats — fine horizontal titanium fins on the key-lit (right) half.
for i in range(7):
    z = bz - 0.096 + i * 0.032
    slat = S.box(f"Bay_Vent_{i}", (0.23, 0.013, 0.055), (0.115, plate_y - 0.02, z), col)
    S.assign(slat, m["titanium"])
    bay_parts.append(slat)

# Left sub-panel — machined recess with a handle rail + two fasteners.
sub = S.box("Bay_Sub", (0.19, BAY_H - 0.07, 0.045), (-0.16, plate_y - 0.004, bz), col)
S.assign(sub, m["graphite"])
bay_parts.append(sub)
handle = S.box("Bay_Handle", (0.03, 0.045, 0.13), (-0.235, plate_y - 0.03, bz), col)
S.assign(handle, m["titanium_polish"])
bay_parts.append(handle)
for sx in (-0.205, -0.075):
    scr = S.cyl(f"Bay_Screw_{sx}", 0.011, 0.03, 10,
                (sx, plate_y - 0.03, bz - 0.075), col)
    scr.rotation_euler = (math.radians(90), 0, 0)
    S.assign(scr, m["graphite_light"])
    bay_parts.append(scr)

Bays = S.join_all(bay_parts, "Bays")
S.bevel(Bays, 0.003, 2)
S.weighted_normal(Bays)
S.shade_smooth(Bays)
S.array(Bays, N_BAY, (0, 0, BAY_H))


# ===========================================================================
# DATA — one thin cyan slot per bay (restrained, soft). Separate object so the
# web runtime can pulse it. Arrayed to match the bays.
# ===========================================================================
slot = S.box("Data_Slot", (0.15, 0.012, 0.014), (-0.13, plate_y - 0.03, bz + 0.075), col)
S.assign(slot, m["data_soft"])
Data = S.join_all([slot], "Data")
S.array(Data, N_BAY, (0, 0, BAY_H))


# ===========================================================================
# CABLES — recessed side channels with bundled dark conduit + one cyan fiber
# (the data conduit) running the height on a single side.
# ===========================================================================
cable_parts = []
for sx in (-1, 1):
    x = sx * (WX / 2 + 0.006)
    for j, oy in enumerate((-0.09, 0.0, 0.09)):
        cbl = S.cyl(f"Cable_{sx}_{j}", 0.022, H - 0.06, 16, (x, oy, H / 2), col)
        S.assign(cbl, m["rubber"])
        cable_parts.append(cbl)
    # Cable-management clamps at intervals — the "conduit is dressed" read.
    for k in range(4):
        cz = 0.3 + k * 0.58
        clamp = S.box(f"Clamp_{sx}_{k}", (0.02, 0.24, 0.03), (x + sx * 0.006, 0, cz), col)
        S.assign(clamp, m["graphite_light"])
        cable_parts.append(clamp)
# One cyan data fiber tucked in the -X channel (restrained, soft).
fiber = S.cyl("Cable_Fiber", 0.008, H - 0.10, 10, (-(WX / 2 + 0.018), -0.09, H / 2), col)
S.assign(fiber, m["data_soft"])
cable_parts.append(fiber)

Cables = S.join_all(cable_parts, "Cables")
S.shade_smooth(Cables)

tris = count_tris()
print(f"[server_rack] objects: {len(col.objects)}  tris: {tris}")
size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Tall portrait framing; near-neutral rim (metal stays cold), the bay data
    # slots supply the restrained cyan.
    S.lookdev_render(REF, cam_loc=(2.5, -3.7, 1.55), target=(0, 0, 1.15),
                     lens=50, samples=80, res=(760, 1000),
                     key_energy=780, rim_color=(0.06, 0.16, 0.17))
