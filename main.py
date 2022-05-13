from fileinput import filename
from time import perf_counter, sleep

import numpy as np

from criticalpoint_processor.criticalpoint_processor import CriticalPointProcessor
from seedpoint_generator.seedpoint_generator import SeedpointGenerator, Template
from seedpoint_processor.seedpoint_processor import EarthSide, SeedpointProcessor, FieldlineStatus
from vectorfieldtopology.vectorfieldtopology import VectorFieldTopology
from vtk_visualization.helpers import start_window

import pandas as pd

def main():
    # # ###################### PART 1: Find critical points #############################

    #filename = 'data/3d__var_2_e20000101-020000-000.dat'
    # filename = 'data/3d__var_2_e20000101-020000-000_high.dat'
    #filename = 'data/cut_mhd_3_e20000101-020000-000.dat'
    filename = 'data/cut_mhd_2_e20000101-020000-000.dat'
    #filename = 'data/experiment/med_res_negbz_and_noise.vtu'
    #filename = 'data/experiment/med_res_flipped_coordsx_bx_inv.vtu'
    #filename = 'data/3d__var_2_e20000101-020000-000_nonsym.dat'

    t1_start = perf_counter()
    vft = VectorFieldTopology()
    vft.read_file(filename, rename_xyz=True)
    #vft.update_vectorfield_from_scalars('inv_bx','by','bz')
    vft.update_vectorfield_from_scalars('B_x [nT]','B_y [nT]','B_z [nT]')
    #vft.update_vectorfield_from_vectors(vectorfield=vft.data_object)
    vft.update_topology_object()
    vft.update_critical_points()
    vft.remove_critical_points_in_sphere(radius=3, center=(0,0,0))
    vft.save_critical_points_to_file()
    # vft.update_list_of_actors(show_critical_points=True, show_separator=False, show_vectorfield=False)
    # vft.visualize()
    # t1_stop = perf_counter()

    # #print(f"\nPart 1 executed in {t1_stop-t1_start} seconds")

    # # ########################## PART 2: PROCESS CRITICAL POINTS ##########################
    #cp_processor = CriticalPointProcessor()
    #cp_processor.set_critical_points_info(vft.critical_points_info)
    # cp_processor.load_critical_points_info('critical_points/critical_points_info.csv')
    #cp_processor.filter_critical_points_by_types(['SADDLE_2_3D','SADDLE_1_3D'])
    #cp_processor.filter_critical_points_by_detailed_types(['NODE_SADDLE_1_3D'])
    # cp_processor.save_critical_points_to_file()
    #cp_processor.update_list_of_actors()
    #cp_processor.visualize()
    # cp_processor.visualize_detailed_types(['NODE_SADDLE_1_3D'])
    # # cp_processor.visualize_detailed_types(['FOCUS_SADDLE_1_3D'])
    # # cp_processor.visualize_detailed_types(['NODE_SADDLE_2_3D'])
    # # cp_processor.visualize_detailed_types(['FOCUS_SADDLE_2_3D'])


    # # ########################## PART 3: GENERATE SEEDPOINTS ################################

    # # t2_start = perf_counter()
    sp_generator = SeedpointGenerator()
    # # sp_generator.load_critical_point_info('critical_points/critical_point_info.csv')
    sp_generator.set_critical_point_info(vft.critical_points_info)
    sp_generator.set_template(Template.SPHERICAL)
    # #sp_generator.set_custom_template('template.txt')
    sp_generator.update_seed_points()
    # sp_generator.save_seed_points_to_file()
    #sp_generator.visualize()
    # # t2_stop = perf_counter()

    # # print(f"\nPart 2 executed in {t2_stop-t2_start} seconds")

    # ######################### PART 4: PROCESS SEEDPOINTS ################################
    # t3_start = perf_counter()

    sp_processor = SeedpointProcessor()
    sp_processor.set_seed_critical_pair(sp_generator.seed_critical_pair)
    sp_processor.set_vector_field_domain(vft.vectorfield)
    sp_processor.update_seed_point_info()
    #sp_processor.remove_useless_seed_points(level=1)
    #sp_processor.filter_seeds(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.CLOSED.value)
    # sp_processor.save_seed_point_info_to_file()
    # sp_processor.save_seed_points_to_file() 
    sp_processor.visualize()
    # sp_processor.visualize(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.CLOSED.value)
    # sp_processor.visualize(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.CLOSED.value)
    # sp_processor.visualize(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.OPEN_NORTH.value)
    # sp_processor.visualize(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.OPEN_SOUTH.value)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE.value, status=FieldlineStatus.IMF.value)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE.value, status=FieldlineStatus.CLOSED.value)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE.value, status=FieldlineStatus.OPEN_NORTH.value)
    # sp_processor.visualize(side=EarthSide.NIGHTSIDE.value, status=FieldlineStatus.OPEN_SOUTH.value)
    # t3_stop = perf_counter()

    # print(f"\nPart 3 executed in {t3_stop-t3_start} seconds")

    # print(f"\nFull program executed in {t3_stop-t1_start} seconds")

if __name__ == '__main__':
    main()
   
    