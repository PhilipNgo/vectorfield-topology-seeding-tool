from criticalpoint_processor.criticalpoint_processor import CriticalPointProcessor
from seedpoint_generator.seedpoint_generator import SeedpointGenerator, Template
from seedpoint_processor.seedpoint_processor import EarthSide, SeedpointProcessor, FieldlineStatus
from vectorfieldtopology.vectorfieldtopology import VectorFieldTopology
from vtk_visualization.helpers import start_window


def main():
    ####################### PART 1: Find critical points #############################

    filename = 'data/cut_mhd_2_e20000101-020000-000.dat'
    
    vft = VectorFieldTopology()
    vft.read_file(filename, rename_xyz=True)
    vft.update_vectorfield_from_scalars('B_x [nT]','B_y [nT]','B_z [nT]')
    vft.update_topology_object()
    vft.update_critical_points()
    vft.remove_critical_points_in_sphere(radius=3, center=(0,0,0))
    vft.save_critical_points_to_file()
    vft.update_list_of_actors(show_critical_points=True, show_separator=False, show_vectorfield=False)
    vft.visualize()
    

    ########################### PART 2: PROCESS CRITICAL POINTS ##########################
    cp_processor = CriticalPointProcessor()
    cp_processor.set_critical_points_info(vft.critical_points_info)
    cp_processor.filter_critical_points_by_types(['SADDLE_2_3D','SADDLE_1_3D'])
    cp_processor.update_list_of_actors()
    cp_processor.visualize()

    ########################## PART 3: GENERATE SEEDPOINTS ################################

    sp_generator = SeedpointGenerator()
    sp_generator.set_critical_point_info(cp_processor.critical_points_info)
    sp_generator.set_template(Template.SPHERICAL)
    sp_generator.update_seed_points()
    sp_generator.save_seed_points_to_file()
    sp_generator.visualize()
    
    # ######################### PART 4: PROCESS SEEDPOINTS ################################

    sp_processor = SeedpointProcessor()
    sp_processor.set_seed_critical_pair(sp_generator.seed_critical_pair)
    sp_processor.set_vector_field_domain(vft.vectorfield)
    sp_processor.update_seed_point_info()
    sp_processor.save_seed_point_info_to_file()
    sp_processor.save_seed_points_to_file() 
    sp_processor.visualize()
    sp_processor.visualize(side=EarthSide.DAYSIDE.value, status=FieldlineStatus.CLOSED.value)
    sp_processor.visualize(side=EarthSide.NIGHTSIDE.value, status=FieldlineStatus.CLOSED.value)

if __name__ == '__main__':
    main()
   
    
   
    