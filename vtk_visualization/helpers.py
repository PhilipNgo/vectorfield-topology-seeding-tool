from typing import List
from vtk import vtkAxesActor, vtkTransform, vtkActor, vtkNamedColors
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

def custom_axes() -> vtkAxesActor:
    """ Returns helper axis """

    # Add X,Y,Z helper axis
    transform = vtkTransform()
    transform.Translate(25.0, -10.0, 0.0)

    axes = vtkAxesActor()
    #  The axes are positioned with a user transform
    axes.SetUserTransform(transform)
    axes.SetTotalLength(5, 5, 5)
    # X-Axis
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.0,0.0,0.0)
    # Y-Axis
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.0,0.0,0.0)
    # Z-Axis
    axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetColor(0.0,0.0,0.0)

    return axes

def start_window(list_of_actors: List[ vtkActor ]) -> None:
    """Starts rendering all the given vtk actors
    :list_of_actors: List containing all the vtkActors
    """
    
    colors = vtkNamedColors()

    axes = custom_axes()
    # Renderer
    renderer = vtkRenderer()
    renderer.AddActor(axes)

    for actor in list_of_actors:
        renderer.AddActor(actor)

    renderer.ResetCamera()
    renderer.SetBackground(colors.GetColor3d('SlateGray'))  # Background Slate Gray

    renWin = vtkRenderWindow() 
    renWin.AddRenderer(renderer)
    renWin.SetSize(1920,1080)
    renWin.SetWindowName('Critical points')

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.Initialize()

    renWin.Render()
    iren.Start()