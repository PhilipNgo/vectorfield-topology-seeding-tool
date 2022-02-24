import os
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

import numpy as np
# from numpy import genfromtxt, cross, linalg as LA
from collections import Counter

from vtk import vtkSimplePointsWriter, vtkTransform, vtkPlaneSource, vtkTransformPolyDataFilter, vtkMaskPoints, vtkArrowSource
from vectorfieldtopology_helper import custom_axes 
from vtkmodules.util.numpy_support import numpy_to_vtk

def generate_seedpoints(infile, outfile, visualize=False):
    """Generate seedpoints with the help of critical points by sampling points around the critical points. 
        :infile: input file with critical points (String)
        :outfile: output file with critical points (String)
    """

    colors = vtkNamedColors()

    # Load data
    data = np.genfromtxt(infile,dtype=float,usecols=[0,1,2])

    # Create point cloud
    points = vtkPoints()
    for x,y,z in data:
        points.InsertNextPoint(x, y, z)

    # ============= Original critcial points position ==================
    cp_polydata = vtkPolyData()
    cp_polydata.SetPoints(points)

    pointSource = vtkSphereSource()
    pointSource.SetThetaResolution(10)
    pointSource.SetPhiResolution(10)
    pointSource.SetRadius(0.1)

    pGlyph3D = vtkGlyph3D()
    pGlyph3D.SetSourceConnection(pointSource.GetOutputPort())
    pGlyph3D.SetInputData(cp_polydata)
    pGlyph3D.Update()

    # Visualize
    pMapper = vtkPolyDataMapper()
    pMapper.SetInputConnection(pGlyph3D.GetOutputPort())

    pActor = vtkActor()
    pActor.SetMapper(pMapper)
    pActor.GetProperty().SetColor(colors.GetColor3d('Black'))


    # ======= Sphere with radius x from the critical point ========= #

    polydata = vtkPolyData()
    polydata.SetPoints(points)

    sphereSource = vtkSphereSource()
    sphereSource.SetThetaResolution(3)
    sphereSource.SetPhiResolution(3)
    sphereSource.SetRadius(1)

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

    # ================================================================ #

    if(visualize):
        
        # Add X,Y,Z helper axis
        transform = vtkTransform()
        transform.Translate(25.0, -10.0, 0.0)
        axes = custom_axes(transform)

        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        renderWindow.SetSize(1920,1080)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        renderer.AddActor(actor)
        renderer.AddActor(pActor)
        renderer.AddActor(axes)
        renderer.SetBackground(colors.GetColor3d('SlateGray'))  # Background Slate Gray
        
        renderWindow.SetWindowName('Sphere generation')
        renderWindow.Render()
        renderWindowInteractor.Start()

    # Write x,y,z coordinates of critical points
    writer = vtkSimplePointsWriter()
    writer.SetDecimalPrecision(5)
    writer.SetFileName(outfile)
    writer.SetInputConnection(glyph3D.GetOutputPort(0))
    writer.Write()

    print(f"Generated {glyph3D.GetOutput().GetPointData().GetNumberOfTuples()} seed points in file: '{outfile}'")


def generate_seedpoints_with_plane(infile, critical_point_infile, outfile, visualize=True, vectorfield=None):
    """Generate seedpoints with the help of critical points by generating a plane with eigenvectors and sampling on that plane. 
        :infile: input file with critical points (String)
        :outfile: output file with critical points (String)
        :visualize: to visualize the points or not (Boolean)
        :vectofield: Takes in a vectorfield. If vectorfield present, it will show in visualization (vtkArrayCalculator())
    """

    # Load data
    data = np.genfromtxt(infile,dtype=float)

    # Load data
    critical_points = np.genfromtxt(critical_point_infile,dtype=float)

    # Find eigenvectors
    plane_vectors = []
    list_of_eigenvectors = []

    for jacobian in data:
        
        eig_val, eig_vec = np.linalg.eig(jacobian.reshape(3,3))
        list_of_eigenvectors.append(eig_vec.tolist())

        # Checks what sign is most common, pos or neg.
        is_pos = Counter(eig_val > 0).most_common(1)[0][0]

        indices = [None,None]
        # Get which indices are of interest
        if(is_pos):
            indices = [i for i,v in enumerate(eig_val) if v > 0]
        else:
            indices = [i for i,v in enumerate(eig_val) if v <= 0]

        plane_vectors.append(eig_vec[indices].tolist())


    # List of points and normal vectors that creates the plane
    planes = []

    for id, vecs in enumerate(plane_vectors):

        v1, v2 = vecs

        point = critical_points[id]

        # the cross product is a vector normal to the plane
        normal = np.cross(v1, v2)
        planes.append({
            'point': point.tolist(), 
            'normal': normal.tolist()
        })


    # ============ VISUAL ====================

    colors = vtkNamedColors()

    # Create point cloud
    points = vtkPoints()
    for x,y,z in critical_points:
        points.InsertNextPoint(x, y, z)

    # ============= Original critcial points position ==================
    cp_polydata = vtkPolyData()
    cp_polydata.SetPoints(points)

    pointSource = vtkSphereSource()
    pointSource.SetThetaResolution(10)
    pointSource.SetPhiResolution(10)
    pointSource.SetRadius(0.1)

    pGlyph3D = vtkGlyph3D()
    pGlyph3D.SetSourceConnection(pointSource.GetOutputPort())
    pGlyph3D.SetInputData(cp_polydata)
    pGlyph3D.Update()

    # Visualize
    pMapper = vtkPolyDataMapper()
    pMapper.SetInputConnection(pGlyph3D.GetOutputPort())

    pActor = vtkActor()
    pActor.SetMapper(pMapper)
    pActor.GetProperty().SetColor(colors.GetColor3d('Black'))


    # ======= PLANE GENERATED FROM EIGENVECTORS ========= #

    plane_polydata = vtkPolyData()
    plane_polydata.SetPoints(points)

    # Generate vectors perpendicular to normal so the plane lays correctly
    # arrayOfPerpNormals = np.array([perpendicular_vector(np.array(p['normal'])).real for p in planes])
    arrayOfPerpNormals = np.array([np.array(p)[0].real for p in plane_vectors])
    plane_polydata.GetPointData().SetNormals(numpy_to_vtk(arrayOfPerpNormals))

    # Create a plane
    planeSource = vtkPlaneSource()
    planeSource.SetXResolution(3)
    planeSource.SetYResolution(3)
    planeSource.Update()

    # Create 3d glyph to map the plane with pointdata
    glyph = vtkGlyph3D()
    glyph.SetInputData(plane_polydata)
    glyph.SetSourceConnection(planeSource.GetOutputPort())
    glyph.SetVectorModeToUseNormal()
    glyph.SetScaleFactor(2)
    glyph.Update()

    # Create a mapper and actor
    mapper = vtkPolyDataMapper()
    mapper.SetInputData(glyph.GetOutput())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Black'))
    actor.GetProperty().SetOpacity(0.5)
    actor.GetProperty().SetRepresentationToWireframe()

    # ================================================================ #

    # Vector Glyphs

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
    normalGlyph.SetScaleFactor(2)
    normalGlyph.Update()

    # Create a mapper and actor
    normalMapper = vtkPolyDataMapper()
    normalMapper.SetInputData(normalGlyph.GetOutput())

    normalActor = vtkActor()
    normalActor.SetMapper(normalMapper)
    normalActor.GetProperty().SetColor(colors.GetColor3d('Yellow'))
    normalActor.GetProperty().SetOpacity(1)
    # normalActor.GetProperty().SetRepresentationToWireframe()


    if(visualize):
        
        # Add X,Y,Z helper axis
        transform = vtkTransform()
        transform.Translate(25.0, -10.0, 0.0)
        axes = custom_axes(transform)

        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        renderWindow.SetSize(1920,1080)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        if(vectorfield != None):
            renderer.AddActor(get_vectorfield(vectorfield))

        renderer.AddActor(actor)
        renderer.AddActor(pActor)
        renderer.AddActor(normalActor)
        renderer.AddActor(axes)
        renderer.SetBackground(colors.GetColor3d('SlateGray'))  # Background Slate Gray
        
        renderWindow.SetWindowName('Plane generation')
        renderWindow.Render()
        renderWindowInteractor.Start()

    
    # Write x,y,z coordinates of critical points
    writer = vtkSimplePointsWriter()
    writer.SetDecimalPrecision(5)
    writer.SetFileName(outfile)
    writer.SetInputConnection(glyph.GetOutputPort(0))
    writer.Write()

    print(f"Generated {glyph.GetOutput().GetPointData().GetNumberOfTuples()} seed points in file: '{outfile}'")


def get_vectorfield(vectorfield):
    

    # Create the glyphs source
    arrowSource = vtkArrowSource()

    # Create the mask (not wanting every single value)
    ptMask = vtkMaskPoints()
    ptMask.SetInputConnection(vectorfield.GetOutputPort())
    ptMask.RandomModeOn()
    ptMask.SetMaximumNumberOfPoints(10000)

    # Create 3D Glyphs
    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    glyph3D.SetInputConnection(ptMask.GetOutputPort())
    glyph3D.SetVectorModeToUseVector()
    
    glyph3D.SetScaleFactor(1)
    glyph3D.Update()

    # Visualize
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0,0,0)
    actor.GetProperty().SetOpacity(0.2)

    return actor

def perpendicular_vector(v):
    if v[1] == 0 and v[2] == 0:
        if v[0] == 0:
            raise ValueError('zero vector')
        else:
            return np.cross(v, [0, 1, 0])
    return np.cross(v, [1, 0, 0])

def normalize_complex_arr(a):
    a_oo = a - a.real.min() - 1j*a.imag.min() # origin offsetted
    return a_oo/np.abs(a_oo).max()
    


