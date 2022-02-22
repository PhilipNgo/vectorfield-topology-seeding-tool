#!/usr/bin/env python

# This simple example shows how to do basic rendering and pipeline
# creation.

# noinspection PyUnresolvedReferences
import os
from matplotlib.font_manager import json_dump
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)

from vtk import vtkArrayCalculator, vtkVectorFieldTopology, vtkMaskPoints, vtkRTAnalyticSource, vtkDataSetMapper, vtkGlyph3D, vtkArrowSource, vtkUnstructuredGrid, vtkTecplotReader, vtkXMLUnstructuredGridReader, vtkSimplePointsWriter, vtkAxesActor, vtkTransform
from vtkmodules.util.numpy_support import vtk_to_numpy
import numpy as np
import json


def main():

    # Create bounding box
    s = vtkRTAnalyticSource()
    factor = 3
    s.SetWholeExtent(-10*factor, 10*factor, -10*factor, 10*factor, -10*factor, 10*factor)

    ############################ FUNCTION BASED DATA ####################################

    # function_ = "(coordsX+coordsZ)*iHat + coordsY*jHat + (coordsX-coordsZ)*kHat"
    # #function_ = "(coordsX-coordsZ)*iHat + (coordsZ) * jHat + (coordsX-coordsZ) * kHat"
    
    # vecFieldCalc2 = vtkArrayCalculator()
    # vecFieldCalc2.AddCoordinateScalarVariable("coordsX",0)
    # vecFieldCalc2.AddCoordinateScalarVariable("coordsY",1)
    # vecFieldCalc2.AddCoordinateScalarVariable("coordsZ",2)
    # vecFieldCalc2.SetFunction(function_)
    # vecFieldCalc2.SetInputConnection(s.GetOutputPort())
    # vecFieldCalc2.SetAttributeTypeToPointData()
    # vecFieldCalc2.Update()

    # plot_vectorfield_topology(vectorfield=vecFieldCalc2, bounding_box=s, show_vectorfield = True, scale = 0.05, max_points = 500, debug = True)

    ################### LOW RES DATA .VTK ########################################################

    # filename = 'data/lowres_sample_data/cut_var_1_e20000101-020000-000.out.vtk'

    # reader = vtkXMLUnstructuredGridReader()
    # reader.SetFileName(filename)
    # reader.Update()

    # #field_to_visualize = 'velocity'
    # field_to_visualize = 'magnetic_field'


    # vecFieldCalc = vtkArrayCalculator()
    # vecFieldCalc.SetInputData(reader.GetOutput())
    # vecFieldCalc.AddVectorArrayName(field_to_visualize)
    # vecFieldCalc.SetResultArrayName(field_to_visualize)
    # vecFieldCalc.SetFunction(field_to_visualize)
    # vecFieldCalc.Update()

    # plot_vectorfield_topology(vectorfield=vecFieldCalc, bounding_box=s, show_vectorfield = True, scale = 2, max_points = 2000, debug = True)

    ###################### LOW RES DATA .DAT #####################

    filename = 'data/lowres_sample_data/cut_mhd_2_e20000101-020000-000.dat'

    # Rename X, Y, Z bx, by, bz in the .dat file
    # rename_variables(filename=filename)

    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()

    # Create unstructured grid
    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))

    # Calculate the vectorfield
    vecFieldCalc = vtkArrayCalculator()
    vecFieldCalc.SetInputData(out)
    vecFieldCalc.AddScalarArrayName('bx')
    vecFieldCalc.AddScalarArrayName('by')
    vecFieldCalc.AddScalarArrayName('bz')
    vecFieldCalc.SetFunction("bx*iHat + by*jHat + bz*kHat")
    vecFieldCalc.SetResultArrayName("magnetic_field")
    vecFieldCalc.Update()

    plot_vectorfield_topology(vectorfield=vecFieldCalc, bounding_box=s, show_vectorfield = True, 
    show_critical_points = True, show_separator = False,  
    scale = 2, max_points = 1000, debug = True, write_file=True)


def plot_vectorfield_topology(vectorfield, bounding_box, show_critical_points = True, show_separator = True, 
show_vectorfield = False, show_separating_surface = False, show_boundary_switch = False, 
scale=1.5, max_points = 1000, debug = False, write_file = False):

    colors = vtkNamedColors()

    if debug: print("Creating vectorfield object..")

    # Create vectorfield analysis object
    vft = vtkVectorFieldTopology()
    vft.SetInputData(vectorfield.GetOutput())
    vft.SetIntegrationStepUnit(1)
    vft.SetSeparatrixDistance(1)
    vft.SetIntegrationStepSize(1)
    vft.SetMaxNumSteps(1000)
    vft.SetComputeSurfaces(show_separating_surface)
    vft.SetUseBoundarySwitchPoints(show_boundary_switch)
    vft.SetUseIterativeSeeding(True) # See if the simple (fast) or iterative (correct version)
    vft.Update()

    if(write_file):
        write_to_file(vft, "seedpoints.txt")    

    #The critical points
    pointMapper = vtkDataSetMapper()
    pointMapper.SetInputConnection(vft.GetOutputPort(0))

    pointActor = vtkActor()
    pointActor.SetMapper(pointMapper)

    if debug: print("Created vectorfield object.")

    if debug: print("Creating Mappers and Actors..")
    # The bounding box
    sMapper = vtkDataSetMapper() 
    sMapper.SetInputConnection(bounding_box.GetOutputPort())

    sActor = vtkActor()
    sActor.SetMapper(sMapper)
    sActor.GetProperty().SetColor(0.4, 0.4, 0.4)
    sActor.GetProperty().SetOpacity(0.1)
    sActor.GetProperty().SetRepresentationToSurface()

    # The critical points
    pointMapper = vtkDataSetMapper()
    pointMapper.SetInputConnection(vft.GetOutputPort(0))

    pointActor = vtkActor()
    pointActor.SetMapper(pointMapper)
    pointActor.GetProperty().SetColor(0., 1., 0.)
    pointActor.GetProperty().SetPointSize(10.)
    pointActor.GetProperty().SetRenderPointsAsSpheres(True)

    # The separating lines
    lineMapper = vtkDataSetMapper()
    lineMapper.SetInputConnection(vft.GetOutputPort(1))

    lineActor = vtkActor()
    lineActor.SetMapper(lineMapper)
    lineActor.GetProperty().SetColor(0.2, 0.2, 0.2)
    lineActor.GetProperty().SetLineWidth(5.)
    lineActor.GetProperty().SetRenderLinesAsTubes(True)


    # The separating surfaces
    surfaceMapper = vtkDataSetMapper()
    surfaceMapper.SetInputConnection(vft.GetOutputPort(2))

    surfaceActor = vtkActor()
    surfaceActor.SetMapper(surfaceMapper)
    surfaceActor.GetProperty().SetColor(0.1, 0.1, 0.1)
    #surfaceActor.GetProperty().SetOpacity(0.12)
    surfaceActor.GetProperty().SetRepresentationToWireframe()

    # The boundary switch lines
    lineMapper2 = vtkDataSetMapper()
    lineMapper2.SetInputConnection(vft.GetOutputPort(3))

    lineActor2 = vtkActor()
    lineActor2.SetMapper(lineMapper2)
    lineActor2.GetProperty().SetColor(0.2, 0.2, 0.2)
    lineActor2.GetProperty().SetLineWidth(35.)
    lineActor2.GetProperty().SetRenderLinesAsTubes(True)


    # The boundary switch surfaces
    surfaceMapper2 = vtkDataSetMapper()
    surfaceMapper2.SetInputConnection(vft.GetOutputPort(4))

    surfaceActor2 = vtkActor()
    surfaceActor2.SetMapper(surfaceMapper2)
    surfaceActor2.GetProperty().SetColor(0, 0, 0)
    #surfaceActor2.GetProperty().SetOpacity(0.5)
    surfaceActor2.GetProperty().SetRepresentationToWireframe()

    if debug: print("Created Mappers and Actors.")

    if debug: print("Creating Renderers..")

    # Add x,y,z axis
    transform = vtkTransform()
    transform.Translate(25.0, -10.0, 0.0)
    axes = custom_axes(transform)
    
    # Renderer
    renderer = vtkRenderer()
    renderer.AddActor(axes)
    renderer.AddActor(sActor)
    if(show_critical_points): renderer.AddActor(pointActor)
    if(show_separator): renderer.AddActor(lineActor)
    if(show_separating_surface): renderer.AddActor(surfaceActor) # Surface
    if(show_boundary_switch):
        renderer.AddActor(lineActor2) # Boundary switch lines
        renderer.AddActor(surfaceActor2) # Boundary switch surface
    renderer.ResetCamera()
    renderer.SetBackground(1., 1., 1.)

    # The vector field
    if(show_vectorfield):

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
        actor.GetProperty().SetColor(0,1,1)
        actor.GetProperty().SetOpacity(0.5)

        renderer.AddActor(actor)

    
    renWin = vtkRenderWindow() 
    renWin.AddRenderer(renderer)
    renWin.SetMultiSamples(0)
    renWin.SetSize(1920,1080)
    renWin.SetWindowName('Vectorfield Topology')

    iren = vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # This allows the interactor to initalize itself. It has to be
    # called before an event loop.
    iren.Initialize()

    # We'll zoom in a little by accessing the camera and invoking a "Zoom"
    # method on it.
    renderer.ResetCamera()
    renderer.GetActiveCamera().Zoom(1.5)
    renWin.Render()

    if debug: print("Created Renderer.")

    # Start the event loop.
    iren.Start()

def rename_variables(filename):
    try:

        print("Renaming variables..")

        # opening the file in read mode
        file = open(filename, "r")

        list_of_lines = file.readlines()
        list_of_lines[1] = 'VARIABLES="X", "Y", "Z ", "Rho [amu/cm^3]", "U_x [km/s]", "U_y [km/s]", "U_z [km/s]", "bx", "by", "bz", "P [nPa]", "J_x [`mA/m^2]", "J_y [`mA/m^2]", "J_z [`mA/m^2]"\n'

        file = open(filename, "w")
        file.writelines(list_of_lines)
        file.close()

        print("Renamed variable X,Y,Z,bx,by,bz")

    except IOError:
        print ("Could not open file!")

def write_to_file(vft, out_filename):

    #gradient = vtk_to_numpy(vft.GetOutput(0).GetPointData().GetArray(0))
    type = vtk_to_numpy(vft.GetOutput(0).GetPointData().GetArray(1))
    detailed_type = vtk_to_numpy(vft.GetOutput(0).GetPointData().GetArray(1))

    # Create target Directory if don't exist
    dirName = "seedpoints"
    if not os.path.exists(dirName):
        os.mkdir(dirName)
        print("Directory " , dirName ,  " Created ")
    else:    
        print("Directory " , dirName ,  " already exists")

    # Write x,y,z coordinates of critical points
    writer = vtkSimplePointsWriter()
    writer.SetDecimalPrecision(5)
    writer.SetFileName("{}/{}".format(dirName, out_filename))
    writer.SetInputConnection(vft.GetOutputPort(0))
    writer.Write()

    json_data = {
        'TYPES': {
            'DEGENERATE_3D': -1,
            'SINK_3D': 0,
            'SADDLE_1_3D': 1,
            'SADDLE_2_3D': 2,
            'SOURCE_3D' : 3,
            'CENTER_3D' : 4,
            'LIST': type.tolist()
        },
        'DETAILED TYPES':{
            'ATTRACTING_NODE_3D' : 0,
            'ATTRACTING_FOCUS_3D' : 1,
            'NODE_SADDLE_1_3D' : 2,
            'FOCUS_SADDLE_1_3D' : 3,
            'NODE_SADDLE_2_3D' : 4,
            'FOCUS_SADDLE_2_3D' : 5,
            'REPELLING_NODE_3D' : 6,
            'REPELLING_FOCUS_3D' : 7,
            'CENTER_DETAILED_3D' : 8,
            'LIST': detailed_type.tolist()
        }
    }

    # Directly from dictionary
    with open("{}/details.json".format(dirName), 'w') as outfile:
        json.dump(json_data, outfile, ensure_ascii=False, indent=4)


def custom_axes(transform):

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


if __name__ == '__main__':
    main()
