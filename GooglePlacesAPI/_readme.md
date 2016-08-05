#Google Places API ArcMap tool

Contained within this folder is a tbx file that can be added to your toolbox menu in ESRI ArcMap. It will take a shapefile, divide it into a series of search point, and then retrieve data for the following GooglePlaces categories:

  - airport
  - church
  - courthouse
  - embassy
  - gas_station
  - grocery_or_supermarket
  - hindu_temple
  - hospital
  - library
  - local_government_office
  - lodging
  - mosque
  - museum
  - parking
  - police
  - school
  - shopping_mall
  - stadium
  - synagogue
  - transit_station



##Inputs
To run the tool you will need to input your own API Key, which can be obtained through Google's Developer's Console.

Other inputs include selecting the layer representing the search area, and designating an output filepath which will also be used as the workspace environment for intermediary processes.

##Future Enhancements

This tool currently searches a 5 km radius, however future improvements could be made to monitor the number of search results and further subdivide areas that exceed the 60 result maximum Google has placed on search results. Adding an option that changes the search radius (and the corresponding size of the grid which is equal to the radius * sqrt 3 ) would also be helpful.

It would also be useful to be able to check off all of the desired search terms within the toolbox menu (or a list of selected items vs exhaustive). This would reduce total runtime.

###Test files

This folder also contains an mxd and a shapefile (in the shp folder) that can be used to test out the tool.
