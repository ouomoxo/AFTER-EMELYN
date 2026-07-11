"""
SOVEREIGN//77 — Machined-detail kit (bpy 4.5 LTS).

A component library of REAL hardware — fasteners, connector ports, cooling
vents, hydraulic actuators, cable harnesses, braided artificial muscle — built
as precise bmesh geometry so a hero asset survives close 65–85mm inspection.
The house language (docs/04): machined, medical, reverent; silhouette and
joinery over surface noise; every edge chamfered so the cold key catches it.

These compose ON TOP of sovereign_bpy.py (S). Nothing here is used by the
door/infrastructure builders — it exists for the HUMAN REVISION hero rebuild.
"""
import math
import bmesh
from mathutils import Vector, Matrix  # type: ignore
import sovereign_bpy as S


# ----------------------------------------------------------------------------
# Orientation helpers — build a primitive at origin along +Z, then aim it.
# The whole "mechanical" read comes from parts that point AT each other
# (actuators, pins, struts), which axis-aligned primitives can never do.
# ----------------------------------------------------------------------------
def _aim(obj, direction, loc):
    obj.rotation_euler = direction.normalized().to_track_quat("Z", "Y").to_euler()
    obj.location = loc


def perp(axis):
    """A stable unit vector perpendicular to `axis`."""
    a = axis.normalized()
    ref = Vector((0, 0, 1)) if abs(a.z) < 0.9 else Vector((1, 0, 0))
    return a.cross(ref).normalized()


def oriented_cyl(name, r, p0, p1, col, verts=16, mat=None, caps=True, r2=None):
    """A cylinder (or cone if r2≠r) spanning world points p0→p1."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = max(d.length, 1e-5)
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=caps, cap_tris=False, segments=verts,
                          radius1=r, radius2=(r if r2 is None else r2), depth=length)
    obj = S.bm_to_obj(bm, name, col)
    _aim(obj, d, p0 + d * 0.5)
    if mat:
        S.assign(obj, mat)
    return obj


def oriented_box(name, size, p0, p1, col, mat=None):
    """A box whose local Z spans p0→p1; size=(x,y) is the cross-section."""
    p0, p1 = Vector(p0), Vector(p1)
    d = p1 - p0
    length = max(d.length, 1e-5)
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((size[0], size[1], length)), verts=bm.verts)
    obj = S.bm_to_obj(bm, name, col)
    _aim(obj, d, p0 + d * 0.5)
    if mat:
        S.assign(obj, mat)
    return obj


# ----------------------------------------------------------------------------
# Fasteners — the single highest-value greeble. A modeled hex bolt with a
# chamfered head and a seated washer reads instantly as "engineered".
# ----------------------------------------------------------------------------
def hex_bolt(name, loc, col, mats, r=0.012, head_h=0.010, axis=(0, 0, 1),
             washer=True, shaft=0.0):
    """A hex-head bolt sitting on `loc`, head pointing along +axis."""
    axis = Vector(axis).normalized()
    parts = []
    base = Vector(loc)
    if washer:
        w = S.tube(f"{name}_w", r * 1.55, r * 1.05, 0.004, 18, (0, 0, 0), col)
        _aim(w, axis, base - axis * 0.002)
        S.assign(w, mats["titanium"])
        parts.append(w)
    head = oriented_cyl(f"{name}_h", r * 1.35, base, base + axis * head_h, col,
                        verts=6, mat=mats["titanium_polish"])
    S.bevel(head, 0.0016, 1)
    parts.append(head)
    # dark hex socket recess in the crown — catches shadow, sells the fastener.
    sock = oriented_cyl(f"{name}_s", r * 0.7, base + axis * (head_h - 0.003),
                        base + axis * head_h, col, verts=6, mat=mats["obsidian_matte"])
    parts.append(sock)
    if shaft > 0:
        sh = oriented_cyl(f"{name}_t", r * 0.85, base, base - axis * shaft, col,
                          verts=12, mat=mats["graphite"])
        parts.append(sh)
    return parts


def socket_cap(name, loc, col, mats, r=0.010, h=0.008, axis=(0, 0, 1)):
    """A cylindrical socket-cap screw with a recessed hex drive."""
    axis = Vector(axis).normalized()
    base = Vector(loc)
    head = oriented_cyl(f"{name}_h", r, base, base + axis * h, col, verts=20,
                        mat=mats["titanium_polish"])
    S.bevel(head, 0.0014, 1)
    drive = oriented_cyl(f"{name}_d", r * 0.55, base + axis * (h - 0.0025),
                         base + axis * h, col, verts=6, mat=mats["obsidian_matte"])
    return [head, drive]


# ----------------------------------------------------------------------------
# Connector port — a keyed medical/military circular connector: outer shell,
# a keyway notch, and a field of pins on a dark insert. Clusters of these read
# as "this plugs into a body".
# ----------------------------------------------------------------------------
def connector_port(name, loc, col, mats, r=0.026, depth=0.02, axis=(0, 0, 1),
                   pins=7, live=False):
    axis = Vector(axis).normalized()
    base = Vector(loc)
    parts = []
    shell = oriented_cyl(f"{name}_shell", r, base - axis * depth * 0.5,
                         base + axis * depth * 0.5, col, verts=24,
                         mat=mats["graphite_light"])
    S.bevel(shell, 0.002, 2)
    parts.append(shell)
    collar = S.tube(f"{name}_collar", r * 1.12, r * 0.98, depth * 0.5, 24, (0, 0, 0), col)
    _aim(collar, axis, base + axis * depth * 0.25)
    S.assign(collar, mats["titanium"])
    parts.append(collar)
    # dark insert the pins sit in
    insert = oriented_cyl(f"{name}_ins", r * 0.82, base + axis * depth * 0.35,
                          base + axis * depth * 0.5, col, verts=24,
                          mat=mats["obsidian_matte"])
    parts.append(insert)
    u = perp(axis)
    v = axis.cross(u).normalized()
    pin_mat = mats["data"] if live else mats["brass"]
    for k in range(pins):
        if k == 0:
            pc = base  # centre pin
        else:
            a = (k / (pins - 1)) * math.tau
            pr = r * 0.5
            pc = base + (u * math.cos(a) + v * math.sin(a)) * pr
        pin = oriented_cyl(f"{name}_p{k}", r * 0.09, pc + axis * depth * 0.32,
                           pc + axis * depth * 0.62, col, verts=8, mat=pin_mat)
        parts.append(pin)
    # keyway tab on the collar
    key = oriented_box(f"{name}_key", (r * 0.16, r * 0.16),
                       base + u * r * 1.02 + axis * depth * 0.1,
                       base + u * r * 1.02 + axis * depth * 0.4, col,
                       mat=mats["titanium"])
    parts.append(key)
    return parts


# ----------------------------------------------------------------------------
# Cooling vent — a recessed frame with angled louver slats. Breaks a flat
# ceramic/metal panel with real depth and directional shadow.
# ----------------------------------------------------------------------------
def vent_louvers(name, center, u, v, w, h, col, mats, slats=6, tilt=0.5):
    """A louvered vent. center=world point; u,v=in-plane unit axes; w,h=size."""
    center = Vector(center)
    u = Vector(u).normalized()
    v = Vector(v).normalized()
    n = u.cross(v).normalized()
    parts = []
    # recessed back plate (dark, so the louver gaps read as depth)
    back = _plate(f"{name}_bk", center - n * 0.012, u, v, w, h, 0.004, col, mats["obsidian_matte"])
    parts.append(back)
    for i in range(slats):
        fy = (i + 0.5) / slats - 0.5
        c = center + v * (fy * h)
        slat = _plate(f"{name}_s{i}", c + n * 0.004, u, (v * math.cos(tilt) + n * math.sin(tilt)),
                      w * 0.94, h / slats * 0.82, 0.003, col, mats["graphite_light"])
        parts.append(slat)
    # frame rails
    for sx in (-1, 1):
        rail = _plate(f"{name}_fu{sx}", center + u * (sx * w * 0.5) + n * 0.006,
                      n, v, 0.02, h * 1.02, 0.006, col, mats["titanium"])
        parts.append(rail)
    return parts


def _plate(name, center, u, v, w, h, thick, col, mat):
    """A thin rectangular slab centred at `center`, spanning ±w/2 u, ±h/2 v,
    with `thick` along u×v. Bevelled so its edges catch light."""
    center = Vector(center)
    u = Vector(u).normalized()
    v = Vector(v).normalized()
    n = u.cross(v).normalized()
    bm = bmesh.new()
    for sx in (-0.5, 0.5):
        for sy in (-0.5, 0.5):
            for sz in (-0.5, 0.5):
                bm.verts.new(center + u * (sx * w) + v * (sy * h) + n * (sz * thick))
    bm.verts.ensure_lookup_table()
    verts = bm.verts
    # 8 corners in order (sx,sy,sz): 000,001,010,011,100,101,110,111
    idx = {(a, b, c): verts[i] for i, (a, b, c) in enumerate(
        [(x, y, z) for x in (0, 1) for y in (0, 1) for z in (0, 1)])}
    def q(a, b, c, d):
        bm.faces.new((idx[a], idx[b], idx[c], idx[d]))
    q((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0))
    q((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1))
    q((0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1))
    q((0, 1, 0), (0, 1, 1), (1, 1, 1), (1, 1, 0))
    q((0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0))
    q((1, 0, 0), (1, 1, 0), (1, 1, 1), (1, 0, 1))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    S.assign(obj, mat)
    S.bevel(obj, min(thick * 0.4, 0.0015), 1)
    return obj


# ----------------------------------------------------------------------------
# Hydraulic actuator — the part that makes a spine read as an articulated
# MACHINE. Body cylinder + polished protruding rod + clevis ends with a
# cross-pin at each anchor.
# ----------------------------------------------------------------------------
def actuator(name, p0, p1, col, mats, r=0.018):
    p0, p1 = Vector(p0), Vector(p1)
    axis = (p1 - p0)
    L = axis.length
    a = axis.normalized()
    parts = []
    # barrel (fixed cylinder) over the first ~55%
    barrel = oriented_cyl(f"{name}_barrel", r, p0 + a * 0.10 * L, p0 + a * 0.58 * L,
                          col, verts=20, mat=mats["graphite"])
    S.bevel(barrel, 0.002, 2)
    parts.append(barrel)
    # gland nut where the rod exits
    gland = oriented_cyl(f"{name}_gland", r * 1.12, p0 + a * 0.55 * L, p0 + a * 0.60 * L,
                         col, verts=6, mat=mats["titanium"])
    parts.append(gland)
    # polished rod over the last ~35%
    rod = oriented_cyl(f"{name}_rod", r * 0.5, p0 + a * 0.56 * L, p0 + a * 0.90 * L,
                       col, verts=16, mat=mats["titanium_polish"])
    parts.append(rod)
    # feed line boss on the barrel
    u = perp(a)
    boss = oriented_cyl(f"{name}_boss", r * 0.28, p0 + a * 0.2 * L,
                        p0 + a * 0.2 * L + u * r * 1.4, col, verts=10, mat=mats["brass"])
    parts.append(boss)
    # clevis + cross-pin at each end
    for tag, anchor, into in ((f"{name}_c0", p0, a), (f"{name}_c1", p1, -a)):
        clev = oriented_cyl(tag, r * 0.7, anchor, anchor + into * 0.10 * L, col,
                            verts=12, mat=mats["graphite_light"])
        parts.append(clev)
        pin = oriented_cyl(f"{tag}_pin", r * 0.28, anchor - u * r * 1.1,
                           anchor + u * r * 1.1, col, verts=10, mat=mats["titanium_polish"])
        parts.append(pin)
    return parts


# ----------------------------------------------------------------------------
# Swept tube — a circular profile carried along an arbitrary poly-path with a
# (optionally varying) radius. The organic spine of cables and muscle.
# ----------------------------------------------------------------------------
def sweep_tube(name, pts, radius, col, mat, segs=10, close_caps=True):
    """radius: float or callable(i, t)->float. Uses parallel-transport framing
    so the tube doesn't twist along curves."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    if n < 2:
        return None
    rad = radius if callable(radius) else (lambda i, t: radius)
    # tangents
    tans = []
    for i in range(n):
        if i == 0:
            t = pts[1] - pts[0]
        elif i == n - 1:
            t = pts[-1] - pts[-2]
        else:
            t = pts[i + 1] - pts[i - 1]
        tans.append(t.normalized())
    # parallel transport of a reference frame
    ref = perp(tans[0])
    frames = [ref]
    for i in range(1, n):
        v = tans[i - 1].cross(tans[i])
        if v.length < 1e-6:
            frames.append(frames[-1])
        else:
            v.normalize()
            ang = math.atan2(tans[i - 1].cross(tans[i]).length, tans[i - 1].dot(tans[i]))
            frames.append((Matrix.Rotation(ang, 4, v) @ frames[-1].to_4d()).to_3d().normalized())
    bm = bmesh.new()
    rings = []
    for i in range(n):
        u = frames[i]
        w = tans[i].cross(u).normalized()
        t = i / (n - 1)
        r = rad(i, t)
        ring = []
        for k in range(segs):
            ang = (k / segs) * math.tau
            off = u * (math.cos(ang) * r) + w * (math.sin(ang) * r)
            ring.append(bm.verts.new(pts[i] + off))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(segs):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % segs],
                          rings[i + 1][(k + 1) % segs], rings[i + 1][k]))
    if close_caps:
        bmesh.ops.contextual_create(bm, geom=rings[0])
        bmesh.ops.contextual_create(bm, geom=rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    obj = S.bm_to_obj(bm, name, col)
    S.assign(obj, mat)
    S.shade_smooth(obj)
    return obj


def braided_strand(name, path_fn, col, mats, n_ply=3, ply_r=0.006, bundle_r=0.02,
                   twist=6.0, samples=34, crimp=True):
    """Artificial muscle: n_ply helical sub-filaments braided around a path.
    path_fn(t)->Vector for t in [0,1]. Adds metal crimp fittings at both ends."""
    parts = []
    base_pts = [path_fn(i / (samples - 1)) for i in range(samples)]
    for ply in range(n_ply):
        phase = (ply / n_ply) * math.tau
        pts = []
        for i in range(samples):
            t = i / (samples - 1)
            c = base_pts[i]
            # local frame from tangent
            if i == 0:
                tan = base_pts[1] - base_pts[0]
            elif i == samples - 1:
                tan = base_pts[-1] - base_pts[-2]
            else:
                tan = base_pts[i + 1] - base_pts[i - 1]
            tan = tan.normalized()
            u = perp(tan)
            w = tan.cross(u).normalized()
            # bundle narrows at the ends (crimped), fat in the belly
            envelope = math.sin(t * math.pi) ** 0.5
            br = bundle_r * (0.25 + 0.75 * envelope)
            ang = phase + t * twist * math.tau
            pts.append(c + (u * math.cos(ang) + w * math.sin(ang)) * br)
        strand = sweep_tube(f"{name}_ply{ply}", pts, ply_r, col, mats["rubber"], segs=7)
        if strand:
            parts.append(strand)
    if crimp:
        for tag, t in ((f"{name}_k0", 0.02), (f"{name}_k1", 0.98)):
            c = path_fn(t)
            nb = path_fn(t + 0.03) if t < 0.5 else path_fn(t - 0.03)
            axis = (nb - c) if t < 0.5 else (c - nb)
            fitting = oriented_cyl(tag, bundle_r * 0.9, c - axis.normalized() * 0.012,
                                   c + axis.normalized() * 0.012, col, verts=12,
                                   mat=mats["titanium"])
            S.bevel(fitting, 0.002, 1)
            parts.append(fitting)
    return parts
