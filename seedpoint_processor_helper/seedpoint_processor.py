from enum import Enum
import logging
import os
from time import perf_counter
from typing import List, Optional, Tuple
import pandas as pd
from vtk import vtkStreamTracer, vtkPoints, vtkPolyDataMapper, vtkActor, vtkPolyData, vtkImageData
from vtkmodules.util.numpy_support import vtk_to_numpy
from seedpoint_processor_helper import constants
from vectorfieldtopology_helper.helpers import get_sphere_actor
from vtk_visualization_helper.helpers import start_window

class StreamlineStatus(Enum): 
    IMF = 'IMF'
    CLOSED = 'CLOSED'
    OPEN_NORTH = 'OPEN_NORTH'
    OPEN_SOUTH = 'OPEN_SOUTH'

class EarthSide(Enum):
    NIGHTSIDE = 'NIGHTSIDE'
    DAYSIDE = 'DAYSIDE'


class SeedpointProcessor():

    def __init__(self, seedpoints: List[float], vectorfield: vtkImageData):
        self.seedpoints = seedpoints
        self.vectorfield = vectorfield
        self.seedpoint_info = pd.DataFrame()

    def generate_seedpoint_info_csv(self) -> None:
        """ Save seedpoints information to a csv file"""

        seed_side = []
        seed_status = []

        logging.info(f"Generating seedpoint information..")

        for i, seed in enumerate(self.seedpoints):
           
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
            else:
                seed_side.append('null')
                seed_status.append('null')
                logging.debug(f"Index {i} has length zero")

        self.seedpoint_info['X'] = [s[0] for s in self.seedpoints]
        self.seedpoint_info['Y'] = [s[1] for s in self.seedpoints]
        self.seedpoint_info['Z'] = [s[2] for s in self.seedpoints]
        self.seedpoint_info['EarthSide'] = seed_side
        self.seedpoint_info['StreamlineStatus'] = seed_status

        dirName = 'seed_points'

        if not os.path.exists(dirName):
            os.mkdir(dirName)
            logging.info(f"Directory {dirName} created.")
        else:    
            logging.info(f"Directory {dirName} already exists.")

        self.seedpoint_info.to_csv(f'{dirName}/seedpoint_status.csv', index=False)
        logging.info(f"Saved seedpoint information to '{dirName}/seedpoint_status.csv'")

    def __get_status_seedpoint(self, streamline_points: Tuple[float,float,float]) -> Tuple[EarthSide, StreamlineStatus]:
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
            result_status = StreamlineStatus.IMF
        elif(hit_earth_top and hit_earth_bottom):
            result_status = StreamlineStatus.CLOSED
        elif(hit_earth_top and not hit_earth_bottom):
            result_status = StreamlineStatus.OPEN_NORTH
        elif(not hit_earth_top and hit_earth_bottom):
            result_status = StreamlineStatus.OPEN_SOUTH
        else:
            logging.info('SOMETHING WRONG HAPPENED')
            raise ValueError()

        return (result_side, result_status)

    def visualize(self, side:Optional[EarthSide] = None, status:Optional[StreamlineStatus] = None) -> None:
        """Visualize the streamlines and starts the rendering"""
        df = self.seedpoint_info
        
        # If we want a specific side or status
        if(side and status):
            df = df.loc[(df['EarthSide'] == side) & (df['StreamlineStatus'] == status)]
        
        elif(side and not status):
            df = df.loc[(df['EarthSide'] == side)]
        
        elif(not side and status):
            df = df.loc[(df['StreamlineStatus'] == status)]

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