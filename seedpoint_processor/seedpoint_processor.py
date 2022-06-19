from enum import Enum
import logging
import os
from typing import List, Optional, Tuple
import warnings
import numpy as np
import pandas as pd
from vtk import vtkStreamTracer, vtkPoints, vtkPolyDataMapper, vtkActor, vtkPolyData, vtkImageData
from vtkmodules.util.numpy_support import vtk_to_numpy
from seedpoint_processor import constants
from vectorfieldtopology.helpers import get_sphere_actor
from vtk_visualization.helpers import start_window

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
        self.list_of_actors = []
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
        level = 1: Removes seedpoints if all the status are the same.
        level = 2: Removes seedpoints if it contains less than 2 different types.
        level = 3: seedpoints if it contains less than 3 different.
        level = 4: Removes seedpoints if it doesn't contain all types.
        """
        if(level > 4 or level < 1):
            raise ValueError("Level should be between 1-4")

        else:

            logging.info(f"Dropping nulls..")
            self.seedpoint_info['CriticalPoint'] = self.seedpoint_info['CriticalPoint'].apply(lambda x: str(x))
            self.seedpoint_info = self.seedpoint_info[self.seedpoint_info["CriticalPoint"].str.contains("null")==False]

            unique_seedtypes_df = self.seedpoint_info.drop_duplicates(['CriticalPoint', 'FieldlineStatus'])

            counter_df = unique_seedtypes_df.groupby(['CriticalPoint']).size().reset_index(name='counts')
            list_of_critical_points_to_remove = counter_df.loc[counter_df['counts'] < level]['CriticalPoint'].to_list()

            self.seedpoint_info = self.seedpoint_info[~self.seedpoint_info['CriticalPoint'].isin(list_of_critical_points_to_remove)] 
            self.seedpoints = list(zip(self.seedpoint_info['X'].to_list(),self.seedpoint_info['Y'].to_list(),self.seedpoint_info['Z'].to_list()))

            logging.info(f"Removed {len(list_of_critical_points_to_remove)} critical points with their corresponding seedpoints. (Not counting nulls)")

    def save_seed_points_to_file(self, filename='seed_points.txt'):
        """
        Creates seed_points directory with critical points as txt file and critical point information as a csv file
        """
        dirName = 'seed_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        np.savetxt(f"{dirName}/{filename}", self.seedpoints, fmt='%1.5f')
        logging.info(f"Saved seedpoints to '{dirName}/{filename}'")
    
    def save_seed_point_info_to_file(self, filename='seedpoint_status.csv') -> None:
        """Save seedpoints information to a csv file"""

        dirName = 'seed_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        self.seedpoint_info.to_csv(f'{dirName}/{filename}', index=False)
        logging.info(f"Saved seedpoint information to '{dirName}/{filename}'")


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
                streamline.SetMaximumPropagation(300)
                streamline.SetInitialIntegrationStep(.2)
                streamline.SetIntegrationDirectionToBoth()
                streamline.SetInterpolatorTypeToCellLocator()
                streamline.SetIntegratorTypeToRungeKutta4()
                streamline.SetMaximumError(1e-06)
                streamline.SetTerminalSpeed(1e-12)
                streamline.SetMaximumNumberOfSteps(2000)
                streamline.SetIntegrationStepUnit(2)
                streamline.Update()

                streamline_points = vtk_to_numpy(streamline.GetOutput().GetPoints().GetData())

                if(len(streamline_points) > 0):
                    side, status = self.__get_status_seedpoint(streamline_points, critical_point)
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

       

    def __get_status_seedpoint(self, streamline_points: Tuple[float,float,float], critical_point: Tuple[float,float,float]) -> Tuple[EarthSide, FieldlineStatus]:
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
        if(critical_point[0] < constants.DAYSIDE_NIGHTSIDE_THRESHOLD):
            result_side = EarthSide.NIGHTSIDE.value
        else:
            result_side = EarthSide.DAYSIDE.value

        if(not hit_earth_top and not hit_earth_bottom):
            result_status = FieldlineStatus.IMF.value
        elif(hit_earth_top and hit_earth_bottom):
            result_status = FieldlineStatus.CLOSED.value
        elif(hit_earth_top and not hit_earth_bottom):
            result_status = FieldlineStatus.OPEN_NORTH.value
        elif(not hit_earth_top and hit_earth_bottom):
            result_status = FieldlineStatus.OPEN_SOUTH.value
        else:
            logging.info('SOMETHING WRONG HAPPENED')
            raise ValueError()

        return (result_side, result_status)

    def visualize(self, side:Optional[EarthSide] = None, status:Optional[FieldlineStatus] = None) -> None:
        """Visualize the streamlines and starts the rendering"""
        self.list_of_actors.clear()

        df = self.seedpoint_info
        
        # If we want a specific side or status
        if(side and status):
            df_side_status = df.loc[(df['EarthSide'] == side) & (df['FieldlineStatus'] == status)]
            actor = self.__get_streamline_actor_from_dataframe(df_side_status)
            self.list_of_actors.append(actor)
            
        elif(side and not status):
            df_side = df.loc[(df['EarthSide'] == side)]
            actor = self.__get_streamline_actor_from_dataframe(df_side)
            self.list_of_actors.append(actor)
        
        elif(not side and status):
            df_status = df.loc[(df['FieldlineStatus'] == status)]
            actor = self.__get_streamline_actor_from_dataframe(df_status)
            self.list_of_actors.append(actor)
        else:
            all_status = [FieldlineStatus.IMF.value,FieldlineStatus.CLOSED.value, FieldlineStatus.OPEN_NORTH.value, FieldlineStatus.OPEN_SOUTH.value]
            colors = [(0,0,0),(0,0,1),(1,1,1),(1,1,1)]

            for color, status in zip(colors, all_status):
                df_status = df.loc[(df['FieldlineStatus'] == status)]
                actor = self.__get_streamline_actor_from_dataframe(df_status, color)
                self.list_of_actors.append(actor)       

        earth = get_sphere_actor(radius=3, center=(0,0,0), opacity=0.4)
        upperbound = get_sphere_actor(radius=0.5, center=(0,0,1), color=(1,1,1))
        lowerbound = get_sphere_actor(radius=0.5, center=(0,0,-1), color=(1,1,1))

        self.list_of_actors.append(earth) 
        self.list_of_actors.append(upperbound)
        self.list_of_actors.append(lowerbound)


        start_window(self.list_of_actors)


    def __get_streamline_actor_from_dataframe(self, df:pd.DataFrame, color: Tuple[float,float,float]=(1,1,1)) -> vtkActor:

        seedpos = list(zip(df['X'],df['Y'],df['Z']))

        seeds = vtkPoints()
        for i, seed in enumerate(seedpos):
            seeds.InsertNextPoint(seed)
                
        poly = vtkPolyData()
        poly.SetPoints(seeds)

        streamline = vtkStreamTracer()
        streamline.SetInputData(self.vectorfield)
        streamline.SetSourceData(poly)
        streamline.SetMaximumPropagation(300)
        streamline.SetInitialIntegrationStep(.2)
        streamline.SetIntegrationDirectionToBoth()
        streamline.SetInterpolatorTypeToCellLocator()
        streamline.SetIntegratorTypeToRungeKutta4()
        streamline.SetMaximumError(1e-06)
        streamline.SetTerminalSpeed(1e-12)
        streamline.SetMaximumNumberOfSteps(2000)
        streamline.SetIntegrationStepUnit(2)
        streamline.Update()

        streamline_mapper = vtkPolyDataMapper()
        streamline_mapper.SetInputConnection(streamline.GetOutputPort())
        streamline_actor = vtkActor()
        streamline_actor.SetMapper(streamline_mapper)
        streamline_actor.VisibilityOn()
        streamline_actor.GetProperty().SetColor(color)
        return streamline_actor

    def __split_dataframe(self, chunk_size = 10000): 

        df = self.seedpoint_info
        chunks = list()
        num_chunks = len(df) // chunk_size + 1
        for i in range(num_chunks):
            chunks.append(df[i*chunk_size:(i+1)*chunk_size])
        return chunks

    def openspace_seeding(self, z_spacing=2, p=1/8, filename='seedpoints_openspace.txt') -> None:  

        #Get pairs of 4
        seedgroups = self.__split_dataframe(5)
        indices_without_one_of_each = []

        final_seed_groups = []
        for index, seedgroup in enumerate(seedgroups):
            seedgroup = seedgroup.drop_duplicates(subset='FieldlineStatus')

            if(len(seedgroup) != 4):
                indices_without_one_of_each.append(index)
            else:
                seedgroup = seedgroup.sort_values("FieldlineStatus")
                seedgroup = seedgroup.reset_index(drop=True)
                seedgroup = seedgroup.reindex([1, 0, 2, 3])
                final_seed_groups.append(seedgroup)


        df_final = pd.concat(final_seed_groups)
        data = list(zip(df_final['X'].tolist(),df_final['Y'].tolist(),df_final['Z'].tolist()))

        # Increase z-axis
        res = []
        curr_ind = 0

        for ind, (x,y,z) in enumerate(data):
            
            if(curr_ind == 4):
                curr_ind = 0

            if(ind < len(data)-1):

                if(curr_ind == 2):
                    if(z < data[ind+1][2]):
                        z_down = z-z_spacing
                        z_up = data[ind+1][2]+z_spacing
                    else:
                        z_up = z+z_spacing
                        z_down = data[ind+1][2]-z_spacing

                    res.append([x-(x*p),y-(y*p),z_up])
                    res.append([x-(x*p),y-(y*p),z_down])

                elif(curr_ind == 0 or curr_ind == 1):
                    res.append([x,y,z])

                curr_ind +=1
            
        np.savetxt(filename, res)
        logging.info(f'Saved openspace seedpoints to: "{filename}"')
