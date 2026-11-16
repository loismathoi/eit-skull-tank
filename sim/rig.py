from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from matplotlib.patches import Circle, Patch

import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
import pyeit.eit.protocol as protocol
import pyeit.eit.greit as greit
from pyeit.mesh.wrapper import PyEITAnomaly_Circle, PyEITMesh

# conductivity, S/m
SIGMA_SALINE = 0.33
SIGMA_SKULL = 0.042
SIGMA_SCALP = 0.31
# radius, normalized: 1 = tank inner wall = electrode ring
R_SKULL_OUT = 0.96
R_SKULL_IN = 0.88

N_EL = 16
# distmesh initial edge length; forward (simulate) and reconstruction meshes differ
H0 = 0.01
H0_REC = 0.04


def head_mesh(h0):
    # saline disc, skull ring R_SKULL_IN..R_SKULL_OUT, scalp outside ring
    m = mesh.multi_circle(
        r=1.0,
        background=SIGMA_SALINE,
        n_el=N_EL,
        h0=h0,
        r_layer=[[R_SKULL_IN, R_SKULL_OUT]],
        perm_per_layer=[SIGMA_SKULL],
        ppl=int(np.ceil(2 * np.pi * R_SKULL_OUT / h0)),  # points per layer boundary, spacing ~h0
    )
    # distmesh can leave a node in no triangle -> singular FEM matrix; drop unused nodes, renumber
    used = np.unique(m.element)
    assert np.isin(m.el_pos, used).all(), "electrode node in no triangle"
    new_id = np.zeros(len(m.node), dtype=int)
    new_id[used] = np.arange(len(used))
    m = PyEITMesh(node=m.node[used], element=new_id[m.element], perm=m.perm, el_pos=new_id[m.el_pos])
    # scalp: elements with centroid outside ring
    r_c = np.linalg.norm(m.node[m.element, :2].mean(axis=1), axis=1)
    m.perm[r_c > R_SKULL_OUT] = SIGMA_SCALP
    return m


mesh_obj = head_mesh(H0)
mesh_rec = head_mesh(H0_REC)

# inclusion, conductivity 2x saline
clot = PyEITAnomaly_Circle(center=[0.25, -0.5], r=0.1, perm=0.66)
mesh_new = mesh.set_perm(mesh_obj, anomaly=[clot])

# adjacent drive, adjacent measure, no rotation, drive electrodes skipped: 16 x 13 = 208 values
protocol_obj = protocol.create(N_EL, dist_exc=1, step_meas=1, parser_meas="std")

# boundary voltages: v0 reference (no clot), v1 with clot
fwd = EITForward(mesh_obj, protocol_obj)
v0 = fwd.solve_eit()
v1 = fwd.solve_eit(perm=mesh_new.perm)

eit = greit.GREIT(mesh_rec, protocol_obj)
# p: noise covariance exponent, lamb: regularization; Jacobian on prior perm, normalized by v0
eit.setup(p=0.50, lamb=0.01, perm=mesh_rec.perm, jac_normalized=True)
ds = eit.solve(v1, v0, normalize=True)  # dv = (v1 - v0) / |v0|
x, y, ds = eit.mask_value(ds, mask_value=np.nan)  # 32 x 32 grid, pixels outside mesh -> NaN

if __name__ == "__main__":
    pts, tri = mesh_obj.node, mesh_obj.element
    el = pts[mesh_obj.el_pos]  # electrode coordinates

    # one fixed colour per region, matched by exact conductivity; no match -> index 0 (saline)
    regions = {
        "saline": (SIGMA_SALINE, "#b9d4e6"),
        "skull": (SIGMA_SKULL, "#e6dcc3"),
        "scalp": (SIGMA_SCALP, "#f2c4a0"),
        "clot": (clot.perm, "#9e1b32"),
    }
    sigma, colour = zip(*regions.values())
    region = np.argmax(mesh_new.perm[:, None] == np.array(sigma), axis=1)

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(11, 4.5), layout="constrained")

    # edges in face colour: no mesh lines, no gaps
    ax0.tripcolor(pts[:, 0], pts[:, 1], tri, region, vmin=0, vmax=len(sigma) - 1,
                  cmap=ListedColormap(colour), edgecolors="face", linewidth=0.2)
    fig.legend(handles=[Patch(color=c, label=f"{n} {s:g} S/m") for n, (s, c) in regions.items()],
               loc="outside left center", frameon=False)
    ax0.set_title("Phantom")

    cmap = LinearSegmentedColormap.from_list("eit", [
        (0, "#6a00a8"), (0.25, "#1f4fff"), (0.5, "#33dd00"),  # 0.5 is 0
        (2 / 3, "#ffee00"), (5 / 6, "#ff8800"), (1, "#dd0000")])
    vmax = np.nanmax(np.abs(ds))
    im = ax1.pcolormesh(x, y, ds, shading="nearest", cmap=cmap, vmin=-vmax, vmax=vmax)
    im.set_clip_path(Circle((0, 0), 1, transform=ax1.transData))  # clip to tank wall
    cb = fig.colorbar(im, ax=ax1, shrink=0.8, label=r"$\Delta\sigma$ (normalized)")
    cb.ax.set_ylim(np.nanmin(ds), np.nanmax(ds))  # bar spans only values present
    # skull ring and tank wall outlines
    for r in (R_SKULL_IN, R_SKULL_OUT, 1):
        ax1.add_patch(Circle((0, 0), r, fill=False, ec="0.4", lw=0.6))
    ax1.set_title("GREIT reconstruction")

    # true clot outline, electrodes
    for ax in (ax0, ax1):
        ax.add_patch(Circle(clot.center, clot.r, fill=False, ec="k", ls="--", lw=1))
        ax.plot(el[:, 0], el[:, 1], "o", ms=4, mfc="k", mec="w")
        ax.set_aspect("equal")
        ax.set_axis_off()

    fig.savefig(Path(__file__).resolve().parents[1] / "img" / "sim-greit-ring.png", dpi=200)
    plt.show()
