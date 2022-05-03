from enum import Enum
import logging
import os
from typing import Dict, List, Tuple
import warnings
import numpy as np
from vtk import vtkPoints, vtkPolyData, vtkSphereSource, vtkGlyph3D
from seedpoint_generator_helper import constants, helpers
from vtkmodules.util.numpy_support import vtk_to_numpy
from vtk_visualization_helper import helpers as vtk_helper
from seedpoint_processor_helper import constants as p_constant

class Template(Enum):
    SPHERICAL = 1
    EIGEN_PLANE = 2
    TRIPPLE_EIGEN_PLANE = 3
    SMART = 4

class SeedpointGenerator():

    def __init__(self, critical_point_info:List[Dict], template=Template.SPHERICAL):
        self.critical_points = [[x['x'], x['y'], x['z']] for x in critical_point_info]
        self.gradient = [x['gradient'] for x in critical_point_info]
        self.seed_points:List[float] = []
        self.template = template
        self.seed_critical_pair = []
        self.list_of_actors = []
        

    def set_critical_points(self, critical_points: List[Tuple[float, float, float]]) -> None:
        """Set the critical points to new list of critical points
        :critical_points: List of critical points
        """
        self.critical_points = critical_points

    def update_seed_points(self) -> None:
        """ Generates seedpoints based on critical points"""

        if(self.template == Template.SPHERICAL):
            glyphs = self.__get_spherical_glyph()
            self.seed_points = vtk_to_numpy(glyphs.GetOutput().GetPoints().GetData())
            self.seed_critical_pair = self.__get_seed_point_critical_point_pair(self.critical_points, self.seed_points)

            actor = helpers.get_sphere_around_points_actor(self.critical_points)
            self.list_of_actors = [actor]
        elif(self.template == Template.EIGEN_PLANE):
            print("Doing fun eigenplane stuff")
            pass
        elif(self.template == Template.TRIPPLE_EIGEN_PLANE):
            poly, self.list_of_actors = self.__get_tripple_plane(show_normal=False)
            self.seed_points = vtk_to_numpy(poly.GetPoints().GetData())
            self.seed_critical_pair = self.__get_seed_point_critical_point_pair(self.critical_points, self.seed_points)

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

            # TODO: REMOVE LATER, THIS IS FOR DEBUG:
    
            with open('seed_critical_pair.txt', 'w') as fp:
                fp.write('\n'.join('{} {}'.format(x[0],x[1]) for x in self.seed_critical_pair))

            # Update list of actors
            dayside_actor = helpers.get_sphere_around_points_actor(critical_points_dayside_position)
            self.list_of_actors.append(dayside_actor)
            for nightside_actor in actors:
                self.list_of_actors.append(nightside_actor)
            


    def visualize(self) -> None:
        """Starts the rendering"""
        if(len(self.list_of_actors) == 0):
            warnings.warn("List of actors is empty. Make sure to update the list of actors with the function update_list_of_actors()")

        vtk_helper.start_window(self.list_of_actors)

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

        np.savetxt(f"{dirName}/seed_points.txt", self.seed_points, fmt='%1.5f')

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
        
        
    def __get_plane(self) -> vtkGlyph3D:
        pass

    


    
        


        
