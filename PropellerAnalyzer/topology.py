from geometry import PropellerGeometry
import config


class TopologyAnalyzer:

    def __init__(self, geometry):

        self.geometry = geometry
        self.shape = geometry.get_shape()


    def analyze_faces(self):

        faces = self.shape.Faces()

        print("="*60)
        print("FACE ANALYSIS")
        print("="*60)

        for i, face in enumerate(faces):

            center = face.Center()

            area = face.Area()

            bb = face.BoundingBox()

            print(f"\nFace {i}")

            print(f"Area : {area:.4f} mm²")

            print(f"Center : ({center.x:.3f}, {center.y:.3f}, {center.z:.3f})")

            print(
                f"BoundingBox : "
                f"{bb.xlen:.3f} × "
                f"{bb.ylen:.3f} × "
                f"{bb.zlen:.3f}"
            )