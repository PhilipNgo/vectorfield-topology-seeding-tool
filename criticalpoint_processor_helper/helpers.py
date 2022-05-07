from vtk import vtkNamedColors, vtkPolyData, vtkSphereSource, vtkGlyph3D, vtkPolyDataMapper, vtkActor, vtkPoints

def get_points_actor_from_list_of_points(list_of_points):

    points = vtkPoints()
    for x,y,z in list_of_points:
        points.InsertNextPoint(x,y,z)

    colors = vtkNamedColors()

    polydata = vtkPolyData()
    polydata.SetPoints(points)

    sphereSource = vtkSphereSource()
    sphereSource.SetThetaResolution(10)
    sphereSource.SetPhiResolution(10)
    sphereSource.SetRadius(0.5)

    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(sphereSource.GetOutputPort())
    glyph3D.SetInputData(polydata)
    glyph3D.Update()

    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d("Red"))
    actor.GetProperty().SetPointSize(5.)
    actor.GetProperty().SetRenderPointsAsSpheres(True)

    return actor