import numpy as np
import trimesh
import trimesh.collision as tc
from vedo import Box, Mesh, Plotter  # only used if visualize=True

def get_sizes_and_collisions(components=None, envelope_size=None, visualize=False):
    if envelope_size is None:
        envelope_size = [711.2, 965.2, 609.6]

    if components is None:
        components = [
            {'name': 'battery1', 'file': r'STL_Parts/Battery_8S6P_V1.STL',
             'mass': 5.9, 'color': 'green', 'offset': [15, 150, 250], 'rotation': [90, 0, 0]},
        ]

    results = {
        "envelope_size_mm": np.asarray(envelope_size, float),
        "components": [],
        "cm_components": None,
    }

    # Visual envelope with min-corner at (0,0,0)
    env_center = [envelope_size[0]/2.0, envelope_size[1]/2.0, envelope_size[2]/2.0]
    envelope_viz = Box(pos=env_center, size=envelope_size, c='blue5', alpha=0.2).wireframe(False)

    meshes_viz = [envelope_viz]
    cm = tc.CollisionManager()  # components-only

    for comp in components:
        mesh_tm = trimesh.load_mesh(comp['file'])
        rc = mesh_tm.centroid.copy()
        rx, ry, rz = comp.get('rotation', [0, 0, 0])
        if rx: mesh_tm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rx), [1, 0, 0], point=rc))
        if ry: mesh_tm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(ry), [0, 1, 0], point=rc))
        if rz: mesh_tm.apply_transform(trimesh.transformations.rotation_matrix(np.radians(rz), [0, 0, 1], point=rc))

        # Offsets are already MIN-corner based → no +env_center
        off = np.array(comp.get('offset', [0, 0, 0]), float)
        mesh_tm.apply_translation(off.tolist())

        meshes_viz.append(Mesh(mesh_tm, c=comp['color'], alpha=0.4).lighting('plastic'))
        cm.add_object(comp['name'], mesh_tm)

        results["components"].append({
            "name": comp['name'],
            "bbox_size_mm": tuple(map(float, mesh_tm.extents.tolist())),
            "mass_kg": float(comp.get('mass', 0.0)),
            "offset_mm": off.tolist(),
            "rotation_deg": list(map(float, comp.get('rotation', [0, 0, 0]))),
        })

    results["cm_components"] = cm

    # Visualize the new box
    # Lx, Ly, Lz = 711.2, 965.2, 276.021265  # mm   (use your printed Sizes* values)
    # xmin, ymin, zmin = 0.0, 0.0, 0.0       # from your result (min corner ~ 0s)
    # cx, cy, cz = xmin + Lx/2, ymin + Ly/2, zmin + Lz/2
    # opt_box = Box(pos=[cx, cy, cz], size=[Lx, Ly, Lz], c='red', alpha=0.35).wireframe(False)
    # meshes_viz.append(opt_box)
    
    if visualize:
        Plotter(title='Satellite Packing', axes=1, bg='white').show(*meshes_viz, viewup='z', interactive=True)

    return results

# get_sizes_and_collisions(visualize=True)

