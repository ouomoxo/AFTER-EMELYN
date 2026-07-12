"""
SOVEREIGN//77 — HERO ENVIRONMENT: Authentication Pressure Door (PROLOGUE / HANDSHAKE).

The "black screen" of the prologue is revealed to be a monumental blast door set
into a machined bulkhead — a bank-vault / blast-bunker plug that dwarfs the
subject. Not a flat scanner panel: a complete architecture with mass, joinery,
and depth.

    Wall           the machined bulkhead the door is set into (portal frame)
    Leaf_L / Leaf_R  two THICK vault leaves that part along the seam (animated)
    Core           the cyan authentication lens at the seam centre (animated)
    Hydraulics     the rams that drive the leaves (revealed as they part)
    LockDogs_L/R   radial locking bolts on the leaf edges
    Tunnel         the lit shaft behind the door the camera is pulled INTO
    Floor          a grated deck giving human scale

Depth is authored along -Z (into the wall / tunnel); the front face is +Z. The
web stands the whole set up (rotation.x=+90°) so width→X, height→Y, front→+Z.

Run:  python3 tools/blender/build_auth_door.py [--render]
Out:  public/assets/models/auth_door.glb
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(__file__))
import bpy, bmesh  # type: ignore
from mathutils import Vector  # type: ignore
import sovereign_bpy as S
import sovereign_kit as K

RENDER = "--render" in sys.argv
OUT = os.path.join(os.path.dirname(__file__), "../../public/assets/models/auth_door.glb")
REF = os.path.join(os.path.dirname(__file__), "../../docs/_ref/auth_door.png")

S.reset()
col = S.collection("AUTH_DOOR")
m = S.mats()

# --- Dimensions (metres). A blast door that dwarfs the subject. ---
PW, PH = 2.05, 2.35        # portal half-width / half-height (opening 4.1 x 4.7)
LT = 0.58                  # leaf thickness (Z)
SEAM = 0.010               # centre gap between leaves
WALL_X, WALL_Y = 5.4, 3.9  # wall half-extents
WALL_BACK = -1.6           # wall rear face (Z)
WALL_FRONT = 0.02          # wall front face (Z)
CORE_R = 0.78              # central authentication boss radius (the eye)

Z = Vector((0, 0, 1))


def hazard_stripe(name, center, u, v, w, h, col, mats, n=6):
    """A flush warning stripe — alternating amber / graphite blocks in the u,v
    plane. u,v are in-plane unit axes so it seats flat on any surface."""
    out = []
    u = Vector(u).normalized(); v = Vector(v).normalized()
    back = K._plate(f"{name}_bk", Vector(center), u, v, w, h, 0.02, col, mats["graphite_worn"])
    out.append(back)
    n2 = u.cross(v).normalized()
    for i in range(n):
        if i % 2:
            continue
        fx = -w / 2 + (i + 0.5) * (w / n)
        blk = K._plate(f"{name}_b{i}", Vector(center) + n2 * 0.008 + u * fx,
                       u, v, w / n * 0.9, h * 0.86, 0.01, col, mats["warning"])
        out.append(blk)
    return out


# ===========================================================================
# WALL — the machined bulkhead. A heavy frame around the portal so the opening
# reads with real depth (its inner faces show the wall's ~1.5m thickness).
# ===========================================================================
wall_parts = []
frame_boxes = [
    ("Wall_Lintel", (0, (PH + WALL_Y) / 2), (WALL_X, (WALL_Y - PH) / 2)),
    ("Wall_Sill",   (0, -(PH + WALL_Y) / 2), (WALL_X, (WALL_Y - PH) / 2)),
    ("Wall_JambL",  (-(PW + WALL_X) / 2, 0), ((WALL_X - PW) / 2, PH)),
    ("Wall_JambR",  ((PW + WALL_X) / 2, 0), ((WALL_X - PW) / 2, PH)),
]
depth = WALL_FRONT - WALL_BACK
zc = (WALL_FRONT + WALL_BACK) / 2
for nm, (cx, cy), (hx, hy) in frame_boxes:
    b = S.box(nm, (hx * 2, hy * 2, depth), (cx, cy, zc), col)
    S.assign(b, m["graphite"]); S.bevel(b, 0.02, 2)
    wall_parts.append(b)

# Portal reveal liner — a machined sealing frame around the opening (front).
for side, (cx, cy, sx, sy) in {
    "T": (0, PH + 0.05, PW + 0.12, 0.10),
    "B": (0, -PH - 0.05, PW + 0.12, 0.10),
    "L": (-PW - 0.06, 0, 0.10, PH),
    "R": (PW + 0.06, 0, 0.10, PH),
}.items():
    liner = S.box(f"Portal_{side}", (sx * 2, sy * 2, 0.30), (cx, cy, WALL_FRONT - 0.14), col)
    S.assign(liner, m["titanium"]); S.bevel(liner, 0.008, 2)
    wall_parts.append(liner)

# Structural bolt rows framing the portal — DOUBLE rows, dense machined fasteners.
for i in range(17):
    fy = -PH + i * (2 * PH / 16)
    for sx in (-1, 1):
        for j, off in enumerate((0.16, 0.30)):
            wall_parts += K.hex_bolt(f"WboltV{i}{sx}{j}", (sx * (PW + off), fy, WALL_FRONT + 0.01),
                                     col, m, r=0.032, head_h=0.032, axis=(0, 0, 1))
for i in range(13):
    fx = -PW + i * (2 * PW / 12)
    for sy in (-1, 1):
        for j, off in enumerate((0.16, 0.30)):
            wall_parts += K.hex_bolt(f"WboltH{i}{sy}{j}", (fx, sy * (PH + off), WALL_FRONT + 0.01),
                                     col, m, r=0.032, head_h=0.032, axis=(0, 0, 1))
# conduit junction boxes on the outer wall (powered infrastructure density)
for (jx, jy) in [(-WALL_X + 1.0, PH + 1.4), (WALL_X - 1.0, -PH - 1.4),
                 (-WALL_X + 1.4, -PH - 0.6), (WALL_X - 1.4, PH + 0.6)]:
    jb = S.box(f"Wjb{jx:.0f}{jy:.0f}", (0.34, 0.5, 0.12), (jx, jy, WALL_FRONT + 0.02), col)
    S.assign(jb, m["graphite"]); S.bevel(jb, 0.006, 1)
    wall_parts.append(jb)
    wall_parts += K.bolt_ring(f"Wjbr{jx:.0f}{jy:.0f}", (jx, jy, WALL_FRONT + 0.08), (0, 0, 1),
                              0.19, 8, col, m, r=0.012, head_h=0.012)
    wall_parts += K.connector_port(f"Wjbc{jx:.0f}{jy:.0f}", (jx, jy - 0.16, WALL_FRONT + 0.06),
                                   col, m, r=0.05, depth=0.03, axis=(0, 0, 1), pins=7)

# Recessed panel seams + machined bands on the big wall faces (break the flats).
for i, fy in enumerate([PH + 0.5, PH + 1.1, -PH - 0.5, -PH - 1.1]):
    band = S.box(f"Wband{i}", (WALL_X * 1.9, 0.05, 0.04), (0, fy, WALL_FRONT), col)
    S.assign(band, m["graphite_worn"]); S.bevel(band, 0.006, 1)
    wall_parts.append(band)
for i, fx in enumerate([-PW - 1.0, -PW - 2.2, PW + 1.0, PW + 2.2]):
    band = S.box(f"WbandV{i}", (0.05, PH * 1.9, 0.04), (fx, 0, WALL_FRONT), col)
    S.assign(band, m["graphite_worn"]); S.bevel(band, 0.006, 1)
    wall_parts.append(band)

# Vertical conduit pipes running the jambs, with collars (the wall is powered).
for sx in (-1, 1):
    for j, off in enumerate([1.15, 1.55]):
        pts = [(sx * (PW + off), y, WALL_FRONT + 0.05) for y in
               [-PH - 0.8, -PH * 0.4, PH * 0.4, PH + 0.8]]
        pipe = K.sweep_tube(f"Wcond{sx}{j}", pts, 0.05, col, m["graphite_light"], segs=12)
        if pipe:
            wall_parts.append(pipe)
        for y in (-PH * 0.4, PH * 0.4):
            coll = S.tube(f"Wcoll{sx}{j}{y:.0f}", 0.075, 0.055, 0.06, 16,
                          (sx * (PW + off), y, WALL_FRONT + 0.05), col)
            S.assign(coll, m["titanium"])
            wall_parts.append(coll)

# Amber warning bands flush above / below the portal (sparse caution grammar).
wall_parts += hazard_stripe("Whaz_top", (0, PH + 0.52, WALL_FRONT + 0.03),
                            (1, 0, 0), (0, 1, 0), 2.8, 0.17, col, m, n=9)
wall_parts += hazard_stripe("Whaz_bot", (0, -(PH + 0.52), WALL_FRONT + 0.03),
                            (1, 0, 0), (0, 1, 0), 2.8, 0.17, col, m, n=9)

wall = S.join_all(wall_parts, "Wall")
S.weighted_normal(wall); S.shade_smooth(wall)


# ===========================================================================
# LEAVES — thick vault plugs. Front-face joinery converges on the seam; the
# inner seam face carries visible armor layers + lock dogs (seen when open).
# ===========================================================================
def make_leaf(name, sign):
    """sign=-1 left / +1 right. A thick armored plug: bright raised perimeter
    frame (so the mass reads against the dark wall), horizontal armor bands with
    rivet rows, corner bolts, and a layered inner-seam edge seen when it opens."""
    parts = []
    inner_x = sign * SEAM / 2
    outer_x = sign * (PW - 0.02)
    cx = (inner_x + outer_x) / 2
    lw = abs(outer_x - inner_x)
    fz = LT - 0.10                                   # slab front-face z
    # main plug slab (heavy chamfer)
    slab = S.box(f"{name}_Slab", (lw, PH * 2 - 0.05, LT), (cx, 0, LT / 2 - 0.10), col)
    S.assign(slab, m["graphite"]); S.bevel(slab, 0.03, 2)
    parts.append(slab)
    # bright raised PERIMETER FRAME — the plate's edge catches light and reads
    frame = [
        (f"{name}_frT", (lw, 0.11, 0.07), (cx, PH - 0.08, fz + 0.02)),
        (f"{name}_frB", (lw, 0.11, 0.07), (cx, -(PH - 0.08), fz + 0.02)),
        (f"{name}_frO", (0.11, PH * 2 - 0.1, 0.07), (outer_x - sign * 0.05, 0, fz + 0.02)),
        (f"{name}_frI", (0.11, PH * 2 - 0.1, 0.07), (inner_x + sign * 0.05, 0, fz + 0.02)),
    ]
    for nm, sz, loc in frame:
        r = S.box(nm, sz, loc, col); S.assign(r, m["titanium_polish"]); S.bevel(r, 0.006, 1)
        parts.append(r)
    # horizontal ARMOR BANDS with DOUBLE dense rivet rows (blast-plate density)
    band_ys = [PH * 0.62, PH * 0.21, -PH * 0.21, -PH * 0.62]
    for bi, by in enumerate(band_ys):
        band = S.box(f"{name}_band{bi}", (lw - 0.24, 0.18, 0.055), (cx, by, fz + 0.015), col)
        S.assign(band, m["graphite_light"]); S.bevel(band, 0.006, 1)
        parts.append(band)
        for row, ry in enumerate((by + 0.052, by - 0.052)):
            for ri in range(11):
                rx = cx - (lw - 0.36) / 2 + ri * (lw - 0.36) / 10
                parts += K.hex_bolt(f"{name}_rv{bi}{row}{ri}", (rx, ry, fz + 0.038),
                                    col, m, r=0.015, head_h=0.015, washer=False, axis=(0, 0, 1))
    # recessed detail panels between the bands + small greeble hardware
    for pi, py in enumerate([PH * 0.415, 0.0, -PH * 0.415]):
        pan = S.box(f"{name}_pan{pi}", (lw - 0.44, 0.30, 0.02), (cx, py, fz - 0.006), col)
        S.assign(pan, m["obsidian_matte"]); S.bevel(pan, 0.004, 1)
        parts.append(pan)
        for gx in (-1, 1):
            parts.append(K.greeble_plate(f"{name}_gp{pi}{gx}",
                         (cx + gx * lw * 0.26, py, fz + 0.008), (1, 0, 0), (0, 1, 0),
                         0.13, 0.09, col, m["titanium"]))
        parts.append(K.greeble_plate(f"{name}_gpc{pi}", (cx, py, fz + 0.008),
                     (1, 0, 0), (0, 1, 0), 0.20, 0.05, col, m["graphite_worn"]))
    # a louvered vent recessed in the lower panel (asymmetric: left leaf only)
    if sign < 0:
        parts += K.vent_louvers(f"{name}_vent", Vector((cx, -PH * 0.415, fz + 0.03)),
                                Vector((1, 0, 0)), Vector((0, 1, 0)), 0.5, 0.2, col, m, slats=8, tilt=0.5)
    # big corner bolts + a ring of medium bolts inside each corner (density)
    for bx in (-1, 1):
        for by in (-1, 1):
            cxy = (cx + bx * (lw / 2 - 0.16), by * (PH - 0.22), fz + 0.03)
            parts += K.hex_bolt(f"{name}_cb{bx}{by}", cxy, col, m, r=0.05, head_h=0.05, axis=(0, 0, 1))
            parts += K.bolt_ring(f"{name}_cbr{bx}{by}", cxy, (0, 0, 1), 0.11, 6, col, m, r=0.012, head_h=0.012)
    # data readout plate with a bolt-ringed bezel (top, outer side)
    dp = K._plate(f"{name}_data", Vector((cx + sign * lw * 0.22, PH * 0.62, fz + 0.06)),
                  Vector((1, 0, 0)), Vector((0, 1, 0)), 0.30, 0.10, 0.02, col, m["data_soft"])
    parts.append(dp)
    # --- inner seam edge: rebate step + layered armor + seal (visible on open) ---
    step = S.box(f"{name}_rebate", (0.12, PH * 2 - 0.1, LT * 0.55),
                 (inner_x + sign * 0.06, 0, LT / 2 - 0.10), col)
    S.assign(step, m["graphite_worn"]); S.bevel(step, 0.006, 1)
    parts.append(step)
    for li, lz in enumerate([-0.18, 0.0, 0.18]):
        armor = S.box(f"{name}_armor{li}", (0.06, PH * 2 - 0.2, 0.11),
                      (inner_x + sign * 0.03, 0, LT / 2 - 0.10 + lz), col)
        S.assign(armor, m["titanium"] if li == 1 else m["graphite_light"])
        S.bevel(armor, 0.004, 1)
        parts.append(armor)
    seal = S.box(f"{name}_seal", (0.025, PH * 2 - 0.3, LT * 0.4),
                 (inner_x, 0, LT / 2 - 0.10), col)
    S.assign(seal, m["rubber"])
    parts.append(seal)
    leaf = S.join_all(parts, name)
    S.weighted_normal(leaf); S.shade_smooth(leaf)
    return leaf, inner_x, outer_x

leaf_L, inL, outL = make_leaf("Leaf_L", -1)
leaf_R, inR, outR = make_leaf("Leaf_R", +1)


# ===========================================================================
# LOCK DOGS — radial locking bolts on each leaf's outer + top/bottom edges.
# Modelled RETRACTED (unlocked) so the door can open; they read as the mechanism.
# ===========================================================================
def lock_dogs(name, sign):
    dogs = []
    ox = sign * (PW - 0.02)
    for fy in (-PH * 0.7, 0, PH * 0.7):                   # side dogs
        dog = K.oriented_cyl(f"{name}_s{fy:.0f}", 0.07, (ox, fy, LT / 2 - 0.10),
                             (ox + sign * 0.22, fy, LT / 2 - 0.10), col, verts=14,
                             mat=m["titanium_polish"])
        S.bevel(dog, 0.005, 1)
        dogs.append(dog)
    for fx in (sign * PW * 0.35, sign * PW * 0.7):        # top/bottom dogs
        for fy in (PH * 2 - 0.06, -(PH * 2 - 0.06)):
            yy = math.copysign(PH * 1.0, fy)
            dog = K.oriented_cyl(f"{name}_t{fx:.1f}{fy:.0f}", 0.055,
                                 (fx, yy, LT / 2 - 0.10),
                                 (fx, yy + math.copysign(0.2, fy), LT / 2 - 0.10),
                                 col, verts=12, mat=m["titanium_polish"])
            dogs.append(dog)
    obj = S.join_all(dogs, name)
    S.shade_smooth(obj)
    return obj

dogs_L = lock_dogs("LockDogs_L", -1)
dogs_R = lock_dogs("LockDogs_R", +1)
# Fuse the dogs into their leaf so they travel with it when it parts.
leaf_L = S.join_all([leaf_L, dogs_L], "Leaf_L"); S.shade_smooth(leaf_L)
leaf_R = S.join_all([leaf_R, dogs_R], "Leaf_R"); S.shade_smooth(leaf_R)


# ===========================================================================
# CORE — the cyan authentication lens at the seam centre. Stays put as the
# leaves part around it (the eye that remains). Single emissive disc for pulse.
# ===========================================================================
cbz = LT - 0.10 + 0.02                              # core front-plane z
mount_parts = []
# machined boss mount (spans the seam; stays centred as the leaves part)
boss = S.cyl("Core_BossBase", CORE_R + 0.14, 0.20, 80, (0, 0, cbz - 0.06), col)
S.assign(boss, m["graphite"]); S.bevel(boss, 0.012, 2)
mount_parts.append(boss)
# heavy machined bezel
bezel = S.tube("Core_Bezel", CORE_R + 0.02, CORE_R - 0.16, 0.18, 96, (0, 0, cbz + 0.05), col)
S.assign(bezel, m["titanium_polish"]); S.bevel(bezel, 0.01, 2)
mount_parts.append(bezel)
# concentric altar rings (digital-religion grammar, restrained)
for i, rr in enumerate([CORE_R - 0.16, CORE_R - 0.28, CORE_R - 0.38]):
    ring = S.tube(f"Core_Ring{i}", rr, rr - 0.03, 0.09 - i * 0.015, 72, (0, 0, cbz + 0.06), col)
    S.assign(ring, m["ceramic"] if i == 1 else m["graphite"])
    mount_parts.append(ring)
# surgical bolt ring around the bezel
for i in range(24):
    a = (i / 24) * math.tau
    bp = (math.cos(a) * (CORE_R + 0.07), math.sin(a) * (CORE_R + 0.07), cbz + 0.02)
    mount_parts += K.hex_bolt(f"Core_bolt{i}", bp, col, m, r=0.02, head_h=0.02,
                              washer=False, axis=(0, 0, 1))
# a dark groove seating the lens
groove = S.tube("Core_Groove", CORE_R - 0.38, CORE_R - 0.46, 0.10, 64, (0, 0, cbz + 0.05), col)
S.assign(groove, m["obsidian_matte"])
mount_parts.append(groove)
core_mount = S.join_all(mount_parts, "Core_Mount")
S.weighted_normal(core_mount); S.shade_smooth(core_mount)
# the press target — its own node "Core", single emissive material (scene pulses it)
core = S.cyl("Core", CORE_R - 0.46, 0.08, 64, (0, 0, cbz + 0.06), col)
S.assign(core, m["data"]); S.bevel(core, 0.006, 1); S.shade_smooth(core)


# ===========================================================================
# HYDRAULICS — the rams that drive the leaves, mounted in the portal reveal.
# Revealed in the gap as the leaves part. Big scaled-up kit actuators.
# ===========================================================================
hyd_parts = []
for sy in (-1, 1):
    for sx in (-1, 1):
        y = sy * PH * 0.62
        p0 = (sx * (PW + 0.28), y, -0.42)              # anchored deep in the jamb
        p1 = (sx * 0.55, y, -0.42)                      # rod toward the leaf edge
        hyd_parts += K.actuator(f"Ram{sx}{sy}", p0, p1, col, m, r=0.14)
hydraulics = S.join_all(hyd_parts, "Hydraulics")
S.shade_smooth(hydraulics)


# ===========================================================================
# TUNNEL — the lit shaft behind the door the camera is pulled into. Receding
# ribbed frames narrowing into fog, with a distant light at the vanishing point.
# ===========================================================================
tun_parts = []
NR = 11
for i in range(NR):
    t = i / (NR - 1)
    z = -0.5 - t * 8.5
    scale = 1.0 - 0.55 * t
    rw, rh = PW * scale, PH * scale
    # a machined rib frame (the shaft wall segments)
    frame = S.box(f"Tun_ring{i}", (rw * 2 + 0.28, rh * 2 + 0.28, 0.22), (0, 0, z), col)
    S.assign(frame, m["graphite"] if i % 2 else m["graphite_worn"]); S.bevel(frame, 0.012, 1)
    inner = S.box(f"Tun_bore{i}", (rw * 2, rh * 2, 0.20), (0, 0, z - 0.02), col)
    S.assign(inner, m["obsidian_matte"])
    tun_parts += [frame, inner]
    # cyan guide strips on every rib (top/bottom/sides) — the powered shaft glows
    for (sw, sh, sx, sy) in [(rw * 1.7, 0.05, 0, rh), (rw * 1.7, 0.05, 0, -rh),
                             (0.05, rh * 1.7, rw, 0), (0.05, rh * 1.7, -rw, 0)]:
        strip = S.box(f"Tun_g{i}_{sx:.1f}_{sy:.1f}", (sw, sh, 0.03), (sx, sy, z + 0.12), col)
        S.assign(strip, m["data_soft"] if i % 2 else m["data"])
        tun_parts.append(strip)
# glowing shaft MOUTH — THIN cyan outline rings receding just behind the door so
# the parted leaves reveal DEPTH (a lit shaft) around the eye without a bright
# wall that competes with the core.
mouth = S.tube("Tun_mouth", CORE_R + 0.92, CORE_R + 0.84, 0.05, 80, (0, 0, -0.40), col)
S.assign(mouth, m["data_soft"])
tun_parts.append(mouth)
mouth2 = S.tube("Tun_mouth2", CORE_R + 0.66, CORE_R + 0.60, 0.05, 80, (0, 0, -1.15), col)
S.assign(mouth2, m["data_soft"])
tun_parts.append(mouth2)
# bright aperture at the vanishing point — the light the camera is pulled toward
endframe = S.box("Tun_endframe", (PW * 0.9, PH * 0.9, 0.10), (0, 0, -9.1), col)
S.assign(endframe, m["titanium"])
endlight = S.box("Tun_end", (PW * 0.62, PH * 0.62, 0.05), (0, 0, -9.05), col)
S.assign(endlight, m["authority"])
halo = S.tube("Tun_halo", PW * 0.66, PW * 0.6, 0.04, 48, (0, 0, -9.0), col)
S.assign(halo, m["data"])
tun_parts += [endframe, endlight, halo]
tunnel = S.join_all(tun_parts, "Tunnel")
S.shade_smooth(tunnel)


# ===========================================================================
# FLOOR — a grated deck giving human scale, running forward toward the subject
# with a hazard threshold at the door base.
# ===========================================================================
floor_parts = []
deck = S.box("Floor_Deck", (WALL_X * 2, 0.12, 9.0), (0, -PH - 0.02, 3.6), col)
S.assign(deck, m["graphite"]); S.bevel(deck, 0.01, 1)
floor_parts.append(deck)
# grating ribs across the deck
for i in range(16):
    zc2 = 0.4 + i * 0.55
    rib = S.box(f"Floor_rib{i}", (WALL_X * 1.9, 0.03, 0.05), (0, -PH + 0.05, zc2), col)
    S.assign(rib, m["graphite_light"])
    floor_parts.append(rib)
# side stringers
for sx in (-1, 1):
    st = S.box(f"Floor_str{sx}", (0.14, 0.16, 9.0), (sx * (WALL_X - 0.2), -PH - 0.02, 3.6), col)
    S.assign(st, m["graphite_worn"]); S.bevel(st, 0.008, 1)
    floor_parts.append(st)
# hazard threshold lying flat on the deck at the door base (normal +Y up)
floor_parts += hazard_stripe("Floor_haz", (0, -PH + 0.05, 0.95),
                             (1, 0, 0), (0, 0, -1), 3.4, 0.55, col, m, n=11)
floor = S.join_all(floor_parts, "Floor")
S.weighted_normal(floor); S.shade_smooth(floor)


# ---------------------------------------------------------------------------
print("[auth_door] parts:", [o.name for o in col.objects])
def tri_count():
    tot = 0
    for o in col.objects:
        o.data.calc_loop_triangles()
        tot += len(o.data.loop_triangles)
    return tot
print("[auth_door] triangles:", tri_count())

size = S.export_glb(OUT, draco=True)
S.report(OUT, size)

if RENDER:
    # Wide establishing read (the whole monumental door + floor + wall), low and
    # near head-on, matching the intended first-frame composition.
    S.lookdev_render(REF, cam_loc=(2.6, -1.4, 12.5), target=(0, -0.2, 0),
                     lens=42, samples=90, res=(1000, 720),
                     key_energy=900, rim_color=(0.30, 0.46, 0.5), bg=0.010)
