> [!WARNING]
> Work in progress. Incomplete and subject to change.

# Electrical Impedance Tomography Skull Phantom

16-electrode EIT system and FDM-printed head phantom, built to see how a skull analogue interacts with EIT imaging and ischemia detection.

## Goals
- How accurate is EIT on a 3D-printed, quasi-2D tank?
- How does the inclusion of a skull-ring impact measurement accuracy?
- Can a neural network improve accuracy and detectable inclusion size compared to GREIT?

## Repository

- [hardware/](hardware/): PCB and tank design files.
- [firmware/](firmware/): code that runs on the PCB.
- [sim/](sim/): simulation of the phantom.
- [img/](img/): images.
- [environment.yml](environment.yml): Python environment.

## System

- CALVA: the PCB, details in [hardware/README.md](hardware/README.md).
- Tank: 3D-printed, TODO.

## Status

- Done: PCB rev 1.0 designed and fabricated.
- Done: stock firmware builds, not flashed yet.
- Done: basic simulation of the tank with GREIT reconstruction.
- TODO: PCB assembly and bring-up.
- TODO: tank design and printing.
- Planning: data acquisition.
- Planning: neural network.

## Credits

- [CN0565](https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/CN0565.html), [EVAL-ADICUP3029](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-adicup3029.html), [no-OS](https://github.com/analogdevicesinc/no-OS), [pyEIT](https://github.com/eitcom/pyEIT)

## License

- [hardware/](hardware/): CERN-OHL-P v2, see [hardware/LICENSE](hardware/LICENSE).
- [firmware/no-OS](https://github.com/loismathoi/no-OS/tree/calva): its own licenses, see [firmware/no-OS/COPYING](https://github.com/loismathoi/no-OS/blob/calva/COPYING).
- Everything else: MIT, see [LICENSE](LICENSE).
