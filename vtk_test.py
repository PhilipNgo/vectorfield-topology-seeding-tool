#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkPointData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
    vtkSphereSource
)
from vtk import vtkNetCDFCFReader, vtkMaskPolyData, vtkMaskPoints, vtkDataSetSurfaceFilter, vtkArrayCalculator
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)



def main():
    colors = vtkNamedColors()

    filename = 'data/tornado3d.nc'

    # Load the data
    reader = vtkNetCDFCFReader()
    reader.SetFileName(filename)
    reader.UpdateMetaData()
    reader.SphericalCoordinatesOff()
    reader.SetOutputTypeToStructured()
    reader.Update()
    #print(reader.GetOutput())
    #reader.ReadAllVectorsOn()
    # reader.ReadAllScalarsOn()
    
    vecFieldCalc = vtkArrayCalculator()
    vecFieldCalc.SetInputData(reader.GetOutput())
    vecFieldCalc.AddScalarArrayName("u")
    vecFieldCalc.AddScalarArrayName("v")
    vecFieldCalc.AddScalarArrayName("w")
    vecFieldCalc.SetFunction("u*iHat + v*jHat + w*kHat")
    vecFieldCalc.SetResultArrayName("velocity")

    # Convert to polydata?
    #input_data = vtkPolyData()
    #input_data.ShallowCopy(reader.GetOutput())
    
    #print(type(input_data))

    # Create the glyphs source
    arrowSource = vtkArrowSource()

    # Create the mask (not wanting every single value)
    ptMask = vtkMaskPoints()
    #ptMask.SetOnRatio(200)
    #ptMask.SetInputData(input_data)
    ptMask.SetInputConnection(vecFieldCalc.GetOutputPort())
    ptMask.RandomModeOn()
    ptMask.SetMaximumNumberOfPoints(1000)

    # Create 3D Glyphs
    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    glyph3D.SetInputConnection(ptMask.GetOutputPort())
    #glyph3D.SetInputData(input_data)
    #glyph3D.SetVectorModeToUseNormal()
    #glyph3D.SetColorModeToColorByVector()
    glyph3D.SetVectorModeToUseVector()
    
    glyph3D.SetScaleFactor(2)
    glyph3D.Update()

    # Visualize
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(colors.GetColor3d('Gold'))

    renderer = vtkRenderer()
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetWindowName('OrientedGlyphs')
    renderWindow.SetSize(1920,1080)

    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    renderer.AddActor(actor)
    renderer.SetBackground(colors.GetColor3d('Black'))

    renderWindow.Render()
    
    camera = renderer.GetActiveCamera()
    camera.SetPosition(-0.399941, -1.070475, 2.931458)
    camera.SetFocalPoint(-0.000000, -0.000000, 0.000000)
    camera.SetViewUp(-0.028450, 0.940195, 0.339448)
    camera.SetDistance(3.146318)
    camera.SetClippingRange(1.182293, 5.626211)

    renderWindow.Render()
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()
