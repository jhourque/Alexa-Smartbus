import json
import urllib2
import requests

class Bus: # Definition of bus class for smartbus
    """Bus class is defined by:
    - type (= bus, API could also be used for rers, metros, bus, tramways, noctiliens)
    - code (line number)
    - station (Slug of the station)
    - stations (list of all station deserved by bus)
    - way (A, R, A+R)
    - wayName (Name of way station)
    - timenext (time of next arrival in station)
    - timefollower (time of following bus in station)
    - RESTUrl url for RATP query
    - query_code (code of last request to RATP API)
    - query_message (message of last request to RATP API)
    """

    def __init__(self, code):
        self.type = "bus"
        self.code = code
        self.station = u'None'
        self.stations = []
        self.way = u'None'
        self.wayName = u'None'
        self.RESTUrl = "https://api-ratp.pierre-grimaud.fr/v3"
        self.query_code = 200
        self.query_message = ""

        self.queryStations()

    def queryStations(self):
        query = '{0}/{1}/{2}/{3}'.format(self.RESTUrl, 'stations', self.type, self.code)
        result = requests.get(query)
        self.query_code = result.status_code
        if result.status_code == 200:
            jsonRes = result.json()['result']['stations']
            self.stations = []
            for j in jsonRes:
                self.stations.append(j[u'name'])
            self.query_message = ""
        else:
            print 'error query returned {0}'.format(result)
            self.query_message = "Bus inconnu"

    def getStations(self):
        message = "Les stations du {0} {1} sont: \n".format(self.type, self.code)
        count = 1
        for s in self.stations:
            station = '{0}: {1}.\n'.format(count, s)
            message += station
            count += 1
        return message

    def setStation(self, station):
        if station in self.stations:
            self.station = station

    def getWay(self):
        print 'A: {0}, R: {1}'.format(self.stations[0], self.stations[-1])

    def setWay(self, way):
        if way == 'A':
            self.way = way
            self.wayName = self.stations[-1]
        elif way == 'R':
            self.way = way
            self.wayName = self.stations[0]
        else:
            print '{0} inconnue. La direction doit etre A ou R'.format(way)

    def querySchedules(self):
        query = '{0}/{1}/{2}/{3}/{4}/{5}'.format(self.RESTUrl, 'schedules', self.type, self.code, self.station, self.way)
        result = requests.get(query)
        self.query_code = result.status_code
        if result.status_code == 200:
            jsonRes = result.json()['result']['schedules']
            self.stations = []
            self.timenext     = jsonRes[0]['message'].replace('mn', 'minutes')
            self.timefollower = jsonRes[1]['message'].replace('mn', 'minutes')
            self.query_message = ""
        else:
            print 'error query returned {0}'.format(result)
            self.query_message = "Erreur de connexion"

    def getSchedules(self):
        self.querySchedules()
        message = 'Le prochain bus numero {0} en direction de {1} passera dans {2}. Le suivant dans {3}'.format(self.code, self.wayName, self.timenext, self.timefollower)
        return message
