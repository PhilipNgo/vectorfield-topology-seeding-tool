import logging
from typing import Tuple
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
from vtk import vtkVectorFieldTopology, vtkMaskPoints, vtkDataSetMapper, vtkGlyph3D, vtkArrowSource, vtkSphereSource, vtkSimplePointsWriter, vtkAxesActor, vtkTransform, vtkArrayCalculator, vtkLineIntegralConvolution2D, vtkXMLUnstructuredGridWriter

def rename_tecplot_header(filename, large_file=False):
    """Renames the variables in the tecplot file to correctly match vtk requirements
        :filename: input file to change (String)
    """

    try:
        print("Renaming variables..")

        # Opening the file in read mode
        file = open(filename, "r")

        list_of_lines = file.readlines()
        if(large_file):
            list_of_lines[1] = 'VARIABLES="X", "Y", "Z", "Rho [amu/cm^3]", "U_x [km/s]", "U_y [km/s]", "U_z [km/s]", "E [J/m^3]", "bx", "by", "bz", "B1_x [nT]", "B1_y [nT]", "B1_z [nT]", "P [nPa]", "jx", "jy", "jz", "Status"\n'
        else:
            list_of_lines[1] = 'VARIABLES="X", "Y", "Z", "Rho [amu/cm^3]", "U_x [km/s]", "U_y [km/s]", "U_z [km/s]", "bx", "by", "bz", "P [nPa]", "jx", "jy", "jz"\n'

        file = open(filename, "w")
        file.writelines(list_of_lines)
        file.close()

        logging.info("Renamed variable X,Y,Z,bx,by,bz,jx,jy,jz")

    except IOError:
        logging.info(f"Could not open file: '{filename}'")
        raise FileNotFoundError()


def get_critical_point_actor(vft: vtkVectorFieldTopology) -> vtkActor:
    # The critical points
    pointMapper = vtkDataSetMapper()
    pointMapper.SetInputConnection(vft.GetOutputPort(0))

    pointActor = vtkActor()
    pointActor.SetMapper(pointMapper)
    pointActor.GetProperty().SetColor(0., 1., 0.)
    pointActor.GetProperty().SetPointSize(10.)
    pointActor.GetProperty().SetRenderPointsAsSpheres(True)
    return pointActor


def get_separator_actor(vft: vtkVectorFieldTopology) -> vtkActor:
    # The separating lines
    lineMapper = vtkDataSetMapper()
    lineMapper.SetInputConnection(vft.GetOutputPort(1))

    lineActor = vtkActor()
    lineActor.SetMapper(lineMapper)
    lineActor.GetProperty().SetColor(0.2, 0.2, 0.2)
    lineActor.GetProperty().SetLineWidth(5.)
    lineActor.GetProperty().SetRenderLinesAsTubes(True)
    return lineActor

def get_separatrix_surface(vft: vtkVectorFieldTopology) -> vtkActor:
    surfaceMapper = vtkDataSetMapper()
    surfaceMapper.SetInputConnection(vft.GetOutputPort(2))

    surfaceActor = vtkActor()
    surfaceActor.SetMapper(surfaceMapper)
    surfaceActor.GetProperty().SetColor(0.1, 0.1, 0.1)
    #surfaceActor.GetProperty().SetOpacity(0.12)
    surfaceActor.GetProperty().SetRepresentationToWireframe()
    return surfaceActor

def get_vector_field_actor(vectorfield) -> vtkActor:
    # Create the glyphs source
    arrowSource = vtkArrowSource()

    # Create the mask (not wanting every single value)
    ptMask = vtkMaskPoints()
    ptMask.SetInputData(vectorfield)
    ptMask.RandomModeOn()
    ptMask.SetMaximumNumberOfPoints(1000)

    # Create 3D Glyphs
    glyph3D = vtkGlyph3D()
    glyph3D.SetSourceConnection(arrowSource.GetOutputPort())
    glyph3D.SetInputConnection(ptMask.GetOutputPort())
    glyph3D.SetVectorModeToUseVector()
    glyph3D.SetScaleModeToDataScalingOff()
    
    glyph3D.SetScaleFactor(1.5)
    glyph3D.Update()

    # Visualize
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(glyph3D.GetOutputPort())

    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(0,1,1)
    actor.GetProperty().SetOpacity(0.5)

    return actor

def get_sphere_actor(radius: float, center: Tuple[float, float, float], color: Tuple[float, float, float] = (0.,0.,1.), opacity: float = 1) -> vtkActor:
    source = vtkSphereSource()
    source.SetCenter(center)
    source.SetRadius(radius)
     
    # mapper
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(source.GetOutputPort())
     
    # actor
    actor = vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(color[0],color[1],color[2])
    actor.GetProperty().SetOpacity(opacity)
    return actor


    