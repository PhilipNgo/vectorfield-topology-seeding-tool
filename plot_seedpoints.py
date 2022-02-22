#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersSources import vtkPointSource
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtk import vtkPoints, vtkPolyData, vtkCellArray, vtkDoubleArray, vtkTransform, vtkAxesActor
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
import numpy as np
from numpy import random, genfromtxt, size

class VtkPointCloud:
    def __init__(self, zMin=-16.5, zMax=16.5, maxNumPoints=1e6):
        self.maxNumPoints = maxNumPoints
        self.vtkPolyData = vtkPolyData()
        self.clearPoints()
        mapper = vtkPolyDataMapper()
        mapper.SetInputData(self.vtkPolyData)
        mapper.SetColorModeToDefault()
        mapper.SetScalarRange(zMin, zMax)
        mapper.SetScalarVisibility(1)
        self.vtkActor = vtkActor()
        self.vtkActor.SetMapper(mapper)
        self.vtkActor.GetProperty().SetPointSize(5.)
        self.vtkActor.GetProperty().SetRenderPointsAsSpheres(True)

    def addPoint(self, point):
        if (self.vtkPoints.GetNumberOfPoints() < self.maxNumPoints):
            pointId = self.vtkPoints.InsertNextPoint(point[:])
            self.vtkDepth.InsertNextValue(point[2])
            self.vtkCells.InsertNextCell(1)
            self.vtkCells.InsertCellPoint(pointId)
        else:
            r = random.randint(0, self.maxNumPoints)
            self.vtkPoints.SetPoint(r, point[:])
        self.vtkCells.Modified()
        self.vtkPoints.Modified()
        self.vtkDepth.Modified()

    def clearPoints(self):
        self.vtkPoints = vtkPoints()
        self.vtkCells = vtkCellArray()
        self.vtkDepth = vtkDoubleArray()
        self.vtkDepth.SetName('DepthArray')
        self.vtkPolyData.SetPoints(self.vtkPoints)
        self.vtkPolyData.SetVerts(self.vtkCells)
        self.vtkPolyData.GetPointData().SetScalars(self.vtkDepth)
        self.vtkPolyData.GetPointData().SetActiveScalars('DepthArray')

def load_data(filename,pointCloud):
    data = genfromtxt(filename,dtype=float,usecols=[0,1,2])

    for k in range(size(data,0)):
        point = data[k] #20*(random.rand(3)-0.5)
        pointCloud.addPoint(point)

    return pointCloud

def custom_axes(transform):

    axes = vtkAxesActor()
    #  The axes are positioned with a user transform
    axes.SetUserTransform(transform)
    # axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetColor(1.0,0.0,0.0)
    axes.SetTotalLength(5, 5, 5)
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetXAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetYAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()
    axes.GetZAxisCaptionActor2D().GetTextActor().SetTextScaleModeToNone()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().SetFontSize(12)
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ItalicOff()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().BoldOff()
    axes.GetZAxisCaptionActor2D().GetCaptionTextProperty().ShadowOff()

    return axes
    
def main():

    # Load the txt file
    filename = 'seedpoints/seedpoints.txt'

    pointCloud = VtkPointCloud()
    pointCloud=load_data(filename,pointCloud)

    # Add x,y,z axis
    transform = vtkTransform()
    transform.Translate(25.0, -10.0, 0.0)
    
    axes = custom_axes(transform=transform)

    # Renderer
    renderer = vtkRenderer()
    renderer.AddActor(pointCloud.vtkActor)
    renderer.AddActor(axes)
    #renderer.SetBackground(.2, .3, .4)
    renderer.SetBackground(0.0, 0.0, 0.0)
    renderer.ResetCamera()

    # Render Window
    renderWindow = vtkRenderWindow()
    renderWindow.AddRenderer(renderer)
    renderWindow.SetSize(1920,1080)

    # Interactor
    renderWindowInteractor = vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    # Begin Interaction
    renderWindow.Render()
    renderWindow.SetWindowName("XYZ Data Viewer")
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()
