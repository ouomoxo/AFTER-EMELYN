"""
Verification render for the HANDSHAKE pressure door: import the exported GLB and
shoot the reads the film uses — a WIDE establishing frame (monumental door in its
architecture), a CORE detail, and a PARTED state (leaves open, exposing their
mass + the lit tunnel behind). Bright, clear set lighting so geometry/joinery is
legible for critique — the cinematic grade is judged later in the web engine.

Run:  python3 tools/blender/render_door_views.py
Out:  docs/_ref/door_wide.png, door_core.png, door_open.png
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

GLB = os.path.join(os.path.dirname(__file__), "../../public/assets/models/auth_door.glb")
REFDIR = os.path.join(os.path.dirname(__file__), "../../docs/_ref")


def _import():
    bpy.ops.import_scene.gltf(filepath=GLB)
    # The glTF Y-up export + the runtime's rotation.x=+90° cancel out, so the
    # door stands in world exactly as AUTHORED (face +Z, up +Y). Preview it in
    # that authored orientation — undo any leftover import rotation.
    for o in bpy.context.scene.objects:
        if o.parent is None and o.type in ("MESH", "EMPTY"):
            o.rotation_euler = (0, 0, 0)


def _light(name, kind, energy, loc, target=(0, 0, 0), color=(0.85, 0.9, 0.96), size=6.0):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind == "AREA":
        ld.size = size
    if kind == "SPOT":
        ld.spot_size = math.radians(70)
        ld.spot_blend = 0.5
    o = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(o)
    o.location = Vector(loc)
    d = Vector(target) - Vector(loc)
    o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    return o


def _render(path, cam_loc, target, lens, res, samples=90):
    scene = bpy.context.scene
    cam_data = bpy.data.cameras.new("C")
    cam_data.lens = lens
    cam = bpy.data.objects.new("C", cam_data)
    scene.collection.objects.link(cam)
    cam.location = Vector(cam_loc)
    cam.rotation_euler = (Vector(target) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam
    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "AgX"
    if scene.world is None:
        scene.world = bpy.data.worlds.new("W")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.012, 0.013, 0.016, 1)
    bg.inputs[1].default_value = 1.0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[door] {os.path.basename(path)}")


def set_lights():
    # Cool key from front-upper, broad fill, cyan kick from the core + tunnel.
    _light("Key", "AREA", 4200, (3.5, 5.0, 9.0), (0, 0, 0.3), (0.85, 0.9, 0.98), size=8)
    _light("Fill", "AREA", 900, (-5.0, 1.5, 8.0), (0, 0, 0.3), (0.6, 0.7, 0.82), size=10)
    _light("CoreGlow", "POINT", 60, (0, 0, 0.9), color=(0.05, 0.68, 0.66))
    _light("Tunnel", "SPOT", 3000, (0, 0, -7.5), (0, 0, 0.3), (0.5, 0.85, 0.9))
    _light("RimR", "AREA", 1600, (6, 2, 2.0), (0, 0, 0.3), (0.6, 0.78, 0.85), size=5)


# --- WIDE establishing (closed): near head-on, slight offset for dimension ---
S.reset()
_import()
set_lights()
_render(os.path.join(REFDIR, "door_wide.png"), (1.3, 0.2, 13.5), (0, 0.0, 0.2), 40, (1000, 760))

# --- CORE detail (closed) ---
S.reset()
_import()
set_lights()
_render(os.path.join(REFDIR, "door_core.png"), (0.5, 0.2, 4.9), (0, 0.0, 0.3), 62, (1000, 700))

# --- PARTED state: 3/4 angle so the parted leaves' thick edges + the lit tunnel
#     both read (leaves slide ±X, so a side-raking view catches their mass). ---
S.reset()
_import()
set_lights()
for o in bpy.context.scene.objects:
    if o.name == "Leaf_L":
        o.location.x -= 2.2
    elif o.name == "Leaf_R":
        o.location.x += 2.2
_render(os.path.join(REFDIR, "door_open.png"), (5.0, 1.0, 10.5), (-0.6, 0.0, -1.2), 46, (1000, 760))
print("[door] done")
