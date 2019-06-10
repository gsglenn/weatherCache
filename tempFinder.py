#import sqlite
#import flask

cityCodePortlandOR='5746545'
expirationSecs=300
weatherAPI=''

def getLastQuery():
    #select most recent entry from weatherCache database

    #convert database record to json
    return 0, mrrJSON

def lastQueryExpired( lQuery):
    curTimestampSecs = 0
    qryTimestampSecs = 0
    #convert timestamp to seconds
    #get current time in seconds
     
    #compare diff in tsSeconds to expirationSecs
    if (curTimestampSecs - qryTimestampSecs) > expirationSecs:
        return True
    else:
        return False

def getTempFromInternet( weatherAPI):
    curTemp = 0
    #get result from API query
    #extract temperature
    return curTemp

def retTemperature( cQuery):
    #push temperature query
    return


rslt, lQuery = getLastQuery()
if lastQueryExpired( lQuery):
    rslt, cQuery = getTempFromInternet( weatherAPI)
else:
    cQuery = lQuery
rslt = retTemperature( cQuery)
