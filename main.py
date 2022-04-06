from matplotlib.pyplot import grid
from vtk import vtkArrayCalculator, vtkRTAnalyticSource, vtkUnstructuredGrid, vtkTecplotReader, vtkXMLUnstructuredGridWriter, vtkXMLImageDataReader
from generate_seedpoint_helper import generate_seedpoints, generate_seedpoints_with_all_eigen_plane, generate_seedpoints_with_plane
from data_process_helper import generate_status, remove_unwanted_critical_points
from vectorfieldtopology_helper import add_inverted_data, add_j_cross_b, find_topological_features, get_vector_field, rename_tecplot_header
from time import perf_counter, sleep 
import logging

# Configure logging information
logging.basicConfig(level=logging.INFO)

def main():

    ###################### PART 1: Find critical points #############################

    # Timer
    t1_start = perf_counter()

    # Create bounding box
    filename = 'data/lowres_sample_data/cut_mhd_2_e20000101-020000-000.dat'
    # filename = 'data/highres_sample_data/cut_mhd_3_e20000101-020000-000.dat' # 600k cells
    # filename = 'data/highres_sample_data/3d__var_2_e20000101-020000-000.dat' # 10 mil cells
    # filename = 'data/highres_sample_data_new/3d__var_2_e20000101-020000-000.dat' #30 sek


    # Rename X, Y, Z bx, by, bz in the .dat file 
    # rename_tecplot_header(filename=filename, large_file=True)

    reader = vtkTecplotReader()
    reader.SetFileName(filename)
    reader.Update()

    t1_stop = perf_counter() 
    
    # Timer
    t2_start = perf_counter()

    # # Create unstructured grid
    out = vtkUnstructuredGrid()
    out.ShallowCopy(reader.GetOutput().GetBlock(0))
    vecFieldCalc = get_vector_field("bx", "by", "bz", out, "magneticfield")

    t2_stop = perf_counter() 

    t3_start = perf_counter() 

    find_topological_features(vectorfield=vecFieldCalc, visualize=True, show_critical_points = True, show_separator = False, 
    show_vectorfield = True, show_separating_surface = False, show_boundary_switch = False, 
    scale=2, max_points = 2000, debug = True, write_file = True)

    t3_stop = perf_counter() 

    logging.info("Part 1 done (Find critical points)") 
    logging.info(f"Elapsed time to load data: {t1_stop - t1_start} seconds")
    logging.info(f"Elapsed time to calculate vectorfield data: {t2_stop - t2_start} seconds") 
    logging.info(f"Elapsed time to find critical points: {t3_stop - t3_start} seconds\n\n") 

    #################### PART 2: REMOVE UNWANTED CRITICAL POINTS #########################

    t4_start = perf_counter() 

    earth_center = [0, 0, 0] # Earths coordinate x,y,z
    radius = 3
    x, y, z = earth_center
    infile_cp = "criticalpoints.txt"

    remove_unwanted_critical_points(x=x,y=y,z=z, radius=radius, infile=infile_cp, indir="unprocessed_data", outdir="processed_data", visualize=True)

    t4_stop = perf_counter()

    logging.info("Part 2 done (Remove unwanted critical points)") 
    logging.info(f"Elapsed time to remove unwanted critical points: {t4_stop - t4_start} seconds\n\n") 

    ########################## PART 3: GENERATE SEEDPOINTS ################################

    t5_start = perf_counter() 

    # Generate spherical seedpoints
    infile_critical_point = f"processed_data/processed_criticalpoints.txt"
    outfile_seedpoint = f"seedpoints.txt"

    generate_seedpoints(infile=infile_critical_point, outfile=outfile_seedpoint, visualize=True)

    
    # # Generate plane seedpoints
    infile = f'processed_data/processed_gradient.txt'
    outfile = f'seedpoints_plane.txt'
    critical_point_infile = 'processed_data/processed_criticalpoints.txt'

    generate_seedpoints_with_plane(infile, critical_point_infile, outfile, visualize=True, vectorfield=None)

    # Generate planes
    infile = f'processed_data/processed_gradient.txt'
    outfile = f'seedpoints_eigen_as_normal_plane.txt'
    critical_point_infile = 'processed_data/processed_criticalpoints.txt'
    generate_seedpoints_with_all_eigen_plane(infile, critical_point_infile, outfile, visualize=True, vectorfield=None)

    t5_stop = perf_counter() 

    logging.info("Part 3 done (Seedpoint generation)") 
    logging.info(f"Elapsed time to generate seed points from critical points: {t5_stop - t5_start} seconds\n\n") 


    # # # ########################### PART 4: GENERATE STATUS ################################
    # t6_start = perf_counter() 

    # generate_status(grid=out, outfile="processed_data/status.csv", critical_point_infile=critical_point_infile)
    
    # t6_stop = perf_counter() 
    # logging.info("Part 4 done (status generation)") 
    # logging.info(f"Elapsed time to generate status.csv: {t6_stop - t6_start} seconds\n\n") 
    # logging.info(f"Elapsed time for whole program: {t6_stop - t1_start} seconds\n\n")





if __name__ == '__main__':
    main()