"""
SOVEREIGN//77 — studio HDRI generator.

Renders a DARK surgical-studio environment as an equirectangular HDR so the
polished titanium / ceramic reflect a believable world: a near-black room with
shaped white softboxes, cool cyan data practicals, and an overhead light rig
whose thin strips give machined surfaces crisp reflection detail. This replaces
the 4-flat-panel procedural PMREM with real image-based lighting.

Run:  python3 tools/blender/build_env_hdri.py
Out:  public/assets/env/studio.hdr   (1024x512 Radiance RGBE)
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector  # type: ignore

OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/env/studio.hdr")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = "CYCLES"
try:
    scene.cycles.device = "CPU"
    scene.cycles.samples = 160
    scene.cycles.use_denoising = True
except Exception:
    pass

# Near-black world so only the shaped emitters light the scene.
scene.world = bpy.data.worlds.new("W")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs[0].default_value = (0.004, 0.005, 0.007, 1)
scene.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0


def emitter(name, color, strength, size, loc, rot=None, aim=True):
    """An emissive plane (softbox / strip) facing the origin."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = (size[0], size[1], 1.0)
    if aim:
        d = Vector((0, 0, 0)) - Vector(loc)
        o.rotation_euler = d.to_track_quat("Z", "Y").to_euler()
    if rot is not None:
        o.rotation_euler = rot
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs[0].default_value = (color[0], color[1], color[2], 1.0)
    em.inputs[1].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs[0], out.inputs[0])
    o.data.materials.append(m)
    return o


WHITE = (0.86, 0.90, 0.98)
COOL = (0.55, 0.68, 0.82)
CYAN = (0.10, 0.72, 0.70)

# --- key + fills (shaped softboxes) ---
emitter("Key", WHITE, 9.0, (5.0, 2.6), (7.5, 5.5, 4.5))       # bright soft key
emitter("Fill", COOL, 2.2, (7.0, 4.5), (-9.0, 1.5, -3.0))     # broad cool fill
emitter("Rim", WHITE, 3.5, (1.2, 4.0), (-4.0, 4.5, -7.5))     # tall back rim
emitter("Top", WHITE, 2.6, (6.0, 6.0), (0.0, 9.0, 0.0))       # overhead soft

# --- cyan data practicals (thin strips at mid height) ---
for i, a in enumerate((0.4, 2.3, 4.1)):
    emitter(f"Cyan{i}", CYAN, 5.0, (0.18, 5.5),
            (math.cos(a) * 8.5, 0.6 + (i - 1) * 0.8, math.sin(a) * 8.5))

# --- overhead light rig: thin strips that read as crisp reflections ---
for i in range(6):
    x = -6.0 + i * 2.4
    emitter(f"Rig{i}", WHITE, 1.8, (0.10, 7.0), (x, 8.2, 0.0),
            rot=(math.radians(90), 0, 0), aim=False)

# --- a few far accent points (distant equipment lights) ---
for i, (ax, ay, az) in enumerate([(9, -1.5, 4), (-8, -1, 6), (6, 3.5, -8), (-5, 2, 8)]):
    emitter(f"Acc{i}", COOL, 3.0, (0.5, 0.5), (ax, ay, az))

# --- dim floor bounce so the lower hemisphere isn't dead black ---
emitter("Floor", (0.03, 0.035, 0.045), 1.0, (26, 26), (0, -11, 0),
        rot=(0, 0, 0), aim=False)

# equirectangular panorama camera at the origin
cam_data = bpy.data.cameras.new("Pano")
cam_data.type = "PANO"
try:
    cam_data.panorama_type = "EQUIRECTANGULAR"
except Exception:
    cam_data.cycles.panorama_type = "EQUIRECTANGULAR"
cam = bpy.data.objects.new("Pano", cam_data)
scene.collection.objects.link(cam)
cam.location = (0, 0, 0)
cam.rotation_euler = (math.radians(90), 0, 0)  # level horizon
scene.camera = cam

scene.render.resolution_x = 1024
scene.render.resolution_y = 512
scene.render.image_settings.file_format = "HDR"   # Radiance RGBE for RGBELoader
scene.view_settings.view_transform = "Raw"        # store scene-linear radiance
os.makedirs(os.path.dirname(OUT), exist_ok=True)
scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
# Blender appends nothing for HDR; ensure .hdr extension
if os.path.exists(OUT):
    print(f"[hdri] wrote {OUT}  ({os.path.getsize(OUT)/1024:.1f} KB)")
else:
    alt = OUT + ".hdr"
    if os.path.exists(alt):
        os.rename(alt, OUT)
        print(f"[hdri] wrote {OUT} (renamed)")
print("[hdri] done")
