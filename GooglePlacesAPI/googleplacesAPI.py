import urllib2, json, csv, os, unicodecsv as csv, time, arcpy

def ApiTypeOutput(outputPath,coordinates,radius,types,key):

    outputWorkspace = os.path.dirname(outputPath)
    arcpy.env.scratchWorkspace = os.path.dirname(outputPath)

    def GooglePlace(coordinates,radius, type, key):
        x = 0
        url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=%s,%s&radius=%s&types=%s&key=%s" % (
        coordinates[1], coordinates[0], radius, str(type), str(key))
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        jsonRaw = response.read()
        jsonData = json.loads(jsonRaw)
        nextPage(jsonData, type)
        return (jsonData)

    def nextPage(x,type):
        while 'next_page_token' in x:
            time.sleep(3)
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?pagetoken=%s&key=%s" % (str(x['next_page_token']), str(key))
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            jsonRawNextPg = response.read()
            jsonDataNextPg = json.loads(jsonRawNextPg)
            writeOutput(type, jsonDataNextPg)
            x = jsonDataNextPg


    def writeOutput(type, data):
        with open(outputWorkspace + '\OutputResults.csv', 'ab') as testfile:
            for item in data['results']:
                csv_writer = csv.writer(testfile, encoding='utf-8')
                csv_writer.writerow([type,item['name'], item['geometry']['location']['lat'],item['geometry'][
                    'location']['lng']])


    for i in xrange(len(types)):
        currentType = types[i]
        arcpy.AddMessage(currentType)
        data = GooglePlace(coordinates, radius, currentType, key)
        writeOutput(currentType, data)
        time.sleep(3)

    print "finished"