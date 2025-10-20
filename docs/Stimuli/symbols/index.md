# Symbol

Render layered geometric shapes—each with an optional texture—to build anything from a single cue to a multi-element stimulus. You pass an items list (or a single shape fast-path); the plugin draws them in order of z (higher = on top). Shapes fill with either a color or a texture (texture takes precedence), and you can use blend modes for richer composites.

## When To Use

- Minimal, highly controlled visual tokens (fixation, cues, placeholders).
- Simple one-off stimuli (e.g., a red triangle for 500 ms).
- Layered composites (e.g., plaid from two stripe textures + a ring overlay).
- Rapid prototyping of visual search, priming, Posner, DMS tasks.
- Adding lightweight noise masks or textured fills without image files.