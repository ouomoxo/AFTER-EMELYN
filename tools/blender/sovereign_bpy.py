"""
SOVEREIGN//77 — Shared Blender authoring library (bpy 4.5 LTS).

This is the canonical asset-authoring layer. Every hero asset is built as real
Blender geometry with real modifiers and Principled-BSDF PBR materials, then
exported to glTF as *neutral* PBR (no baked view-transform) per
docs/06_BLENDER_PIPELINE.md. The web runtime supplies tone-mapping and grade.

Design language (docs/04_ART_DIRECTION.md):
    Corporate Monolith + Surgical Technology + Digital Religion.
    Machined, medical, reverent. Silhouette and joinery over surface noise.

Run headless:  python3 tools/blender/build_<asset>.py
"""

import math
import os
import bpy
import bmesh
from mathutils import Vector  # type: ignore


# ----------------------------------------------------------------------------
# Palette — mirrors src/util/palette.ts. Linear-ish sRGB values for BSDF input.
# glTF stores base color in sRGB; Blender base color sockets are scene-linear,
# so we convert with srgb() where a swatch is a "designed" color.
# ----------------------------------------------------------------------------
PAL = {
    "obsidian": (0.020, 0.021, 0.023),
    "obsidian_deep": (0.010, 0.010, 0.012),
    "graphite": (0.045, 0.050, 0.058),
    "graphite_light": (0.11, 0.12, 0.14),
    "surgical": (0.86, 0.89, 0.89),
    "surgical_dim": (0.30, 0.33, 0.34),
    "cyan": (0.05, 0.68, 0.66),
    "cyan_deep": (0.010, 0.14, 0.14),
    "amber": (0.80, 0.36, 0.06),
    "emergency": (0.78, 0.03, 0.02),
    "titanium": (0.38, 0.39, 0.40),
    "brass": (0.52, 0.38, 0.16),
}


def srgb(c):
    """Convert an sRGB triple to linear for Blender color sockets."""
    def _l(u):
        return u / 12.92 if u <= 0.04045 else ((u + 0.055) / 1.055) ** 2.4
    return (_l(c[0]), _l(c[1]), _l(c[2]), 1.0)


# ----------------------------------------------------------------------------
# Scene lifecycle
# ----------------------------------------------------------------------------
def reset():
    """Empty factory scene; metric units; AgX view transform for lookdev only."""
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    try:
        scene.view_settings.view_transform = "AgX"
    except Exception:
        pass
    # Deterministic: no random seeds leak into exported geometry.
    return scene


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def link(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)
    return obj


# ----------------------------------------------------------------------------
# Material factory — Principled BSDF, glTF-clean.
# ----------------------------------------------------------------------------
def _principled(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    return nt.nodes.get("Principled BSDF")


def material(name, base, metallic=0.0, roughness=0.5, *, emission=None,
             emission_strength=0.0, transmission=0.0, ior=1.45,
             clearcoat=0.0, is_srgb=True):
    """Create (or fetch) a PBR material. `base` is an sRGB triple by default."""
    existing = bpy.data.materials.get(name)
    if existing:
        return existing
    mat = bpy.data.materials.new(name)
    b = _principled(mat)
    col = srgb(base) if is_srgb else (base[0], base[1], base[2], 1.0)
    b.inputs["Base Color"].default_value = col
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = roughness
    if "IOR" in b.inputs:
        b.inputs["IOR"].default_value = ior
    if transmission and "Transmission Weight" in b.inputs:
        b.inputs["Transmission Weight"].default_value = transmission
        mat.blend_method = "BLEND"
    if clearcoat and "Coat Weight" in b.inputs:
        b.inputs["Coat Weight"].default_value = clearcoat
        b.inputs["Coat Roughness"].default_value = 0.08
    if emission is not None:
        b.inputs["Emission Color"].default_value = srgb(emission)
        b.inputs["Emission Strength"].default_value = emission_strength
    # Tag for glTF: keep factors, no baked textures.
    mat["sovereign_role"] = name
    return mat


# Canonical material set — reused across assets so the film reads as one system.
def mats():
    return {
        "obsidian": material("M_Obsidian", PAL["obsidian"], 0.0, 0.34, clearcoat=0.6),
        "obsidian_matte": material("M_ObsidianMatte", PAL["obsidian_deep"], 0.0, 0.72),
        "graphite": material("M_Graphite", PAL["graphite"], 1.0, 0.42),
        "graphite_worn": material("M_GraphiteWorn", PAL["graphite"], 1.0, 0.58),
        "graphite_light": material("M_GraphiteLight", PAL["graphite_light"], 1.0, 0.5),
        "titanium": material("M_Titanium", PAL["titanium"], 1.0, 0.36),
        "titanium_polish": material("M_TitaniumPolish", PAL["titanium"], 1.0, 0.16),
        "ceramic": material("M_Ceramic", PAL["surgical"], 0.0, 0.28, clearcoat=0.4),
        "ceramic_matte": material("M_CeramicMatte", PAL["surgical"], 0.0, 0.6),
        "brass": material("M_Brass", PAL["brass"], 1.0, 0.44),
        "glass": material("M_SmokedGlass", (0.02, 0.03, 0.03), 0.0, 0.06,
                          transmission=0.92, ior=1.5),
        "rubber": material("M_Carbon", PAL["obsidian_deep"], 0.0, 0.85),
        # Emission kept restrained: the web PostFX bloom does the "glow" work, so
        # GLB emissive strength stays modest and Cycles lookdev doesn't flood.
        "data": material("M_Data", PAL["cyan"], 0.0, 0.4,
                         emission=PAL["cyan"], emission_strength=2.6),
        "data_soft": material("M_DataSoft", PAL["cyan_deep"], 0.0, 0.5,
                              emission=PAL["cyan"], emission_strength=1.3),
        "authority": material("M_Authority", PAL["surgical"], 0.0, 0.3,
                              emission=PAL["surgical"], emission_strength=1.8),
        "warning": material("M_Warning", PAL["amber"], 0.0, 0.4,
                            emission=PAL["amber"], emission_strength=2.4),
        "emergency": material("M_Emergency", PAL["emergency"], 0.0, 0.4,
                             emission=PAL["emergency"], emission_strength=3.2),
    }


def assign(obj, mat, slot=0):
    while len(obj.data.materials) <= slot:
        obj.data.materials.append(None)
    obj.data.materials[slot] = mat
    return obj


# ----------------------------------------------------------------------------
# Modifier helpers — the "surgical machining" look comes from bevel + weighted
# normals + subtle subdivision, never from noise textures.
# ----------------------------------------------------------------------------
def bevel(obj, width=0.004, segments=2, angle=1.05, clamp=True):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = angle
    m.harden_normals = True
    m.use_clamp_overlap = clamp
    return m


def weighted_normal(obj):
    m = obj.modifiers.new("WN", "WEIGHTED_NORMAL")
    m.keep_sharp = True
    return m


def subsurf(obj, levels=1, render=2):
    m = obj.modifiers.new("Subsurf", "SUBSURF")
    m.levels = levels
    m.render_levels = render
    return m


def solidify(obj, thickness=0.02, offset=-1.0):
    m = obj.modifiers.new("Solidify", "SOLIDIFY")
    m.thickness = thickness
    m.offset = offset
    return m


def mirror(obj, axis=(True, False, False), empty=None):
    m = obj.modifiers.new("Mirror", "MIRROR")
    m.use_axis = axis
    if empty:
        m.mirror_object = empty
    m.use_clip = True
    return m


def array(obj, count, offset, use_relative=False):
    m = obj.modifiers.new("Array", "ARRAY")
    m.count = count
    m.use_relative_offset = use_relative
    m.use_constant_offset = not use_relative
    if not use_relative:
        m.constant_offset_displace = offset
    else:
        m.relative_offset_displace = offset
    return m


def shade_smooth(obj, angle=math.radians(35)):
    """Smooth shading with angle-based sharp edges (4.1+ replaced auto-smooth)."""
    for p in obj.data.polygons:
        p.use_smooth = True
    try:
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.shade_smooth_by_angle(angle=angle)
    except Exception:
        pass
    return obj


def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    for m in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=m.name)
        except Exception:
            pass
    return obj


# ----------------------------------------------------------------------------
# bmesh primitives — precise, low-poly hero parts.
# ----------------------------------------------------------------------------
def bm_to_obj(bm, name, col=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new(name, me)
    (col or bpy.context.scene.collection).objects.link(obj)
    return obj


def box(name, size=(1, 1, 1), loc=(0, 0, 0), col=None):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = bm_to_obj(bm, name, col)
    obj.location = loc
    return obj


def cyl(name, radius=0.5, depth=1.0, verts=32, loc=(0, 0, 0), col=None, caps=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm, cap_ends=caps, cap_tris=False, segments=verts,
        radius1=radius, radius2=radius, depth=depth,
    )
    obj = bm_to_obj(bm, name, col)
    obj.location = loc
    return obj


def tube(name, r_out=0.5, r_in=0.4, depth=1.0, verts=48, loc=(0, 0, 0), col=None):
    """A hollow annular ring (open both ends) — machined bezel / bearing race."""
    bm = bmesh.new()
    hz = depth / 2.0
    rings = {}  # (side, radius_key) -> [verts]
    for zi, z in ((0, -hz), (1, hz)):
        for rk, r in (("o", r_out), ("i", r_in)):
            loop = []
            for k in range(verts):
                a = (k / verts) * math.tau
                loop.append(bm.verts.new((math.cos(a) * r, math.sin(a) * r, z)))
            rings[(zi, rk)] = loop

    def bridge(a, b, flip=False):
        for k in range(verts):
            v1 = a[k]; v2 = a[(k + 1) % verts]
            v3 = b[(k + 1) % verts]; v4 = b[k]
            f = (v1, v2, v3, v4) if not flip else (v4, v3, v2, v1)
            bm.faces.new(f)

    bridge(rings[(0, "o")], rings[(1, "o")])          # outer wall
    bridge(rings[(1, "i")], rings[(0, "i")])          # inner wall
    bridge(rings[(1, "o")], rings[(1, "i")])          # top annulus
    bridge(rings[(0, "i")], rings[(0, "o")])          # bottom annulus
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = bm_to_obj(bm, name, col)
    obj.location = loc
    return obj


def torus(name, major=0.5, minor=0.06, mj=48, mn=16, loc=(0, 0, 0), col=None):
    bm = bmesh.new()
    rings = []
    for i in range(mj):
        a = (i / mj) * math.tau
        centre = Vector((math.cos(a) * major, math.sin(a) * major, 0.0))
        radial = Vector((math.cos(a), math.sin(a), 0.0))
        loop = []
        for j in range(mn):
            b = (j / mn) * math.tau
            v = centre + radial * (math.cos(b) * minor) + Vector((0, 0, math.sin(b) * minor))
            loop.append(bm.verts.new(v))
        rings.append(loop)
    for i in range(mj):
        cur = rings[i]
        nxt = rings[(i + 1) % mj]
        for j in range(mn):
            v1 = cur[j]; v2 = cur[(j + 1) % mn]
            v3 = nxt[(j + 1) % mn]; v4 = nxt[j]
            bm.faces.new((v1, v2, v3, v4))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = bm_to_obj(bm, name, col)
    obj.location = loc
    return obj


def panel_cut(obj, count=6, depth=0.006, axis="Z"):
    """Inset-and-extrude thin recessed panel lines — the machined seam look."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    faces = list(bm.faces)
    for i, f in enumerate(faces):
        if i % max(1, len(faces) // count) != 0:
            continue
        r = bmesh.ops.inset_individual(bm, faces=[f], thickness=0.01, depth=0.0)
        inner = [g for g in ([f] + r.get("faces", []))]
        bmesh.ops.translate(bm, verts=list({v for g in inner for v in g.verts}),
                            vec=f.normal * -depth)
    bm.to_mesh(me)
    bm.free()
    return obj


# ----------------------------------------------------------------------------
# Export — neutral PBR glTF, web-friendly, optional Draco.
# ----------------------------------------------------------------------------
def join_all(objs, name):
    # Deselect everything first so we never sweep unrelated objects into the join.
    bpy.ops.object.select_all(action="DESELECT")
    objs = [o for o in objs if o and o.name in bpy.data.objects]
    # Bake each part's modifiers BEFORE joining. Otherwise the first part's live
    # Bevel/Subsurf re-applies to every part joined into it (silent tri blow-up).
    for o in objs:
        apply_modifiers(o)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    if len(objs) > 1:
        bpy.ops.object.join()
    result = bpy.context.view_layer.objects.active
    result.name = name
    result.data.name = name
    bpy.ops.object.select_all(action="DESELECT")
    return result


def set_origin_bottom(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="BOUNDS")
    return obj


def export_glb(path, draco=True, only_selected=False):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    kwargs = dict(
        filepath=path,
        export_format="GLB",
        export_apply=True,            # apply modifiers
        export_yup=True,              # glTF convention
        export_normals=True,
        export_tangents=True,
        export_materials="EXPORT",
        export_cameras=False,
        export_lights=False,
        use_selection=only_selected,
    )
    if draco:
        kwargs.update(
            export_draco_mesh_compression_enable=True,
            export_draco_mesh_compression_level=6,
        )
    bpy.ops.export_scene.gltf(**kwargs)
    return os.path.getsize(path)


def report(path, size):
    print(f"[SOVEREIGN] exported {path}  ({size/1024:.1f} KB)")


# ----------------------------------------------------------------------------
# Lookdev render — a cold three-point studio matching the film's key light.
# Used to visually verify each asset (Critic Mode) without a GPU.
# ----------------------------------------------------------------------------
def lookdev_render(path, cam_loc=(2.4, -3.0, 1.6), target=(0, 0, 0.4),
                   lens=65, samples=64, res=(960, 600), key_energy=600,
                   rim_color=(0.05, 0.68, 0.66), bg=0.016):
    scene = bpy.context.scene

    cam_data = bpy.data.cameras.new("LookCam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("LookCam", cam_data)
    scene.collection.objects.link(cam)
    cam.location = Vector(cam_loc)
    # aim
    direction = Vector(target) - Vector(cam_loc)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    scene.camera = cam

    # Cold key (surgical white), soft fill, cyan data rim.
    def area(name, energy, size, loc, color=(1, 1, 1)):
        ld = bpy.data.lights.new(name, "AREA")
        ld.energy = energy
        ld.size = size
        ld.color = color
        o = bpy.data.objects.new(name, ld)
        scene.collection.objects.link(o)
        o.location = Vector(loc)
        d = Vector(target) - Vector(loc)
        o.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
        return o

    # Neutral cold key dominates; cyan rim is a restrained accent, not a flood.
    area("Key", key_energy, 3.0, (3.0, -2.5, 4.0), (0.86, 0.9, 0.96))
    area("Fill", key_energy * 0.16, 4.0, (-3.5, -1.0, 1.5), (0.66, 0.74, 0.82))
    area("Rim", key_energy * 0.30, 1.6, (-1.5, 3.0, 2.0), rim_color)

    scene.render.engine = "CYCLES"
    try:
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = True
    except Exception:
        pass
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("W")
    scene.world.use_nodes = True
    bgn = scene.world.node_tree.nodes["Background"]
    bgn.inputs[0].default_value = (bg, bg, bg * 1.1, 1)
    bgn.inputs[1].default_value = 1.0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print(f"[SOVEREIGN] lookdev {path}")
    return path


# ----------------------------------------------------------------------------
# Texture baking — Cycles AO / occlusion enrichment ("재질 베이크", docs/06).
#
# The canonical materials are factor-only PBR, so the ONE map that genuinely
# enriches a hero is ambient occlusion: soft contact shadows in the machined
# joinery and seams. We unwrap every part of an asset, PACK them into a single
# shared 0..1 atlas, and bake all parts into ONE image in a single pass. The
# result is then (a) multiplied into Base Color — the robust path that survives
# glTF as a baseColorTexture — and (b) exposed as a true glTF *occlusionTexture*
# (R channel) via the exporter's "glTF Material Output" node group. Roughness and
# Metallic stay factors: with flat per-material PBR there is no per-texel R/M
# variation to bake, so a baked ORM would only bloat the GLB (docs/06 §4 policy).
#
# These are additive helpers — nothing above depends on them, and the existing
# build_*.py scripts are unaffected.
# ----------------------------------------------------------------------------
def smart_uv(obj, angle=66, island_margin=0.02):
    """Angle-based Smart UV Project on a single object.

    Enters edit mode, selects all, unwraps with `bpy.ops.uv.smart_project`, and
    returns to object mode. Creates a UV layer if the object has none (imported
    factor-only meshes ship without UVs). Leaves the object deselected.
    """
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(angle),
                             island_margin=island_margin)
    bpy.ops.object.mode_set(mode="OBJECT")
    obj.select_set(False)
    return obj


def _pack_atlas(objs, margin=0.01):
    """Multi-object UV pack: lay every object's islands into one shared 0..1 atlas
    so a single shared bake image has no overlap between parts."""
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.uv.pack_islands(margin=margin)
    except Exception:
        pass
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")


def _materials_of(objs):
    """Ordered unique list of materials used by a set of objects (shared-safe)."""
    seen = []
    for o in objs:
        for slot in o.material_slots:
            if slot.material and slot.material not in seen:
                seen.append(slot.material)
    return seen


def bake_ao(objs, path, res=1024, samples=64, margin=8, ao_distance=0.3,
            isolate=False):
    """Bake Cycles ambient occlusion for `objs` into ONE shared image atlas.

    Each object is unwrapped (if needed) and all islands are packed into a single
    0..1 atlas. Every material used by `objs` gets an Image Texture node pointing
    at the shared image, set active/selected, so a single `bake(type='AO')` over
    all selected objects writes each part's AO into its packed region (objects
    with multiple material slots — e.g. a join_all()'d layer — are handled: every
    slot targets the same image). The image is saved as PNG at `path` and packed.

    `isolate=False` (default) bakes all parts together, so parts mutually occlude
    each other — the right choice for a STATIC assembly (e.g. the auth-door iris),
    where contact shadows between nested rings/bolts are the whole point.

    `isolate=True` bakes each object alone (others hidden), so the AO is pure
    self-occlusion. Use it for a MODULAR asset whose named parts separate/animate
    apart (e.g. the cybernetic spine's 5 layers): mutual baking would "print" one
    layer's silhouette onto another as a contact-shadow decal that looks wrong the
    moment the layers explode. Self-occlusion is valid in every assembly state.

    Returns the baked bpy.types.Image.
    """
    objs = [o for o in objs if o and getattr(o, "type", None) == "MESH"]
    if not objs:
        raise ValueError("bake_ao: no mesh objects to bake")

    # 1. Unwrap any object still missing UVs, then pack all into a shared atlas.
    for o in objs:
        if not o.data.uv_layers:
            smart_uv(o)
    _pack_atlas(objs)

    # 2. Shared AO image — linear data, black (fully-lit) background.
    name = os.path.splitext(os.path.basename(path))[0]
    img = bpy.data.images.new(name, res, res, alpha=False, float_buffer=False)
    img.colorspace_settings.name = "Non-Color"
    img.generated_color = (0.0, 0.0, 0.0, 1.0)

    # 3. Point every material's active image node at the shared atlas.
    for mat in _materials_of(objs):
        nt = mat.node_tree
        for n in nt.nodes:
            n.select = False
        node = next((n for n in nt.nodes
                     if n.type == "TEX_IMAGE" and n.image == img), None)
        if node is None:
            node = nt.nodes.new("ShaderNodeTexImage")
            node.image = img
            node.location = (-1000, -420)
        node.select = True
        nt.nodes.active = node

    # 4. Cycles CPU AO bake. use_clear=False so every part accumulates into the
    #    one atlas; world AO distance keeps occlusion contact-range, not global.
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    try:
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_denoising = False   # AO is data; denoise would smear seams
    except Exception:
        pass
    if scene.world is None:
        scene.world = bpy.data.worlds.new("BakeWorld")
    scene.world.light_settings.distance = ao_distance
    bake = scene.render.bake
    bake.use_clear = False
    bake.margin = margin
    bake.use_selected_to_active = False

    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    if isolate:
        # Bake each object alone (pure self-occlusion), accumulating into the
        # atlas. Hide EVERY other mesh in the scene — not just the other bake
        # targets but any un-baked/skipped part too — so nothing prints its
        # silhouette onto a part that will later separate from it.
        scene_meshes = [m for m in bpy.data.objects if m.type == "MESH"]
        prev_hide = {m.name: m.hide_render for m in scene_meshes}
        for o in objs:
            for m in scene_meshes:
                m.hide_render = (m is not o)
            bpy.ops.object.select_all(action="DESELECT")
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.bake(type="AO")
        for m in scene_meshes:
            m.hide_render = prev_hide.get(m.name, False)
    else:
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.bake(type="AO")

    # 5. Save + pack so the map travels inside the GLB.
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.filepath_raw = path
    img.file_format = "PNG"
    img.save()
    try:
        img.pack()
    except Exception:
        pass
    print(f"[SOVEREIGN] baked AO {path}  ({res}x{res}, {samples} spp)")
    return img


def _gltf_occlusion_group():
    """Fetch/create the exporter-recognised 'glTF Material Output' node group
    (an 'Occlusion' float input). Connecting an AO image's Color to a group-node
    instance of this tells the glTF exporter to write a real occlusionTexture."""
    name = "glTF Material Output"
    grp = bpy.data.node_groups.get(name)
    if grp is None:
        grp = bpy.data.node_groups.new(name, "ShaderNodeTree")
        grp.interface.new_socket("Occlusion", socket_type="NodeSocketFloat")
        grp.nodes.new("NodeGroupOutput")
        gi = grp.nodes.new("NodeGroupInput")
        gi.location = (-200, 0)
    return grp


def apply_ao_to_material(mat, image, strength=0.85, gltf_occlusion=True):
    """Wire a baked AO `image` into `mat`.

    (1) Multiply the AO into Base Color (MixRGB MULTIPLY, `strength` as factor) so
        the contact shadows survive glTF export as a baseColorTexture — the simple,
        robust, universally-visible path. Emission sockets are left untouched, so
        cyan-data and amber-warning glows keep full strength.
    (2) Best-effort: also expose the AO as a true glTF occlusionTexture (R channel)
        via the 'glTF Material Output' node group, so a PBR-correct runtime can read
        it from the dedicated slot. Wrapped so it can never break export.
    """
    if not mat.use_nodes:
        return mat
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF") or next(
        (n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return mat

    tex = next((n for n in nt.nodes
                if n.type == "TEX_IMAGE" and n.image == image), None)
    if tex is None:
        tex = nt.nodes.new("ShaderNodeTexImage")
        tex.image = image
    tex.image.colorspace_settings.name = "Non-Color"
    tex.location = (-1000, -200)

    # (1) AO * Base Color
    base_in = bsdf.inputs["Base Color"]
    mix = nt.nodes.new("ShaderNodeMixRGB")
    mix.blend_type = "MULTIPLY"
    mix.inputs["Fac"].default_value = strength
    mix.location = (-560, 200)
    if base_in.is_linked:
        nt.links.new(base_in.links[0].from_socket, mix.inputs["Color1"])
    else:
        mix.inputs["Color1"].default_value = list(base_in.default_value)
    nt.links.new(tex.outputs["Color"], mix.inputs["Color2"])
    nt.links.new(mix.outputs["Color"], base_in)

    # (2) glTF occlusionTexture (R channel) — best effort
    if gltf_occlusion:
        try:
            gnode = nt.nodes.new("ShaderNodeGroup")
            gnode.node_tree = _gltf_occlusion_group()
            gnode.location = (-260, -420)
            nt.links.new(tex.outputs["Color"], gnode.inputs["Occlusion"])
        except Exception:
            pass
    return mat
