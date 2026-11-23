import bpy
import math

# Clear existing objects
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# --- Sun ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
sun = bpy.context.active_object
sun.name = "Sun"
sun_mat = bpy.data.materials.new(name="SunMat")
sun_mat.diffuse_color = (1.0, 0.8, 0.0, 1.0)
sun.data.materials.append(sun_mat)
bpy.ops.object.shade_smooth()

# --- Planet definitions: (name, radius, orbit_radius, colour) ---
planets = [
    ("Mercury", 0.15, 2.5, (0.7, 0.7, 0.7, 1.0)),
    ("Venus",   0.25, 4.0, (0.9, 0.7, 0.3, 1.0)),
    ("Earth",   0.28, 6.0, (0.1, 0.3, 0.9, 1.0)),
    ("Mars",    0.20, 8.0, (0.9, 0.2, 0.1, 1.0)),
]

for name, radius, orbit_r, color in planets:
    # Planet sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=(orbit_r, 0, 0))
    planet = bpy.context.active_object
    planet.name = name
    mat = bpy.data.materials.new(name=name + "Mat")
    mat.diffuse_color = color
    planet.data.materials.append(mat)
    bpy.ops.object.shade_smooth()

    # Orbit ring (thin torus)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=orbit_r,
        minor_radius=0.01,
        major_segments=64,
        minor_segments=8,
        location=(0, 0, 0)
    )
    orbit = bpy.context.active_object
    orbit.name = name + "_Orbit"
    orbit_mat = bpy.data.materials.new(name=name + "OrbitMat")
    orbit_mat.diffuse_color = (0.5, 0.5, 0.5, 1.0)
    orbit.data.materials.append(orbit_mat)
    bpy.ops.object.shade_smooth()
