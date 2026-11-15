# Firmware

- no-OS/: fork of Analog Devices' [no-OS](https://github.com/analogdevicesinc/no-OS), branch calva, submodule.
- Project cn0565, variant eit_iio.
- Get it: `git submodule update --init firmware/no-OS`

## Build

- [CrossCore® Embedded Studio](https://www.analog.com/en/resources/evaluation-hardware-and-software/software/adswt-cces.html) 3.1.0
- `python tools/scripts/no_os_build.py build --project cn0565 --variant eit_iio --board eval-adicup3029`
- Output: no-OS/build/

## Flashing

- SWD probe on J2, add `--probe openocd --flash`. Not tested yet.

## Licence

- no-OS keeps its own licences, see no-OS/COPYING.
