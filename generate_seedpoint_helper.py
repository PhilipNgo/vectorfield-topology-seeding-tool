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

from numpy import genfromtxt
from vtk import vtkSimplePointsWriter 

def generate_seedpoints(infile, outfile, visualize=False):
    """Generate seedpoints with the help of critical points by sampling points around the critical points. 
        :infile: input file with critical points (String)
        :outfile: output file with critical points (String)
    """

    colors = vtkNamedColors()

    # Load data
    data = genfromtxt(infile,dtype=float,usecols=[0,1,2])

    # Create point cloud
    points = vtkPoints()
    for x,y,z in data:
        points.InsertNextPoint(x, y, z)

    # ============= Original critcial points position ==================
    cp_polydata = vtkPolyData()
    cp_polydata.SetPoints(points)

    # Glyph data
    polydata = vtkPolyData()
    polydata.SetPoints(points)

    pointSource = vtkSphereSource()
    pointSource.SetThetaResolution(10)
    pointSource.SetPhiResolution(10)
    pointSource.SetRadius(0.1)

    pGlyph3D = vtkGlyph3D()
    pGlyph3D.SetSourceConnection(pointSource.GetOutputPort())
    pGlyph3D.SetInputData(polydata)
    pGlyph3D.Update()

    # Visualize
    pMapper = vtkPolyDataMapper()
    pMapper.SetInputConnection(pGlyph3D.GetOutputPort())

    pActor = vtkActor()
    pActor.SetMapper(pMapper)
    pActor.GetProperty().SetColor(colors.GetColor3d('Black'))



    # ======= Sphere with radius x from the critical point ========= #

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

    # ================================================================

    if(visualize):
        
        renderer = vtkRenderer()
        renderWindow = vtkRenderWindow()
        renderWindow.AddRenderer(renderer)
        renderWindow.SetSize(1920,1080)

        renderWindowInteractor = vtkRenderWindowInteractor()
        renderWindowInteractor.SetRenderWindow(renderWindow)

        renderer.AddActor(actor)
        renderer.AddActor(pActor)
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

    print("Seed points successfully generated..")


