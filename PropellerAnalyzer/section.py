import numpy as np


class SectionExtractor:

    def __init__(self, geometry):

        self.geometry = geometry

        self.radius = geometry.get_radius()

    def create_sections(self,
                        n_sections=20,
                        root_ratio=0.20,
                        tip_ratio=0.95):

        ratios = np.linspace(root_ratio,
                             tip_ratio,
                             n_sections)

        radii = ratios * self.radius

        return radii