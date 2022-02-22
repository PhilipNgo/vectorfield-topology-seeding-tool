import numpy as np

def remove_earth_cp(x,y,z, radius, infile, outfile):
    """Removes unwanted critical points, eg. near earth critical points. 
        Creates text file with correct critical points.
        :x: x coord for earths center (Float)
        :y: y coord for earths center (Float)
        :z: z coord for earths center (Float)
        :radius: radius of earth in terms of coordinate system to ignore (Float)
        :infile: input file with critical points (String)
        :outfile: output file with critical points (String)
    """
    # Constant
    RADIUS = radius
    ex = x
    ey = y
    ez = z

    # Load seedpoints
    seed_points = np.loadtxt(infile)

    seed_points_no_earth = []

    for seed in seed_points:

        sx, sy, sz = seed
        #Check if point is inside/on sphere 
        is_inside = ((sx-ex)**2+(sy-ey)**2+(sz-ez)**2 <= RADIUS**2)

        if(not is_inside):
            seed_points_no_earth.append([sx,sy,sz])

    np.savetxt(outfile, seed_points_no_earth, fmt='%1.5f')

    print("Generated new critical points at {}".format(outfile))
    


