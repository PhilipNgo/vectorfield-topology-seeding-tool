# Vector field topology object. Used in update_topology_object()
INTEGRATION_STEP_UNIT = 1
SEPARATRIX_DISTANCE = 1
INTEGRATION_STEP_SIZE = 1
MAX_NUM_STEPS = 3000

# Used in save_critical_points_to_file()
TYPES = dict([
    (-1, 'DEGENERATE_3D'),
    (0,'SINK_3D'),
    (1,'SADDLE_1_3D'),
    (2,'SADDLE_2_3D'),
    (3,'SOURCE_3D'),
    (4,'CENTER_3D')
])

DETAILED_TYPES = dict([
     (0,'ATTRACTING_NODE_3D'),
     (1,'ATTRACTING_FOCUS_3D'),
     (2,'NODE_SADDLE_1_3D'),
     (3,'FOCUS_SADDLE_1_3D'),
     (4,'NODE_SADDLE_2_3D'),
     (5,'FOCUS_SADDLE_2_3D'),
     (6,'REPELLING_NODE_3D'),
     (7,'REPELLING_FOCUS_3D'),
     (8,'CENTER_DETAILED_3D')
]) 

