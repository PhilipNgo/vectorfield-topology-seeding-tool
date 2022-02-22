import numpy as np

# Constant
EARTH_MIDPOINT = [10.743, -0.21628, -0.012009] # X, Y, Z
RADIUS = 4
ex, ey, ez = EARTH_MIDPOINT

# Load seedpoints
filename = 'seedpoints/seedpoints.txt'
seed_points = np.loadtxt(filename)

seed_points_no_earth = []

for seed in seed_points:

    x, y, z = seed
    #Check if point is inside/on sphere 
    is_inside = ((x-ex)**2+(y-ey)**2+(z-ez)**2 <= RADIUS**2)

    if(not is_inside):
        seed_points_no_earth.append([x,y,z])

out_filename = "seedpoints/seed_points_no_earth.txt"
np.savetxt(out_filename, seed_points_no_earth, fmt='%1.5f')
    


