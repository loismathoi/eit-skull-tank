import matplotlib.pyplot as plt
import numpy as np

import pyeit.mesh as mesh
from pyeit.eit.fem import EITForward
import pyeit.eit.protocol as protocol
import pyeit.eit.greit as greit
from pyeit.mesh.wrapper import PyEITAnomaly_Circle

# S/m, one saline inside and outside the ring
SIGMA_SCALP = 0.33
SIGMA_BRAIN = 0.33
SIGMA_SKULL = SIGMA_BRAIN / 60


# normalized to tank inner radius
R_SKULL_OUT = 0.75
R_SKULL_IN = 0.7

N_EL = 16
H0 = 0.02

mesh_obj = mesh.multi_circle(
    r=1.0,
    background=SIGMA_SCALP / SIGMA_BRAIN,
    n_el=N_EL,
    h0=H0,
    r_layer=[[R_SKULL_IN, R_SKULL_OUT]],
    perm_per_layer=[SIGMA_SKULL / SIGMA_BRAIN],
    ppl=int(np.ceil(2 * np.pi * R_SKULL_OUT / H0)),
)

anomaly = [
    # PyEITAnomaly_Circle(center=[0.4, 0], r=0.1, perm=10.0),
    # PyEITAnomaly_Circle(center=[-0.4, 0], r=0.1, perm=10.0),
    # PyEITAnomaly_Circle(center=[0, 0.5], r=0.1, perm=0.1),
    PyEITAnomaly_Circle(center=[0, -0.5], r=0.1, perm=0.1),
]

mesh_new = mesh.set_perm(mesh_obj, anomaly=anomaly)

protocol_obj = protocol.create(N_EL, dist_exc=1, step_meas=1, parser_meas="std")

fwd = EITForward(mesh_obj, protocol_obj)
v0 = fwd.solve_eit()
v1 = fwd.solve_eit(perm=mesh_new.perm)

eit = greit.GREIT(mesh_obj, protocol_obj)
eit.setup(p=0.50, lamb=0.01, perm=mesh_obj.perm, jac_normalized=True)
# reconstruct dsigma/sigma0: with absolute dsigma the resistive skull columns dominate J
# ponytail: private pyEIT methods, pinned to pyeit 1.2.4
eit.H = eit._compute_h(eit.J * mesh_obj.perm, eit._compute_grid_weights(eit.xg, eit.yg))
ds = eit.solve(v1, v0, normalize=True)
x, y, ds = eit.mask_value(ds, mask_value=np.nan)


if __name__ == "__main__":
    pts = mesh_obj.node
    tri = mesh_obj.element
    el_pos = mesh_obj.el_pos
    mesh_obj.print_stats()

    fig, axes = plt.subplots(2, 1, figsize=(6, 10))

    ax = axes[0]
    im = ax.tripcolor(pts[:, 0], pts[:, 1], tri, np.real(mesh_new.perm), shading="flat")
    ax.plot(pts[el_pos, 0], pts[el_pos, 1], "ro")
    fig.colorbar(im, ax=ax, label="conductivity / brain")
    ax.set_title("true")

    ax = axes[1]
    im = ax.pcolormesh(x, y, np.real(ds), shading="nearest", cmap=plt.cm.viridis)
    fig.colorbar(im, ax=ax, label="normalized change")
    ax.set_title("GREIT")

    for ax in axes:
        ax.axis("equal")
        ax.set_xlabel("x")
        ax.set_ylabel("y")
    plt.show()
