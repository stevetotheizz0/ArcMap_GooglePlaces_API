# Import system modules

"""

This script creates a series of points that are offset in a way that would create a hexagon Theesan polygon between
each point. This reduced the overlap of search radii.

The distance to points is set to X * sqrt(3). This allows for the search radius to = X, where each radius will touch
the neighboring radii with minimal overlap at the outermost extent.

The final part of this script selects coordinates whos search radius overlaps with the area of interest (the
shapefile input for the program.

"""



import sys, os, arcpy, traceback, math
from arcpy import env

# overwrite setting
env.overwriteOutput = 1

def hexagonCentroids(inputAOI, outputTheissen, width, clipToAOI=True):
    """A function to check for correct field types between the from and to fields."""
    arcpy.AddMessage("Starting HexCentroids")
    descInput = arcpy.Describe(inputAOI)
    if descInput.dataType == 'FeatureLayer':
        inputAreaOfInterest = descInput.CatalogPath
    else:
        inputAreaOfInterest = inputAOI

    arcpy.AddMessage(inputAreaOfInterest)
    # Describe the Input and get its extent properties
    desc = arcpy.Describe(inputAreaOfInterest)
    ext = desc.extent
    xcoord = ext.XMin
    ycoord = ext.YMin
    urxcoord = ext.XMax
    urycoord = ext.YMax
    height = float(width) * math.sqrt(3)

    # Invert the height and width so that the flat side of the hexagon is on the bottom and top
    tempWidth = width
    width = height
    height = tempWidth

    # Calculate new offset origin, opposite corner and Y axis point coordinates
    factor1 = -2.0
    origin = str(xcoord + float(width) * factor1) + " " + str(ycoord + float(height) * factor1)
    originX = str(xcoord + float(width) * factor1)
    originY = str(ycoord + float(height) * factor1)

    factor2 = 2.0
    oppositeCorner = str(urxcoord + float(width) * factor2) + " " + str(urycoord + float(height) * factor2)
    oppositeCornerX = str(urxcoord + float(width) * factor2)
    oppositeCornerY = str(urycoord + float(height) * factor2)

    factor3 = 0.5
    newOrigin = str(float(originX) + float(width) * factor3) + " " + str(float(originY) + float(height) * factor3)
    newOriginX = str(float(originX) + float(width) * factor3)
    newOriginY = str(float(originY) + float(height) * factor3)

    newOppositeCorner = str(float(oppositeCornerX) + float(width) * factor3) + " " + str(float(oppositeCornerY) + float(height) * factor3)
    newOppositeCornerX = str(float(oppositeCornerX) + float(width) * factor3)
    newOppositeCornerY = str(float(oppositeCornerY) + float(height) * factor3)

    yAxisCoordinates1 = str(float(originX)) + " " + str(float(oppositeCornerY))
    yAxisCoordinates2 = str(float(newOriginX)) + " " + str(float(newOppositeCornerY))

    # Calculate Length, hexagonal area and number of columns
    sideLength =  float(height) / math.sqrt(3)
    hexagonArea = 2.598076211 * pow(sideLength, 2)
    numberOfColumns = int((urxcoord - xcoord)  / int(width))

    # Add Messages
    arcpy.AddMessage("------------------------")
    arcpy.AddMessage("Width: " + str(height))
    arcpy.AddMessage("Height: " + str(width))
    arcpy.AddMessage("Hexagon Area: " + str(hexagonArea))
    arcpy.AddMessage("Number of Columns: " + str(numberOfColumns))
    arcpy.AddMessage("------------------------")

    try:

        outputWorkspace = os.path.dirname(outputTheissen)
        arcpy.env.scratchWorkspace = os.path.dirname(outputTheissen)
        #REMOVE LINE BELOW AFTER TESTING
        arcpy.AddMessage(outputWorkspace)

        # Process: Create Fishnet...
        fishnetPath1 = (os.path.join(outputWorkspace, "Fishnet_1"))
        fishnet1 = arcpy.CreateFishnet_management(fishnetPath1, origin, yAxisCoordinates1, width, height, "0", "0", oppositeCorner, "LABELS", "")

        # Process: Create Fishnet (2)...
        fishnetPath2 = (os.path.join(outputWorkspace, "Fishnet_2"))
        fishnet2 = arcpy.CreateFishnet_management(fishnetPath2, newOrigin, yAxisCoordinates2, width, height, "0", "0", newOppositeCorner, "LABELS")

        # Process: Create Feature Class: Using 3785 allows for the buffer to be the right size
        spatialRef = arcpy.Describe(inputAreaOfInterest).spatialReference
        hexPoints = arcpy.CreateFeatureclass_management(outputWorkspace, "hex_points", "POINT", "", "", "", 3785)

        # Get fishnet labels from the results of the fishnet tool...
        fishnetLabel1 = fishnet1.getOutput(1)
        fishnetLabel2 = fishnet2.getOutput(1)

        # Define projection for the fishnet labels
        arcpy.DefineProjection_management(fishnetLabel1, spatialRef)
        arcpy.DefineProjection_management(fishnetLabel2, spatialRef)

        # Process: Append...
        inputForAppend = "{0};{1}".format(fishnetLabel1, fishnetLabel2)
        arcpy.Append_management(inputForAppend, hexPoints, "NO_TEST", "", "")

        #Create points and add XY to attributes
        arcpy.MakeFeatureLayer_management(hexPoints, "hex_points", "", "", "")

        #Creating Buffer to Keep Points Just Outside the Boundaries
        hexPointBuffer = outputWorkspace + "\hexPointBuffer"
        arcpy.Buffer_analysis(hexPoints, hexPointBuffer, "5000 METERS","","","","","PLANAR")
        hexPointBuffer = hexPointBuffer + ".shp"

        #Adding Layer to the Map to Allow for Select by Location
        mxd = arcpy.mapping.MapDocument("CURRENT")
        df = arcpy.mapping.ListDataFrames(mxd, "*")[0]
        addLayer = arcpy.mapping.Layer(str(hexPointBuffer))
        arcpy.mapping.AddLayer(df, addLayer, "TOP")

        #Points won't select within a distance of the AOI for whatever reason. Workaround by using buffer,
        #select overlap, and export.
        arcpy.SelectLayerByLocation_management("hexPointBuffer","",inputAOI,0,"new_selection")
        hexPointBufferClipped = outputWorkspace + "\hexPointBufferClipped"
        arcpy.CopyFeatures_management("hexPointBuffer", hexPointBufferClipped)

        # Chaning the projection to 4326 changes units from meters to decimals so that the XY match Google's API
        arcpy.Project_management(hexPointBufferClipped + ".shp", hexPoints, 4326)
        arcpy.FeatureToPoint_management(hexPoints, outputTheissen)
        arcpy.AddXY_management(outputTheissen)

        #Delete temporary files
        for lyr in arcpy.mapping.ListLayers(mxd, "", df):
            if lyr.name.lower() == "hexpointbuffer":
                arcpy.mapping.RemoveLayer(df, lyr)
        arcpy.Delete_management(fishnet1)
        arcpy.Delete_management(fishnet2)
        arcpy.Delete_management(fishnetLabel1)
        arcpy.Delete_management(fishnetLabel2)
        arcpy.Delete_management(hexPointBufferClipped + ".shp")
        arcpy.Delete_management(hexPointBuffer)
        arcpy.Delete_management(hexPoints)


    except:
        # get the traceback object
        tb = sys.exc_info()[2]
        # tbinfo contains the line number that the code failed on and the code from that line
        tbinfo = traceback.format_tb(tb)[0]
        # concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_type)+ ": " + str(sys.exc_value) + "\n"
        # generate a message string for any geoprocessing tool errors
        msgs = "GP ERRORS:\n" + arcpy.GetMessages(2) + "\n"

        # return gp messages for use with a script tool
        arcpy.AddError(msgs)
        arcpy.AddError(pymsg)

        # print messages for use in Python/PythonWin
        print msgs
        print pymsg



if __name__ == '__main__':
    argv = tuple(arcpy.GetParameterAsText(i)
             for i in range(arcpy.GetArgumentCount()))
    hexagonCentroids(*argv)
