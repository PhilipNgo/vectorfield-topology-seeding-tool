#!/usr/bin/env python

# noinspection PyUnresolvedReferences
from matplotlib.pyplot import sca
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
)
from vtk import vtkNetCDFCFReader, vtkMaskPoints, vtkArrayCalculator
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def main():

    filename = 'data/tornado3d.nc'
    #filename = 'data/ctbl3d.nc'

    # Load the data
    reader = vtkNetCDFCFReader()
    reader.SetFileName(filename)
    reader.UpdateMetaData()
    reader.SphericalCoordinatesOff()
    reader.SetOutputTypeToAutomatic()
    reader.Update()
    
    vecFieldCalc = vtkArrayCalculator()
    vecFieldCalc.SetInputData(reader.GetOutput())
    vecFieldCalc.AddScalarArrayName("u")
    vecFieldCalc.AddScalarArrayName("v")
    vecFieldCalc.AddScalarArrayName("w")
    vecFieldCalc.SetFunction("u*iHat + v*jHat + w*kHat")
    vecFieldCalc.SetResultArrayName("velocity")
    vecFieldCalc.Update()

    plot_vectorfield(vectorfield=vecFieldCalc, max_points=1000, scale=1.5)
    
    ######## UNCOMMENT BELOW TO SEE FUNCTION BASED VECTORFIELD ##########
    
    # s = vtkRTAnalyticSource()
    # s.SetWholeExtent(-10,10,-10,10,-10,10)

    # function_ = "(coordsX+coordsZ)*iHat + coordsY*jHat + (coordsX-coordsZ)*kHat"
    # #function_ = "(coordsX)*iHat + (coordsY)*jHat + (coordsX)*kHat"

    # vecFieldCalc = vtkArrayCalculator()
    # vecFieldCalc.AddCoordinateScalarVariable("coordsX", 0)
    # vecFieldCalc.AddCoordinateScalarVariable("coordsY", 1)
    # vecFieldCalc.AddCoordinateScalarVariable("coordsZ", 2)
    # vecFieldCalc.SetFunction(function_)
    # vecFieldCalc.SetInputConnection(s.GetOutputPort())
    # vecFieldCalc.Update()

    # plot_vectorfield(vectorfield=vecFieldCalc, max_points=500, scale=0.05)

    ######################################################################


def plot_vectorfield(vectorfield, max_points = 1000, scale = 1.5):

    colors = vtkNamedColors()

    # Create the glyphs source
    arrowSource = vtkArrowSource()

    # Create the mask (not wanting every single value)
    ptMask = vtkMaskPoints()
    ptMask.SetInputConnection(vectorfield.GetOutputPort())
    ptMask.RandomModeOn()
    ptMask.SetMaximumNumberOfPoints(max_points)

    # Create 3D Glyphs
    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    glyph3D.SetInputConnection(ptMask.GetOutputPort())
    glyph3D.SetVectorModeToUseVector()
    
    glyph3D.SetScaleFactor(scale)
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
    renderWindow.SetWindowName('Vectorfield')
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
