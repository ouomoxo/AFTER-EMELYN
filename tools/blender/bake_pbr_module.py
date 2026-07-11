"""
Full-PBR bake for the HUMAN REVISION hero: import the shipped GLB, inject
procedural micro-surface, bake normal + roughness + AO into a shared 2048 atlas,
re-export cybernetic_module_baked.glb, then RE-IMPORT the baked GLB and render an
85mm close-up to verify the maps survive glTF export and read as real machined
surface (reliable verification vs. the slow in-engine path).

Run:  python3 tools/blender/bake_pbr_module.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

HERE = os.path.dirname(__file__)
SRC = os.path.join(HERE, "../../public/assets/models/cybernetic_module.glb")
OUT = os.path.join(HERE, "../../public/assets/models/cybernetic_module_baked.glb")
BAKEDIR = os.path.join(HERE, "../../BLENDER/EXPORT/bake")
REF = os.path.join(HERE, "../../docs/_ref/module_pbr.png")

S.reset()
bpy.ops.import_scene.gltf(filepath=SRC)
for o in bpy.context.scene.objects:
    if o.parent is None:
        o.rotation_euler = (0, 0, 0)
meshes = [o for o in bpy.data.objects if o.type == "MESH"]
print("[pbr] parts:", [o.name for o in meshes])

# Bake normal + roughness + AO. add_surface_detail skips emissive/glass internally,
# so the neural conductor + data cores stay pristine automatically.
S.bake_pbr(meshes, BAKEDIR, "cybernetic_module", res=1024, samples=48,
           ao_distance=0.10, ao_samples=80, isolate_ao=True)

size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

# --- verify: reimport the baked GLB and render a close-up ---
S.reset()
bpy.ops.import_scene.gltf(filepath=OUT)
for o in bpy.context.scene.objects:
    if o.parent is None:
        o.rotation_euler = (0, 0, 0)
S.lookdev_render(REF, cam_loc=(0.75, -0.95, 1.72), target=(0, 0.0, 1.5),
                 lens=85, samples=120, res=(1050, 760), rim_color=(0.34, 0.48, 0.52))
print("[pbr] done")
