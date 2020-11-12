from dolfin import *
import numpy as np
import mshr
import vtk_py
import os

## Import the appropriate mesh to mmoth-vent
#
# As of 10/23/2020, choices include unit_cube (single cell sims),
# cylinder, path_to_existing? (exising to just load in mesh from specified path?)
def import_mesh(sim_geometry, options):

    if sim_geometry == "cylinder":

        # initialize dictionary
        cylinder_specs = {}

        # default values
        #----------------
        # Center point for end of cylinder
        cylinder_specs["end_x"] = 10.0
        cylinder_specs["end_y"] = 0.0
        cylinder_specs["end_z"] = 0.0

        # Center point for base of cylinder
        cylinder_specs["base_x"] = 0.0
        cylinder_specs["base_y"] = 0.0
        cylinder_specs["base_z"] = 0.0

        # Base radius
        cylinder_specs["base_radius"] = 1.0
        cylinder_specs["end_radius"] = 1.0

        # Segments for approximating round shape
        cylinder_specs["segments"] = 20

        # Refinement of mesh
        cylinder_specs["refinement"] = 30

        # If user provides any alternate values, update
        # the cylinder_specs dictionary now
        cylinder_specs.update(options)

        cyl_bottom_center = Point(cylinder_specs["base_x"],cylinder_specs["base_y"],cylinder_specs["base_z"])
        cyl_top_center    = Point(cylinder_specs["x"],cylinder_specs["y"],cylinder_specs["z"])

        # Create cylinder geometry
        cylinder_geometry = mshr.Cylinder(cyl_top_center,cyl_bottom_center,cylinder_specs["end_radius"],cylinder_specs["base_radius"],cylinder_specs["segments"])

        # Create mesh
        print "Creating cylinder mesh"
        mesh = mshr.generate_mesh(cylinder_geometry,cylinder_specs["refinement"])

    if sim_geometry == "unit_cube":

        # Use built in function
        mesh = UnitCubeMesh(1,1,1)

    if sim_geometry == "ventricle" or sim_geometry == "ellipsoid":
        if sim_geometry == "ellipsoid":
            casename = "ellipsoidal"
        else:
            casename = "New_mesh" #New_mesh is the default casename in scripts sent from Dr. Lee

        mesh_path = options["mesh_path"][0]

        # check to see if it exists
        if not os.path.exists(mesh_path):
            print "mesh file not found"
            exit()

        if "hdf5" in mesh_path:

            mesh = Mesh()
            f = HDF5File(mpi_comm_world(), mesh_path, 'r')
            f.read(mesh, casename, False)
            ugrid = vtk_py.convertXMLMeshToUGrid(mesh)
            ugrid = vtk_py.rotateUGrid(ugrid, sx=0.1, sy=0.1, sz=0.1)
            mesh = vtk_py.convertUGridToXMLMesh(ugrid)
            f.close()

    return mesh