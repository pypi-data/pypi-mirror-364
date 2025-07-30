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
# For further information, see <http://www.gnu.org/licenses/>.
import numpy as np
import scipy.sparse as sp
import scipy.linalg as lg
from .abstract import display, __AbstractMesh, tic, toc


class Mesh(__AbstractMesh):
    def __init__(self, meshFile=None, debug=0):
        """Load a 2D triangle mesh in the INRIA mesh file format.

        INPUT:
            meshFile  :  the path of the mesh to read. Supported format: 
                         .mesh and .meshb. If meshFile=None, the instantiates
                         an empty 2D mesh.
            debug     :  an integer tuning the level of verbosity."""
        super().__init__(meshFile, debug)
        if self.Dimension is None:
            self.Dimension = 2
        if self.Dimension != 2:
            raise Exception("Error: the mesh "+meshFile+" is not of dimension"
                            " 2.")

    @property
    def x(self):
        """
        Returns x coordinate of all vertices.
        """
        return self.vertices[:,0]

    @property
    def y(self):
        """
        Returns y coordinate of all vertices.
        """
        return self.vertices[:,1]

    @property
    def jacobians(self) -> np.ndarray:
        """
        Returns 2 times the area of each triangle, that is 
        | x_B-x_A  x_C-xA  |
        |                  |
        | y_B-y_A  y_C-y_A |

        """
        if not hasattr(self, '_Mesh__jacobian'):
            vertices0 = self.vertices[self.triangles[:, 0]-1]
            vertices1 = self.vertices[self.triangles[:, 1]-1]
            vertices2 = self.vertices[self.triangles[:, 2]-1]
            xA = vertices0[:, 0]
            xB = vertices1[:, 0]
            xC = vertices2[:, 0]
            yA = vertices0[:, 1]
            yB = vertices1[:, 1]
            yC = vertices2[:, 1]
            self.__jacobian = (xB-xA)*(yC-yA)-(yB-yA)*(xC-xA)
        return self.__jacobian

    def plot(self, colormap=None, XLIM=None, YLIM=None, doNotPlot=False,
             edgeColor='gray', axis='off',
             boundary=None, boundary_linewidth=2, triangles_linewidth=0.3,
             title=None,
             nodeIndices=False, bcEdgeIndices=False, triIndices=False,
             nodeLabels=False, bcEdgeLabels=False, triLabels=False,
             boundaryColor='b',
             fig=None, ax=None, **kwargs):
        """Plot a 2D mesh with the matplotlib library."""
        import matplotlib as mp
        import matplotlib.pyplot as plt
        if not fig:
            fig, ax = plt.subplots()
        if kwargs.get('plotMesh', True):
            x, y = self.vertices[:, 0], self.vertices[:, 1]
            tris = self.triangles[:, :-1]-1
            colors = np.zeros_like(self.triangles[:, -1])
            colors[np.where(self.triangles[:, -1] == 3)] = 1
            if colormap == 'bw':
                colormap = [[0, 0, 0], [1, 1, 1]]
                edgeColor = 'face'
            elif colormap == 'dim':
                colormap = [[0.9, 0.9, 1], [1, 1, 0.9]]
            elif colormap is None:
                colormap = np.array([[0.5, 1, 0.5], [1, 1, 0.5]])
            cmap = mp.colors.ListedColormap(colormap)
            ax.tripcolor(x, y, tris, facecolors=colors, edgecolors=edgeColor,
                         cmap=cmap,
                         linewidth=triangles_linewidth, antialiased=True,
                         **kwargs)
        lines = []
        if boundary:
            if boundary == 'all':
                boundary = self.Boundaries.keys()
                width = max(np.max(self.vertices[:,0])-np.min(self.vertices[:,0]),
                            np.max(self.vertices[:,1])-np.min(self.vertices[:,1]))
            for i, bc in enumerate(boundary):
                edges = self.edges[np.where(self.edges[:, -1] == bc)[0]]
                X = self.vertices[edges[:, 0]-1][:, :-1]
                Y = self.vertices[edges[:, 1]-1][:, :-1]
                midpoints = 0.5*(X+Y)
                center = np.mean(midpoints, axis=0)
                # Compute distances from each midpoint to center
                dists = np.linalg.norm(midpoints - center, axis=1)
                
                # Find index of the closest edge
                idx_closest = np.argmin(dists)
                closest_midpoint = midpoints[idx_closest]

                #Compute outward normal
                tri = self.elemToTri(edges[idx_closest,:-1])[0]
                edge = edges[idx_closest,:]
                A = self.vertices[edge[0]-1]
                B = self.vertices[edge[1]-1]
                idxC = np.setdiff1d(self.triangles[tri][:-1],edge[:-1])[0]
                C = self.vertices[idxC-1]
                edge_vec = B-A 
                normal = np.array([edge_vec[1],-edge_vec[0]])
                normal = normal / np.linalg.norm(normal)
                normal = -np.sign(np.dot(C[:-1]-A[:-1],normal))*normal

                lines = [[tuple(x), tuple(y)]
                         for (x, y) in zip(X.tolist(), Y.tolist())]
                color = mp.cm.Dark2(i)
                lc = mp.collections.LineCollection(
                    lines, linewidths=boundary_linewidth, colors=color,
                    zorder=100)
                ax.add_collection(lc)
                # Add annotation
                ax.text(closest_midpoint[0]+normal[0]*0.04*width, closest_midpoint[1]+normal[1]*0.04*width, str(bc),

                        color=color, fontsize=12, weight='bold',
                        ha='center', va='center', zorder=101)
        ax.set_aspect('equal')
        if axis == 'off':
            ax.tick_params(axis='both', which='both', length=0)
            plt.setp(ax.get_xticklabels(), visible=False)
            plt.setp(ax.get_yticklabels(), visible=False)
            ax.axis('off')
        ax.margins(0.01)

        if nodeIndices:
            for (i, pt) in enumerate(self.vertices.tolist()):
                ax.annotate(str(i+1), (pt[0], pt[1]), color='k')
        if triIndices:
            for (i, tri) in enumerate(self.triangles.tolist()):
                center = (self.vertex(tri[0])+self.vertex(tri[1])
                          + self.vertex(tri[2]))/3
                ax.annotate(str(i), (center[0], center[1]), color='b')
        if bcEdgeIndices:
            for (i, e) in enumerate(self.edges.tolist()):
                center = (self.vertex(e[0])+self.vertex(e[1]))/2
                ax.annotate(str(i), (center[0], center[1]), color='r')
        if nodeLabels:
            for (i, pt) in enumerate(self.vertices.tolist()):
                ax.annotate(str(pt[-1]), (pt[0], pt[1]), color='k')
        if triLabels:
            for (i, tri) in enumerate(self.triangles.tolist()):
                center = (self.vertex(tri[0])+self.vertex(tri[1])
                          + self.vertex(tri[2]))/3
                ax.annotate(str(tri[-1]), (center[0], center[1]), color='b')
        if bcEdgeLabels:
            for (i, e) in enumerate(self.edges.tolist()):
                center = (self.vertex(e[0])+self.vertex(e[1]))/2
                ax.annotate(e[-1], (center[0], center[1]), color='r')

        if not XLIM is None:
            ax.set_xlim(XLIM)
        if not YLIM is None:
            ax.set_ylim(YLIM)
        if title:
            plt.title(title)
        if not doNotPlot:
            plt.show()
        return fig, ax


def square(nx: int, ny: int, transfo=None, debug=0) -> Mesh:
    """Returns a 2D square triangle mesh.

    INPUT:
        nx, ny     :number of mesh elements along each axis

        transfo    : a transformation [funx,funy,funz] to apply on the vertices
                     (X,Y,Z) <- (funx(X,Y,Z),funy(X,Y,Z),funz(X,Y,Z))

        debug      : an integer assigning a level of verbosity
    """
    M = Mesh(None, debug)
    tic()
    # Create vertices and their numerotation
    x = np.linspace(0, 1, nx+1)
    y = np.linspace(0, 1, ny+1)
    X, Y = np.meshgrid(x, y, indexing='ij')
    if transfo:
        if isinstance(transfo, list):
            X, Y = transfo[0](X, Y), transfo[1](X, Y)
        else:
            X, Y = transfo(X,Y)
    M.nv = (nx+1)*(ny+1)
    M.vertices = np.zeros((M.nv, 3))
    M.vertices[:, 0] = X.flatten()
    M.vertices[:, 1] = Y.flatten()
    numerotation = np.array(range(M.nv)).reshape((nx+1, ny+1))+1

    # Create all the triangles
    x1 = numerotation[:-1, :-1].flatten()
    x2 = numerotation[1:, :-1].flatten()
    x3 = numerotation[:-1, 1:].flatten()
    x4 = numerotation[1:, 1:].flatten()

    label = np.zeros_like(x1)

    tri1 = np.column_stack((x1, x2, x4, label))
    tri2 = np.column_stack((x1, x4, x3, label))

    M.triangles = np.row_stack((tri1, tri2))

    # Create all the boundary edges
    x1left = numerotation[0, :-1].flatten()
    x3left = numerotation[0, 1:].flatten()
    x1bottom = numerotation[:-1, 0].flatten()
    x2bottom = numerotation[1:, 0].flatten()
    x2right = numerotation[-1, :-1].flatten()
    x4right = numerotation[-1, 1:].flatten()
    x4top = numerotation[1:, -1].flatten()
    x3top = numerotation[:-1, -1].flatten()

    labelLeft = np.full((len(x1left),), 4)
    labelRight = np.full((len(x2right),), 2)
    labelBottom = np.full((len(x1bottom),), 1)
    labelTop = np.full((len(x3top),), 3)

    edgesLeft = np.column_stack((x1left, x3left, labelLeft))
    edgesTop = np.column_stack((x3top, x4top, labelTop))
    edgesRight = np.column_stack((x4right, x2right, labelRight))
    edgesBottom = np.column_stack((x1bottom, x2bottom, labelBottom))
    M.edges = np.row_stack((edgesLeft, edgesTop, edgesRight, edgesBottom))

    # Corners
    corners = [numerotation[x, y] for x in [0, -1] for y in [0, -1]]
    M.corners = np.asarray(corners).reshape((len(corners), 1))
    M.requiredVertices = M.corners

    M._AbstractMesh__updateNumbers()
    M._AbstractMesh__updateBoundaries()
    display("Generated square mesh in "+toc()+".", 2, debug)
    return M


def shapeGradients(M: Mesh) -> np.ndarray:
    """
    Compute the gradients of the shape functions of each triangle.

    Output:
         (gradLambdaA, gradLambdaB, gradLambdaC)

    where gradLambdaA is a ntri x 2 matrix such that 
    gradLambdaA[i,:] is the shape gradient of the function phiI satisfying
    phiI(A) = 1
    phiI(B) = phi(C)  0 
    where  [A, B, C] are the vertices of the triangle M.triangle[i,:-1]

    and similarly for  gradLambdaB, gradLambdaC 

    2
    |`
    |  `
    |_____1
    0
    """
    #lambda1=lambda x : 1-x[0]-x[1]
    #lambda2=lambda x : x[0]
    #lambda3=lambda x : x[1]
    # gradLambda=np.asarray([[-1,1,0],
    #                       [-1,0,1]])
    if not hasattr(M, '_Mesh__shapeGradients'):
        vertices0 = M.vertices[M.triangles[:, 0]-1]
        vertices1 = M.vertices[M.triangles[:, 1]-1]
        vertices2 = M.vertices[M.triangles[:, 2]-1]
        xA = vertices0[:, 0]
        xB = vertices1[:, 0]
        xC = vertices2[:, 0]
        yA = vertices0[:, 1]
        yB = vertices1[:, 1]
        yC = vertices2[:, 1]
        jacobian = (xB-xA)*(yC-yA)-(yB-yA)*(xC-xA)
        gradLambdaA = (np.column_stack((yB-yC, xC-xB)).T/jacobian).T
        gradLambdaB = (np.column_stack((yC-yA, xA-xC)).T/jacobian).T
        gradLambdaC = (np.column_stack((yA-yB, xB-xA)).T/jacobian).T
        M._Mesh__shapeGradients = (gradLambdaA, gradLambdaB, gradLambdaC)
    return M._Mesh__shapeGradients


def connectedComponents(M: Mesh) -> np.ndarray:
    """ Compute the connected components of the 2D mesh according to 
    their label : two triangles are connected if they
    are connected by an edge and if their labels are equal

    Output : a np.array of length M.nt
    containing the reference of each triangle"""
    trisToTris = M.trianglesToTriangles
    tic(1)
    I, J = trisToTris.nonzero()
    toKeep = np.where(M.triangles[I, -1] == M.triangles[J, -1])[0]
    graph = sp.csr_matrix(([1]*len(toKeep), (I[toKeep], J[toKeep])))
    n_components, labels = \
        sp.csgraph.connected_components(csgraph=graph,
                                        directed=False, return_labels=True)

    display("Computed connected components in "+toc(1)+".", 2, M.debug,
            "green")
    return labels


def trunc(M: Mesh, region, return_new2old=False) -> Mesh:
    """Trunc a 2D Mesh according to a region.

    INPUT
    -----

    M      : Input 2D mesh

    region : integer of the interior triangles label to keep

    return_new2old : if set to True, then will return the new2old
                    numerotation as a second output variable

    OUTPUT
    ------

    newM    : truncated 2D mesh
    new2old : (only if return_new2old == True) 
              dictionary with newM.nt entries such that 
              for each vertex i in newM, new2old[i] is the index of the same 
              vertex in M 
    """
    newM = Mesh(debug=M.debug)
    display(f"Truncating mesh from region {region}", 1, M.debug, "orange_4a")
    tic()
    tris = np.where(M.triangles[:, -1] == region)[0]

    # new vertices numerotation
    old = np.unique(M.triangles[tris][:, :-1].flatten())
    new = range(1, len(old)+1)
    old2new = dict(zip(old, new))
    new2old = old #dict(zip(new, old))
    changeNum = np.vectorize(old2new.__getitem__)

    # new vertices
    newM.vertices = M.vertices[old-1]
    display(f"Added {len(old)} vertices.", 2, M.debug, "green")

    # new triangles
    newM.triangles = M.triangles[tris]
    newM.triangles = np.column_stack((changeNum(newM.triangles[:, :-1]),
                                      newM.triangles[:, -1]))
    display(f"Added {len(newM.triangles)} triangles", 2, M.debug, "green")

    # new edges
    edges_in = np.all(np.isin(M.edges[:, :-1], old), 1)
    if np.any(edges_in):
        newM.edges = M.edges[edges_in]
        newM.edges = np.column_stack((changeNum(newM.edges[:, :-1]),
                                      newM.edges[:, -1]))
        display(f"Added {len(newM.edges)} edges", 2, M.debug, "green")
        oldEdges = np.where(edges_in)[0]+1
        old2newEdges = dict(zip(oldEdges, range(1, len(oldEdges)+1)))
        changeNumEdges = np.vectorize(old2newEdges.__getitem__)

    # new requiredEdges
    if M.nre and np.any(edges_in):
        requiredEdges_in = np.isin(M.requiredEdges, oldEdges)
        if np.any(requiredEdges_in):
            newM.requiredEdges = \
                changeNumEdges(M.requiredEdges[requiredEdges_in])
            display(f"Added {len(newM.requiredEdges)} requiredEdges", 2,
                    M.debug, "green")

    def addField(n, title):
        if n:
            field_in = np.isin(getattr(M, title)[:, 0], old)
            if np.any(field_in):
                setattr(newM, title,
                        changeNum(getattr(M, title)[field_in, 0]).reshape((-1, 1)))
                display(
                    f"Added {len(getattr(newM,title))} {title}", 2,
                    M.debug, "green")
            return field_in
        else:
            return None

    addField(M.nc, 'corners')
    addField(M.nr, 'requiredVertices')

    newM._AbstractMesh__updateNumbers()
    newM._AbstractMesh__updateBoundaries()
    display("Truncated mesh in "+toc()+".", 2, M.debug, "orange_4a")

    if return_new2old:
        return newM, new2old
    else:
        return newM


def chainBc(M: Mesh, bcIndex=10, startIndex=None):
    """Returns a list of connected vertices by boundary edges
    obtained by moving from edges along edges on a 2D mesh boundary.

    INPUT:
    ------

    M : 2D Mesh

    bcIndex : label of the boundary

    startIndex : index of the first vertex of the chain. If None, then 
                 the chain starts with M.Boundaries[bcIndex][0]

    OUTPUT: 
    -------

    The list of vertices obtained by travelling around the edges of the 
    boundary starting from startIndex"""
    if not startIndex:
        startIndex = M.edge(M.Boundaries[bcIndex][0])[0]-1
    verticesToEdges = M.verticesToEdges
    verticesToVertices = verticesToEdges.dot(verticesToEdges.T)
    # Find vertices couples of connected to only 1 edge
    I, J, K = sp.find(verticesToVertices == 1)
    graph = sp.csr_matrix((K, (I, J)))
    chain = sp.csgraph.depth_first_order(graph, startIndex,
                                         return_predecessors=False)+1
    return chain


def metric(M: Mesh, computeEigenvalues=True):
    """Evaluate the metric tensor of a 2D mesh M.
    INPUT
    ----- 

    M: 2D Mesh

    computeEigenvalues: if set to true, then the eigenvalues of the metric 
                        are returned 

    OUTPUT
    ------

    metric: a (M.nv,3) array with the value of the metric components 
             (m_xx,m_yy,m_xy) at each vertex

    eigenvalues: (if computeEigenvalues==True) a (M.nv x 2) array with the
                 eigenvalues of the metric at each vertex
    """
    A = M.vertices[M.triangles[:, 0]-1, :-1]
    B = M.vertices[M.triangles[:, 1]-1, :-1]
    C = M.vertices[M.triangles[:, 2]-1, :-1]
    U = C-A
    V = B-A
    system = np.asarray([[U[:, 0]*U[:, 0], U[:, 1]*U[:, 1], 2*U[:, 0]*U[:, 1]],
                         [V[:, 0]*V[:, 0], V[:, 1]*V[:, 1], 2*V[:, 0]*V[:, 1]],
                         [U[:, 0]*V[:, 0], U[:, 1]*V[:, 1],
                          U[:, 0]*V[:, 1]+U[:, 1]*V[:, 0]]])
    system = system.reshape((9, M.nt))

    def solve(m):
        """solve
        """
        v = m.reshape((3, 3))
        sol = lg.solve(v, [1, 1, 0.5])
        return sol
    solutions = np.apply_along_axis(solve, 0, system)
    matrices = np.asarray([[solutions[0, :], solutions[2, :]],
                           [solutions[2, :], solutions[1, :]]])
    matrices = np.moveaxis(matrices, -1, 0)
    if computeEigenvalues:
        eigenvalues = np.linalg.eigvals(matrices)
        return (solutions, eigenvalues)
    else:
        return solutions


def meshCenters(M: Mesh):
    """
    Returns the coordinates of the center of each mesh triangle
    as a np.array of size (M.nt,2)
    """
    return (M.vertices[M.triangles[:, 0]-1, :-1]
            + M.vertices[M.triangles[:, 1]-1, :-1]
            + M.vertices[M.triangles[:, 2]-1, :-1])/3


def integrateP0P1Matrix(M: Mesh)->sp.csc_matrix:
    """Returns the sparse matrix A such that
    v^T * A * u = int_M uv dx
    for u : P0Function
        v : P1Function"
    """
    if not hasattr(M, '_Mesh__integrateP0P1Matrix'):
        tic(10)
        jacobian = M.jacobians
        triangles = M.triangles
        integrateP0P1 = sp.csc_matrix((M.nv, M.nt))
        # Trick for fast matrix assembly:
        # sp.csc_matrix(K,(I,J)) does
        # for (i,j) in zip(I,J):
        #   M(i,j)<-M(i,j)+K(i,j)
        for i in range(3):
            I = triangles[:, i]-1
            J = range(M.nt)
            K = jacobian/6
            integrateP0P1 += sp.csc_matrix((K, (I, J)), (M.nv, M.nt))
        display(
            f"Assembled P0 to P1 matrix in {toc(10)}.", 2, M.debug, "green")
        M._Mesh__integrateP0P1Matrix = integrateP0P1
    return M._Mesh__integrateP0P1Matrix


def integrateP1P1Matrix(M: Mesh)->sp.csc_matrix:
    """Returns the sparse matrix A such that
    v^T * A * u = int_M uv dx
    for u : P1Function
        v : P1Function"
    """
    if not hasattr(M, '_Mesh__integrateP1P1Matrix'):
        tic(10)
        jacobian = M.jacobians
        triangles = M.triangles
        I = []
        J = []
        K = []
        E = [[1/12, 1/24, 1/24],
             [1/24, 1/12, 1/24],
             [1/24, 1/24, 1/12]]
        integrateP1P1 = sp.csc_matrix((K, (I, J)), (M.nv, M.nv))
        for i in range(3):
            for j in range(3):
                I = triangles[:, i]-1
                J = triangles[:, j]-1
                K = E[i][j]*jacobian
                integrateP1P1 += sp.csc_matrix((K, (I, J)), (M.nv, M.nv))
        display(
            f"Assembled P1 to P1 matrix in {toc(10)}.", 2, M.debug, "green")
        M._Mesh__integrateP1P1Matrix = integrateP1P1
    return M._Mesh__integrateP1P1Matrix
