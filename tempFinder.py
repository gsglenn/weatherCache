from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from sqlalchemy import create_engine
import json
from urllib import urlopen
import sqlite3
from datetime import datetime
import time
import pprint

dbName="/home/ubuntu/proj/pyWeatherCache/weathercache.db"
#cityCodePortlandOR='5746545'
zipCodePortlandOR='97214'
expirationSecs=300
weatherZipURL='http://api.openweathermap.org/data/2.5/weather?zip='
owmAPPID='781238aec79628b3c6647322cb2537f2'
pp = pprint.PrettyPrinter(indent=4)

#CODE for TESTING
#class TempQuery:
class TempQuery(Resource):
    def saveQuery( self, curs, tempF):
        #insert most recent entry from weatherCache database
        timestamp = int(time.time())

        query = "INSERT INTO temperature (timestamp, zipCode, tempF) VALUES(" + str(timestamp) + "," + tempF['zipCode'] + "," + str(tempF['temperature']) + ")"

        #data format check
        #print ("SAVEQUERY query:\n")
        #pp.pprint( query)

        curs.execute( query)
        return True


    def getLast( self, curs, zipCode):
        #select most recent entry from weatherCache database
        query = "SELECT timestamp, zipCode, tempF FROM temperature WHERE zipCode=" + zipCode + " ORDER BY timestamp DESC LIMIT 1"
        rslt = curs.execute( query)
        qRow = curs.fetchone()

        #data format check
        #print ("GETLAST Query result:\n")
        #pp.pprint( qRow)
        if qRow is not None:
            return {"temperature":qRow[2], "timestamp":qRow[0], "zipCode":qRow[1]} 
        else:
            #if no prev queries, return dummy query that will prompt Internet query
            return {"temperature":0.0, "timestamp":0.0, "zipCode":zipCode}


    def isExpired( self, lQuery):
        #Determine if last query occurred > expirationSec(ond)s ago [default=300 or 5 mins]

        #get query datetime from query timestamp
        lQueryTime = datetime.fromtimestamp( lQuery["timestamp"])
 
        #get current datetime
        curTime = datetime.now()

        #create timedelta from diff between datetimes
        timediff = curTime - lQueryTime

        if timediff.total_seconds() > expirationSecs:
            return True
        else:
            return False


    def getTempFromInternet( self, zipCode):
        #get current weather data at city desig. by zipCode from openweathermap.org

        dfltURL = weatherZipURL
        url = dfltURL + zipCode+ ',us&mode=json&APPID=' + owmAPPID

        #data format check
        #print( "getTempFromNet url:\n")
        #pp.pprint( url)

        #get result from API query
        urlOut = urlopen( url).read()
        urlOut = urlOut.decode('utf-8')

        #convert result to JSON format
        weather = json.loads( urlOut)

        #data format check
        #print( "getTempFromNet weather:\n")
        #pp.pprint( weather)

        #extract temperature from weather data
        curTemp = weather['main']['temp']

        #data format check
        #print( "getTempFromNet curTemp:\n")
        #pp.pprint( curTemp)

        return {"temperature":curTemp, "timestamp":time.time(), "zipCode":zipCode} 


    def get( self):
        #return current temperature at city desig. by dfltZip(Code);
        #if last query saved in DB was > 5min ago, return last query temperature;
        #else get current temperature from default API, and save the query data in DB
        #return temperature data in JSON format

        dfltZip = zipCodePortlandOR

        conn = sqlite3.connect( dbName)
        conn.row_factory = sqlite3.Row
        curs = conn.cursor()

        #get most recent query
        lQuery = self.getLast( curs, dfltZip)

        #data format check
        #print( "GET lQuery:\n")
        #pp.pprint( lQuery)

        #check if query has been called recently
        if self.isExpired( lQuery):
            #get weather/temp data from Internet
            curTemp = self.getTempFromInternet( dfltZip)
            #save results of recent query and save results to DB
            rslt = self.saveQuery( curs, curTemp)
            conn.commit()
        else:
            curTemp = lQuery

        #data format check
        #print( "GET curTemp:\n")
        #pp.pprint( curTemp)

        #close DB connection
        conn.close()

        #return data in JSON format
        return jsonify( curTemp)


app = Flask(__name__)
api = Api(app)
api.add_resource(TempQuery, '/temperature')

if __name__ == '__main__':
    app.run(port='9001')

#CODE for TESTING
#tQuery = TempQuery()
#tQuery.get()
