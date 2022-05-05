from time import perf_counter, sleep

import numpy as np

from seedpoint_generator_helper.seedpoint_generator import SeedpointGenerator, Template
from seedpoint_processor_helper.seedpoint_processor import EarthSide, SeedpointProcessor, FieldlineStatus
from vectorfieldtopology_helper.helpers import get_sphere_actor
from vectorfieldtopology_helper.vectorfieldtopology import VectorFieldTopology
from vtk_visualization_helper.helpers import start_window

import pandas as pd

def main():
    # # ###################### PART 1: Find critical points #############################

    filename = 'data/3d__var_2_e20000101-020000-000.dat'
    # filename = 'data/3d__var_2_e20000101-020000-000_high.dat'
    #filename = 'data/cut_mhd_3_e20000101-020000-000.dat'
    #filename = 'data/cut_mhd_2_e20000101-020000-000.dat'
    #filename = 'data/experiment/med_res_negbz_and_noise.vtu'

    t1_start = perf_counter()
    vft = VectorFieldTopology()
    vft.read_file(filename, rename_xyz=False)
    vft.update_vectorfield_from_scalars('B_x [nT]','B_y [nT]','B_z [nT]')
    #vft.update_vectorfield_from_vectors(vectorfield=vft.data_object)
    # vft.update_vectorfield_from_scalars(scalar_name_x="bx_noise", scalar_name_y="by_noise", scalar_name_z="bz_noise")
    vft.update_topology_object()
    vft.update_critical_points()
    vft.remove_critical_points_in_sphere(radius=3, center=(0,0,0))
    vft.save_critical_points_to_file()
    # vft.update_list_of_actors(show_critical_points=True, show_separator=False, show_vectorfield=False)
    # vft.visualize()
    t1_stop = perf_counter()

    print(f"\nPart 1 executed in {t1_stop-t1_start} seconds")

    # ########################## PART 2: GENERATE SEEDPOINTS ################################

    t2_start = perf_counter()
    sp_generator = SeedpointGenerator()
    # sp_generator.load_critical_point_info('critical_points/critical_point_info.csv')
    sp_generator.set_critical_point_info(vft.critical_points_info)
    sp_generator.set_template(Template.SPHERICAL)
    sp_generator.update_seed_points()
    sp_generator.save_seed_points_to_file()
    sp_generator.visualize()
    t2_stop = perf_counter()

    # print(f"\nPart 2 executed in {t2_stop-t2_start} seconds")

    ######################### PART 3: PROCESS SEEDPOINTS ################################
    t3_start = perf_counter()

    sp_processor = SeedpointProcessor()
    sp_processor.set_seed_critical_pair(sp_generator.seed_critical_pair)
    sp_processor.set_vector_field_domain(vft.vectorfield)
    sp_processor.update_seed_point_info()
    sp_processor.remove_useless_seed_points(level=0)
    sp_processor.filter_seeds(side=EarthSide.DAYSIDE, status=FieldlineStatus.IMF)
    sp_processor.save_seed_point_info_to_file()
    sp_processor.save_seed_points_to_file() 
    sp_processor.visualize()
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.IMF)
    # sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.CLOSED)
    # sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.OPEN_NORTH)
    # sp_processor.visualize(side=EarthSide.DAYSIDE, status=FieldlineStatus.OPEN_SOUTH)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.IMF)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.CLOSED)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.OPEN_NORTH)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=FieldlineStatus.OPEN_SOUTH)
    t3_stop = perf_counter()

    print(f"\nPart 3 executed in {t3_stop-t3_start} seconds")

    print(f"\nFull program executed in {t3_stop-t1_start} seconds")

if __name__ == '__main__':
    main()
   
    