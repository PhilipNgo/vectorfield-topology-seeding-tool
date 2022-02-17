from cdflib import cdfread

import argparse
import numpy as np
import sys

import vtk
from vtk.util.numpy_support import numpy_to_vtk

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_cdf_file",
                        type = str,
                        help = "The input .cdf file name")
    parser.add_argument("output_vtk_file",
                        type = str,
                        help = "The output .vtu file generated with 3D Delaunay triangulation")
                        
    args = parser.parse_args()
    cdf_file_name = args.input_cdf_file
    vtk_file_name = args.output_vtk_file

    cdf_file = cdfread.CDF(cdf_file_name)
    if (cdf_file.file == None):
        print("Could not load CDF file. Exiting ...")
        sys.exit(1)
    
    info = cdf_file.cdf_info()

    globalaAttrs = cdf_file.globalattsget(expand=True)
    zvars = info['zVariables']
    #print('no of zvars=', len(zvars))

    outputVTK = vtk.vtkPolyData()

    xData = cdf_file.varget(variable="x")[0]
    yData = cdf_file.varget(variable="y")[0]
    zData = cdf_file.varget(variable="z")[0]
    pts = np.column_stack([xData, yData, zData])
    vtkPts = vtk.vtkPoints()
    vtkPts.SetData(numpy_to_vtk(pts, deep=True))
    
    outputVTK.SetPoints(vtkPts)

    bxData = cdf_file.varget(variable="bx")[0]
    byData = cdf_file.varget(variable="by")[0]
    bzData = cdf_file.varget(variable="bz")[0]
    bData = np.column_stack([bxData, byData, bzData]).ravel()
    bVTK = numpy_to_vtk(bData, deep=True)
    bVTK.SetName("magnetic_field")
    bVTK.SetNumberOfComponents(3)

    uxData = cdf_file.varget(variable="ux")[0]
    uyData = cdf_file.varget(variable="uy")[0]
    uzData = cdf_file.varget(variable="uz")[0]
    uData = np.column_stack([uxData, uyData, uzData]).ravel()
    uVTK = numpy_to_vtk(uData, deep=True)
    uVTK.SetName("velocity")
    uVTK.SetNumberOfComponents(3)

    pData = cdf_file.varget(variable="p")[0]
    pVTK = numpy_to_vtk(pData, deep=True)
    pVTK.SetName("pressure")

    rhoData = cdf_file.varget(variable="rho")[0]
    rhoVTK = numpy_to_vtk(rhoData, deep=True)
    rhoVTK.SetName("rho")

    eData = cdf_file.varget(variable="e")[0]
    eVTK = numpy_to_vtk(eData, deep=True)
    eVTK.SetName("e")

    outputVTK.GetPointData().AddArray(bVTK)
    outputVTK.GetPointData().AddArray(uVTK)
    outputVTK.GetPointData().AddArray(pVTK)
    outputVTK.GetPointData().AddArray(rhoVTK)
    outputVTK.GetPointData().AddArray(eVTK)

    #writer = vtk.vtkXMLPolyDataWriter()
    #writer.SetFileName(vtk_file_name)
    #writer.SetInputData(outputVTK)
    #writer.Write()

    #print("Data generated and written to file ....")

    delaunay = vtk.vtkDelaunay3D()
    delaunay.SetInputData(outputVTK);

    writer = vtk.vtkXMLUnstructuredGridWriter()
    writer.SetFileName(vtk_file_name)
    writer.SetInputConnection(delaunay.GetOutputPort())
    writer.Write()

    #from scipy.spatial import Delaunay
    #tri = Delaunay(pts)
    #print(tri.simplices)

    print("Delaunay triangulation generated and written to file ...")

    cdf_file.close()

