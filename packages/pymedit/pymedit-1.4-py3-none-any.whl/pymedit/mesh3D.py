# This file is part of pymedit.
#
# pymedit is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# pymedit is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# A copy of the GNU General Public License is included below.
# For further information, see <http://www.gnu.org/licenses/>
import tempfile
import subprocess
import numpy as np
import scipy.sparse as sp
from .abstract import display, tic, toc, __AbstractMesh, exec2, ExecException
from .abstract import __AbstractSol


class Mesh3D(__AbstractMesh):
    def __init__(self, meshFile=None, debug=0):
        """Load a 3D tetrahedral mesh in the INRIA mesh file format.

        INPUT:
            meshFile  :  the path of the mesh to read. Supported format: 
                         .mesh and .meshb. If meshFile=None, the instantiates
                         an empty 2D mesh.
            debug     :  an integer tuning the level of verbosity."""
        super().__init__(meshFile, debug)
        if self.Dimension is None:
            self.Dimension = 3
        if self.Dimension != 3:
            raise Exception("Error: the mesh "+meshFile+" is not of dimension"
                            " 3.")

    @property
    def verticesToTetra(self):
        """Sparse matrix M of size nv x ntet 
            such that M_ij=1 if and only if 
            tetrahedra number j contains the vertex i."""
        if not hasattr(self, '_Mesh3D__verticesToTetra'):
            tic()
            A = self.tetrahedra[:, 0] - 1
            B = self.tetrahedra[:, 1] - 1
            C = self.tetrahedra[:, 2] - 1
            D = self.tetrahedra[:, 3] - 1
            I = np.append(A, [B, C, D])
            nums = range(self.ntet)
            J = np.append(nums, [nums, nums, nums])
            self.__verticesToTetra = sp.csr_matrix(([1]*4*self.ntet, (I, J)),
                                                   shape=(self.nv, self.ntet))
            display("Computed vertices to tetra in : " +
                    toc()+".", 2, self.debug)
        return self.__verticesToTetra

    @property
    def tetrahedronToTetrahedron(self):
        """Sparse matrix M of size ntet x ntet
           such that M_ij=1 if tetrahedra i and j are connected by a face."""
        if not hasattr(self, '_Mesh3D__tetraToTetra'):
            verticesToTetra = self.verticesToTetra
            tic()
            connectivity = verticesToTetra.T.dot(verticesToTetra)
            connectivity = sp.find(connectivity == 3)
            self.__tetraToTetra = \
                sp.csr_matrix(([1]*len(connectivity[0]),
                               (connectivity[1], connectivity[0])))
            display("Computed connectivity matrices for tetrahedra in "
                    + toc()+".", 2, self.debug)
        return self.__tetraToTetra

    def vertexToTetra(self, i):
        """Returns the list of tetrahedra connected to the vertex number i"""
        return self.verticesToTetra[i-1].indices

    def elemToTetra(self, elem):
        """Returns the set of tetrahedra connected to the element elem.
        INPUT:
            elem : a list of vertex indices (numerotation starting from 1)
                   elem is of size 1 if it is a vertex
                   elem is of size 2 if it is an edge
                           of size 3 if it is a triangle
        """
        return list(set.intersection(*[set(self.vertexToTetra(pt))
                                       for pt in elem]))

    @property
    def jacobiansTriangles(self):
        """
        Returns 2 times the area of each boundary triangle, that is 
                                 ||AB|| x  ||AC||
                            -----------------------
                                 __________________
                                /        AB . AC
                             | / 1 - --------------
                             |/      ||AB|| x ||AC||
        """
        if not hasattr(self, '_Mesh3D__jacobiansTriangles'):
            tic()
            A = self.vertices[self.triangles[:, 0]-1]
            B = self.vertices[self.triangles[:, 1]-1]
            C = self.vertices[self.triangles[:, 2]-1]
            AB = B-A
            AC = C-A
            normAB = np.sqrt(AB[:, 0]**2+AB[:, 1]**2+AB[:, 2]**2)
            normAC = np.sqrt(AC[:, 0]**2+AC[:, 1]**2+AC[:, 2]**2)
            dotProdABAC = AB[:, 0]*AC[:, 0]+AB[:, 1]*AC[:, 1]+AB[:, 2]*AC[:, 2]
            self.__jacobiansTriangles = normAB*normAC * \
                np.sqrt(1-dotProdABAC/(normAB*normAC))
            display("Computed jacobians of boundary triangles in "+toc()+"s",
                    2, self.debug)
        return self.__jacobiansTriangles

    @property
    def jacobians(self):
        """
        Returns 2 times the volume of each tetrahedra, that is 
        | xB-xA  xC-xA xD-xA  |
        | yB-yA  yC-yA yD-yA  |
        | zB-zA  zC-zA zD-zA  |
        """
        if not hasattr(self, '_Mesh3D__jacobians'):
            tic()
            vertices0 = self.vertices[self.tetrahedra[:, 0]-1]
            vertices1 = self.vertices[self.tetrahedra[:, 1]-1]
            vertices2 = self.vertices[self.tetrahedra[:, 2]-1]
            vertices3 = self.vertices[self.tetrahedra[:, 3]-1]
            xA = vertices0[:, 0]
            xB = vertices1[:, 0]
            xC = vertices2[:, 0]
            xD = vertices3[:, 0]
            yA = vertices0[:, 1]
            yB = vertices1[:, 1]
            yC = vertices2[:, 1]
            yD = vertices3[:, 1]
            zA = vertices0[:, 2]
            zB = vertices1[:, 2]
            zC = vertices2[:, 2]
            zD = vertices3[:, 2]
            self.__jacobians = det3d(xB-xA, yB-yA, zB-zA,
                                     xC-xA, yC-yA, zC-zA,
                                     xD-xA, yD-yA, zD-zA)
            display("Computed jacobians of tetrahedra in "+toc()+"s.", 2,
                    self.debug)
        return self.__jacobians

    def checkQuality(self):
        """Check the quality of the mesh:
              - Attempts to find degenerate tetrahedra (jacobian < 1e-10)
              - Attempts to find very close vertices (len < 1e-7) within
              - Verify that boundary triangles are in the mesh
              - Verify that boundary triangle connect tetrahedra with different
                 labels
              - Verify that boundary triangles have at most two adjacent tetra
              - Verify that tetrahedra have at most 4 adjacent neighbors
              - Detect isolated vertices
        """
        jacobians = self.jacobians
        problems = self.tetrahedra[jacobians < 1e-10]
        print(f"{len(problems)} flat tetrahedra found.")
        for tet in np.argsort(jacobians)[:15]:
            print(f"{tet} ({self.tetrahedra[tet,:-1]})\t:  K = {jacobians[tet]}.")
        combinations = [(i, j) for i in range(4) for j in range(4) if i < j]
        lengths = np.asarray([np.linalg.norm(self.vertices[problems[:, c[1]]-1] -
                                             self.vertices[problems[:, c[0]]-1], axis=1) for c in combinations])
        (I, J) = np.where(lengths < 1e-7)
        tofusion = [(problems[j, combinations[i][0]], problems[j,
                                                               combinations[i][1]]) for (i, j) in zip(I, J)]
        tetproblems = np.asarray([ntet for ntet in range(
            self.ntet) if jacobians[ntet] < 1e-10])[list(set(J))]
        print(f"{len(tetproblems)} tetrahedra with at least two very close vertices.")

        for (ntri, tri) in enumerate(self.triangles):
            adjacents = self.elemToTetra(tri[:-1])
            if not adjacents:
                print(f"Warning triangle {ntri} not in mesh.")
            if len(adjacents) == 2 and self.tetrahedra[adjacents[0]][-1] \
                    == self.tetrahedra[adjacents[1]][-1]:
                print(f"Triangle {ntri} connecting tetrahedra " + str(adjacents)
                      + "is not a true border.")
            if max(tri[:-1]) > self.nv:
                print(f"Triangle {ntri} has a wrong vertex.")
            if len(adjacents) > 2:
                print(
                    f"Triangle {ntri} has more than two adjacent tetra:", adjacents)

        tetraToTetra = self.tetrahedronToTetrahedron
        numConnected = sp.find((tetraToTetra == 1).sum(0) >= 5)[1]
        if numConnected:
            print(f"Found {len(numConnected)} tetrahedra with more than 4"
                  "adjacent neighbors:")
            print(numConnected)

        isolatedVertices = sp.find(self.verticesToTetra.sum(1) == 0)[1]
        if isolatedVertices:
            print(f"Found {len(isolatedVertices)} isolated vertices:")
            print(isolatedVertices)

    def plot(self, title=None, keys=[], silent=True):
        """Plot a 3D mesh with medit.
        INPUTS:
            title : a message to be printed in the console before plotting
            keys  : a set of key strokes to be sent to the medit graphical 
                    window
            silent: (default True) If silent, then standard output of medit is 
                    hidden in the python execution shell"""
        from .external import medit
        if title:
            display(title, level=0, debug=self.debug, color="green")
        medit(self, keys=keys, silent=silent)


def cube(nx: int, ny: int, nz: int, transfo=None, debug=0) -> Mesh3D:
    """Returns a 3D cubic tetrahedral mesh.

    INPUT:
        nx, ny, nz : number of mesh elements along each axis
        transfo    : a transformation [funx,funy,funz] to apply on the vertices
                     (X,Y,Z) <- (funx(X,Y,Z),funy(X,Y,Z),funz(X,Y,Z))
    """
    M = Mesh3D(None, debug)
    tic()
    # Create vertices and their numerotation
    x = np.linspace(0, 1, nx+1)
    y = np.linspace(0, 1, ny+1)
    z = np.linspace(0, 1, nz+1)
    X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
    if transfo:
        if isinstance(transfo, list):
            X, Y, Z = transfo[0](X, Y, Z), transfo[1](
                X, Y, Z), transfo[2](X, Y, Z)
        else:
            X, Y, Z = transfo(X, Y, Z)
    M.nv = (nx+1)*(ny+1)*(nz+1)
    M.vertices = np.zeros((M.nv, 4))
    M.vertices[:, 0] = X.flatten()
    M.vertices[:, 1] = Y.flatten()
    M.vertices[:, 2] = Z.flatten()
    numerotation = np.array(range(M.nv)).reshape((nx+1, ny+1, nz+1))+1

    # Create all the tetrahedra
    x1 = numerotation[:-1, :-1, :-1].flatten()
    x2 = numerotation[1:, :-1, :-1].flatten()
    x3 = numerotation[:-1, 1:, :-1].flatten()
    x4 = numerotation[1:, 1:, :-1].flatten()
    x5 = numerotation[:-1, :-1, 1:].flatten()
    x6 = numerotation[1:, :-1, 1:].flatten()
    x7 = numerotation[:-1, 1:, 1:].flatten()
    x8 = numerotation[1:, 1:, 1:].flatten()

    label = np.full((len(x1),), 0)

    tet1 = np.column_stack((x5, x1, x7, x8, label))
    tet2 = np.column_stack((x1, x5, x6, x8, label))
    tet3 = np.column_stack((x2, x1, x6, x8, label))
    tet4 = np.column_stack((x1, x2, x4, x8, label))
    tet5 = np.column_stack((x3, x1, x4, x8, label))
    tet6 = np.column_stack((x1, x3, x7, x8, label))

    M.tetrahedra = np.row_stack((tet1, tet2, tet3, tet4, tet5, tet6))

    # Create all the boundary triangles
    x1front = numerotation[:-1, :-1, 0].flatten()
    x2front = numerotation[1:, :-1, 0].flatten()
    x3front = numerotation[:-1, 1:, 0].flatten()
    x4front = numerotation[1:, 1:, 0].flatten()
    x5back = numerotation[:-1, :-1, -1].flatten()
    x6back = numerotation[1:, :-1, -1].flatten()
    x7back = numerotation[:-1, 1:, -1].flatten()
    x8back = numerotation[1:, 1:, -1].flatten()
    x1left = numerotation[0, :-1, :-1].flatten()
    x3left = numerotation[0, 1:, :-1].flatten()
    x5left = numerotation[0, :-1, 1:].flatten()
    x7left = numerotation[0, 1:, 1:].flatten()
    x2right = numerotation[-1, :-1, :-1].flatten()
    x4right = numerotation[-1, 1:, :-1].flatten()
    x6right = numerotation[-1, :-1, 1:].flatten()
    x8right = numerotation[-1, 1:, 1:].flatten()
    x3top = numerotation[:-1, -1, :-1].flatten()
    x4top = numerotation[1:, -1, :-1].flatten()
    x7top = numerotation[:-1, -1, 1:].flatten()
    x8top = numerotation[1:, -1, 1:].flatten()
    x1bottom = numerotation[:-1, 0, :-1].flatten()
    x2bottom = numerotation[1:, 0, :-1].flatten()
    x5bottom = numerotation[:-1, 0, 1:].flatten()
    x6bottom = numerotation[1:, 0, 1:].flatten()

    labelFront = np.full((len(x1front),), 5)
    labelBack = np.full((len(x5back),), 6)
    labelLeft = np.full((len(x1left),), 4)
    labelRight = np.full((len(x2right),), 2)
    labelBottom = np.full((len(x1bottom),), 1)
    labelTop = np.full((len(x3top),), 3)

    trisBack1 = np.column_stack((x5back, x7back, x8back, labelBack))
    trisBack2 = np.column_stack((x8back, x6back, x5back, labelBack))
    trisLeft1 = np.column_stack((x5left, x1left, x7left, labelLeft))
    trisLeft2 = np.column_stack((x1left, x3left, x7left, labelLeft))
    trisBottom1 = np.column_stack((x1bottom, x5bottom, x6bottom, labelBottom))
    trisBottom2 = np.column_stack((x2bottom, x1bottom, x6bottom, labelBottom))
    trisRight1 = np.column_stack((x2right, x6right, x8right, labelRight))
    trisRight2 = np.column_stack((x8right, x4right, x2right, labelRight))
    trisFront1 = np.column_stack((x1front, x2front, x4front, labelFront))
    trisFront2 = np.column_stack((x3front, x1front, x4front, labelFront))
    trisTop1 = np.column_stack((x3top, x4top, x8top, labelTop))
    trisTop2 = np.column_stack((x8top, x7top, x3top, labelTop))
    M.triangles = np.row_stack((trisBack1, trisBack2,
                                trisLeft1, trisLeft2,
                                trisBottom1, trisBottom2,
                                trisRight1, trisRight2,
                                trisTop1, trisTop2,
                                trisFront1, trisFront2))

    # Corners
    corners = [numerotation[x, y, z] for x in [0, -1] for y in [0, -1]
               for z in [0, -1]]
    M.corners = np.asarray(corners).reshape((len(corners), 1))
    M.requiredVertices = M.corners

    # Ridges
    edge13 = numerotation[0, :-1, 0], numerotation[0, 1:, 0]
    slice_start = [[(slice(0, nx), x, y),
                    (x, slice(0, ny), y),
                    (x, y, slice(0, nz))] for x in [0, -1] for y in [0, -1]]
    slice_start = sum(slice_start, [])
    slice_end = [[(slice(1, nx+1), x, y),
                  (x, slice(1, ny+1), y),
                  (x, y, slice(1, nz+1))] for x in [0, -1] for y in [0, -1]]
    slice_end = sum(slice_end, [])
    edges = \
        np.row_stack(list(np.column_stack((numerotation[s0], numerotation[s1]))
                          for (s0, s1) in zip(slice_start, slice_end)))
    M.edges = np.column_stack((edges, np.full((edges.shape[0], 1), 0)))
    M.ridges = np.array(range(1, len(M.edges)+1)).reshape((len(M.edges), 1))

    M._AbstractMesh__updateNumbers()
    M._AbstractMesh__updateBoundaries()
    display("Generated cubic mesh in "+toc()+".", 1, debug)
    return M


def trunc3DMesh(M: Mesh3D, region: int, return_new2old=False) -> Mesh3D:
    """Trunc a 2D Mesh according to a region.

    INPUT
    -----

    M      : Input 3D mesh

    region : integer of the interior tetrahedron label to keep

    return_new2old : if set to True, then will return the new2old
                    numerotation as a second output variable

    OUTPUT
    ------

    newM    : truncated 3D mesh
    new2old : (only if return_new2old == True) 
              dictionary with newM.ntet entries such that 
              for each vertex i in newM, new2old[i] is the index of the same 
              vertex in M 
    tetra    : (only if return_new2old == True) 
                return the new2old array mapping new tetras to old tetras
    """
    newM = Mesh3D(debug=M.debug)
    display(f"Truncating mesh from region {region}", 1, M.debug, "orange_4a")
    tic()
    tetra = np.where(M.tetrahedra[:, -1] == region)[0]

    # new vertices numerotation
    old = np.unique(M.tetrahedra[tetra][:, :-1].flatten())
    new = range(1, len(old)+1)
    old2new = dict(zip(old, new))
    #new2old = dict(zip(new, old))
    new2old = old
    changeNum = np.vectorize(old2new.__getitem__)

    # new vertices
    newM.vertices = M.vertices[old-1]
    display(f"Added {len(old)} vertices.", 5, M.debug, "green")

    # new tetrahedra
    newM.tetrahedra = M.tetrahedra[tetra]
    newM.tetrahedra = np.column_stack((changeNum(newM.tetrahedra[:, :-1]),
                                       newM.tetrahedra[:, -1]))
    display(f"Added {len(newM.tetrahedra)} tetrahedra", 5, M.debug, "green")

    # new triangles
    triToTetra = M.verticesToTriangles.T @ M.verticesToTetra    
    indices = np.where(triToTetra.data!=3)[0]
    triToTetra.data[indices] = 0
    triToTetra.eliminate_zeros()
    I, J = triToTetra.nonzero()     
    tetr = np.where(M.tetrahedra[J][:,-1]==region)[0]

    #triangles_in = np.all(np.isin(M.triangles[:, :-1], old), 1)
    triangles_in = I[tetr]
    if np.any(triangles_in):
        newM.triangles = M.triangles[triangles_in]
        newM.triangles = np.column_stack((changeNum(newM.triangles[:, :-1]),
                                          newM.triangles[:, -1]))
        display(f"Added {len(newM.triangles)} triangles", 5, M.debug, "green")

    # new edges
    if M.ne:
        edges_in = np.all(np.isin(M.edges[:, :-1], old), 1)
        if np.any(edges_in):
            newM.edges = M.edges[edges_in]
            newM.edges = np.column_stack((changeNum(newM.edges[:, :-1]),
                                          newM.edges[:, -1]))
            display(f"Added {len(newM.edges)} edges", 2, M.debug, "green")
            oldEdges = np.where(edges_in)[0]+1
            old2newEdges = dict(zip(oldEdges, range(1, len(oldEdges)+1)))
            changeNumEdges = np.vectorize(old2newEdges.__getitem__)

        # new ridges & requiredEdges
        if M.nri and np.any(edges_in):
            ridges_in = np.isin(M.ridges, oldEdges)
            if np.any(ridges_in):
                newM.ridges = changeNumEdges(M.ridges[ridges_in]).reshape((-1, 1))
                display(f"Added {len(newM.ridges)} ridges", 5, M.debug, "green")
        if M.nre:
            requiredEdges_in = np.isin(M.requiredEdges, oldEdges)
            if np.any(requiredEdges_in):
                newM.requiredEdges = \
                    changeNumEdges(M.requiredEdges[requiredEdges_in])
                display(f"Added {len(newM.requiredEdges)} requiredEdges", 5,
                        M.debug, "green")

    def addField(n, title):
        if n:
            field_in = np.isin(getattr(M, title)[:, 0], old)
            if np.any(field_in):
                setattr(newM, title,
                        changeNum(getattr(M, title)[field_in, 0]).reshape((-1, 1)))
                display(
                    f"Added {len(getattr(newM,title))} {title}", 5, M.debug, "green")
            return field_in

    addField(M.nc, 'corners')
    addField(M.nr, 'requiredVertices')
    verticesNormals = addField(M.iv, 'normalAtVertices')
    if np.any(verticesNormals):
        newM.normalAtVertices = \
            np.column_stack((newM.normalAtVertices,
                             range(1, len(newM.normalAtVertices)+1)))
        newM.normals = M.normals[verticesNormals]
        display(f"Added {len(newM.normals)} normals",
                5, M.debug, "green")

    verticesTangents = addField(M.tv, 'tangentAtVertices')
    if np.any(verticesTangents):
        newM.tangentAtVertices = \
            np.column_stack((newM.tangentAtVertices,
                             range(1, len(newM.tangentAtVertices)+1)))
        newM.tangents = M.tangents[verticesTangents]
        display(f"Added {len(newM.tangents)} tangents",
                5, M.debug, "green")

    newM._AbstractMesh__updateNumbers()
    newM._AbstractMesh__updateBoundaries()
    display("Truncated mesh in "+toc()+".", 1, M.debug, "orange_4a")

    if return_new2old:
        return newM, new2old, tetra
    else:
        return newM


def det3d(a11, a12, a13,
          a21, a22, a23,
          a31, a32, a33):
    """3D determinant for shape Gradients"""
    return a11*(a22*a33-a32*a23)-a21*(a12*a33-a32*a13)+a31*(a12*a23-a22*a13)


def shapeGradients3D(M: Mesh3D):
    """
    Compute the gradients of the shape functions of each tetrahedra.

    Output:
         (gradLambdaA, gradLambdaB, gradLambdaC, gradLambdaD)

    where gradLambdaA is a ntet x 3 matrix such that 
    gradLambdaA[i,:] is the shape gradient of the function phiI satisfying
    phiI(A) = 1
    phiI(B) = phi(C) = phi(D) 0 
    where  [A, B, C, D] are the vertices of the tetra M.tetrahedra[i,:-1]

    and similarly for  gradLambdaB, gradLambdaC, gradLambdaD

    2       
    |\ `
    | \  `3
    |  \ '  
    0___\ 1
    """
    tic(2)
    vertices0 = M.vertices[M.tetrahedra[:, 0]-1]
    vertices1 = M.vertices[M.tetrahedra[:, 1]-1]
    vertices2 = M.vertices[M.tetrahedra[:, 2]-1]
    vertices3 = M.vertices[M.tetrahedra[:, 3]-1]
    xA = vertices0[:, 0]
    xB = vertices1[:, 0]
    xC = vertices2[:, 0]
    xD = vertices3[:, 0]
    yA = vertices0[:, 1]
    yB = vertices1[:, 1]
    yC = vertices2[:, 1]
    yD = vertices3[:, 1]
    zA = vertices0[:, 2]
    zB = vertices1[:, 2]
    zC = vertices2[:, 2]
    zD = vertices3[:, 2]
    jacobian = det3d(xB-xA, yB-yA, zB-zA,
                     xC-xA, yC-yA, zC-zA,
                     xD-xA, yD-yA, zD-zA)
    gradLambdaAx = det3d(-1, yB-yA, zB-zA,
                         -1, yC-yA, zC-zA,
                         -1, yD-yA, zD-zA)/jacobian
    gradLambdaAy = det3d(xB-xA, -1, zB-zA,
                         xC-xA, -1, zC-zA,
                         xD-xA, -1, zD-zA)/jacobian
    gradLambdaAz = det3d(xB-xA, yB-yA, -1,
                         xC-xA, yC-yA, -1,
                         xD-xA, yD-yA, -1)/jacobian
    gradLambdaBx = -det3d(-1, yA-yB, zA-zB,
                          -1, yC-yB, zC-zB,
                          -1, yD-yB, zD-zB)/jacobian
    gradLambdaBy = -det3d(xA-xB, -1, zA-zB,
                          xC-xB, -1, zC-zB,
                          xD-xB, -1, zD-zB)/jacobian
    gradLambdaBz = -det3d(xA-xB, yA-yB, -1,
                          xC-xB, yC-yB, -1,
                          xD-xB, yD-yB, -1)/jacobian
    gradLambdaCx = det3d(-1, yA-yC, zA-zC,
                         -1, yB-yC, zB-zC,
                         -1, yD-yC, zD-zC)/jacobian
    gradLambdaCy = det3d(xA-xC, -1, zA-zC,
                         xB-xC, -1, zB-zC,
                         xD-xC, -1, zD-zC)/jacobian
    gradLambdaCz = det3d(xA-xC, yA-yC, -1,
                         xB-xC, yB-yC, -1,
                         xD-xC, yD-yC, -1)/jacobian
    gradLambdaA = np.column_stack((gradLambdaAx, gradLambdaAy, gradLambdaAz))
    gradLambdaB = np.column_stack((gradLambdaBx, gradLambdaBy, gradLambdaBz))
    gradLambdaC = np.column_stack((gradLambdaCx, gradLambdaCy, gradLambdaCz))
    gradLambdaD = -gradLambdaA-gradLambdaB-gradLambdaC
    display("Computed shape gradients in "+toc(2)+".", 2, M.debug, "green")
    return (gradLambdaA, gradLambdaB, gradLambdaC, gradLambdaD)


def connectedComponents3D(M: Mesh3D):
    """ Compute the connected components of the mesh according to 
    their label : two tetrahedra are connected if they
    are connected by a face and if their labels are equal

    Output : a np.array of length M.ntet
    containing the reference label of each tetrahedra"""
    tetraToTetra = M.tetrahedronToTetrahedron
    tic(1)
    I, J = tetraToTetra.nonzero()
    toKeep = np.where(M.tetrahedra[I, -1] == M.tetrahedra[J, -1])[0]
    graph = sp.csr_matrix(([1]*len(toKeep), (I[toKeep], J[toKeep])))
    n_components, labels = \
        sp.csgraph.connected_components(csgraph=graph,
                                        directed=False, return_labels=True)

    display("Computed connected components in "+toc(1)+".", 2, M.debug,
            "green")
    return labels


def getInfosTetra(M: Mesh3D, ntet):
    """Print some connectivity information about the tetrahedra number ntet"""
    print("TETRAHEDRA ", ntet)
    print("Jacobian : ", M.jacobians[ntet])
    print("Vertices : ")
    label = M.tetrahedra[ntet][-1]
    pts = M.tetrahedra[ntet][:-1]
    for pt in pts:
        print("Point ", pt, " : ", M.vertex(pt))
    tris = [frozenset({pts[0], pts[1], pts[2]}),
            frozenset({pts[1], pts[2], pts[3]}),
            frozenset({pts[2], pts[3], pts[0]}),
            frozenset({pts[3], pts[0], pts[1]})]
    for tri in tris:
        if tri in M.triangleNums:
            print("Boundary triangle ",
                  M.triangleNums[tri], "=", M.triangles[M.triangleNums[tri]])
    neighbors = M.elemToTetra(list(tri))
    for nb in neighbors:
        print("Adjacent tetra ", nb, " : label ", M.tetrahedra[nb][-1])


def integrateP0P1Matrix3D(M: Mesh3D) -> sp.csc_matrix:
    """Returns the sparse matrix A such that
    v^T * A * u = int_M uv dx
    for u : P0Function3D
        v : P1Function3D"
    """
    if not hasattr(M, '_Mesh3D__integrateP0P1Matrix'):
        tic(10)
        jacobian = M.jacobians
        tetrahedra = M.tetrahedra
        integrateP0P1 = sp.csc_matrix((M.nv, M.ntet))
        # Trick for fast matrix assembly:
        # sp.csc_matrix(K,(I,J)) does
        # for (i,j) in zip(I,J):
        #   M(i,j)<-M(i,j)+K(i,j)
        for i in range(4):
            I = tetrahedra[:, i]-1
            J = range(M.ntet)
            K = jacobian/8
            integrateP0P1 += sp.csc_matrix((K, (I, J)), (M.nv, M.ntet))
        display(
            f"Assembled P0 to P1 matrix in {toc(10)}.", 2, M.debug, "green")
        M._Mesh3D__integrateP0P1Matrix = integrateP0P1
    return M._Mesh3D__integrateP0P1Matrix


def integrateP1P1Matrix3D(M: Mesh3D) -> sp.csc_matrix:
    """Returns the sparse matrix A such that
    v^T * A * u = int_M uv dx
    for u : P1Function3D
        v : P1Function3D"
    """
    if not hasattr(M, '_Mesh3D__integrateP0P1Matrix'):
        tic(10)
    jacobian = M.jacobians
    tetrahedra = M.tetrahedra
    I = []
    J = []
    K = []
    E = [[1/20, 1/40, 1/40, 1/40],
         [1/40, 1/20, 1/40, 1/40],
         [1/40, 1/40, 1/20, 1/40],
         [1/40, 1/40, 1/40, 1/20]]
    integrateP1P1 = sp.csc_matrix((K, (I, J)), (M.nv, M.nv))
    for i in range(4):
        for j in range(4):
            I = tetrahedra[:, i]-1
            J = tetrahedra[:, j]-1
            K = E[i][j]*jacobian
            integrateP1P1 += sp.csc_matrix((K, (I, J)), (M.nv, M.nv))
    display(f"Assembled P0 to P1 matrix in {toc(10)}.", 2, M.debug, "green")
    M._Mesh3D__integrateP1P1Matrix = integrateP1P1
    return M._Mesh3D__integrateP1P1Matrix


def meshCenters3D(M: Mesh3D):
    return (M.vertices[M.tetrahedra[:, 0]-1, :-1]
            + M.vertices[M.tetrahedra[:, 1]-1, :-1]
            + M.vertices[M.tetrahedra[:, 2]-1, :-1]
            + M.vertices[M.tetrahedra[:, 3]-1, :-1])/4
