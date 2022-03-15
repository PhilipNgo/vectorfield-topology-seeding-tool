from random import paretovariate
from time import perf_counter
import numpy as np
from vtk import vtkArrayCalculator, vtkRTAnalyticSource, vtkUnstructuredGrid, vtkTecplotReader, vtkPoints, vtkCellLocator, vtkCellPicker, vtkPointLocator, vtkSelectionNode, vtkIdTypeArray, vtkSelection, vtkExtractSelection, vtkXMLUnstructuredGridReader, vtkDataSetMapper
from collections import defaultdict
import json
from vtkmodules.numpy_interface import dataset_adapter as dsa
import pandas as pd
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk

def generate_json(filename, critical_point_filename):

    # Load data
    data = np.genfromtxt(critical_point_filename,dtype=float,usecols=[0,1,2])

    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()

    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))

    locator = vtkCellLocator()
    locator.SetDataSet(out)
    locator.BuildLocator()

    res = defaultdict(list)

    for position in data:

        cell_id = locator.FindCell(position)
        res[cell_id].append(position.tolist())

    with open("position_with_cell_ids.json", 'w') as outfile:
        json.dump(res, outfile, ensure_ascii=False, indent=4)

    # # cell_id = locator.FindCell(data[0])
    # # print(cell_id)
    # cell_id = 2345951

    # cell = out.GetCell(2345951)

    # print("number of cells", out.GetNumberOfCells())
    # print("array status", out.GetPointData().GetArray(15))
    # print("pointer", out.GetPointData().GetArray(15).Get)

def find_point_ids(filename, critical_point_filename, outfile):

    print("Finding..")

     # Load data
    data = np.genfromtxt(critical_point_filename,dtype=float,usecols=[0,1,2])

    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()

    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))

    locator = vtkPointLocator()
    locator.SetDataSet(out)
    # locator.SetTolerance(10.0)
    locator.Update()

    ids = []

    for d in data:
        point_id = locator.FindClosestPoint(d)
        ids.append(point_id)

    # return ids
    # np.savetxt(outfile, ids, fmt='%i')


def get_status_from_csv(filename):
    df = pd.read_csv(filename)

    df_status = df['Status']

    print(df_status.tolist())

    np.savetxt("critical_point_status.txt", df_status.tolist(), fmt='%f')

    # with open('critical_point_status.txt', 'w') as f:
    #     for text in df_status.tolist():
    #         f.write(str(text) + '\n')




def _idlist_to_numpy(a):
    n = a.GetNumberOfIds()
    return np.array([a.GetId(i) for i in range(n)])

def main():

    # Timer
    t1_start = perf_counter()

    filename = 'data/highres_sample_data/3d__var_2_e20000101-020000-000.dat' # 10 mil cells
    # filename = 'data/lowres_sample_data/cut_mhd_2_e20000101-020000-000.dat'
    infile = f"saved_data/processed_data_highres/processed_criticalpoints.txt"

    print("Loading data..")

     # Load data
    critical_point_positions = np.genfromtxt(infile, dtype=float,usecols=[0,1,2])

    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()

    t1_stop = perf_counter() 

    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))

    point_locator = vtkPointLocator()
    point_locator.SetDataSet(out)
    point_locator.Update()

    cell_locator = vtkCellLocator()
    cell_locator.SetDataSet(out)
    cell_locator.BuildLocator()

    critical_point_ids = []
    critical_point_cell_ids = []
    critical_point_cell_boundary_ids = []

    t2_start = perf_counter()

    for position in critical_point_positions:

        point_id = point_locator.FindClosestPoint(position)
        cell_id = cell_locator.FindCell(position)
        cell_point_ids = _idlist_to_numpy(out.GetCell(cell_id).GetPointIds())

        critical_point_ids.append(point_id)
        critical_point_cell_ids.append(cell_id)
        critical_point_cell_boundary_ids.append(cell_point_ids)

    t2_stop = perf_counter()


    t3_start = perf_counter()
    # Status for critical point
    critical_point_status = []

    for id in critical_point_ids:
        status = out.GetPointData().GetArray("Status").GetValue(id)
        critical_point_status.append(status)

    # Status for critical point boundary
    cell_boundary_status = [] 

    for ids in critical_point_cell_boundary_ids:
        status_list = []
        for id in ids:
            status = out.GetPointData().GetArray("Status").GetValue(id)
            status_list.append(float(status))
        
        cell_boundary_status.append(status_list)

    t3_stop = perf_counter()


    collection_arr = list(zip(critical_point_ids, critical_point_cell_ids, critical_point_cell_boundary_ids, critical_point_status, cell_boundary_status))


    pd.DataFrame(collection_arr).to_csv("status.csv", header=["Point ID", "Cell ID", "Cell Boundary IDs", "Status Point", "Status Boundary"], index=False)
    
    print(f"\n\nElapsed time to load data: {t1_stop - t1_start} seconds")
    print(f"\n\nElapsed time to find IDs: {t2_stop - t2_start} seconds")
    print(f"\n\nElapsed time to find Status of IDs: {t3_stop - t3_start} seconds")

if __name__ == '__main__':
    main()







