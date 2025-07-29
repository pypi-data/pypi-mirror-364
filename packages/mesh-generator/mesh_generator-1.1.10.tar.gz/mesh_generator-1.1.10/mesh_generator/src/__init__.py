"""

Usage:
In this subpackage are the most important mesh calculations.
Returns adjusted and legacy mesh (step 2 and 3 of creating a mesh).
For more details: https://q.predsci.com/docs/mesh_generator/

Important modules:
mesh.py
mesh_segment.py

1D Mesh example:
https://q.predsci.com/docs/mesh_generator/example1d/
"""

from mesh_generator.src.mesh_segment import MeshSegment
from mesh_generator.src.mesh import Mesh