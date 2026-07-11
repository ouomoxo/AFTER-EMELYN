"""
SOVEREIGN//77 — ACT I "CITY NERVOUS SYSTEM" prerendered flythrough (Cycles).

Builds the dense machine-interior of the vertical data shaft and flies a camera
descending through it for 72 frames (3s @ 24fps), then encodes a VP9/VP8 webm and
writes the FINAL camera transform to JSON so the realtime InfrastructureScene can
match its first frame — the prerender -> realtime cut is meant to be invisible.

World is authored in a THREE.js-compatible frame (Y is up, camera looks down its
local -Z, sensor 24mm VERTICAL) so exported transforms drop straight into the
realtime scene (src/engine/core/CameraDirector.lensToFov uses sensor=24, vertical
FOV). Geometry, palette and lighting mirror src/engine/scenes/InfrastructureScene.ts:
central emissive-cyan core, graphite ring "vertebrae", spiralling server racks /
cooling units / fiber boxes on the walls at radius ~4, vertical data conduits,
drones, and a cool key that travels with the camera raking the passing organs.

Run headless:
    python3 tools/blender/render_infra_flythrough.py           # full 72-frame render
    INFRA_QUICK=1 python3 tools/blender/render_infra_flythrough.py   # 3 frames, low smp

Out:
    public/assets/video/infra_flythrough.webm     (VP8/VP9)
    public/assets/video/infra_flythrough.json     (final camera contract)
    docs/_ref/infra_flythrough_first.png / _last.png
"""

import os
import sys
import math
import json
import shutil
import subprocess

sys.path.insert(0, os.path.dirname(__file__))
import bpy  # type: ignore
from mathutils import Vector, Quaternion  # type: ignore
import sovereign_bpy as S

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MODELS = os.path.join(ROOT, "public", "assets", "models")
VIDEO_DIR = os.path.join(ROOT, "public", "assets", "video")
SEQ_DIR = os.path.join(VIDEO_DIR, "infra_seq")
REF_DIR = os.path.join(ROOT, "docs", "_ref")
OUT_WEBM = os.path.join(VIDEO_DIR, "infra_flythrough.webm")
OUT_JSON = os.path.join(VIDEO_DIR, "infra_flythrough.json")
REF_FIRST = os.path.join(REF_DIR, "infra_flythrough_first.png")
REF_LAST = os.path.join(REF_DIR, "infra_flythrough_last.png")

SCRATCH = os.environ.get(
    "INFRA_SCRATCH",
    "/tmp/claude-0/-home-user-AFTER-EMELYN/2b60fd1f-0b2f-564a-a625-0f28992513cb/scratchpad",
)
FRAMES_DIR = os.path.join(SCRATCH, "infra_frames")

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
QUICK = os.environ.get("INFRA_QUICK") == "1"
FPS = 24
N_FRAMES = 72
RES = (1280, 720)
SAMPLES = 20 if QUICK else int(os.environ.get("INFRA_SAMPLES", "18"))
QUICK_FRAMES = [1, 24, 48, 72]

# Camera descent law (Y-up, mirrors InfrastructureScene: cam at (0,camY,camZ)
# looking at (0, camY-4, 0); lens widens on the fall).
Y_START, Y_END = 6.0, -56.0
Z_START, Z_END = 6.6, 3.7
LENS_START, LENS_END = 22.0, 28.0
LOOK_DROP = 4.0            # target sits this far below the camera (down the shaft)
SENSOR_H = 24.0           # full-frame height -> matches CameraDirector.lensToFov

# Emission (kept restrained; AgX rolls the highlights so the core never clips).
CORE_EMIT = 1.5
CONDUIT_EMIT = 1.4
MOTE_EMIT = 4.5

# Shaft extents
Y_TOP, Y_BOT = 14.0, -132.0


# ----------------------------------------------------------------------------
# Easing — the 3-beat "slow -> move -> settle".
# ----------------------------------------------------------------------------
def _clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)


def smoothstep(x):
    x = _clamp01(x)
    return x * x * (3.0 - 2.0 * x)


def smootherstep(x):
    x = _clamp01(x)
    return x * x * x * (x * (x * 6.0 - 15.0) + 10.0)


def descent_ease(u):
    # Slow establish, committed plunge, decelerating settle.
    return smootherstep(u)


def lens_ease(u):
    # Hold the tight 22mm through the establish beat, then breathe wider.
    return smoothstep(_clamp01((u - 0.14) / 0.86))


def lerp(a, b, t):
    return a + (b - a) * t


# ----------------------------------------------------------------------------
# Scene / render setup
# ----------------------------------------------------------------------------
def setup_scene():
    scene = S.reset()
    scene.render.engine = "CYCLES"
    cy = scene.cycles
    cy.device = "CPU"
    cy.samples = SAMPLES
    cy.use_denoising = True
    try:
        cy.denoiser = "OPENIMAGEDENOISE"
    except Exception:
        pass
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.05
    # Dark enclosed shaft: deep GI is costly and near-invisible. Direct light +
    # emissive core carry the image; one indirect bounce is plenty with denoise.
    cy.max_bounces = 3
    cy.diffuse_bounces = 1
    cy.glossy_bounces = 1
    cy.transmission_bounces = 0
    cy.transparent_max_bounces = 2
    cy.volume_bounces = 0
    cy.sample_clamp_indirect = 2.0
    cy.sample_clamp_direct = 0.0
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.use_fast_gi = False
    try:
        cy.use_light_tree = True
        cy.light_sampling_threshold = 0.05
    except Exception:
        pass
    scene.render.threads_mode = "AUTO"

    scene.render.use_persistent_data = True
    scene.render.resolution_x, scene.render.resolution_y = RES
    scene.render.resolution_percentage = 100
    scene.render.fps = FPS
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.compression = 15

    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "None"
    except Exception:
        pass

    # Dark blue-black void — echoes FogExp2(0x04060a) in the realtime scene.
    world = bpy.data.worlds.new("W_Infra")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.0052, 0.0068, 0.0092, 1.0)
    bg.inputs[1].default_value = 1.0
    return scene


# ----------------------------------------------------------------------------
# Geometry helpers
# ----------------------------------------------------------------------------
def vcyl(name, radius, y0, y1, verts, mat, col, caps=True):
    """A cylinder that runs along the world Y axis (the shaft is vertical)."""
    depth = y1 - y0
    o = S.cyl(name, radius=radius, depth=depth, verts=verts, col=col, caps=caps)
    o.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    o.location = (0.0, (y0 + y1) * 0.5, 0.0)
    S.assign(o, mat)
    return o


def unlink_everywhere(obj):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)


def instance_along_y(proto, placements, col, name):
    """Linked-duplicate `proto` (shares mesh data -> Cycles instances it)."""
    out = []
    for i, (loc, rot, scl) in enumerate(placements):
        d = proto.copy()
        d.name = f"{name}_{i:03d}"
        d.location = loc
        if rot is not None:
            d.rotation_euler = rot
        if scl is not None:
            d.scale = (scl, scl, scl)
        col.objects.link(d)
        out.append(d)
    return out


# ----------------------------------------------------------------------------
# GLB import + collection-instance placement (shared BVH, cheap to render).
# ----------------------------------------------------------------------------
def _find_layer_collection(root, name):
    if root.collection.name == name:
        return root
    for ch in root.children:
        r = _find_layer_collection(ch, name)
        if r:
            return r
    return None


def import_asset(name, decimate=0.5):
    scene = bpy.context.scene
    vl = bpy.context.view_layer
    src = bpy.data.collections.new("SRC_" + name)
    scene.collection.children.link(src)
    lc = _find_layer_collection(vl.layer_collection, src.name)
    vl.active_layer_collection = lc

    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=os.path.join(MODELS, name + ".glb"))
    new = [o for o in bpy.data.objects if o not in before]

    # These are background organs seen at distance and in motion — collapse the
    # fine machining so the BVH is cheap to trace (halves per-sample cost).
    if decimate and decimate < 1.0:
        for o in new:
            if o.type != "MESH" or len(o.data.polygons) < 200:
                continue
            md = o.modifiers.new("Dec", "DECIMATE")
            md.ratio = decimate
            bpy.context.view_layer.objects.active = o
            try:
                bpy.ops.object.modifier_apply(modifier=md.name)
            except Exception:
                pass

    mins = [1e9, 1e9, 1e9]
    maxs = [-1e9, -1e9, -1e9]
    for o in new:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for k in range(3):
                mins[k] = min(mins[k], w[k])
                maxs[k] = max(maxs[k], w[k])
    dims = tuple(maxs[k] - mins[k] for k in range(3))
    # instance_offset = base-centre (asset is Z-up, base near z=min).
    src.instance_offset = ((mins[0] + maxs[0]) * 0.5, (mins[1] + maxs[1]) * 0.5, mins[2])
    lc.exclude = True  # hide originals from the render; instances still draw.
    return src, dims


def tame_emitters(mode="camera", keep=("M_ShaftCore",)):
    """The GLB machinery ships emissive materials (cyan slots, amber ticks); with
    ~60 instances that is hundreds of mesh lights in the light tree — the dominant
    per-sample cost. Take every emissive material (except the hero core) out of the
    light tree so it no longer acts as a scene light. 'camera' keeps the on-screen
    glow by gating emission to camera rays only; 'zero' drops emission entirely.
    Either way it is a large render-time win with (near) no change to the look.
    """
    for mat in bpy.data.materials:
        if not mat.use_nodes or mat.name in keep:
            continue
        nt = mat.node_tree
        bsdf = nt.nodes.get("Principled BSDF")
        if bsdf is None:
            continue
        es = bsdf.inputs.get("Emission Strength")
        if es is None or es.default_value <= 0.0:
            continue
        base = float(es.default_value)
        if mode == "zero":
            es.default_value = 0.0
        elif mode == "camera":
            lp = nt.nodes.new("ShaderNodeLightPath")
            mul = nt.nodes.new("ShaderNodeMath")
            mul.operation = "MULTIPLY"
            mul.inputs[1].default_value = base
            nt.links.new(lp.outputs["Is Camera Ray"], mul.inputs[0])
            nt.links.new(mul.outputs[0], es)
        mat["_tamed"] = base
    return None


def place_module(src, col, radius, azimuth, y_base, scale, name):
    """Stand a Z-up asset up along +Y and face its front (-Y local) inward."""
    e = bpy.data.objects.new(name, None)
    e.instance_type = "COLLECTION"
    e.instance_collection = src
    e.empty_display_size = 0.2
    e.location = (radius * math.cos(azimuth), y_base, radius * math.sin(azimuth))
    beta = math.atan2(-math.cos(azimuth), -math.sin(azimuth))
    q = Quaternion((0.0, 1.0, 0.0), beta) @ Quaternion((1.0, 0.0, 0.0), math.radians(-90.0))
    e.rotation_euler = q.to_euler()
    e.scale = (scale, scale, scale)
    col.objects.link(e)
    return e


# ----------------------------------------------------------------------------
# Build the machine interior
# ----------------------------------------------------------------------------
def build_world():
    scene = setup_scene()
    world_col = S.collection("INFRA")

    m_core = S.material("M_ShaftCore", S.PAL["cyan"], 0.0, 0.30,
                        emission=S.PAL["cyan"], emission_strength=CORE_EMIT)
    # Matte dark shell (dielectric, not metal) — cheap to shade, kills the void.
    m_shell = S.material("M_ShaftShell", S.PAL["obsidian_deep"], 0.0, 0.9)
    m_ring = S.material("M_Vertebra", S.PAL["graphite_light"], 1.0, 0.40)
    m_conduit = S.material("M_Conduit", S.PAL["graphite"], 1.0, 0.50)
    m_conduit_hi = S.material("M_ConduitLit", S.PAL["cyan"], 0.0, 0.40,
                              emission=S.PAL["cyan"], emission_strength=CONDUIT_EMIT)
    m_mote = S.material("M_DataMote", S.PAL["cyan"], 0.0, 0.40,
                        emission=S.PAL["cyan"], emission_strength=MOTE_EMIT)

    # --- Shaft shell: a dark matte tube enclosing the descent (no void). -----
    # Radius must exceed the camera's outermost Z (Z_START) so we stay inside it.
    shell = vcyl("ShaftShell", 9.0, Y_BOT, Y_TOP, 48, m_shell, world_col, caps=False)
    # Flip normals inward so we see the interior wall from inside.
    for p in shell.data.polygons:
        p.flip()

    # --- Central emissive-cyan core (the spine). -----------------------------
    vcyl("ShaftCore", 0.28, Y_BOT, Y_TOP, 24, m_core, world_col)

    # --- Ring "vertebrae" descending the shaft (instanced torus). ------------
    ring = S.torus("RingProto", major=2.55, minor=0.10, mj=44, mn=10, col=world_col)
    ring.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    bpy.context.view_layer.objects.active = ring
    ring.select_set(True)
    bpy.ops.object.transform_apply(rotation=True)
    ring.select_set(False)
    S.assign(ring, m_ring)
    unlink_everywhere(ring)
    ring_places = []
    y = Y_TOP - 2.0
    while y > Y_BOT + 2.0:
        ring_places.append(((0.0, y, 0.0), None, None))
        y -= 3.7
    instance_along_y(ring, ring_places, world_col, "Ring")

    # --- Vertical conduits: nerves & cabling for parallax streaks. -----------
    dark_proto = vcyl("ConduitProto", 0.06, Y_BOT, Y_TOP, 6, m_conduit, world_col)
    unlink_everywhere(dark_proto)
    lit_proto = vcyl("ConduitLitProto", 0.035, Y_BOT, Y_TOP, 6, m_conduit_hi, world_col)
    unlink_everywhere(lit_proto)
    # Conduits ride the mid-layer (outside the core, inside the machinery) so the
    # central cyan spine stays alone. Only a few carry data light — the rest are
    # dark structure, so cyan reads as restrained data, not a flood.
    dark_places, lit_places = [], []
    N_COND = 20
    for i in range(N_COND):
        a = (i / N_COND) * math.tau + 0.15
        r = 3.15 + (i % 4) * 0.34
        loc = (r * math.cos(a), 0.0, r * math.sin(a))
        if i % 7 == 0:  # ~3 lit conduits only
            lit_places.append((loc, None, None))
        else:
            dark_places.append((loc, None, 1.0 + (i % 3) * 0.4))
    instance_along_y(dark_proto, dark_places, world_col, "Conduit")
    instance_along_y(lit_proto, lit_places, world_col, "ConduitLit")

    # --- Machinery spiralling on the walls (server racks dominate). ----------
    assets = {}
    for name in ("server_rack", "cooling_unit", "fiber_box"):
        assets[name], _ = import_asset(name)
    seq = ["server_rack", "cooling_unit", "server_rack", "fiber_box",
           "server_rack", "cooling_unit", "fiber_box", "server_rack"]
    scale_of = {"server_rack": 1.30, "cooling_unit": 1.15, "fiber_box": 1.35}
    N_MOD = 46
    for i in range(N_MOD):
        a = (i / N_MOD) * math.tau * 3.0 + (i % 2) * 0.42
        y = 7.0 - i * 2.55
        r = 4.2 + (i % 3) * 0.5
        name = seq[i % len(seq)]
        place_module(assets[name], world_col, r, a, y, scale_of[name], f"mod_{i:02d}")

    # One continuous server "spine" for a strong vertical anchor (kept modest —
    # stacked racks are the heaviest geometry, so we use just one column).
    if os.environ.get("INFRA_NOSPINE") != "1":
        base_a = math.radians(210.0)
        yy = 5.0
        k = 0
        while yy > -70.0:
            place_module(assets["server_rack"], world_col, 4.8,
                         base_a + 0.04 * k, yy, 1.28, f"spine_{k:02d}")
            yy -= 2.35 * 1.28  # rack height * scale -> flush stack
            k += 1

    # --- Data motes drifting up past the fall (echoes the DataStream). -------
    mote = S.cyl("MoteProto", radius=0.028, depth=0.16, verts=6, col=world_col)
    S.assign(mote, m_mote)
    unlink_everywhere(mote)
    import random
    random.seed(77)
    motes = []
    for i in range(26):
        a = random.random() * math.tau
        r = 0.6 + random.random() * 3.4
        loc = (r * math.cos(a), random.uniform(Y_END - 6, Y_START + 8), r * math.sin(a))
        d = mote.copy()
        d.name = f"Mote_{i:02d}"
        d.location = loc
        d.rotation_euler = (0, 0, random.random() * math.tau)
        world_col.objects.link(d)
        d["spd"] = 0.6 + random.random() * 1.8
        d["ry"] = loc[1]
        motes.append(d)

    # --- Maintenance drones drifting in the shaft (instanced GLB). -----------
    drone_src, _ = import_asset("maintenance_drone")
    # (drone placement below)
    drones = []
    random.seed(12)
    for i in range(5):
        y = 2.0 - i * 13.0
        a = random.random() * math.tau
        r = 0.8 + random.random() * 1.6
        e = bpy.data.objects.new(f"Drone_{i}", None)
        e.instance_type = "COLLECTION"
        e.instance_collection = drone_src
        e.location = (r * math.cos(a), y, r * math.sin(a))
        e.rotation_euler = (math.radians(-90.0), 0.0, random.random() * math.tau)
        e.scale = (1.1, 1.1, 1.1)
        e.empty_display_size = 0.2
        world_col.objects.link(e)
        e["base_y"] = y
        e["ph"] = random.random() * math.tau
        drones.append(e)

    tame_emitters(mode=os.environ.get("INFRA_EMIT_MODE", "camera"))
    return scene, m_core, motes, drones


# ----------------------------------------------------------------------------
# Lighting — cold travelling key + restrained cyan data accent.
# ----------------------------------------------------------------------------
def build_lights(scene):
    col = S.collection("INFRA_LIGHT")

    def mklight(name, kind, energy, color, size=1.0):
        ld = bpy.data.lights.new(name, kind)
        ld.energy = energy
        ld.color = color
        if kind == "AREA":
            ld.size = size
        if kind == "POINT":
            ld.shadow_soft_size = size
        o = bpy.data.objects.new(name, ld)
        col.objects.link(o)
        return o

    if os.environ.get("INFRA_LIGHTS") == "simple":
        key = mklight("TravelKey", "SPOT", 6000.0, (0.80, 0.87, 0.96), size=0.2)
        key.data.spot_size = math.radians(90.0)
        key.data.spot_blend = 0.4
        fill = mklight("TravelFill", "SUN", 0.35, (0.42, 0.56, 0.70))
        rim = mklight("DataRim", "POINT", 120.0, (0.05, 0.68, 0.66), size=0.5)
        return {"key": key, "fill": fill, "rim": rim}
    key = mklight("TravelKey", "AREA", 3400.0, (0.80, 0.87, 0.96), size=3.0)
    fill = mklight("TravelFill", "AREA", 520.0, (0.42, 0.56, 0.70), size=4.0)
    rim = mklight("DataRim", "AREA", 240.0, (0.05, 0.68, 0.66), size=1.8)
    return {"key": key, "fill": fill, "rim": rim}


def aim(obj, at):
    d = Vector(at) - obj.location
    if d.length < 1e-6:
        return
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def place_lights(lights, cam_loc, cam_z):
    cx, cy, cz = cam_loc
    lights["key"].location = Vector((3.0, cy + 1.8, cz + 0.6))
    aim(lights["key"], (0.0, cy - 6.0, 0.0))
    lights["fill"].location = Vector((-3.4, cy + 0.5, cz + 1.0))
    aim(lights["fill"], (0.0, cy - 5.0, 0.0))
    lights["rim"].location = Vector((-0.6, cy - 3.2, 1.3))
    aim(lights["rim"], (0.0, cy - 6.0, 0.0))


# ----------------------------------------------------------------------------
# Camera
# ----------------------------------------------------------------------------
def make_camera(scene):
    cd = bpy.data.cameras.new("FlyCam")
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = SENSOR_H
    cd.clip_start = 0.03
    cd.clip_end = 500.0
    cam = bpy.data.objects.new("FlyCam", cd)
    S.collection("INFRA_LIGHT").objects.link(cam)
    scene.camera = cam
    return cam


def camera_state(u):
    """Return (location, look_at, lens) for normalized timeline u in [0,1]."""
    td = descent_ease(u)
    tl = lens_ease(u)
    cy = lerp(Y_START, Y_END, td)
    cz = lerp(Z_START, Z_END, td)
    loc = (0.0, cy, cz)
    look = (0.0, cy - LOOK_DROP, 0.0)
    lens = lerp(LENS_START, LENS_END, tl)
    return loc, look, lens


def apply_camera(cam, loc, look, lens):
    cam.location = Vector(loc)
    d = Vector(look) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.data.lens = lens


# ----------------------------------------------------------------------------
# Per-frame animation of the living world
# ----------------------------------------------------------------------------
def animate(f, m_core, motes, drones):
    t = f / FPS
    # Core breathes (no blow-out — mirrors InfrastructureScene emissive pulse).
    nt = m_core.node_tree
    b = nt.nodes.get("Principled BSDF")
    if b is not None:
        b.inputs["Emission Strength"].default_value = CORE_EMIT * (0.9 + 0.12 * math.sin(t * 3.0))
    for d in motes:
        y = d["ry"] + t * d["spd"] * 6.0
        span = (Y_START + 8) - (Y_END - 6)
        y = (Y_END - 6) + ((y - (Y_END - 6)) % span)
        d.location.y = y
    for d in drones:
        d.location.y = d["base_y"] + math.sin(t * 0.6 + d["ph"]) * 0.7
        d.rotation_euler.z += 0.02


# ----------------------------------------------------------------------------
# Render
# ----------------------------------------------------------------------------
def render_frames():
    scene, m_core, motes, drones = build_world()
    lights = build_lights(scene)
    cam = make_camera(scene)

    os.makedirs(FRAMES_DIR, exist_ok=True)
    env_frames = os.environ.get("INFRA_FRAMES")
    if env_frames:
        frame_list = [int(x) for x in env_frames.split(",") if x.strip()]
    elif QUICK:
        frame_list = QUICK_FRAMES
    else:
        frame_list = list(range(1, N_FRAMES + 1))
    written = []
    for f in frame_list:
        u = (f - 1) / (N_FRAMES - 1)
        loc, look, lens = camera_state(u)
        apply_camera(cam, loc, look, lens)
        place_lights(lights, loc, loc[2])
        animate(f, m_core, motes, drones)
        scene.frame_set(f)
        out = os.path.join(FRAMES_DIR, f"frame_{f:04d}")
        scene.render.filepath = out
        print(f"[INFRA] render frame {f}/{N_FRAMES}  camY={loc[1]:.1f} lens={lens:.1f}", flush=True)
        bpy.ops.render.render(write_still=True)
        written.append(out + ".png")
    return written


# ----------------------------------------------------------------------------
# Encode + refs + JSON
# ----------------------------------------------------------------------------
def find_ffmpeg():
    for c in ("/opt/pw-browsers/ffmpeg-1011/ffmpeg-linux",
              "/opt/pw-browsers/ffmpeg-1011/ffmpeg"):
        if os.path.exists(c) and os.access(c, os.X_OK):
            return c
    return shutil.which("ffmpeg")


def write_refs():
    first = os.path.join(FRAMES_DIR, "frame_0001.png")
    last = os.path.join(FRAMES_DIR, f"frame_{N_FRAMES:04d}.png")
    os.makedirs(REF_DIR, exist_ok=True)
    if os.path.exists(first):
        shutil.copyfile(first, REF_FIRST)
    if os.path.exists(last):
        shutil.copyfile(last, REF_LAST)


def encode_webm():
    """Concatenate rendered PNGs -> JPEG stream -> VP8/VP9 webm via ffmpeg."""
    ff = find_ffmpeg()
    os.makedirs(VIDEO_DIR, exist_ok=True)
    frames = [os.path.join(FRAMES_DIR, f"frame_{f:04d}.png") for f in range(1, N_FRAMES + 1)]
    frames = [p for p in frames if os.path.exists(p)]
    if ff is None or len(frames) < N_FRAMES:
        # Fallback: publish the PNG image sequence.
        os.makedirs(SEQ_DIR, exist_ok=True)
        for i, p in enumerate(frames, 1):
            shutil.copyfile(p, os.path.join(SEQ_DIR, f"frame_{i:04d}.png"))
        return None, "no-ffmpeg" if ff is None else "missing-frames"

    from PIL import Image
    mjpeg = os.path.join(FRAMES_DIR, "concat.mjpeg")
    with open(mjpeg, "wb") as fh:
        for p in frames:
            Image.open(p).convert("RGB").save(fh, "JPEG", quality=92)

    # Codec: prefer VP9, fall back to VP8 (this ffmpeg build only ships libvpx/VP8).
    codecs = []
    enc = subprocess.run([ff, "-hide_banner", "-encoders"], capture_output=True, text=True)
    if "libvpx-vp9" in enc.stdout:
        codecs.append(("libvpx-vp9", ["-b:v", "0", "-crf", "33"]))
    if "libvpx" in enc.stdout:
        codecs.append(("libvpx", ["-b:v", "2400k", "-crf", "12", "-auto-alt-ref", "0"]))
    used = None
    for codec, extra in codecs:
        # image2pipe needs the input codec named explicitly (concatenated JPEGs).
        cmd = [ff, "-y", "-f", "image2pipe", "-vcodec", "mjpeg", "-framerate", str(FPS),
               "-i", mjpeg, "-c:v", codec, *extra, "-pix_fmt", "yuv420p", "-r", str(FPS),
               "-an", OUT_WEBM]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and os.path.exists(OUT_WEBM) and os.path.getsize(OUT_WEBM) > 0:
            used = codec
            break
        else:
            print("[INFRA] ffmpeg failed for", codec, "\n", r.stderr[-800:], flush=True)
    return (OUT_WEBM if used else None), (used or "encode-failed")


def write_json():
    loc, look, lens = camera_state(1.0)
    d = Vector(look) - Vector(loc)
    quat = d.to_track_quat("-Z", "Y")
    eul = quat.to_euler()
    aspect = RES[0] / RES[1]
    vfov = math.degrees(2.0 * math.atan(SENSOR_H / (2.0 * lens)))
    hfov = math.degrees(2.0 * math.atan((SENSOR_H * aspect) / (2.0 * lens)))
    data = {
        "_comment": "Final camera of infra_flythrough.webm. Realtime InfrastructureScene "
                    "matches this on its first frame for an invisible video->realtime cut. "
                    "Y-up, right-handed, camera looks down local -Z (three.js convention). "
                    "FOV convention matches CameraDirector.lensToFov (sensor height 24mm, vertical).",
        "position": [round(loc[0], 5), round(loc[1], 5), round(loc[2], 5)],
        "lookAt": [round(look[0], 5), round(look[1], 5), round(look[2], 5)],
        "up": [0.0, 1.0, 0.0],
        "rotationEuler": [round(eul.x, 6), round(eul.y, 6), round(eul.z, 6)],
        "rotationEulerOrder": "XYZ",
        "quaternion": [round(quat.x, 6), round(quat.y, 6), round(quat.z, 6), round(quat.w, 6)],
        "lens_mm": round(lens, 4),
        "sensor_fit": "VERTICAL",
        "sensor_height_mm": SENSOR_H,
        "fov_vertical_deg": round(vfov, 4),
        "fov_horizontal_deg": round(hfov, 4),
        "aspect": round(aspect, 6),
        "resolution": list(RES),
        "fps": FPS,
        "frames": N_FRAMES,
    }
    os.makedirs(VIDEO_DIR, exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(data, fh, indent=2)
    return data


# ----------------------------------------------------------------------------
def main():
    render_frames()
    write_refs()
    if QUICK:
        print("[INFRA] QUICK mode: skipped encode.")
        write_json()
        return
    path, codec = encode_webm()
    data = write_json()
    if path:
        sz = os.path.getsize(path)
        print(f"[INFRA] webm: {path}  {sz/1024/1024:.2f} MB  codec={codec}")
    else:
        print(f"[INFRA] no webm ({codec}); PNG sequence in {SEQ_DIR}")
    print("[INFRA] final camera:", json.dumps(data))


if __name__ == "__main__":
    main()
