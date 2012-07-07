#!/usr/bin/env python

"""Wrapper for the Strava (http://www.strava.com) API.

See https://stravasite-main.pbworks.com/w/browse/ for API documentation."""

__author__    = "Brian Landers"
__contact__   = "brian@packetslave.com"
__copyright__ = "Copyright 2012, Brian Landers"
__license__   = "Apache"
__version__   = "1.0"


BASE_API = "http://www.strava.com/api/v1"

from collections import defaultdict
from datetime import date, timedelta
import json
import urllib2


class APIError(Exception):
    pass


class StravaObject(object):

    def __init__(self, oid):
        self._id = oid

    def load(self, url, key):
        try:
            req = urllib2.Request(BASE_API + url)
            rsp = urllib2.urlopen(req)
            txt = rsp.read()
        except urllib2.HTTPError as e:
            raise APIError("%s: request failed: %s" % (url, e))

        try:
            return json.loads(txt)[key]
        except (ValueError, KeyError) as e:
            raise APIError("%s: parsing response failed: %s" % (url, e))

    @property
    def id(self):
        return self._id


class Athlete(StravaObject):

    def __init__(self, oid):
        super(Athlete, self).__init__(oid)
        self._url = "/rides?athleteId=%s" % self.id

    def rides(self, start_date=None):
        out = []

        url = self._url
        if start_date:
            url += "&startDate=%s" % start_date.isoformat()
            
        for ride in self.load(url, "rides"):
            out.append(Ride(ride["id"], ride["name"]))

        return out

    def weekly_stats(self):
        start = date.today() - timedelta(days=7)
        stats = defaultdict(float)
        
        for ride in self.rides(start_date=start):
            stats["rides"] += 1
            stats["moving_time"] += ride.detail.moving_time
            stats["distance"] += ride.detail.distance

        return stats
    
        
class Ride(StravaObject):

    def __init__(self, oid, name):
        super(Ride, self).__init__(oid)
        self._name = name
        self._detail = None
        self._segments = []
        
    @property
    def name(self):
        return self._name

    @property
    def detail(self):
        if not self._detail:
            self._detail = RideDetail(self.id)
        return self._detail

    @property
    def segments(self):
        if not self._segments:
            for effort in self.load("/rides/%s/efforts" % self.id, "efforts"):
                self._segments.append(Segment(effort))
        return self._segments


class RideDetail(StravaObject):
    def __init__(self, oid):
        super(RideDetail, self).__init__(oid)
        self._attr = self.load("/rides/%s" % oid, u"ride")

    @property
    def athlete(self):
        return self._attr["athlete"]["name"]

    @property
    def athlete_id(self):
        return self._attr["athlete"]["id"]

    @property
    def bike(self):
        return self._attr["bike"]["name"]

    @property
    def bike_id(self):
        return self._attr["bike"]["id"]

    @property
    def location(self):
        return self._attr["location"]

    @property
    def distance(self):
        return self._attr["distance"]

    @property
    def moving_time(self):
        return self._attr["movingTime"]


class Segment(StravaObject):
    def __init__(self, attr):
        super(Segment, self).__init__(attr["id"])
        self._segment = attr["segment"]
        self._time = attr["elapsed_time"]
        self._detail = None
        
    @property
    def time(self):
        return self._time
    
    @property
    def name(self):
        return self._segment["name"]

    @property
    def detail(self):
        if not self._detail:
            self._detail = SegmentDetail(self._segment["id"], self.id)
        return self._detail


class SegmentDetail(StravaObject):
    def __init__(self, segment_id, effort_id):
        super(SegmentDetail, self).__init__(segment_id)
        self._effort_attr = self.load("/efforts/%s" % effort_id, "effort")
        self._segment_attr = self.load("/segments/%s" % segment_id, "segment")

    @property
    def distance(self):
        return self._segment_attr["distance"]

    @property
    def elapsed_time(self):
        return self._effort_attr["elapsedTime"]

    @property
    def moving_time(self):
        return self._effort_attr["movingTime"]

    @property
    def average_speed(self):
        return self._effort_attr["averageSpeed"]

    @property
    def maximum_speed(self):
        return self._effort_attr["maximumSpeed"]

    @property
    def average_watts(self):
        return self._effort_attr["averageWatts"]

    @property
    def average_grade(self):
        return self._segment_attr["averageGrade"]

    @property
    def climb_category(self):
        return self._segment_attr["climbCategory"]

    @property
    def elevations(self):
        return (self._segment_attr["elevationLow"],
                self._segment_attr["elevationHigh"],
                self._segment_attr["elevationGain"])
