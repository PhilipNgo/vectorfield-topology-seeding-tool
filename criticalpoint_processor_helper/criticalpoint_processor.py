

import csv
from enum import Enum
import logging
import os
from typing import Dict, List
import warnings

import numpy as np
import pandas as pd
import criticalpoint_processor_helper.helpers as helpers
from vtk_visualization_helper import helpers as vtk_helper
from vectorfieldtopology_helper.constants import TYPES, DETAILED_TYPES 

class CriticalPointProcessor:

    def __init__(self):
        
        self.critical_points_info = []
        self.critical_points = []
        self.list_of_actors = []

    def load_critical_points_info(self, critical_points_info_filename:str):
        """Loads critical point info from csv file"""

        if(os.path.exists(critical_points_info_filename)):
            df = pd.read_csv('critical_points/critical_points_info.csv')
            self.critical_points_info = df.to_dict('records')
            self.critical_points = [[x['X'], x['Y'], x['Z']] for x in self.critical_points_info]
        else:
            raise FileNotFoundError("File not found..")
        
    def set_critical_points_info(self, critical_points_info:List[Dict]):
        """Sets the critical point info"""
        self.critical_points_info = critical_points_info

    def __filter_according_to(self, key:str, possible_types:List[str], wanted_types:List[str])-> List[Dict]:

        if(set(wanted_types).issubset(set(possible_types))):
            df = pd.DataFrame(self.critical_points_info)
            df = df[df[key].isin(wanted_types)]
            return df.to_dict('records')
        else:
            raise ValueError(f"List of types is not a subset of {list(possible_types)}")


    def filter_critical_points_by_types(self, list_of_types: List[str]) -> None:
        """
        Filters the critical points by a certain type or types. 
        :list_of_types: List containing the types we want to keep.  
        """

        if(len(self.critical_points_info) == 0):
            raise IndexError("Critical point info is empty.. Run the set_critical_points_info() or load_critical_points_info()")
        
        self.critical_points_info = self.__filter_according_to(key='Type_text', possible_types=list(TYPES.values()), wanted_types=list_of_types)
        self.critical_points = [[x['X'], x['Y'], x['Z']] for x in self.critical_points_info]
        
        

    def filter_critical_points_by_detailed_types(self, list_of_detailed_types: List[str]) -> None:
        """
        Filters the critical points by a certain type or types. 
        :list_of_types: List containing the types we want to keep.  
        """

        if(len(self.critical_points_info) == 0):
            raise IndexError("Critical point info is empty.. Run the set_critical_points_info() or load_critical_points_info()")
        
        self.critical_points_info = self.__filter_according_to(key='Detailed_type_text', possible_types=list(DETAILED_TYPES.values()), wanted_types=list_of_detailed_types)
        self.critical_points = [[x['X'], x['Y'], x['Z']] for x in self.critical_points_info]
       

    def update_list_of_actors(self) -> None:
        """Clears list of actors and updates based on current instance values of critical points"""
        self.list_of_actors.clear()
        critical_point_actor = helpers.get_points_actor_from_list_of_points(self.critical_points)
        self.list_of_actors.append(critical_point_actor)

    def visualize(self) -> None:
        """Starts the rendering"""
        if(len(self.list_of_actors) == 0):
            warnings.warn("List of actors is empty. Make sure to update the list of actors with the function update_list_of_actors()")

        vtk_helper.start_window(self.list_of_actors)

    def visualize_types(self, list_of_types):
        """Filteres critical points without overwriting the class attribute. Only used for visualization and starts the rendering."""
        info = self.__filter_according_to('Type_text', TYPES.values(), list_of_types)
        filtered_cp = [[x['X'], x['Y'], x['Z']] for x in info]
        critical_point_actor = helpers.get_points_actor_from_list_of_points(filtered_cp)

        vtk_helper.start_window([critical_point_actor])

    def visualize_detailed_types(self, list_of_types):
        """Filteres critical points without overwriting the class attribute. Only used for visualization and starts the rendering."""
        info = self.__filter_according_to('Detailed_type_text', DETAILED_TYPES.values(), list_of_types)
        filtered_cp = [[x['X'], x['Y'], x['Z']] for x in info]
        critical_point_actor = helpers.get_points_actor_from_list_of_points(filtered_cp)
       
        vtk_helper.start_window([critical_point_actor])

    def save_critical_points_to_file(self) -> None:
        """
        Creates processed_critical_points directory with critical points as txt file and critical point information as a csv file
        :filename: Output filename
        """
        dirName = 'processed_critical_points'

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

            # # TODO: Remove this, is for debugging in paraview.
            # df = pd.read_csv(f'{dirName}/critical_points_info.csv')
            # df.drop('gradient', inplace=True, axis=1)
            # df.to_csv(f'{dirName}/critical_points_info_no_gradient.csv', index=False)
            # # ===========================================================
            
            np.savetxt(f"{dirName}/critical_points.txt", self.critical_points, fmt='%1.5f')
            logging.info(f"Saved critical point files.")
        except IOError as io:
            print('\n',io)
