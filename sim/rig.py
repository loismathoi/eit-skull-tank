import matplotlib.pyplot as plt
import numpy as np

import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
import pyeit.eit.protocol as protocol
import pyeit.eit.greit as greit
from pyeit.mesh.wrapper import PyEITAnomaly_Circle

# S/m, one saline inside and outside the ring
SIGMA_SALINE = 0.33
SIGMA_SKULL = 0.0042


# normalized to tank inner radius
R_SKULL_OUT = 0.96
R_SKULL_IN = 0.88

N_EL = 16
H0 = 0.02

mesh_obj = mesh.multi_circle(
    r=1.0,
    background=SIGMA_SALINE,
    n_el=N_EL,
    h0=H0,
    r_layer=[[R_SKULL_IN, R_SKULL_OUT]],
    perm_per_layer=[SIGMA_SKULL],
    ppl=int(np.ceil(2 * np.pi * R_SKULL_OUT / H0)),
)

anomaly = [
    PyEITAnomaly_Circle(center=[0.25, -0.5], r=0.05, perm=0.66),
]

mesh_new = mesh.set_perm(mesh_obj, anomaly=anomaly)

protocol_obj = protocol.create(N_EL, dist_exc=1, step_meas=1, parser_meas="std")

fwd = EITForward(mesh_obj, protocol_obj)
v0 = fwd.solve_eit()
v1 = fwd.solve_eit(perm=mesh_new.perm)

eit = greit.GREIT(mesh_obj, protocol_obj)
eit.setup(p=0.50, lamb=0.001, perm=mesh_obj.perm, jac_normalized=True)
# reconstruct dsigma/sigma0: with absolute dsigma the resistive skull columns dominate J
# ponytail: private pyEIT methods, pinned to pyeit 1.2.4
eit.H = eit._compute_h(eit.J * mesh_obj.perm, eit._compute_grid_weights(eit.xg, eit.yg))
ds = eit.solve(v1, v0, normalize=True)
x, y, ds = eit.mask_value(ds, mask_value=np.nan)

if __name__ == "__main__":
    from pathlib import Path
    from matplotlib.colors import CenteredNorm, ListedColormap
    from matplotlib.patches import Circle

    pts, tri = mesh_obj.node, mesh_obj.element
    el = pts[mesh_obj.el_pos, :2]
    a = anomaly[0]

    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(10, 4.5), layout="constrained")

    # one fixed colour per region: bone, saline, blood
    perm = np.real(mesh_new.perm)
    region = np.select([perm == SIGMA_SKULL, perm == a.perm], [0, 2], 1)
    ax0.tripcolor(pts[:, 0], pts[:, 1], tri, region, vmin=0, vmax=2, edgecolors="face", linewidth=0.2,
                  cmap=ListedColormap(["#e6dcc3", "#b9d4e6", "#9e1b32"]))
    arrow = dict(arrowstyle="-", color="k", lw=0.8)
    ax0.text(0, 0.15, f"saline\n{SIGMA_SALINE:g} S/m", ha="center", va="center")
    ax0.annotate(f"skull ring\n{SIGMA_SKULL:g} S/m", xy=(-0.65, 0.65), xytext=(-0.35, 0.4),
                 ha="center", va="center", arrowprops=arrow)
    ax0.annotate(f"clot\n{a.perm:g} S/m", xy=a.center, xytext=(a.center[0] - 0.4, a.center[1] + 0.05),
                 ha="center", va="center", arrowprops=arrow)
    ax0.set_title("Phantom", pad=14)

    e = int(np.floor(np.log10(np.nanmax(np.abs(ds)))))
    im = ax1.pcolormesh(x, y, np.real(ds) / 10**e, shading="nearest", cmap="PuOr_r", norm=CenteredNorm())
    im.set_clip_path(Circle((0, 0), 1, transform=ax1.transData))
    ax1.add_patch(Circle((0, 0), 1, fc="0.85", ec="none", zorder=0))  # grey: rim pixels GREIT masks
    # colorbar as an inset so both panels keep the same size
    cb = fig.colorbar(im, cax=ax1.inset_axes([1.04, 0.1, 0.04, 0.8]),
                      label=rf"$\Delta\sigma / \sigma_0$  ($\times 10^{{{e}}}$)")
    cb.ax.set_ylim(np.nanmin(ds) / 10**e, np.nanmax(ds) / 10**e)  # bar spans only values present
    for r in (R_SKULL_IN, R_SKULL_OUT, 1):
        ax1.add_patch(Circle((0, 0), r, fill=False, ec="0.4", lw=0.6))
    ax1.set_title("GREIT reconstruction", pad=14)

    for ax in (ax0, ax1):
        ax.add_patch(Circle(a.center, a.r, fill=False, ec="k", ls="--", lw=1))
        ax.plot(el[:, 0], el[:, 1], "o", ms=4, mfc="k", mec="w")
        ax.set_aspect("equal")
        ax.set_axis_off()

    fig.savefig(Path(__file__).resolve().parent.parent / "img" / "sim-greit-ring.png", dpi=200,
                bbox_inches="tight", pad_inches=0.3)
    plt.show()
