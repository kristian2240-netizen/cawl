---
name: blender
description: "Blender 5.1 automation and scripting. Apply when Blender is open or when the user wants to work with 3D, modeling, rendering, scripting, or animation."
user-invocable: true
---

# Blender 5.1 — The Omnissiah's Forge

Blender is installed at `C:\Program Files\Blender Foundation\Blender 5.1\`. The `blender` command launches it.

## Core Rules When Blender Is Open

1. **Never modify the user's scene without explicit permission.** Always ask before deleting, moving, or renaming objects.
2. **Always save before risky operations.** Remind the user to save or offer to save via script.
3. **Use the Info panel.** When Blender is open, the user can see all operations in the Info panel at the top. Mirror what they see.
4. **Prefer Python scripting over manual instructions.** If the user asks "how do I do X", give them a Python script they can paste into Blender's Text Editor and run.
5. **Respect the undo stack.** Don't chain too many operations in one script without checkpoints.
6. **Match Blender's coordinate system.** Z-up, right-handed. Don't mix up matrices.
7. **Use Blender's API correctly.** For Blender 5.1, use `bpy` module. Always check `bpy.context.selected_objects` not `bpy.context.selected_objects` (it's a set, not a list).

## Blender Python API Quick Reference

### Common Operations

```python
import bpy

# Clear selection
bpy.ops.object.select_all(action='DESELECT')

# Select object by name
bpy.data.objects['Cube'].select_set(True)
bpy.context.view_layer.objects.active = bpy.data.objects['Cube']

# Create mesh primitive
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
bpy.ops.mesh.primitive_uv_sphere_add(radius=1, location=(3, 0, 0))
bpy.ops.mesh.primitive_cylinder_add(radius=1, depth=2, location=(0, 3, 0))

# Delete selected
bpy.ops.object.delete()

# Move object
obj = bpy.data.objects['Cube']
obj.location = (1, 2, 3)

# Rotate object (Euler radians)
obj.rotation_euler = (0, 0, 1.5708)  # 90 degrees on Z

# Scale object
obj.scale = (2, 2, 2)

# Apply transform
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# Join selected objects
bpy.ops.object.join()

# Separate by material
bpy.ops.object.separate(type='MATERIAL')

# Set shade smooth
bpy.ops.object.shade_smooth()

# Add modifier
bpy.ops.object.modifier_add(type='SUBSURF')
obj.modifiers["Subdivision"].levels = 2

# Apply modifier
bpy.ops.object.modifier_apply(modifier="Subdivision")

# Add material
mat = bpy.data.materials.new(name="MyMaterial")
mat.use_nodes = True
obj.data.materials.append(mat)

# Set material color (Principled BSDF)
bsdf = mat.node_tree.nodes["Principled BSDF"]
bsdf.inputs['Base Color'].default_value = (1, 0, 0, 1)  # RGBA red
bsdf.inputs['Metallic'].default_value = 0.8
bsdf.inputs['Roughness'].default_value = 0.2

# Render settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.samples = 128
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.filepath = "//render.png"
bpy.ops.render.render(write_still=True)

# Camera setup
bpy.ops.object.camera_add(location=(7, -7, 5))
cam = bpy.context.object
cam.rotation_euler = (1.1, 0, 0.785)
bpy.context.scene.camera = cam

# Light setup
bpy.ops.object.light_add(type='AREA', location=(5, -5, 5))
light = bpy.context.object
light.data.energy = 1000

# Import/Export
bpy.ops.import_scene.gltf(filepath="model.glb")
bpy.ops.export_scene.gltf(filepath="export.glb")

# UV Unwrap
bpy.ops.uv.smart_project()

# Keyframe animation
obj.location = (0, 0, 0)
obj.keyframe_insert(data_path="location", frame=1)
obj.location = (5, 5, 5)
obj.keyframe_insert(data_path="location", frame=60)

# Set frame range
bpy.context.scene.frame_start = 1
bpy.context.scene.frame_end = 120

# Play animation
bpy.ops.anim.play()

# Console print (visible in Blender's console)
print("Hello from C.A.W.L.")
```

### Selection & Context

```python
# Get active object
obj = bpy.context.active_object

# Get all selected objects
selected = bpy.context.selected_objects  # This is a set!

# Get all objects in scene
all_objects = bpy.data.objects

# Get object by name (with null check)
obj = bpy.data.objects.get("MyObject")
if obj:
    print(f"Found: {obj.name}")
else:
    print("Object not found")

# Get mesh data
mesh = obj.data
print(f"Vertices: {len(mesh.vertices)}")
print(f"Faces: {len(mesh.polygons)}")
```

### Common Gotchas in Blender 5.1

1. **`selected_objects` is a set, not a list.** Use `list(bpy.context.selected_objects)` if you need indexing.
2. **`bpy.ops` requires context.** Some ops only work in Object Mode, Edit Mode, etc. Check `bpy.context.mode`.
3. **Undo is limited.** Default 32 steps. Can increase: `bpy.context.preferences.edit.undo_steps = 128`
4. **File paths use `//` for relative.** `//textures/` means relative to the .blend file.
5. **Materials use nodes.** `mat.use_nodes = True` before accessing `mat.node_tree`.
6. **Render is blocking.** `bpy.ops.render.render()` blocks until complete. Use `bpy.ops.render.render(write_still=True)` for file output.
7. **Coordinate system is Z-up.** Don't confuse with Y-up systems.

## Workflow Patterns

### Pattern 1: User Asks "How Do I...?"
1. Check if Blender is open (ask or check process)
2. Provide Python script for Text Editor
3. Explain what the script does
4. Offer to run it via command line if needed

### Pattern 2: User Wants to Automate
1. Ask what they want to achieve
2. Write a complete Python script
3. Save to a `.py` file
4. Run: `blender --background --python script.py`

### Pattern 3: User Wants to Learn
1. Explain the concept
2. Show the Python equivalent
3. Link to Blender documentation
4. Suggest hands-on practice

### Pattern 4: Rendering
1. Set up scene (camera, lights, materials)
2. Configure render settings
3. Render to file
4. Show result or provide file path

## Command Line Operations

```bash
# Open Blender with a file
blender "project.blend"

# Run script in background (no GUI)
blender --background --python script.py

# Render from command line
blender --background --python render.py

# Export to glTF
blender --background --python export.py -- --input scene.blend --output model.glb

# Import and convert
blender --background --python convert.py -- --input obj_file.obj --output blend_file.blend
```

## Error Handling

```python
import bpy
import sys

try:
    # Your code here
    bpy.ops.mesh.primitive_cube_add()
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    # Optionally raise to Blender's error handler
    raise
```

## Anti-Patterns

- Never delete `bpy.context.scene.camera` without setting a new one
- Never remove all materials without checking if objects need them
- Never modify `bpy.data.objects` while iterating over it
- Never use `bpy.ops` in a loop without proper context overrides
- Never render at full resolution for preview (use viewport render first)
- Never assume objects exist — always check with `.get()`
