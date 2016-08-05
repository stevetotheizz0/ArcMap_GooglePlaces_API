import arcpy, os, fileinput
from arcpy import env

#table = "C:\Users\Qs8\Desktop\GooglePlacesAPI\shp\OutputResults.csv"

def createPointfile(input) :
    directory = os.path.dirname(input)
    arcpy.env.workspace = os.path.dirname(input)
    table = os.path.dirname(input) + "\OutputResults.csv"


    #Adding headers into the CSV
    headers = 'Category,Name,Latitude,Longitude'
    for line in fileinput.input([table], inplace=True):
        if fileinput.isfirstline():
            print headers
        print line,
    #Converting to DBF to import as shapefile (may not be a necessary step)
    arcpy.TableToTable_conversion (table, directory, "Output_as_DBF")
    arcpy.MakeXYEventLayer_management("Output_as_DBF.dbf", "Longitude","Latitude", "firestations_points",4326)
    arcpy.CopyFeatures_management("firestations_points", input)

    #Cleaning up intermediate files created through the processes.
    arcpy.Delete_management("firestation_points.lyr")
    arcpy.Delete_management("OutputResults.csv")
    arcpy.Delete_management("Output_as_DBF.dbf")

    #Removing duplicate points created by overlapping search radii
    fields = ["Category", "Name","Latitude","Longitude"]

    arcpy.DeleteIdentical_management (input, fields)
