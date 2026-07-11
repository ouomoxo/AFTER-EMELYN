"""
SOVEREIGN//77 — Cycles AO texture-bake pass for the hero assets ("재질 베이크").

The canonical materials are factor-only PBR (docs/06 §4). The single map that
genuinely enriches a hero is *ambient occlusion*: soft contact shadows in the
machined joinery and seams that flat factors cannot express. This pass, for each
hero asset:

    1. imports the shipped GLB   public/assets/models/<name>.glb
    2. Smart-UV unwraps every named part and packs them into one shared atlas
    3. bakes Cycles AO into a single shared image (BLENDER/EXPORT/bake/<name>_ao.png)
    4. wires the AO to multiply Base Color (survives glTF as a baseColorTexture)
       AND as a true glTF occlusionTexture (R channel), leaving emission untouched
    5. re-exports  public/assets/models/<name>_baked.glb  (Draco, originals kept)
    6. renders an "after" Cycles reference  docs/_ref/<name>_baked.png

The original GLBs and lookdev refs are left intact, so <name>.png (before) vs
<name>_baked.png (after) is a directly comparable pair — same camera rig.

Roughness/Metallic are deliberately NOT baked: with flat per-material PBR there is
no per-texel R/M variation, so a baked ORM would only bloat the GLB. The occlusion
half of ORM *is* delivered, as the dedicated glTF occlusionTexture.

Run:  python3 tools/blender/bake_hero_assets.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S

HERE = os.path.dirname(__file__)
MODELS = os.path.join(HERE, "../../public/assets/models")
REF = os.path.join(HERE, "../../docs/_ref")
BAKEDIR = os.path.join(HERE, "../../BLENDER/EXPORT/bake")


def _mesh_objects():
    return [o for o in bpy.data.objects if o.type == "MESH"]


def bake_asset(name, res, samples, ao_distance, ao_strength, render_kw,
               explode=None, isolate=False, skip=None):
    """Import <name>.glb, bake AO, apply it, export <name>_baked.glb, render.

    `skip` is a set of object names to keep PRISTINE (unbaked). AO reads as depth
    only in dense joinery; baking smooth convex covers (the ceramic dermal shells)
    or thin self-lit filaments (the neural conductor) just adds facet noise and
    muddies the surgical look, so those parts are excluded. Skipped parts are given
    independent material copies first, so wiring AO into the baked parts' (possibly
    shared) materials can never darken a skipped part.
    """
    src = os.path.join(MODELS, f"{name}.glb")
    out = os.path.join(MODELS, f"{name}_baked.glb")
    aotex = os.path.join(BAKEDIR, f"{name}_ao.png")
    ref = os.path.join(REF, f"{name}_baked.png")
    skip = set(skip or [])

    S.reset()
    bpy.ops.import_scene.gltf(filepath=src)
    objs = _mesh_objects()
    bake_objs = [o for o in objs if o.name not in skip]
    skip_objs = [o for o in objs if o.name in skip]
    print(f"[bake:{name}] imported {len(objs)} parts; baking {len(bake_objs)}"
          f"{' (skip: ' + ', '.join(sorted(skip)) + ')' if skip else ''}")

    # Give skipped parts their own material copies so the shared canonical
    # materials they use stay clean when AO is wired into the baked parts.
    for o in skip_objs:
        for slot in o.material_slots:
            if slot.material:
                slot.material = slot.material.copy()

    # Unwrap only the parts we bake (shared-atlas packing happens in bake_ao).
    for o in bake_objs:
        S.smart_uv(o)

    img = S.bake_ao(bake_objs, aotex, res=res, samples=samples,
                    ao_distance=ao_distance, isolate=isolate)

    mats = S._materials_of(bake_objs)
    for mat in mats:
        S.apply_ao_to_material(mat, img, strength=ao_strength)
    print(f"[bake:{name}] AO wired into {len(mats)} materials")

    size = S.export_glb(out, draco=True)
    orig = os.path.getsize(src)
    S.report(out, size)
    print(f"[bake:{name}] {name}.glb {orig/1024:.1f} KB  ->  "
          f"{name}_baked.glb {size/1024:.1f} KB  (+{(size-orig)/1024:.1f} KB)")

    # "After" reference — same rig as the original build script's lookdev.
    if explode:
        for nm, off in explode.items():
            o = bpy.data.objects.get(nm)
            if o:
                o.location = o.location + off
    S.lookdev_render(ref, **render_kw)
    return dict(name=name, out=out, size=size, orig=orig, res=res, tex=aotex)


CONFIGS = [
    # Cybernetic spine: MODULAR (5 layers explode apart) -> isolate each layer so
    # AO is pure self-occlusion (no cross-layer shadow decals). Small, tightly
    # stacked joinery -> short AO distance.
    dict(
        # The rebuilt spine is far denser (articulated vertebrae, actuators,
        # fasteners) so it needs a larger atlas for the contact shadows to
        # resolve; ao_strength eased to 0.7 so the baked occlusion adds seam
        # depth without muddying the polished titanium.
        name="cybernetic_module", res=2048, samples=128,
        ao_distance=0.10, ao_strength=0.7, isolate=True,
        # Keep the smooth ceramic covers and the thin glowing neural filaments
        # pristine — AO only enriches the dense joinery (vertebral core, muscle
        # bundle + bands, heatsink fins).
        skip={"Dermal_Shell_L", "Dermal_Shell_R", "Neural_Conductor"},
        render_kw=dict(cam_loc=(1.9, -2.3, 1.15), target=(0, 0.0, 0.8),
                       lens=60, samples=90, res=(900, 1050),
                       rim_color=(0.34, 0.48, 0.52)),
        explode={
            "Dermal_Shell_L": Vector((0.60, 0, 0)),
            "Dermal_Shell_R": Vector((-0.60, 0, 0)),
            "Muscle_Layer": Vector((0, -0.40, 0)),
            "Neural_Conductor": Vector((0, 0.22, 0)),
            "Memory_Coprocessor": Vector((0, 0, 0.42)),
        },
    ),
    # Auth-door iris: STATIC assembly -> mutual occlusion (nested rings/bolts cast
    # contact shadows into each other, which is exactly the depth we want). 1024²
    # keeps the baked variant lean; the iris parts dominate the atlas so the focal
    # point still resolves soft, clean AO.
    dict(
        name="auth_door", res=1024, samples=96,
        ao_distance=0.28, ao_strength=0.85, isolate=False,
        # Bake AO only on the machined ring joinery (the focal iris). Skip the big
        # graphite leaves (dark base -> AO invisible, yet they'd eat most of the
        # atlas), the flat aperture blades (artifact-prone, not joinery), and the
        # negligible bolts / emissive warn ticks. This hands the whole atlas to the
        # iris so its contact shadows resolve crisp and clean.
        skip={"Leaf_L", "Leaf_R", "Iris_Blades", "BoltRing", "Warn_0", "Warn_1"},
        render_kw=dict(cam_loc=(0.6, -3.4, 4.6), target=(0, 0, 0.2),
                       lens=55, samples=80, res=(1000, 660)),
    ),
]


def main():
    os.makedirs(BAKEDIR, exist_ok=True)
    # Optional CLI filter: bake only the named asset(s), e.g.
    #   python3 tools/blender/bake_hero_assets.py cybernetic_module
    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
    configs = [c for c in CONFIGS if (not wanted or c["name"] in wanted)]
    results = []
    for cfg in configs:
        results.append(bake_asset(**cfg))
    print("\n[bake] SUMMARY")
    for r in results:
        print(f"  {r['name']:20s} {r['res']}²  "
              f"{r['orig']/1024:7.1f} KB -> {r['size']/1024:7.1f} KB  "
              f"({'+' if r['size']>=r['orig'] else ''}{(r['size']-r['orig'])/1024:.1f} KB)")


if __name__ == "__main__":
    main()
