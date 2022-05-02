from time import perf_counter, sleep

import numpy as np

from seedpoint_generator_helper.seedpoint_generator import SeedpointGenerator, Template
from seedpoint_processor_helper.seedpoint_processor import EarthSide, SeedpointProcessor, FieldlineStatus
from vectorfieldtopology_helper.helpers import get_sphere_actor
from vectorfieldtopology_helper.vectorfieldtopology import VectorFieldTopology
from vtk_visualization_helper.helpers import start_window



def main():
    # # ###################### PART 1: Find critical points #############################
    filename = 'data/3d__var_2_e20000101-020000-000.dat'
    #filename = 'data/cut_mhd_3_e20000101-020000-000.dat'
    #filename = 'data/cut_mhd_2_e20000101-020000-000.dat'
    #filename = 'data/experiment/med_res_negbz_and_noise.vtu'

    t1_start = perf_counter()
    vft = VectorFieldTopology()
    vft.read_file(filename, rename_header=False)
    vft.update_vectorfield_from_scalars('bx','by','bz')
    #vft.update_vectorfield_from_scalars(scalar_name_x="bx_noise", scalar_name_y="by_noise", scalar_name_z="bz_noise")
    vft.update_topology_object()
    vft.update_critical_points()
    vft.remove_critical_points_in_sphere(radius=3, center=(0,0,0))
    vft.save_critical_points_to_file()
    vft.update_list_of_actors(show_critical_points=True, show_separator=False, show_vectorfield=False)
    vft.visualize()
    t1_stop = perf_counter()

    # # ########################## PART 2: GENERATE SEEDPOINTS ################################

    t2_start = perf_counter()
    sp_generator = SeedpointGenerator(vft.critical_points_info, Template.SMART)
    sp_generator.update_seed_points()
    sp_generator.save_seedpoints_to_file()
    sp_generator.visualize()
    t2_stop = perf_counter()

    ########################## PART 3: PROCESS SEEDPOINTS ################################
    t3_start = perf_counter()
    sp_processor = SeedpointProcessor(sp_generator.seed_points, vft.vectorfield)
    sp_processor.generate_seedpoint_info_csv()
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.IMF)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.CLOSED)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.OPEN_NORTH)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.OPEN_SOUTH)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.IMF)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.CLOSED)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.OPEN_NORTH)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.OPEN_SOUTH)
    t3_stop = perf_counter()

    print(f"Program executed in {t3_stop-t1_start} seconds")

if __name__ == '__main__':
    main()
   
    