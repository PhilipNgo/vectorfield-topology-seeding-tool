import csv
import logging
from typing import Dict, List, Tuple
from enum import Enum, auto

import pandas as pd
from vectorfieldtopology import constants, helpers
from vtk import vtkUnstructuredGrid, vtkTecplotReader, vtkVectorFieldTopology, vtkImageData, vtkArrayCalculator, vtkActor, vtkXMLUnstructuredGridReader
from vtkmodules.util.numpy_support import vtk_to_numpy
import os
import numpy as np
from vtk_visualization import helpers as vtk_helper
import warnings

logging.basicConfig(level=logging.INFO)

class CriticalPoint(Enum):
    X = float
    Y = float
    Z = float
    GRADIENT = auto()
    DETAILED_TYPE = int

class CriticalPointInfo(Enum):
    x = float
    y = float
    z = float
    gradient = auto()
    type = int
    type_text = str
    detailed_type = int
    detailed_type_text = str


class VectorFieldTopology():
    def __init__(self) -> None:
        self.critical_points: List[Tuple[float, float, float]] = []
        self.critical_points_info: List[CriticalPointInfo] = []
        self.list_of_actors = []
        self.data_object = vtkUnstructuredGrid()
        self.vectorfield = vtkImageData()
        self.topology_object = vtkVectorFieldTopology()
        self.is_debug = False
        self.sphere_removed_actor = vtkActor()

    def set_debug(self, value:bool) -> None:
        """Sets the debug status of the class.
        :value: True or False (Boolean)
        """
        self.is_debug = value

    def read_file(self, filename:str, rename_xyz:bool = False) -> None:
        """
        Reads file and creates vectorfield from given scalars. Able to process .dat and .vtu files.
        :filename: Path to file (String)
        """
        # Write this if statement to rename the file header before opening it with vtk, since vtk needs X,Y,Z variables.
        if(rename_xyz):
            a_file = open(filename, "r")
            list_of_lines = a_file.readlines()
            list_of_lines[1] = list_of_lines[1].replace("X [R]", "X").replace("Y [R]", "Y").replace("Z [R]", "Z")

            a_file = open(filename, "w")
            a_file.writelines(list_of_lines)
            a_file.close()
        
        if(os.path.exists(filename)):
        
            if(filename.endswith('.dat')):
                reader = vtkTecplotReader()
                reader.SetFileName(filename)
                reader.Update()
                self.data_object.ShallowCopy(reader.GetOutput().GetBlock(0))
                logging.info("Read file done.") 

            elif(filename.endswith('.vtu')):
                reader = vtkXMLUnstructuredGridReader()
                reader.SetFileName(filename)
                reader.Update()
                self.data_object.ShallowCopy(reader.GetOutput())
                logging.info("Read file done.") 

        else:
            raise FileNotFoundError()

    def update_vectorfield_from_scalars(self, scalar_name_x:str, scalar_name_y:str, scalar_name_z:str, noise_factor:float=0.0) -> None:
        """Returns vectorfield data
        :scalar_name_x: Name of x component (String)
        :scalar_name_y: Name of y component (String)
        :scalar_name_z: Name of z component (String)
        """

        # Create new vectorfield from scalars
        vecFieldCalc = vtkArrayCalculator()
        vecFieldCalc.SetInputData(self.data_object)
        vecFieldCalc.AddScalarArrayName(scalar_name_x)
        vecFieldCalc.AddScalarArrayName(scalar_name_y)
        vecFieldCalc.AddScalarArrayName(scalar_name_z)
        
        # TODO: Remove or not??
        #noise_string = f"(sqrt({scalar_name_x}^2+{scalar_name_y}^2+{scalar_name_z}^2)*{noise_factor})" # delta b = mag*noise_percent
        #bx_string = f"({scalar_name_x}+{noise_string}/{scalar_name_x})*iHat"
        #by_string = f"({scalar_name_y}+{noise_string}/{scalar_name_y})*jHat"
        #bz_string = f"({scalar_name_z}+{noise_string}/{scalar_name_z})*kHat"

        if((' ' in scalar_name_x) == True):
            scalar_name_x = f'"{scalar_name_x}"'
        if((' ' in scalar_name_y) == True):
            scalar_name_y = f'"{scalar_name_y}"'
        if((' ' in scalar_name_z) == True):
            scalar_name_z = f'"{scalar_name_z}"'
        
        vecFieldCalc.SetFunction(f'{scalar_name_x}*iHat+{scalar_name_y}*jHat+{scalar_name_z}*kHat')
        vecFieldCalc.SetResultArrayName("Vectorfield")
        vecFieldCalc.Update()

        self.vectorfield = vecFieldCalc.GetOutput()

    def update_vectorfield_from_vectors(self, vectorfield: vtkImageData) -> None:
        """Returns vectorfield data
        :vectorfield: vtkImageData or vtkUnstructuredGrid
        """
        self.vectorfield = vectorfield

    def update_topology_object(self) -> None:
        """Updates vector field topology object. Contains only critical points now.
        """
        self.topology_object.SetInputData(self.vectorfield)
        self.topology_object.SetIntegrationStepUnit(constants.INTEGRATION_STEP_UNIT)
        self.topology_object.SetSeparatrixDistance(constants.SEPARATRIX_DISTANCE)
        self.topology_object.SetIntegrationStepSize(constants.INTEGRATION_STEP_SIZE)
        self.topology_object.SetMaxNumSteps(constants.MAX_NUM_STEPS)
        self.topology_object.SetComputeSurfaces(False)
        self.topology_object.SetUseBoundarySwitchPoints(False)
        self.topology_object.SetUseIterativeSeeding(True) # See if the simple (fast) or iterative (correct version)
        self.topology_object.SetExcludeBoundary(True)
        self.topology_object.Update()

        logging.info("Updated topology object.") 

    def update_critical_points(self) -> None:
        """ Set the critical points property self.critical_points
        """

        critical_points = vtk_to_numpy(self.topology_object.GetOutput(0).GetPoints().GetData())
        gradients = vtk_to_numpy(self.topology_object.GetOutput(0).GetPointData().GetArray(0))
        types = vtk_to_numpy(self.topology_object.GetOutput(0).GetPointData().GetArray(1))
        detailed_types = vtk_to_numpy(self.topology_object.GetOutput(0).GetPointData().GetArray(2))
        
        self.critical_points.clear() # Empty list in case there are already values in it.
        self.critical_points_info.clear()

        for critial_point, gradient, cp_type, detail_type in zip(critical_points, gradients, types, detailed_types):

            # Fill critical point info list
            self.critical_points_info.append({
                'X': critial_point[0],
                'Y': critial_point[1],
                'Z': critial_point[2],
                'Gradient': np.array(gradient),
                'Type': cp_type,
                'Type_text': str(constants.TYPES[int(cp_type)]),
                'Detailed_type': detail_type,
                'Detailed_type_text': str(constants.DETAILED_TYPES[int(detail_type)])
            })

            # Fill critical points list
            self.critical_points.append(critial_point)
        
        logging.info(f"Updated critical points.")

    
    def remove_critical_points_in_sphere(self, radius:float, center:Tuple[float, float, float]) -> None:

        initial_size = len(self.critical_points)
        list_of_indices_to_keep = []

        for ind, critical_point in enumerate(self.critical_points):

            sx, sy, sz = critical_point
            ex, ey, ez = center

            is_inside = ((sx-ex)**2+(sy-ey)**2+(sz-ez)**2 <= radius**2)

            if(not is_inside):
                list_of_indices_to_keep.append(ind)

        # Keep indices of interest and remove the rest.
        self.critical_points = [self.critical_points[x] for x in list_of_indices_to_keep]
        self.critical_points_info = [self.critical_points_info[x] for x in list_of_indices_to_keep]

        # Update sphere removed actor 
        if(radius > 0):
            self.sphere_removed_actor = helpers.get_sphere_actor(radius=radius, center=center)

        logging.info(f"Removed {initial_size-len(self.critical_points)} critical points.")
        

    def save_critical_points_to_file(self) -> None:
        """
        Creates critical_points directory with critical points as txt file and critical point information as a csv file
        """
        dirName = 'critical_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        keys = self.critical_points_info[0].keys()

        try:
            with open(f'{dirName}/critical_points_info.csv', mode='w',encoding='utf8', newline='') as output_to_csv:
                dict_csv_writer = csv.DictWriter(output_to_csv, fieldnames=keys, dialect='excel')
                dict_csv_writer.writeheader()
                dict_csv_writer.writerows(self.critical_points_info)

            # TODO: Remove this, is for debugging in paraview.
            df = pd.read_csv(f'{dirName}/critical_points_info.csv')
            df.drop('Gradient', inplace=True, axis=1)
            df.to_csv(f'{dirName}/critical_points_info_no_gradient.csv', index=False)
            # ===========================================================
            
            np.savetxt(f"{dirName}/critical_points.txt", self.critical_points, fmt='%1.5f')
            logging.info(f"Saved critical point files.")
        except IOError as io:
            print('\n',io)

    def update_list_of_actors(self, show_critical_points:bool=True, show_separator:bool=False, show_vectorfield:bool=False) -> None:
        """
        Updates the list of actors with actors that have the current data. Possible to trigger seperate actors.
        :show_critical_points: Boolean on wether to show critical points or not.
        :show_saperator: Boolean on wether to show separator or not.
        :show_vectorfield: Boolean on wether to show vectorfield or not.
        """

        self.list_of_actors.clear()

        if(show_critical_points):
            critical_point_actor = helpers.get_critical_point_actor(self.topology_object)
            self.list_of_actors.append(critical_point_actor)

        if(show_separator):
            separator_actor = helpers.get_separator_actor(self.topology_object)
            self.list_of_actors.append(separator_actor)

        if(show_vectorfield):
            vectorfield_actor = helpers.get_vector_field_actor(self.vectorfield)
            self.list_of_actors.append(vectorfield_actor)

        self.list_of_actors.append(self.sphere_removed_actor)


    def visualize(self) -> None:
        """Starts the rendering"""
        if(len(self.list_of_actors) == 0):
            warnings.warn("List of actors is empty. Make sure to update the list of actors with the function update_list_of_actors()")

        vtk_helper.start_window(self.list_of_actors)



        

