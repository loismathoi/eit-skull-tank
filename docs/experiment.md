# Experiment

This is a plan. No measurements exist yet.

## Research question

How does a skull-analog ring change the minimum detectable inclusion size and the localization error?

Secondary: does a model trained on pyEIT simulation frames work on real tank frames?

## Plan

1. **Perfboard:** resistor tests, Y-line mismatch, electrode map.
2. **Stamps:** effective conductivity per hole size and density, with current passing radially through the wall.
3. **Simulation:** choose the ring and check that the expected effect is measurable.
4. **Tank:** build it, then measure noise and drift with no inclusion.
5. **Main dataset:** with and without ring, several inclusion sizes, several radii and angles, repeats, and references before and after.
6. **pyEIT comparison:** same conditions, measured conductivity, normalized differences.
7. **U-Net:** train on simulation, test on real frames, compare against GREIT.

## Detection threshold

The detection threshold will be fixed before measuring, so the data cannot influence it. Its value and criterion are not set yet.

## Open question: one saline or two

The ring's holes connect the inside and outside of the tank, so saline can pass between them. Whether the tank uses one saline is undecided.

[`sim/rig.py`](../sim/rig.py) currently models two regions, plus the ring between them:

| Region | Radius (normalized to tank inner radius) | Conductivity (S/m) |
| --- | --- | --- |
| Inside ring | below 0.70 | 0.33 |
| Ring | 0.70-0.75 | 0.33 / 60 |
| Outside ring | above 0.75 | 0.29 |
