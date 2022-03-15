import os
import numpy as np
import pandas as pd

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
from vtk import vtkTransform, vtkPointLocator, vtkCellLocator
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
    """Removes unwanted lines from a text file.
        :indir: Directory of file (String)
        :filename: File to remove lines from (String)
        :outdir: Directory of output file (String)
        :indices_to_remove: List of indicies to remove (List)
    """
    data = np.genfromtxt(f"{indir}/{filename}", dtype=float)
    data = np.delete(data, indices_to_remove, axis=0)
    np.savetxt(f"{outdir}/processed_{filename}", data)

def remove_lines_json(indir, filename, outdir, indices_to_remove):
    """Removes unwanted lines from a json file.
        :indir: Directory of file (String)
        :filename: File to remove lines from (String)
        :outdir: Directory of output file (String)
        :indices_to_remove: List of indicies to remove (List)
    """

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
    """Plots points on the screen
        :ex: x component of earths position
        :ey: y component of earths position
        :ez: z component of earths position
        :r: radius component of earths position
        :criticalpoints: List of criticalpoints to visualize (List)
    """

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


def _idlist_to_numpy(a):
    """Returns the vtkIdList as a numpy list
        :a: list component (vtkIdList)
    """

    n = a.GetNumberOfIds()
    return np.array([a.GetId(i) for i in range(n)])

def generate_status(grid, outfile, critical_point_infile):
    """Generates a csv file with status information of the critical points and the cell it is in.
        :grid: The grid where the points lie (vtkUnstructeredGrid())
        :outfile: Name of the output file (String)
        :critical_point_infile: Filename of the file containing all the critical points (String)
    """

    critical_point_positions = np.genfromtxt(critical_point_infile, dtype=float,usecols=[0,1,2])

    point_locator = vtkPointLocator()
    point_locator.SetDataSet(grid)
    point_locator.Update()

    cell_locator = vtkCellLocator()
    cell_locator.SetDataSet(grid)
    cell_locator.BuildLocator()

    critical_point_ids = []
    critical_point_cell_ids = []
    critical_point_cell_boundary_ids = []

    for position in critical_point_positions:

        point_id = point_locator.FindClosestPoint(position)
        cell_id = cell_locator.FindCell(position)
        cell_point_ids = _idlist_to_numpy(grid.GetCell(cell_id).GetPointIds())

        critical_point_ids.append(point_id)
        critical_point_cell_ids.append(cell_id)
        critical_point_cell_boundary_ids.append(cell_point_ids)

    # Status for critical point
    critical_point_status = []

    for id in critical_point_ids:
        status = grid.GetPointData().GetArray("Status").GetValue(id)
        critical_point_status.append(status)

    # Status for critical point boundary
    cell_boundary_status = [] 

    for ids in critical_point_cell_boundary_ids:
        status_list = []
        for id in ids:
            status = grid.GetPointData().GetArray("Status").GetValue(id)
            status_list.append(float(status))
        
        cell_boundary_status.append(status_list)

    collection_arr = list(zip(critical_point_ids, critical_point_cell_ids, critical_point_cell_boundary_ids, critical_point_status, cell_boundary_status))

    pd.DataFrame(collection_arr).to_csv(outfile, header=["Point ID", "Cell ID", "Cell Boundary IDs", "Status Point", "Status Boundary"], index=False)
