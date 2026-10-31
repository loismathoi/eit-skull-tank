# Firmware

CALVA runs Analog Devices' no-OS `cn0565` project, variant `eit_iio`. The firmware exposes the AFE and mux as IIO devices over UART, and Python on the PC controls the measurement.

The source is the [`firmware/no-OS`](../firmware/no-OS) submodule, a fork on branch `calva` with no edits yet. None of this has run on CALVA hardware yet.

```
git submodule update --init firmware/no-OS
```

## Build environment

Building requires CCES 3.1.0 (CrossCore Embedded Studio) and your own licence for it. Builds run in a Docker container, while editing and Python run on the host.

The image is not reproducible from this repo. It contains:

- Ubuntu 22.04 with the i386 architecture enabled
- CCES 3.1.0 and the ADuCM302x_DFP 3.2.0 pack
- `cmake==3.31.*` (CMake 4.x breaks the build), ninja, xvfb
- `/usr/tmp` with mode 1777
- user `builder` with the host UID, owning the `ARM/packs` folder

For a graphical session, run `xhost +local:docker` on the host and `export DISPLAY=:0` as `builder`.

## Build

With the repo mounted at `/work` in a container named `cces`:

```
docker start cces && docker exec -it cces su - builder
cd /work/firmware/no-OS
python tools/scripts/no_os_build.py build --project cn0565 --variant eit_iio --board eval-adicup3029
```

Output goes to `firmware/no-OS/build/`.

## Flashing

Flash through an SWD probe on J2 by adding `--probe openocd --flash` to the build command. This needs a container with USB access and the OpenOCD fix under [known issues](#known-issues). The flow has not been run yet. UART download needs a second-stage loader, and none was found.

## Python setup

Setup was tested on Arch Linux. Install `libiio` from pacman because conda-forge's `libiio` has no serial backend, then create the environment:

```
sudo pacman -S libiio
conda env create -f environment.yml
conda activate eit-skull-tank
```

[`environment.yml`](../environment.yml) installs pyEIT, matplotlib, `pyadi-iio` and `pylibiio==0.25`. The environment holds no `libiio` of its own, so `pylibiio` loads the system library.

Stock firmware uses 230400 baud, 8N1.

## Required fixes in `daq/`

Stock firmware matches CALVA's pins, baud rate, Y0-Y3 routing and RCAL. Two differences need handling in the acquisition code, in a `daq/` folder that does not exist yet:

1. `0x71` is IC8 (E8-E15), and `pyadi-iio` adds it first, so the stock electrode order is rotated by 180 degrees.
2. `all_voltages` assumes 12 X lines per chip, while CALVA wires 8. Use:

   ```python
   XLINE = [12 + i for i in range(8)] + list(range(8))
   ```

## Known issues

- **OpenOCD:** `aducm302x.tcl` in the DFP fails on OpenOCD 0.12. The fix uses `dap create` plus `-dap` instead of `-chain-position`, and `adapter speed` instead of `adapter_khz`. It has been tested on a copy without hardware and is not applied yet.
- **Mux lines:** the mux closes Y0-Y3, while `bia_measurement.c` uses Y0 and Y4-Y7. See [hardware open issues](hardware.md#open-issues).
- **SWD probe:** not yet available, so flashing is untested.
- **libiio versions:** on the test machine, the `pylibiio` 0.25 bindings load Arch's `libiio` 0.26. Imports work, but serial communication with a board is untested.
