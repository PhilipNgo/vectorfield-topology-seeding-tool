# trace generated using paraview version 5.10.0
#import paraview
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 10

#### import the simple module from the paraview
from paraview.simple import *

def run(inputfile, outfile, threshold=30):

    #### disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()

    # create a new 'Tecplot Reader'
    inputTecPlotData = TecplotReader(registrationName='inputTecplotFile', FileNames=[inputfile])
    inputTecPlotData.DataArrayStatus = ['Rho [amu_cm^3]', 'U_x [km_s]', 'U_y [km_s]', 'U_z [km_s]', 'E [J_m^3]', 'B_x [nT]', 'B_y [nT]', 'B_z [nT]', 'B1_x [nT]', 'B1_y [nT]', 'B1_z [nT]', 'P [nPa]', 'J_x [`mA_m^2]', 'J_y [`mA_m^2]', 'J_z [`mA_m^2]', 'Status']

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')

    # show data in view
    inputTecPlotDataDisplay = Show(inputTecPlotData, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    inputTecPlotDataDisplay.Representation = 'Surface'
    inputTecPlotDataDisplay.ColorArrayName = [None, '']
    inputTecPlotDataDisplay.SelectTCoordArray = 'None'
    inputTecPlotDataDisplay.SelectNormalArray = 'None'
    inputTecPlotDataDisplay.SelectTangentArray = 'None'
    inputTecPlotDataDisplay.OSPRayScaleArray = 'B1_x [nT]'
    inputTecPlotDataDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
    inputTecPlotDataDisplay.SelectOrientationVectors = 'None'
    inputTecPlotDataDisplay.ScaleFactor = 38.400000000000006
    inputTecPlotDataDisplay.SelectScaleArray = 'B1_x [nT]'
    inputTecPlotDataDisplay.GlyphType = 'Arrow'
    inputTecPlotDataDisplay.GlyphTableIndexArray = 'B1_x [nT]'
    inputTecPlotDataDisplay.GaussianRadius = 1.92
    inputTecPlotDataDisplay.SetScaleArray = ['POINTS', 'B1_x [nT]']
    inputTecPlotDataDisplay.ScaleTransferFunction = 'PiecewiseFunction'
    inputTecPlotDataDisplay.OpacityArray = ['POINTS', 'B1_x [nT]']
    inputTecPlotDataDisplay.OpacityTransferFunction = 'PiecewiseFunction'
    inputTecPlotDataDisplay.DataAxesGrid = 'GridAxesRepresentation'
    inputTecPlotDataDisplay.PolarAxes = 'PolarAxesRepresentation'
    inputTecPlotDataDisplay.ScalarOpacityUnitDistance = 3.580920757821633
    inputTecPlotDataDisplay.OpacityArrayName = ['POINTS', 'B1_x [nT]']
    inputTecPlotDataDisplay.InputVectors = [None, '']
    inputTecPlotDataDisplay.SelectInputVectors = ['POINTS', 'B1_x [nT]']
    inputTecPlotDataDisplay.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    inputTecPlotDataDisplay.ScaleTransferFunction.Points = [-42.962459564208984, 0.0, 0.5, 0.0, 42.962459564208984, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    inputTecPlotDataDisplay.OpacityTransferFunction.Points = [-42.962459564208984, 0.0, 0.5, 0.0, 42.962459564208984, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView1.ResetCamera(False)

    # update the view to ensure updated data information
    renderView1.Update()

    # create a new 'Calculator'
    calculator1 = Calculator(registrationName='Calculator1', Input=inputTecPlotData)
    calculator1.Function = ''

    # Properties modified on calculator1
    calculator1.ResultArrayName = 'pbx'
    calculator1.Function = '"P [nPa]"/(("B_x [nT]"^2)*(2*1.25663706e-6))'

    # show data in view
    calculator1Display = Show(calculator1, renderView1, 'UnstructuredGridRepresentation')

    # get color transfer function/color map for 'pbx'
    pbxLUT = GetColorTransferFunction('pbx')

    # get opacity transfer function/opacity map for 'pbx'
    pbxPWF = GetOpacityTransferFunction('pbx')

    # trace defaults for the display properties.
    calculator1Display.Representation = 'Surface'
    calculator1Display.ColorArrayName = ['POINTS', 'pbx']
    calculator1Display.LookupTable = pbxLUT
    calculator1Display.SelectTCoordArray = 'None'
    calculator1Display.SelectNormalArray = 'None'
    calculator1Display.SelectTangentArray = 'None'
    calculator1Display.OSPRayScaleArray = 'pbx'
    calculator1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    calculator1Display.SelectOrientationVectors = 'None'
    calculator1Display.ScaleFactor = 38.400000000000006
    calculator1Display.SelectScaleArray = 'pbx'
    calculator1Display.GlyphType = 'Arrow'
    calculator1Display.GlyphTableIndexArray = 'pbx'
    calculator1Display.GaussianRadius = 1.92
    calculator1Display.SetScaleArray = ['POINTS', 'pbx']
    calculator1Display.ScaleTransferFunction = 'PiecewiseFunction'
    calculator1Display.OpacityArray = ['POINTS', 'pbx']
    calculator1Display.OpacityTransferFunction = 'PiecewiseFunction'
    calculator1Display.DataAxesGrid = 'GridAxesRepresentation'
    calculator1Display.PolarAxes = 'PolarAxesRepresentation'
    calculator1Display.ScalarOpacityFunction = pbxPWF
    calculator1Display.ScalarOpacityUnitDistance = 3.580920757821633
    calculator1Display.OpacityArrayName = ['POINTS', 'pbx']
    calculator1Display.InputVectors = [None, '']
    calculator1Display.SelectInputVectors = ['POINTS', 'B1_x [nT]']
    calculator1Display.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    calculator1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 4.4101914759686866e+38, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    calculator1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 4.4101914759686866e+38, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(inputTecPlotData, renderView1)

    # show color bar/color legend
    calculator1Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # create a new 'Calculator'
    calculator2 = Calculator(registrationName='Calculator2', Input=calculator1)
    calculator2.Function = ''

    # Properties modified on calculator2
    calculator2.ResultArrayName = 'pby'
    calculator2.Function = '"P [nPa]"/(("B_y [nT]"^2)/(2*1.25663706e-6))'

    # show data in view
    calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

    # get color transfer function/color map for 'pby'
    pbyLUT = GetColorTransferFunction('pby')

    # get opacity transfer function/opacity map for 'pby'
    pbyPWF = GetOpacityTransferFunction('pby')

    # trace defaults for the display properties.
    calculator2Display.Representation = 'Surface'
    calculator2Display.ColorArrayName = ['POINTS', 'pby']
    calculator2Display.LookupTable = pbyLUT
    calculator2Display.SelectTCoordArray = 'None'
    calculator2Display.SelectNormalArray = 'None'
    calculator2Display.SelectTangentArray = 'None'
    calculator2Display.OSPRayScaleArray = 'pby'
    calculator2Display.OSPRayScaleFunction = 'PiecewiseFunction'
    calculator2Display.SelectOrientationVectors = 'None'
    calculator2Display.ScaleFactor = 38.400000000000006
    calculator2Display.SelectScaleArray = 'pby'
    calculator2Display.GlyphType = 'Arrow'
    calculator2Display.GlyphTableIndexArray = 'pby'
    calculator2Display.GaussianRadius = 1.92
    calculator2Display.SetScaleArray = ['POINTS', 'pby']
    calculator2Display.ScaleTransferFunction = 'PiecewiseFunction'
    calculator2Display.OpacityArray = ['POINTS', 'pby']
    calculator2Display.OpacityTransferFunction = 'PiecewiseFunction'
    calculator2Display.DataAxesGrid = 'GridAxesRepresentation'
    calculator2Display.PolarAxes = 'PolarAxesRepresentation'
    calculator2Display.ScalarOpacityFunction = pbyPWF
    calculator2Display.ScalarOpacityUnitDistance = 3.580920757821633
    calculator2Display.OpacityArrayName = ['POINTS', 'pby']
    calculator2Display.InputVectors = [None, '']
    calculator2Display.SelectInputVectors = ['POINTS', 'B1_x [nT]']
    calculator2Display.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    calculator2Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 3.521183870546056e+28, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    calculator2Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 3.521183870546056e+28, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(calculator1, renderView1)

    # show color bar/color legend
    calculator2Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(calculator1)

    # Properties modified on calculator1
    calculator1.Function = '"P [nPa]"/(("B_x [nT]"^2)/(2*1.25663706e-6))'

    # update the view to ensure updated data information
    renderView1.Update()

    # set active source
    SetActiveSource(calculator2)

    # create a new 'Calculator'
    calculator3 = Calculator(registrationName='Calculator3', Input=calculator2)
    calculator3.Function = ''

    # Properties modified on calculator3
    calculator3.ResultArrayName = 'pbz'
    calculator3.Function = '"P [nPa]"/(("B_z [nT]"^2)/(2*1.25663706e-6))'

    # show data in view
    calculator3Display = Show(calculator3, renderView1, 'UnstructuredGridRepresentation')

    # get color transfer function/color map for 'pbz'
    pbzLUT = GetColorTransferFunction('pbz')

    # get opacity transfer function/opacity map for 'pbz'
    pbzPWF = GetOpacityTransferFunction('pbz')

    # trace defaults for the display properties.
    calculator3Display.Representation = 'Surface'
    calculator3Display.ColorArrayName = ['POINTS', 'pbz']
    calculator3Display.LookupTable = pbzLUT
    calculator3Display.SelectTCoordArray = 'None'
    calculator3Display.SelectNormalArray = 'None'
    calculator3Display.SelectTangentArray = 'None'
    calculator3Display.OSPRayScaleArray = 'pbz'
    calculator3Display.OSPRayScaleFunction = 'PiecewiseFunction'
    calculator3Display.SelectOrientationVectors = 'None'
    calculator3Display.ScaleFactor = 38.400000000000006
    calculator3Display.SelectScaleArray = 'pbz'
    calculator3Display.GlyphType = 'Arrow'
    calculator3Display.GlyphTableIndexArray = 'pbz'
    calculator3Display.GaussianRadius = 1.92
    calculator3Display.SetScaleArray = ['POINTS', 'pbz']
    calculator3Display.ScaleTransferFunction = 'PiecewiseFunction'
    calculator3Display.OpacityArray = ['POINTS', 'pbz']
    calculator3Display.OpacityTransferFunction = 'PiecewiseFunction'
    calculator3Display.DataAxesGrid = 'GridAxesRepresentation'
    calculator3Display.PolarAxes = 'PolarAxesRepresentation'
    calculator3Display.ScalarOpacityFunction = pbzPWF
    calculator3Display.ScalarOpacityUnitDistance = 3.580920757821633
    calculator3Display.OpacityArrayName = ['POINTS', 'pbz']
    calculator3Display.InputVectors = [None, '']
    calculator3Display.SelectInputVectors = ['POINTS', 'B1_x [nT]']
    calculator3Display.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    calculator3Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.202810251522807e+20, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    calculator3Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.202810251522807e+20, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(calculator2, renderView1)

    # show color bar/color legend
    calculator3Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # create a new 'Calculator'
    calculator4 = Calculator(registrationName='Calculator4', Input=calculator3)
    calculator4.Function = ''

    # Properties modified on calculator4
    calculator4.ResultArrayName = 'plasmabeta'
    calculator4.Function = 'pbx*iHat+pby*jHat+pbz*kHat'

    # show data in view
    calculator4Display = Show(calculator4, renderView1, 'UnstructuredGridRepresentation')

    # trace defaults for the display properties.
    calculator4Display.Representation = 'Surface'
    calculator4Display.ColorArrayName = ['POINTS', 'pbz']
    calculator4Display.LookupTable = pbzLUT
    calculator4Display.SelectTCoordArray = 'None'
    calculator4Display.SelectNormalArray = 'None'
    calculator4Display.SelectTangentArray = 'None'
    calculator4Display.OSPRayScaleArray = 'pbz'
    calculator4Display.OSPRayScaleFunction = 'PiecewiseFunction'
    calculator4Display.SelectOrientationVectors = 'plasmabeta'
    calculator4Display.ScaleFactor = 38.400000000000006
    calculator4Display.SelectScaleArray = 'pbz'
    calculator4Display.GlyphType = 'Arrow'
    calculator4Display.GlyphTableIndexArray = 'pbz'
    calculator4Display.GaussianRadius = 1.92
    calculator4Display.SetScaleArray = ['POINTS', 'pbz']
    calculator4Display.ScaleTransferFunction = 'PiecewiseFunction'
    calculator4Display.OpacityArray = ['POINTS', 'pbz']
    calculator4Display.OpacityTransferFunction = 'PiecewiseFunction'
    calculator4Display.DataAxesGrid = 'GridAxesRepresentation'
    calculator4Display.PolarAxes = 'PolarAxesRepresentation'
    calculator4Display.ScalarOpacityFunction = pbzPWF
    calculator4Display.ScalarOpacityUnitDistance = 3.580920757821633
    calculator4Display.OpacityArrayName = ['POINTS', 'pbz']
    calculator4Display.InputVectors = ['POINTS', 'plasmabeta']
    calculator4Display.SelectInputVectors = ['POINTS', 'plasmabeta']
    calculator4Display.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    calculator4Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.202810251522807e+20, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    calculator4Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.202810251522807e+20, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(calculator3, renderView1)

    # show color bar/color legend
    calculator4Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # create a new 'Contour'
    contour1 = Contour(registrationName='Contour1', Input=calculator4)
    contour1.ContourBy = ['POINTS', 'pbz']
    contour1.Isosurfaces = [6.014051257614035e+19]
    contour1.PointMergeMethod = 'Uniform Binning'

    # Properties modified on contour1
    contour1.ContourBy = ['POINTS', 'B_z [nT]']
    contour1.Isosurfaces = [0.0]

    # show data in view
    contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

    # get color transfer function/color map for 'B_znT'
    b_znTLUT = GetColorTransferFunction('B_znT')

    # trace defaults for the display properties.
    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = ['POINTS', 'B_z [nT]']
    contour1Display.LookupTable = b_znTLUT
    contour1Display.SelectTCoordArray = 'None'
    contour1Display.SelectNormalArray = 'Normals'
    contour1Display.SelectTangentArray = 'None'
    contour1Display.OSPRayScaleArray = 'B_z [nT]'
    contour1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    contour1Display.SelectOrientationVectors = 'plasmabeta'
    contour1Display.ScaleFactor = 3.5484783172607424
    contour1Display.SelectScaleArray = 'B_z [nT]'
    contour1Display.GlyphType = 'Arrow'
    contour1Display.GlyphTableIndexArray = 'B_z [nT]'
    contour1Display.GaussianRadius = 0.1774239158630371
    contour1Display.SetScaleArray = ['POINTS', 'B_z [nT]']
    contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display.OpacityArray = ['POINTS', 'B_z [nT]']
    contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
    contour1Display.DataAxesGrid = 'GridAxesRepresentation'
    contour1Display.PolarAxes = 'PolarAxesRepresentation'
    contour1Display.InputVectors = ['POINTS', 'plasmabeta']
    contour1Display.SelectInputVectors = ['POINTS', 'plasmabeta']
    contour1Display.WriteLog = ''

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    contour1Display.ScaleTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    contour1Display.OpacityTransferFunction.Points = [0.0, 0.0, 0.5, 0.0, 1.1757813367477812e-38, 1.0, 0.5, 0.0]

    # hide data in view
    Hide(calculator4, renderView1)

    # show color bar/color legend
    contour1Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # get opacity transfer function/opacity map for 'B_znT'
    b_znTPWF = GetOpacityTransferFunction('B_znT')

    # set active source
    SetActiveSource(calculator4)

    # Properties modified on calculator4
    calculator4.Function = 'ln(pbx*iHat+pby*jHat+pbz*kHat)'

    # update the view to ensure updated data information
    renderView1.Update()

    # create a query selection
    #QuerySelect(QueryString='(plasmabeta >= 30)', FieldType='POINT', InsideOut=0)

    # set active source
    SetActiveSource(contour1)

    # create a query selection
    QuerySelect(QueryString=f'(plasmabeta >= {threshold})', FieldType='POINT', InsideOut=0)

    # create a new 'Extract Selection'
    extractSelection1 = ExtractSelection(registrationName='ExtractSelection1', Input=contour1)

    # # show data in view
    extractSelection1Display = Show(extractSelection1, renderView1, 'UnstructuredGridRepresentation')

    # hide data in view
    Hide(contour1, renderView1)

    # update the view to ensure updated data information
    renderView1.Update()

    fileToDownload = GetActiveSource()

    # save data
    SaveData(outfile, proxy=fileToDownload, ChooseArraysToWrite=1,
        PointDataArrays=['B_x [nT]', 'B_y [nT]', 'B_z [nT]'])
        
        
def rename_file(filename):
    a_file = open(filename, "r")
    list_of_lines = a_file.readlines()
    list_of_lines[1] = list_of_lines[1].replace("X [R]", "X").replace("Y [R]", "Y").replace("Z [R]", "Z")

    a_file = open(filename, "w")
    a_file.writelines(list_of_lines)
    a_file.close()


# Filenames, needs to be absolute path!
filename = 'ABSOLUTEPATH/YOUR_INPUT_FILENAME.dat'
outfile = 'ABSOLUTEPATH/YOUR_OUPUT_FILENAME.csv'
threshold = -12

# Rename the XYZ Component. Comment this part if axis is already named: "X", "Y", "Z"
rename_file(filename)

# Extracts points to path given. These points can be implemented in the pipeline.
run(inputfile=filename, outfile=outfile, threshold=threshold)