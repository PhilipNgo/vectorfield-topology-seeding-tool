from vtk import vtkArrayCalculator, vtkRTAnalyticSource, vtkUnstructuredGrid, vtkTecplotReader
from generate_seedpoint_helper import generate_seedpoints
from data_process_helper import remove_earth_cp
from vectorfieldtopology_helper import plot_vectorfield_topology, rename_tecplot_header

def main():

    ####################### PART 1: Find critical points #############################
    # Create bounding box
    s = vtkRTAnalyticSource()
    factor = 3
    s.SetWholeExtent(-10*factor, 10*factor, -10*factor, 10*factor, -10*factor, 10*factor)

    filename = 'data/lowres_sample_data/cut_mhd_2_e20000101-020000-000.dat'

    # Rename X, Y, Z bx, by, bz in the .dat file 
    # rename_tecplot_header(filename=filename)

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

    input("Part 1 done, press any key to continue")


    #################### PART 2: REMOVE UNWANTED CRITICAL POINTS #########################

    fake_earth_center = [5.4609, -11.454, -0.00042683] # Earths coordinate x,y,z
    x, y, z = fake_earth_center
    infile_cp = "seedpoints/criticalpoints.txt"
    outfile_cp = "seedpoints/criticalpoints_no_earth.txt"

    remove_earth_cp(x=x,y=y,z=z,radius=0.5,infile=infile_cp, outfile=outfile_cp)
    
    input("Part 2 done, press any key to continue")


    #################### PART 3: GENERATE SEEDPOINTS #########################

    infile_seedpoint = outfile_cp
    outfile_seedpoint = "seedpoints/seedpoints.txt"

    generate_seedpoints(infile=infile_seedpoint, outfile=outfile_seedpoint, visualize=True)

    input("Part 3 done, press any key to continue")


if __name__ == '__main__':
    main()