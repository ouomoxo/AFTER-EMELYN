"""
Verification render for the HUMAN REVISION hero: import the EXPORTED GLB (proving
it round-trips through Draco/glTF) and shoot two reads the film actually uses —
the assembled hero (shells closed, the first frame the subject sees) and an
85mm co-processor close-up (does it survive inspection?).

Run:  python3 tools/blender/render_module_views.py
Out:  docs/_ref/module_assembled.png, docs/_ref/module_memory.png
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

GLB = os.path.join(os.path.dirname(__file__), "../../public/assets/models/cybernetic_module.glb")
REFDIR = os.path.join(os.path.dirname(__file__), "../../docs/_ref")

S.reset()
bpy.ops.import_scene.gltf(filepath=GLB)
names = [o.name for o in bpy.context.scene.objects if o.type in ("MESH", "EMPTY")]
print("[views] imported nodes:", names)
# glTF import stands the asset up Y-up; re-orient to Z-up so our cameras match.
for o in bpy.context.scene.objects:
    if o.parent is None:
        o.rotation_euler = (0, 0, 0)

# Assembled hero — the closed module, lens 65mm.
S.lookdev_render(os.path.join(REFDIR, "module_assembled.png"),
                 cam_loc=(1.7, -2.1, 1.05), target=(0, 0, 0.8),
                 lens=65, samples=110, res=(880, 1050),
                 rim_color=(0.34, 0.48, 0.52))

# Reset lights/camera by reloading, then a tight 85mm co-processor read.
S.reset()
bpy.ops.import_scene.gltf(filepath=GLB)
for o in bpy.context.scene.objects:
    if o.parent is None:
        o.rotation_euler = (0, 0, 0)
S.lookdev_render(os.path.join(REFDIR, "module_memory.png"),
                 cam_loc=(0.75, -0.95, 1.72), target=(0, 0.0, 1.62),
                 lens=85, samples=120, res=(1050, 760),
                 rim_color=(0.34, 0.48, 0.52))
print("[views] done")
