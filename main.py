from time import perf_counter, sleep

import numpy as np

from seedpoint_generator_helper.seedpoint_generator import SeedpointGenerator, Template
from seedpoint_processor_helper.seedpoint_processor import EarthSide, SeedpointProcessor, StreamlineStatus
from vectorfieldtopology_helper.helpers import get_sphere_actor
from vectorfieldtopology_helper.vectorfieldtopology import VectorFieldTopology
from vtk_visualization_helper.helpers import start_window



def main():
    # # ###################### PART 1: Find critical points #############################
    filename = 'data/3d__var_2_e20000101-020000-000.dat'
    # filename = 'data/cut_mhd_3_e20000101-020000-000.dat'
    # # filename = 'data/cut_mhd_2_e20000101-020000-000.dat'

    t1_start = perf_counter()
    vft = VectorFieldTopology()
    vft.read_file(filename)
    vft.update_vectorfield('bx','by','bz')
    vft.update_topology_object()
    vft.update_critical_points()
    vft.remove_critical_points_in_sphere(radius=3, center=(0,0,0))
    vft.save_critical_points_to_file()
    vft.update_list_of_actors()
    #vft.visualize()
    t1_stop = perf_counter()

    # # ########################## PART 2: GENERATE SEEDPOINTS ################################

    t2_start = perf_counter()
    sp_generator = SeedpointGenerator(vft.critical_points_info, Template.SPHERICAL)
    sp_generator.update_seed_points()
    sp_generator.save_seedpoints_to_file()
    #sp_generator.visualize()
    t2_stop = perf_counter()

    ########################## PART 3: PROCESS SEEDPOINTS ################################
    t3_start = perf_counter()
    #seedpoints = np.loadtxt('seed_points/seed_points.txt')
    sp_processor = SeedpointProcessor(sp_generator.seed_points, vft.vectorfield)
    sp_processor.generate_seedpoint_info_csv()
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=StreamlineStatus.IMF)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=StreamlineStatus.CLOSED)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=StreamlineStatus.OPEN_NORTH)
    sp_processor.visualize(side=EarthSide.DAYSIDE, status=StreamlineStatus.OPEN_SOUTH)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=StreamlineStatus.IMF)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=StreamlineStatus.CLOSED)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=StreamlineStatus.OPEN_NORTH)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE, status=StreamlineStatus.OPEN_SOUTH)
    t3_stop = perf_counter()

if __name__ == '__main__':
    main()
   
    