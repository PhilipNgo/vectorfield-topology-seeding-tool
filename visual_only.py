import os
import numpy as np

# Temp import:
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
from vtk import vtkTransform, vtkUnstructuredGrid, vtkTecplotReader, vtkArrowSource, vtkMaskPoints
from vectorfieldtopology_helper import add_j_cross_b, custom_axes, get_vector_field


def main():

    critical_points_lowres = 'saved_data/unprocessed_data/criticalpoints.txt' # lowres 5 sec
    critical_points_highres = 'saved_data/unprocessed_data_highres/criticalpoints.txt' # highres 162 sec
    critical_points_inverted = 'saved_data/inverted_data/unprocessed_data/criticalpoints.txt' # critical points of the inverted data
    critical_points_current = 'saved_data/current_field_data/unprocessed_data/criticalpoints.txt' #100+ sec
    critical_points_jcb = 'saved_data/unprocessed_data_jcb_d1000/criticalpoints.txt' # 57 minutes
    critical_points_in_same_cell = 'saved_data/critical_points_that_might_cancel.txt'

    # # Create point cloud
    points_lowres = get_point_data(critical_points_lowres)
    points_highres = get_point_data(critical_points_highres)
    # points_inverted = get_point_data(critical_points_inverted)
    points_current = get_point_data(critical_points_current)
    points_jcb = get_point_data(critical_points_jcb)
    points_cp_cancels = get_point_data(critical_points_in_same_cell)

    # # Get actor
    actor_lowres = get_pointcloud_actor(points_lowres, 1., 0., 0.)
    actor_highres = get_pointcloud_actor(points_highres, 1., 1., 1.)
    # actor_inverted = get_pointcloud_actor(points_inverted, 1., 0., 0.,)
    actor_current = get_pointcloud_actor(points_current, 0., 0., 1.)
    actor_jcb = get_pointcloud_actor(points_jcb, 0., 0., 0.)
    actor_cancelled_cp = get_pointcloud_actor(points_cp_cancels, 0.,0.,0.,)



    # Show vectorfield:
    # filename = 'data/lowres_sample_data/cut_mhd_2_e20000101-020000-000.dat'
    # vecFieldJCrossB = generate_j_cross_b(filename)
    # vecfield_actor_jcb = get_vector_field_actor(vectorfield=vecFieldJCrossB, maxpoints=2000,R=1.)

    # # List of actors we want to visualize
    # list_of_actors = [actor_cancelled_cp, actor_highres] #
    list_of_actors = [actor_jcb]#, actor_current, actor_lowres]

    colors = vtkNamedColors()

    # Add X,Y,Z helper axis
    transform = vtkTransform()
    transform.Translate(25.0, -10.0, 0.0)
    axes = custom_axes(transform)

    # Generate renderer
    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1920,1080)

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    for _actor in list_of_actors:
        renderer.AddActor(_actor)
    renderer.AddActor(axes)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))  # Background Slate Gray
    
    renderWindow.SetWindowName('Visualization of existing values')
    renderWindow.Render()
    renderWindowInteractor.Start()

def get_point_data(filename):
    """Returns points (vtkPoints) of the points in a given filename
        :filename: Name of file (String)
    """

    pointdata = np.genfromtxt(filename,dtype=float,usecols=[0,1,2])

    points = vtkPoints()

    for x,y,z in pointdata: 
        points.InsertNextPoint(x, y, z)

    return points


def generate_j_cross_b(filename):
    """Vectorfield of J cross B (vtkArrayCalculator()) of the points given
        :filename: Name of file (String)
    """
    
    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()
    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))
    out = add_j_cross_b(out)

    # print(out.GetPointData())
    vecFieldJCrossB = get_vector_field("jcb_x", "jcb_y", "jcb_z", out, "j_cross_b")
    return vecFieldJCrossB



def get_pointcloud_actor(points, R=0., G=0., B=0.):
    """Returns the actor (vtkRenderingOpenGL) of the points given
        :points: Points where the critical points lies (vtkPoint())
        :R: Color value between 0-1 for point (Float)
        :G: Color value between 0-1 for point (Float)
        :B: Color value between 0-1 for point (Float)
    """
    
    cp_polydata = vtkPolyData()
    cp_polydata.SetPoints(points)

    # Source
    pointSource = vtkSphereSource()
    pointSource.SetThetaResolution(10)
    pointSource.SetPhiResolution(10)
    pointSource.SetRadius(0.1)

    # Glyph
    pGlyph3D = vtkGlyph3D()
    pGlyph3D.SetSourceConnection(pointSource.GetOutputPort())
    pGlyph3D.SetInputData(cp_polydata)
    pGlyph3D.Update()

    # Mapper
    pMapper = vtkPolyDataMapper()
    pMapper.SetInputConnection(pGlyph3D.GetOutputPort())

    # Actor
    pActor = vtkActor()
    pActor.SetMapper(pMapper)
    pActor.GetProperty().SetColor(R,G,B)
    pActor.GetProperty().SetOpacity(0.5)
    return pActor

def get_vector_field_actor(vectorfield, maxpoints=1000, scale=2, R=0, G=0, B=0):
    """Returns the actor (vtkRenderingOpenGL) of the points given
        :vectorfield: Takes in a vectorfield (vtkArrayCalculator())
        :maxpoints: Max number of arrows shown (Int)
        :scale: Scale of the arrow glyphs (Float)
        :R: Color value between 0-1 for point (Float)
        :G: Color value between 0-1 for point (Float)
        :B: Color value between 0-1 for point (Float)
    """

    # Create the glyphs source
    arrowSource = vtkArrowSource()

    # Create the mask (not wanting every single value)
    ptMask = vtkMaskPoints()
    ptMask.SetInputConnection(vectorfield.GetOutputPort())
    ptMask.RandomModeOn()
    ptMask.SetMaximumNumberOfPoints(maxpoints)

    # Create 3D Glyphs
    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    glyph3D.SetInputConnection(ptMask.GetOutputPort())
    glyph3D.SetVectorModeToUseVector()
    glyph3D.SetScaleFactor(scale)
    glyph3D.Update()

    # Mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    # Actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(R,G,B)
    actor.GetProperty().SetOpacity(0.5)

    return actor



if __name__ == '__main__':
    main()