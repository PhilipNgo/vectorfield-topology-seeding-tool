from enum import Enum
import logging
import os
from typing import List, Optional, Tuple
import warnings
import numpy as np
import pandas as pd
from vtk import vtkStreamTracer, vtkPoints, vtkPolyDataMapper, vtkActor, vtkPolyData, vtkImageData
from vtkmodules.util.numpy_support import vtk_to_numpy
from seedpoint_processor_helper import constants
from vectorfieldtopology_helper.helpers import get_sphere_actor
from vtk_visualization_helper.helpers import start_window

class FieldlineStatus(Enum): 
    IMF = 'IMF'
    CLOSED = 'CLOSED'
    OPEN_NORTH = 'OPEN_NORTH'
    OPEN_SOUTH = 'OPEN_SOUTH'

class EarthSide(Enum):
    NIGHTSIDE = 'NIGHTSIDE'
    DAYSIDE = 'DAYSIDE'


class SeedpointProcessor():

    def __init__(self):
        #self.seedpoints = seedpoints
        self.seed_critical_pair = None
        self.seedpoints = []
        
        self.seedpoint_info = pd.DataFrame()

    def set_seed_critical_pair(self, seed_critical_pair: List[Tuple[List[Tuple[float,float,float]], List[Tuple[float,float,float]]]]) -> None:
        """Sets the seedpoints and seedpoint/criticalpoint pairs"""
        self.seed_critical_pair = seed_critical_pair
        
        for _, seeds in seed_critical_pair:
            for seed in seeds:
                self.seedpoints.append(seed)
        
        logging.info("Updated seed_critical_pair")        

    def set_vector_field_domain(self, vectorfield: vtkImageData) -> None:
        """Sets the vectorfield"""
        self.vectorfield = vectorfield

    def filter_seeds(self, side:Optional[EarthSide] = None, status:Optional[FieldlineStatus] = None):
        """Filters the seedpoints to the ones we want."""

        self.seedpoint_info

        if(side and status):
            self.seedpoint_info = self.seedpoint_info.loc[(self.seedpoint_info['EarthSide'] == side) & (self.seedpoint_info['FieldlineStatus'] == status)]
        
        elif(side and not status):
            self.seedpoint_info = self.seedpoint_info.loc[(self.seedpoint_info['EarthSide'] == side)]
        
        elif(not side and status):
            self.seedpoint_info = self.seedpoint_info.loc[(self.seedpoint_info['FieldlineStatus'] == status)]

        else:
            warnings.warn("Unused filter function..")

        self.seedpoints = list(zip(self.seedpoint_info['X'].to_list(),self.seedpoint_info['Y'].to_list(),self.seedpoint_info['Z'].to_list()))


    

    def remove_useless_seed_points(self, level:int):
        """
        Removes seedpoints where the FieldlineStatus doesn't change. 
        :level: How strictly it removes is dependent on level (1-4)
        level = 1: Removes seedpoints if all the status are the same
        level = 2: Removes seedpoints if it only contains 2 types
        level = 3: Removes seedpoints if it only contains 3 types
        level = 4: Removes seedpoints if it doesn't contain all types
        """
        if(level > 4 or level < 1):
            raise ValueError("Level should be between 1-4")

        else:

            self.seedpoint_info['CriticalPoint'] = self.seedpoint_info['CriticalPoint'].apply(lambda x: str(x))
            unique_seedtypes_df = self.seedpoint_info.drop_duplicates(['CriticalPoint', 'FieldlineStatus'])
            counter_df = unique_seedtypes_df.groupby(['CriticalPoint']).size().reset_index(name='counts')
            list_of_critical_points_to_remove = counter_df.loc[counter_df['counts'] < level]['CriticalPoint'].to_list()

            self.seedpoint_info = self.seedpoint_info[~self.seedpoint_info['CriticalPoint'].isin(list_of_critical_points_to_remove)] 
            self.seedpoints = list(zip(self.seedpoint_info['X'].to_list(),self.seedpoint_info['Y'].to_list(),self.seedpoint_info['Z'].to_list()))

            logging.info(f"Removed {len(list_of_critical_points_to_remove)} critical points with their corresponding seedpoints")

    def save_seed_points_to_file(self):
        """
        Creates seed_points directory with critical points as txt file and critical point information as a csv file
        """
        dirName = 'seed_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        np.savetxt(f"{dirName}/seed_points.txt", self.seedpoints, fmt='%1.5f')
    
    def save_seed_point_info_to_file(self) -> None:
        """Save seedpoints information to a csv file"""

        dirName = 'seed_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        self.seedpoint_info.to_csv(f'{dirName}/seedpoint_status.csv', index=False)
        logging.info(f"Saved seedpoint information to '{dirName}/seedpoint_status.csv'")


    def update_seed_point_info(self) -> None:
        """
        Updates seedpoint information based on seedpoints and critical points. 
        Information is a dataframe containing: 'FieldlineStatus', 'EarthSide', 'X', 'Y', 'Z', 'CriticalPoint'.
        """

        seed_side = []
        seed_status = []
        critical_point_location = []

        logging.info(f"Generating seedpoint information..")

        for i, (critical_point, seed_points) in enumerate(self.seed_critical_pair):
            
            for seed in seed_points:

                seeds = vtkPoints()
                seeds.InsertNextPoint(seed)
                    
                poly = vtkPolyData()
                poly.SetPoints(seeds)

                streamline = vtkStreamTracer()
                streamline.SetInputData(self.vectorfield)
                streamline.SetSourceData(poly)
                streamline.SetMaximumPropagation(200)
                streamline.SetInitialIntegrationStep(.2)
                streamline.SetIntegrationDirectionToBoth()
                streamline.Update()

                streamline_points = vtk_to_numpy(streamline.GetOutput().GetPoints().GetData())

                if(len(streamline_points) > 0):
                    side, status = self.__get_status_seedpoint(streamline_points)
                    seed_side.append(side)
                    seed_status.append(status)
                    critical_point_location.append(critical_point)
                else:
                    seed_side.append('null')
                    seed_status.append('null')
                    critical_point_location.append('null')
                    logging.debug(f"Index {i} has length zero")

        self.seedpoint_info['X'] = [s[0] for s in self.seedpoints]
        self.seedpoint_info['Y'] = [s[1] for s in self.seedpoints]
        self.seedpoint_info['Z'] = [s[2] for s in self.seedpoints]
        self.seedpoint_info['EarthSide'] = seed_side
        self.seedpoint_info['FieldlineStatus'] = seed_status
        self.seedpoint_info['CriticalPoint'] = critical_point_location

       

    def __get_status_seedpoint(self, streamline_points: Tuple[float,float,float]) -> Tuple[EarthSide, FieldlineStatus]:
        """ Gets the status of a certain streamline """
    
        ux, uy, uz = constants.UPPERBOUND
        lx, ly, lz = constants.LOWERBOUND
        rad = constants.BOUND_RADIUS

        hit_earth_top = False
        hit_earth_bottom = False

        for sx,sy,sz in streamline_points:

            if(((sx-ux)**2+(sy-uy)**2+(sz-uz)**2 <= rad**2)):
                hit_earth_top = True
            elif(((sx-lx)**2+(sy-ly)**2+(sz-lz)**2 <= rad**2)):
                hit_earth_bottom = True

        # If the x value is less than certain threshhold. Then we regard it as nightside.
        streamline_points_x = [d[0] for d in streamline_points]
        if(min(streamline_points_x) < constants.DAYSIDE_NIGHTSIDE_THRESHOLD):
            result_side = EarthSide.NIGHTSIDE
        else:
            result_side = EarthSide.DAYSIDE

        if(not hit_earth_top and not hit_earth_bottom):
            result_status = FieldlineStatus.IMF
        elif(hit_earth_top and hit_earth_bottom):
            result_status = FieldlineStatus.CLOSED
        elif(hit_earth_top and not hit_earth_bottom):
            result_status = FieldlineStatus.OPEN_NORTH
        elif(not hit_earth_top and hit_earth_bottom):
            result_status = FieldlineStatus.OPEN_SOUTH
        else:
            logging.info('SOMETHING WRONG HAPPENED')
            raise ValueError()

        return (result_side, result_status)

    def visualize(self, side:Optional[EarthSide] = None, status:Optional[FieldlineStatus] = None) -> None:
        """Visualize the streamlines and starts the rendering"""
        df = self.seedpoint_info
        
        # If we want a specific side or status
        if(side and status):
            df = df.loc[(df['EarthSide'] == side) & (df['FieldlineStatus'] == status)]
        
        elif(side and not status):
            df = df.loc[(df['EarthSide'] == side)]
        
        elif(not side and status):
            df = df.loc[(df['FieldlineStatus'] == status)]

        seedpos = list(zip(df['X'],df['Y'],df['Z']))

        seeds = vtkPoints()
        for i, seed in enumerate(seedpos):
            seeds.InsertNextPoint(seed)
                
        poly = vtkPolyData()
        poly.SetPoints(seeds)

        streamline = vtkStreamTracer()
        streamline.SetInputData(self.vectorfield)
        streamline.SetSourceData(poly)
        streamline.SetMaximumPropagation(200)
        streamline.SetInitialIntegrationStep(.2)
        streamline.SetIntegrationDirectionToBoth()
        streamline.Update()

        streamline_mapper = vtkPolyDataMapper()
        streamline_mapper.SetInputConnection(streamline.GetOutputPort())
        streamline_actor = vtkActor()
        streamline_actor.SetMapper(streamline_mapper)
        streamline_actor.VisibilityOn()

        earth = get_sphere_actor(radius=3, center=(0,0,0), opacity=0.4)
        upperbound = get_sphere_actor(radius=0.5, center=(0,0,1), color=(1,1,1))
        lowerbound = get_sphere_actor(radius=0.5, center=(0,0,-1), color=(1,1,1))

        list_of_actors = [earth, streamline_actor, upperbound, lowerbound]

        start_window(list_of_actors)