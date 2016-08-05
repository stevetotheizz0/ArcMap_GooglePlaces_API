from RadiusPoints import hexagonCentroids
from googleplacesAPI import ApiTypeOutput
from createPoints import createPointfile
import arcpy, os
hexsize = 8660.2540378
key = arcpy.GetParameterAsText(0)
shapeFile = arcpy.GetParameterAsText(1)
outputPath = arcpy.GetParameterAsText(2)

types = ["airport","church","courthouse","embassy","gas_station","grocery_or_supermarket","hindu_temple","hospital","library","local_government_office","lodging","mosque","museum","parking","police","school","shopping_mall","stadium","synagogue","transit_station"
]

outputWorkspace = os.path.dirname(outputPath)
arcpy.env.scratchWorkspace = os.path.dirname(outputPath)
myPythonModules = outputWorkspace
sys.path.append(myPythonModules)

def ReadCoordinatesShapefile(shapefile) :
    cursor = arcpy.SearchCursor(shapefile)
    for row in cursor:
        arcpy.AddMessage(row)
        coordinates = [row.getValue("POINT_X"),row.getValue("POINT_Y")]
        ApiTypeOutput(outputPath,coordinates, 5000, types, key)


hexagonCentroids(shapeFile, outputPath, width='8660.2540378', clipToAOI=True)
ReadCoordinatesShapefile(outputPath)
createPointfile(outputPath)
