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
from vtk import vtkTransform
import json
from vectorfieldtopology_helper import custom_axes

def remove_unwanted_critical_points(x,y,z, radius, infile, indir="unprocessed_data", outdir="processed_data", visualize=False):
    """Removes unwanted critical points, eg. near earth critical points. 
        Creates text file with correct critical points.
        :x: x coord for earths center (Float)
        :y: y coord for earths center (Float)
        :z: z coord for earths center (Float)
        :radius: radius of earth in terms of coordinate system to ignore (Float)
        :infile: input file with critical points (String)
        :indir: directory where the file is (String)
        :outdir: directory where the file should be saved (String)
        :visualize: wether to visualize the removed points or not (Boolean)
    """
    # Constant
    RADIUS = radius
    ex = x
    ey = y
    ez = z

    # Load criticalpoints
    criticalpoints = np.genfromtxt(f"{indir}/{infile}",dtype=float,usecols=[0,1,2])

    criticalpoints_processed = []
    indices_to_remove = []

    for ind, seed in enumerate(criticalpoints):

        sx, sy, sz = seed
        #Check if point is inside/on sphere 
        is_inside = ((sx-ex)**2+(sy-ey)**2+(sz-ez)**2 <= RADIUS**2)

        if(not is_inside):
            criticalpoints_processed.append([sx,sy,sz])
        else:
            indices_to_remove.append(ind)

    if not os.path.exists(outdir):
        os.mkdir(outdir)
        print(f"Directory {outdir} created ")
    else:    
        print(f"Directory {outdir} already exists")

    np.savetxt(f"{outdir}/processed_{infile}", criticalpoints_processed, fmt='%1.5f')

    # Remove lines and save file 
    remove_lines_json(indir=indir, filename='details.json', outdir=outdir, indices_to_remove=indices_to_remove)
    remove_lines(indir=indir, filename="gradient.txt", outdir=outdir, indices_to_remove=indices_to_remove)

    np.savetxt(f"{outdir}/removed_indices.txt", indices_to_remove, '%i')

    if(visualize):
        visualize_points(ex=ex, ey=ey, ez=ez, r=RADIUS, criticalpoints=criticalpoints)

    print(f"Updated critical points and files in directory '{outdir}' (Removed {len(indices_to_remove)} critical points)")

def remove_lines(indir, filename, outdir, indices_to_remove):

    data = np.genfromtxt(f"{indir}/{filename}", dtype=float)
    data = np.delete(data, indices_to_remove, axis=0)
    np.savetxt(f"{outdir}/processed_{filename}", data)

def remove_lines_json(indir, filename, outdir, indices_to_remove):
    
    f = open(f'{indir}/{filename}')

    data = json.load(f)

    processed_data = data["DETAILED TYPES"]["LIST"]
    processed_data = np.delete(processed_data, indices_to_remove)
    data["DETAILED TYPES"]["LIST"] = processed_data.tolist()

    processed_data = data["TYPES"]["LIST"]
    processed_data = np.delete(processed_data, indices_to_remove)
    data["TYPES"]["LIST"] = processed_data.tolist()

    # Directly from dictionary
    with open(f"{outdir}/processed_{filename}", 'w') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)

    print(f"Details saved to: '{outdir}/processed_{filename}'")

    f.close()
    
def visualize_points(ex,ey,ez,r,criticalpoints):

    colors = vtkNamedColors()

    # Create point cloud
    points = vtkPoints()
    for x,y,z in criticalpoints:
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

    # ===================== EARTH ============================

    points = vtkPoints()

    points.InsertNextPoint(ex, ey, ez)

    earth_polydata = vtkPolyData()
    earth_polydata.SetPoints(points)

    earthSource = vtkSphereSource()
    earthSource.SetThetaResolution(20)
    earthSource.SetPhiResolution(20)
    earthSource.SetRadius(r)

    earthGlyph3D = vtkGlyph3D()
    earthGlyph3D.SetSourceConnection(earthSource.GetOutputPort())
    earthGlyph3D.SetInputData(earth_polydata)
    earthGlyph3D.Update()

    # Visualize
    earthMapper = vtkPolyDataMapper()
    earthMapper.SetInputConnection(earthGlyph3D.GetOutputPort())

    earthActor = vtkActor()
    earthActor.SetMapper(earthMapper)
    earthActor.GetProperty().SetColor(colors.GetColor3d('Blue'))
    earthActor.GetProperty().SetOpacity(0.5)
    
    # ========================================================

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

    renderer.AddActor(pActor)
    renderer.AddActor(earthActor)
    renderer.AddActor(axes)
    renderer.SetBackground(colors.GetColor3d('SlateGray'))  # Background Slate Gray
    
    renderWindow.SetWindowName('Sphere generation')
    renderWindow.Render()
    renderWindowInteractor.Start()


