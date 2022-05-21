from enum import Enum
import logging
import os
from typing import Dict, List, Tuple
import warnings
import numpy as np
import pandas as pd
from vtk import vtkPoints, vtkPolyData, vtkSphereSource, vtkGlyph3D
from seedpoint_generator import constants, helpers
from vtkmodules.util.numpy_support import vtk_to_numpy
from vectorfieldtopology.vectorfieldtopology import CriticalPointInfo
from vtk_visualization import helpers as vtk_helper
from seedpoint_processor import constants as p_constant

class Template(Enum):
    SPHERICAL = 1
    EIGEN_PLANE = 2
    TRIPPLE_EIGEN_PLANE = 3
    SMART = 4
    USER_CHOICE = 5

class SeedpointGenerator():

    def __init__(self):
        """
        Init function
        :critical_point_info: Contains information about critical point. Position, gradient and type
        :template: Contains the seedpoint template, If the template is Tempate.USER_CHOICE, then template fire is required.
        ::
        """
        self.critical_points = []
        self.gradient = []
        self.seed_points:List[float] = []
        self.template = None
        self.seed_critical_pair = []
        self.list_of_actors = []

    def set_template(self, template: Template):
        """Sets the template value"""
        self.template = template

    def set_custom_template(self, template_filename:str):
        """Sets the template value based on custom txt file"""

        self.template = Template.USER_CHOICE

        if(os.path.exists(template_filename)):
            self.template_filename = template_filename
        else:
            raise FileNotFoundError("File not found..")
        
    def load_critical_point_info(self, critical_point_info_filename:str) -> None:
        """Loads a csv file containing the critical_point_info"""
        if(os.path.exists(critical_point_info_filename)):
            df = pd.read_csv(critical_point_info_filename)
            critical_point_info = df.to_dict('records')

            self.critical_points = [[x['X'], x['Y'], x['Z']] for x in critical_point_info]
            self.gradient = [x['Gradient'] for x in critical_point_info]
        else:
            raise FileNotFoundError("File not found..")

    def set_critical_point_info(self, critical_point_info: List[CriticalPointInfo]) -> None:
        """Set the critical points to new list of critical points
        :critical_points: List of critical points
        """
        self.critical_points = [[x['X'], x['Y'], x['Z']] for x in critical_point_info]
        self.gradient = [x['Gradient'] for x in critical_point_info]

    def set_custom_points(self, custom_points: List[Tuple[float,float,float]]) -> None:
        """Uses to our own custom points we want to seed around. Works for custom template and spherical template
        :custom_points: A list of points with x,y,z coordinates.
        """
        self.critical_points = custom_points

    def load_custom_points(self, custom_point_filename:str):
        """Loads a csv file containing the custom points with 'X','Y','Z' columns."""
        if(os.path.exists(custom_point_filename)):
            df = pd.read_csv(custom_point_filename)
            custom_points_dict = df.to_dict('records')

            self.critical_points = [[x['X'], x['Y'], x['Z']] for x in custom_points_dict]
        else:
            raise FileNotFoundError("File not found..")


    def update_seed_points(self, is_custom_points = False) -> None:
        """ Generates seedpoints based on critical points"""

        if(self.template == Template.SPHERICAL):
            # Generate seedpoint by sampling a sphere around the critical point
            glyphs = self.__get_spherical_glyph()
            self.seed_points = vtk_to_numpy(glyphs.GetOutput().GetPoints().GetData())
            self.seed_critical_pair = self.__get_seed_point_critical_point_pair(self.critical_points, self.seed_points)
            actor = helpers.get_sphere_around_points_actor(self.critical_points)
            self.list_of_actors = [actor]
        elif(self.template == Template.EIGEN_PLANE):
            print("Doing fun eigenplane stuff")
            pass
        elif(self.template == Template.TRIPPLE_EIGEN_PLANE):
            # Generate seedpoint by sampling the planes created by the eigen vector of the critical point as the normal of the planes.
            poly, self.list_of_actors = self.__get_tripple_plane(show_normal=False)
            self.seed_points = vtk_to_numpy(poly.GetPoints().GetData())
            self.seed_critical_pair = self.__get_seed_point_critical_point_pair(self.critical_points, self.seed_points)

        elif(self.template == Template.USER_CHOICE):
            # Generate seedpoint by sampling the template given by the user.
            poly = self.__get_custom_seedpoints_from_file_template()
            self.seed_points = vtk_to_numpy(poly.GetPoints().GetData())
            self.seed_critical_pair = self.__get_seed_point_critical_point_pair(self.critical_points, self.seed_points)
            actor = helpers.get_points_actor(poly.GetPoints())
            self.list_of_actors = [actor]

        elif(self.template == Template.SMART):
            self.seed_points.clear()
            self.list_of_actors.clear()

            # Get dayside and nightside.
            critical_points_dayside_position = np.array([ cp for cp in self.critical_points if cp[0] >= p_constant.DAYSIDE_NIGHTSIDE_THRESHOLD ])
            critical_points_nightside_info = [ (cp,ind) for ind, cp in enumerate(self.critical_points) if cp[0] < p_constant.DAYSIDE_NIGHTSIDE_THRESHOLD ]
            critical_point_nighside_position = np.array([i[0] for i in critical_points_nightside_info])
            critical_point_nightside_gradient = np.array([self.gradient[i[1]] for i in critical_points_nightside_info])

            # Get planes and glyphs where the seedpoint lies
            glyphs = self.__get_spherical_glyph_from_critical_points(critical_points_dayside_position)
            poly, actors = self.__get_tripple_plane_from_critical_points(critical_point_nightside_gradient, critical_point_nighside_position)

            seed_dayside = vtk_to_numpy(glyphs.GetOutput().GetPoints().GetData())
            seed_nightside = vtk_to_numpy(poly.GetPoints().GetData())

            # Generate pair information to know which seed points corresponds to which critical point
            seed_critical_pair_dayside = self.__get_seed_point_critical_point_pair(critical_points_dayside_position, seed_dayside)
            seed_critical_pair_nightside = self.__get_seed_point_critical_point_pair(critical_point_nighside_position, seed_nightside)

            # Update seedpoints and seedpoint pairs
            self.seed_critical_pair = np.concatenate([np.array(seed_critical_pair_dayside, dtype=object), np.array(seed_critical_pair_nightside, dtype=object)])
            self.seed_points = np.concatenate([seed_dayside, seed_nightside])

            # Update list of actors
            dayside_actor = helpers.get_sphere_around_points_actor(critical_points_dayside_position)
            self.list_of_actors.append(dayside_actor)
            for nightside_actor in actors:
                self.list_of_actors.append(nightside_actor)
        else:
            raise ValueError("No template has been selected. To update template, use set_template() function")


    def visualize(self) -> None:
        """Starts the rendering"""
        if(len(self.list_of_actors) == 0):
            warnings.warn("List of actors is empty. Make sure to update the list of actors with the function update_list_of_actors()")

        vtk_helper.start_window(self.list_of_actors)

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

        np.savetxt(f"{dirName}/{filename}", self.seed_points, fmt='%1.5f')

    def __get_seed_point_critical_point_pair(self, critical_points:List[Tuple[float, float, float]], seedpoints: List[Tuple[float, float, float]]):
        
        if(len(critical_points) > 0):
            #print(seedpoints)
            seed_point_chunks = np.array_split(np.array(seedpoints), len(critical_points))

            return list(zip(critical_points, seed_point_chunks))
        else:
            warnings.warn("Zero critical points.. ")
            return []

    def __get_spherical_glyph_from_critical_points(self, critical_points: List[Tuple[float, float, float]]) -> vtkGlyph3D:
        points = vtkPoints()
        for x,y,z in critical_points:
            points.InsertNextPoint(x, y, z)
        
        polydata = vtkPolyData()
        polydata.SetPoints(points)

        sphereSource = vtkSphereSource()
        sphereSource.SetThetaResolution(constants.THETA_RESOLUTION)
        sphereSource.SetPhiResolution(constants.PHI_RESOLUTION)
        sphereSource.SetRadius(constants.RADIUS)

        glyph3D = vtkGlyph3D()
        glyph3D.SetSourceConnection(sphereSource.GetOutputPort())
        glyph3D.SetInputData(polydata)
        glyph3D.Update()

        return glyph3D
    
    def __get_spherical_glyph(self) -> vtkGlyph3D:
        """Return glyph that contains structure of seedpoints. This case, a spheres surrounding the critical points"""
        return self.__get_spherical_glyph_from_critical_points(self.critical_points)

        
    def __get_tripple_plane_from_critical_points(self, gradients:List[float], critical_points:List[Tuple[float,float,float]], show_normal=False) -> vtkPolyData:
        list_of_eigenvectors = []

        for jacobian in gradients:
            
            _, eig_vec = np.linalg.eig(jacobian.reshape(3,3))
            list_of_eigenvectors.append(eig_vec.tolist())

        planes_to_generate = []
        
        # Create point cloud
        points = vtkPoints()
        for point, vecs in zip(critical_points, list_of_eigenvectors):

            for vec in vecs: 

                planes_to_generate.append({
                    'point': point.tolist(), 
                    'normal': vec
                })

                #Add point multiple time.
                points.InsertNextPoint(point[0], point[1], point[2])

        # loop through critical points and go through each of the eigen vectors at that point and generate a plane actor.
        list_of_plane_actors = []
        list_of_polys = []
        for p in planes_to_generate:
            actor, poly = helpers.get_disc_actor(p['normal'], p['point'])
            list_of_plane_actors.append(actor)
            list_of_polys.append(poly)

        all_points = vtkPoints()

        for poly in list_of_polys:
            for p in vtk_to_numpy(poly.GetPoints().GetData()):
                all_points.InsertNextPoint(p[0],p[1],p[2])

        cp_polydata = vtkPolyData()
        cp_polydata.SetPoints(all_points)

        if(show_normal):
            normals_actor = helpers.get_plane_normal_actor(points, planes_to_generate)
            list_of_plane_actors.append(normals_actor)

        return cp_polydata, list_of_plane_actors

    def __get_tripple_plane(self, show_normal=False) -> vtkPolyData:
        return self.__get_tripple_plane_from_critical_points(self.gradient, self.critical_points, show_normal)
        
    
    def __get_custom_seedpoints_from_file_template(self):

        custom_template = np.loadtxt(self.template_filename)

        seedpoints = vtkPoints()

        for cp in self.critical_points:
            for t in custom_template:
                res = np.add(cp,t)
                seedpoints.InsertNextPoint(res[0],res[1],res[2])
                
        cp_polydata = vtkPolyData()
        cp_polydata.SetPoints(seedpoints)

        return cp_polydata

    def __get_plane(self) -> vtkGlyph3D:
        pass

    


    
        


        
