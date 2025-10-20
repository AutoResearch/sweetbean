# Gabor

Render one or more **true sinusoidal Gabor patches** (grating × Gaussian). Each patch exposes **orientation**, **spatial frequency** (sf_cpp / sf_cpd), **phase**, **contrast**, and **Gaussian sigma/size**; positions are in pixels (or degrees with `px_per_deg`). Multiple patches can be shown at once, and you can collect keyboard and/or mouse responses.
Not for flat geometric shapes, annuli, bars/stripe fills, or noise masks — use **Symbol** (with stripe/noise textures and layering) for those or if you need more complex composites (e.g., a Gabor with an annular mask).

## When To Use
- Orientation / contrast / **phase** judgments where **sf/phase/sigma** must be controlled precisely.
- 2AFC with **Gabor** patches (e.g., which side has higher contrast?).
- Spatial-frequency tuning, phase sweeps, or multi-patch Gabor arrays (crowding/surround interactions).
