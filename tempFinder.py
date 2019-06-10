from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engin
from json import dumps
from flask.ext.jsonify import jsonify, loads
from urllib.request import urlopen
import sqlite3
import datetime
import pprint

dbName="/home/ubuntu/proj/pyWeatherCache/weatherCache.db"
cityCodePortlandOR='5746545'
zipCodePortlandOR='97214'
expirationSecs=300
weatherZipURL='http://api.openweathermap.org/data/2.5/weather?zip='
weatherIdURL='http://api.openweathermap.org/data/2.5/weather?id='
pp = pprint.PrettyPrinter(indent=4)

class TempQuery(Resource):
    def saveQuery( curs, tempF, zipCode):
        #insert most recent entry from weatherCache database
        timestamp = datetime.timestamp()
        rslt = curs.execute("INSERT INTO {tn} (timestamp, zipCode, tempF) VALUES({ts}, {cz}, {tf})"\
                .format(tn='tempByCity', ts=timestamp, cz=zipCode, tf=tempF) )
        return rslt


    def getLast( curs, zipCode):
        #select most recent entry from weatherCache database
        query = curs.execute("SELECT timestamp, zipCode, tempF FROM {tn} WHERE zipCode={cz} ORDER BY timestamp DESC LIMIT 1".format(tn='tempByCity', cz=zipCode) )

        #data format check
        print ("GETLAST Query result:\n")
        pp.print( query)

        return {"temperature":query[2], "timestamp":query[0], "zipCode":query[1]} 


    def isExpired( lQuery):
        #Determine if last query occurred > expirationSec(ond)s ago [default=300 or 5 mins]

        #get query datetime from query timestamp
        lQueryTime = datetime.fromtimestamp( lQuery["timestamp"])
 
        #get current datetime
        curTS = datetime.now()

        #create timedelta from diff between datetimes
        timediff = curTime - lQueryTime

        if timediff.total_seconds() > expirationSecs:
            return True
        else:
            return False


    def getTempFromInternet( zipCode):
        #get current weather data at city desig. by zipCode from openweathermap.org

        dfltURL = weatherZipURL
        url = dfltURL + zipCode

        #get result from API query
        urlOut = urlopen( url).read()
        urlOut = urlOut.decode('utf-8')

        #convert result to JSON format
        weather = json.loads( urlOut)

        #data format check
        print( "getTempFromNet weather:\n")
        pp.print( weather)

        #extract temperature from weather data
        curTemp = weather['main']['temp']

        #data format check
        print( "getTempFromNet curTemp:\n")
        pp.print( curTemp)

        return {"temperature":curTemp, "timestamp":datetime.timestamp(), "zipCode":zipCode} 


    def get( self):
        #return current temperature at city desig. by dfltZip(Code);
        #if last query saved in DB was > 5min ago, return last query temperature;
        #else get current temperature from default API, and save the query data in DB
        #return temperature data in JSON format

        dfltZip = zipCodePortlandOR

        conn = sqlite3.connect( dbName)
        curs = conn.cursor()

        #get most recent query
        lQuery = getLast( curs)

        #data format check
        print( "GET lQuery:\n")
        pp.print( lQuery)

        #check if query has been called recently
        if isExpired( lQuery):
            #get weather/temp data from Internet
            curTemp = getTempFromInternet( dfltZip)
            #save results of recent query and save results to DB
            rslt = saveQuery( curs, curTemp, dfltZip)
            conn.commit()
        else:
            curTemp = lQuery

        #data format check
        print( "GET curTemp:\n")
        pp.print( curTemp)

        #close DB connection
        conn.close()

        #return data in JSON format
        return jsonify(result)


#app = Flask(__name__)
#api = Api(app)
#api.add_resource(TempQuery, '/temperature')

#if __name__ == '__main__':
#    app.run(port='9001')
#else:
    TempQuery.get()
