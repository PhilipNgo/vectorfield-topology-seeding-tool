from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
) 

from vtk import vtkSimplePointsWriter, vtkPoints, vtkTransform, vtkDiskSource, vtkTransformPolyDataFilter, vtkArrowSource
import numpy as np
from seedpoint_generator_helper import constants
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy

def write_seed_points_to_file(outfile, glyph):
    """Writes the glyph data into a file
        :outfile: Name of the file you want to write the file to (String)
        :glyph: Glyph containing the array data you want to save (vtkGlyph3D())
    """

    # # Write x,y,z coordinates of critical points
    writer = vtkSimplePointsWriter()
    writer.SetDecimalPrecision(5)
    writer.SetFileName(outfile)
    writer.SetInputConnection(glyph.GetOutputPort(0))
    writer.Write()

    print(f"Generated {glyph.GetOutput().GetPointData().GetNumberOfTuples()} seed points in file: '{outfile}'")

def get_sphere_around_points_actor(critical_points) -> vtkActor:
    """Returns the actor of the sphere surrounding a point. Returns glyph data if wanted.
        :points: Points where the normal vector lies (vtkPoint())
        :plane_vectors: List of eigen vectors building up the plane ([[v1,w1],..,[vn,wn]])
    """
    colors = vtkNamedColors()

    points = vtkPoints()
    for x,y,z in critical_points:
        points.InsertNextPoint(x, y, z)
    
    polydata = vtkPolyData()
    polydata.SetPoints(points)

    sphereSource = vtkSphereSource()
    sphereSource.SetThetaResolution(constants.THETA_RESOLUTION)
    sphereSource.SetPhiResolution(constants.PHI_RESOLUTION)
    sphereSource.SetRadius(constants.RADIUS)

    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(sphereSource.GetOutputPort())
    glyph3D.SetInputData(polydata)
    glyph3D.Update()

    # Visualize seed points
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Salmon'))
    actor.GetProperty().SetOpacity(0.5)
    actor.GetProperty().SetRepresentationToWireframe()
    
    return actor

def get_disc_actor(normal, point):
    colors = vtkNamedColors()

    # Default is (0,0,1)
    diskSource = vtkDiskSource()
    diskSource.SetInnerRadius(0.01)
    diskSource.SetOuterRadius(0.5)
    diskSource.SetRadialResolution(2)
    diskSource.SetCircumferentialResolution(12)

    matrix = rotation_matrix_from_vectors([0,0,1], normal)

    # Transformer
    transform = vtkTransform()
    transform.PreMultiply()
    transform.SetMatrix(matrix.real.flatten())
    transform.PostMultiply()
    # transform.RotateX(20)
    transform.Translate(point[0], point[1], point[2])
    transform.Update()

    transformFilter = vtkTransformPolyDataFilter()
    transformFilter.SetTransform(transform)
    transformFilter.SetInputConnection(diskSource.GetOutputPort())
    transformFilter.Update()

    # Create a mapper and actor.
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(transformFilter.GetOutputPort())

    actor = vtkActor()
    actor.GetProperty().SetColor(colors.GetColor3d("Black"))
    actor.GetProperty().SetOpacity(0.5)
    actor.SetMapper(mapper)

    return actor, transformFilter.GetOutput()

def get_plane_normal_actor(points, planes):
    """Returns the actor of the normal of the given planes
        :points: Points where the normal vector lies (vtkPoint())
        :planes: List of plane objects [{"point": [x1,y1,z1], "normal": [x2,y2,z2]}]
    """

    colors = vtkNamedColors()

    plane_normal_polydata = vtkPolyData()
    plane_normal_polydata.SetPoints(points)

    # Generate normal vectors to see how it is pointed
    arrayOfNormals = np.array([np.array(p['normal']).real for p in planes])
    plane_normal_polydata.GetPointData().SetNormals(numpy_to_vtk(arrayOfNormals))

    # Create a plane
    normalArrowSource = vtkArrowSource()
    normalArrowSource.Update()

    # Create 3d glyph to map the plane with pointdata
    normalGlyph = vtkGlyph3D()
    normalGlyph.SetInputData(plane_normal_polydata)
    normalGlyph.SetSourceConnection(normalArrowSource.GetOutputPort())
    normalGlyph.SetVectorModeToUseNormal()
    normalGlyph.SetScaleFactor(1)
    normalGlyph.Update()

    # Create a mapper and actor
    normalMapper = vtkPolyDataMapper()
    normalMapper.SetInputData(normalGlyph.GetOutput())

    normalActor = vtkActor()
    normalActor.SetMapper(normalMapper)
    normalActor.GetProperty().SetColor(colors.GetColor3d('Yellow'))
    normalActor.GetProperty().SetOpacity(1)
    # normalActor.GetProperty().SetRepresentationToWireframe()

    return normalActor

def get_points_actor(points):

    colors = vtkNamedColors()

    polydata = vtkPolyData()
    polydata.SetPoints(points)

    sphereSource = vtkSphereSource()
    sphereSource.SetThetaResolution(10)
    sphereSource.SetPhiResolution(10)
    sphereSource.SetRadius(0.1)

    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(sphereSource.GetOutputPort())
    glyph3D.SetInputData(polydata)
    glyph3D.Update()

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.GetProperty().SetColor(colors.GetColor3d("Black"))
    actor.GetProperty().SetOpacity(1)
    actor.SetMapper(mapper)

    return actor

def rotation_matrix_from_vectors(vec1, vec2):
    """ Find the rotation matrix that aligns vec1 to vec2
    :param vec1: A 3d "source" vector
    :param vec2: A 3d "destination" vector
    :return mat: A transform matrix (4x4) which when applied to vec1, aligns it with vec2.
    """

    vec1 = np.array(vec1).real
    vec2 = np.array(vec2).real

    a, b = (vec1 / np.linalg.norm(vec1)).reshape(3), (vec2 / np.linalg.norm(vec2)).reshape(3)
    v = np.cross(a, b)
    c = np.dot(a, b)
    s = np.linalg.norm(v)
    kmat = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    rotation_matrix = np.eye(3) + kmat + kmat.dot(kmat) * ((1 - c) / (s ** 2))
    rotation_matrix = np.c_[rotation_matrix, np.zeros(3)] # Add zeros column
    rotation_matrix = np.r_[rotation_matrix, [[0,0,0,1]]] # Add zeros column

    return rotation_matrix

