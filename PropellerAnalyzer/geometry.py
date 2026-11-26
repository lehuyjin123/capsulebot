import cadquery as cq
import numpy as np


class PropellerGeometry:

    def __init__(self, filename):

        self.filename = filename

        self.model = cq.importers.importStep(filename)

        self.shape = self.model.val()

        self.bbox = self.shape.BoundingBox()


    # ===========================
    # Basic Geometry
    # ===========================

    def get_shape(self):
        return self.shape


    def get_bbox(self):
        return self.bbox


    def get_volume(self):
        return self.shape.Volume()


    def get_surface_area(self):
        return self.shape.Area()


    def get_center_of_mass(self):

        c = self.shape.Center()

        return np.array([c.x, c.y, c.z])


    # ===========================
    # Dimensions
    # ===========================

    def get_length_x(self):
        return self.bbox.xlen


    def get_length_y(self):
        return self.bbox.ylen


    def get_length_z(self):
        return self.bbox.zlen


    def get_diameter(self):

        return max(self.bbox.xlen,
                   self.bbox.zlen)


    def get_radius(self):

        return self.get_diameter()/2


    def get_disk_area(self):

        r = self.get_radius()/1000.0

        return np.pi*r*r


    # ===========================
    # Topology
    # ===========================

    def get_faces(self):

        return self.shape.Faces()


    def get_edges(self):

        return self.shape.Edges()


    def get_vertices(self):

        return self.shape.Vertices()


    def face_count(self):

        return len(self.get_faces())


    def edge_count(self):

        return len(self.get_edges())


    def get_rotation_axis(self):
        """
        Rotation axis = Y axis
        """

        bb = self.get_bbox()

        x0 = (bb.xmin + bb.xmax) / 2
        y0 = (bb.ymin + bb.ymax) / 2
        z0 = (bb.zmin + bb.zmax) / 2

        return np.array([x0, y0, z0])


    def get_hub_center(self):

        return self.get_rotation_axis()


    # ===========================
    # Summary
    # ===========================

    def summary(self):

        print("="*60)
        print("PROPELLER GEOMETRY")
        print("="*60)

        print(f"STEP File        : {self.filename}")

        print()

        print("Bounding Box")

        print(f"X Length         : {self.get_length_x():.6f} mm")
        print(f"Y Length         : {self.get_length_y():.6f} mm")
        print(f"Z Length         : {self.get_length_z():.6f} mm")

        print()

        print(f"Diameter         : {self.get_diameter():.6f} mm")
        print(f"Radius           : {self.get_radius():.6f} mm")

        print()

        print(f"Disk Area        : {self.get_disk_area():.8e} m²")

        print()

        print(f"Surface Area     : {self.get_surface_area()/1e6:.8e} m²")
        print(f"Volume           : {self.get_volume()/1e9:.8e} m³")

        print()

        com = self.get_center_of_mass()

        print(f"Center of Mass   : ({com[0]:.4f}, {com[1]:.4f}, {com[2]:.4f})")

        print()

        print("Topology")

        print(f"Faces            : {self.face_count()}")
        print(f"Edges            : {self.edge_count()}")
        print(f"Vertices         : {self.vertex_count()}")

        print("="*60)
        axis = self.get_rotation_axis()

        print()
        print("Rotation Axis")

        print(f"({axis[0]:.4f}, {axis[1]:.4f}, {axis[2]:.4f})")