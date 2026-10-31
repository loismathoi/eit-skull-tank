# Hardware

CALVA rev 1.0 is a 100 x 51 mm, 4-layer board. It drives one AC excitation and reads one differential voltage through an impedance front end. Two crosspoint switches route those signals to any of the 16 electrodes. Everything touching the tank sits behind an isolation barrier.

Source: [KiCad project](../hardware/eit-skull-tank/), [schematic PDF](../hardware/eit-skull-tank/eit-skull-tank.pdf).

## Reference designs

Parts of the circuit follow two public Analog Devices design documents, consulted as references. No Analog Devices design files are in this repo, and the project is not affiliated with or endorsed by Analog Devices.

| Reference | Informed |
| --- | --- |
| [CN0565](https://www.analog.com/en/resources/reference-designs/circuits-from-the-lab/CN0565.html) | AFE, mux, isolation, isolated power |
| [EVAL-ADICUP3029](https://www.analog.com/en/resources/evaluation-hardware-and-software/evaluation-boards-kits/eval-adicup3029.html) | MCU, clocks, SWD, LEDs |

## Sheets

| Sheet | Function | Main parts |
| --- | --- | --- |
| `usb_power` | USB-C input, USB-UART bridge, 3.3 V regulator | J1 USB4110-GF-A, U1 MCP2221A, IC1 ADP124 |
| `mcu` | Microcontroller, 26 MHz crystal, SWD header, LEDs, push buttons | IC2 ADuCM3029, Y1, J2, SW1, SW2 |
| `iso_power` | Isolated DC-DC, isolated 3.3 V rail, charge-pump inverter | IC3 ADuM5020, IC4 ADM7150, IC5 ADM8828 |
| `iso_comm` | SPI, reset and interrupt isolator; I2C isolator | U2 ADuM3151, U3 ADuM1250 |
| `afe` | Impedance measurement front end | IC6 AD5941 |
| `mux` | Crosspoint switches, electrode connector | IC7, IC8 ADG2128; J3 |

The 32 kHz crystal inputs on IC2 are unconnected.

## Electrode routing

Each ADG2128 connects any X line to any Y line. The Y lines of both chips are joined, and the X lines go to the electrodes.

| Switch | I2C address | X0-X7 | X8-X11 |
| --- | --- | --- | --- |
| IC7 | `0x70` | E0-E7 | unconnected |
| IC8 | `0x71` | E8-E15 | unconnected |

J3 is a 2 x 10, 2.54 mm header. Pins 3-18 carry E0-E15 in order. Pins 1, 2, 19 and 20 are `GND_ISO`.

## Stackup

Nominal thickness 1.6 mm, ENIG finish. Power is routed as tracks, not planes.

| Layer | Copper | Dielectric below | Use |
| --- | --- | --- | --- |
| F.Cu | 35 um | 0.138 mm | Signal |
| In1.Cu | 35 um | 1.113 mm | GND |
| In2.Cu | 35 um | 0.138 mm | GND, some I2C, reset and LED tracks |
| B.Cu | 35 um | | Signal |

## Isolation barrier

The barrier runs along x = 139.1 mm in KiCad board coordinates and is 2.5 mm wide. Only IC3, U2 and U3 connect the two ground domains. The isolation follows CN0565. No isolation voltage was targeted or tested, so CALVA claims no isolation rating.

## MCU pin map

| Function | Pins |
| --- | --- |
| SPI0 to AFE | P0_00 SCLK, P0_01 MOSI, P0_02 MISO |
| AFE chip select | P1_10 |
| AFE reset | P0_13 |
| AFE interrupt | P0_15 |
| I2C0 to mux | P0_04 SCL, P0_05 SDA |
| UART0 to MCP2221A | P0_10 TX, P0_11 RX |

The MCP2221A supports up to 460800 baud, 8N1.

## Fabrication

- Manufacturer: AISLER, 4-layer, 1.6 mm, ENIG. Export with the AISLER KiCad plugin.
- Design rules: [`eit-skull-tank.kicad_dru`](../hardware/eit-skull-tank/eit-skull-tank.kicad_dru).
- Vias untented.
- Assembly: stencil and reflow.

## Footprint warnings

Do not run "update footprint from library" on these parts. It would overwrite differences from the library:

- J3, IC1, IC2, IC4, IC6, R20, R22: local edits.
- IC7, IC8: differ from the library.

J2 uses `Samacsys:FTSH10501LDVK`, with 0.74 x 2.79 mm pads and 4.07 mm row pitch.

SamacSys symbols and footprints are embedded in the KiCad files. The SamacSys library and its 3D models are not in this repo, so 3D views show those parts without models.

## Open issues

- **Mux lines:** the mux closes Y0-Y3 (CE0, RE0, SE0, DE0), while `bia_measurement.c` in no-OS uses CE0, AIN0, AIN1, AIN2 and AIN3 (Y0, Y4-Y7). This is unexplained and will be settled with the resistor test.
- **J2 footprint:** it came from componentsearchengine. It matches the Samtec catalog drawing, but that drawing has no land pattern, so the footprint is not checked against a manufacturer land pattern.
- **MCP2221A reset:** RST is left open on the internal pull-up, as the datasheet allows.
- **SWD probe:** a probe and a 10-pin 1.27 mm cable still have to be ordered.
