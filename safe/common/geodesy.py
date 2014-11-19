# coding=utf-8
"""point.py - Represents a generic point on a sphere as a Python object.

   See documentation of class Point for details.
   Ole Nielsen, ANU 2002
"""


from math import cos, sin, pi
from math import acos as unsafe_acos  # this may cause a domain error

import numpy


def acos(c):
    """acos -  Safe inverse cosine

       :param c: This value is shrunk to admissible interval
           to avoid case where a small rounding error causes
           a math domain error.
       :type c: float

       :returns: Arcos of the parameter c.
       :rtype: float
    """
    if c > 1:
        c = 1
    if c < -1:
        c = -1

    return unsafe_acos(c)


class Point(object):
    """Definition of a generic point on the sphere.

    Defines a point in terms of latitude and longitude
    and computes distances to other points on the sphere.

    Initialise as
      Point(lat, lon), where lat and lon are in decimal degrees (dd.dddd)

    Public Methods:
        distance_to(P)
        bearing_to(P)
        dist(P)

    Author: Ole Nielsen, ANU 2002
    """

    # class constants
    R = 6372000  # Approximate radius of Earth (m)
    degrees2radians = pi / 180.0

    def __init__(self, latitude=None, longitude=None):
        """ Point constructor.
        :param latitude: The latitudinal position of the point
        :type latitude: float

        :param longitude: The longitudinal position of the point
        :type longitude: float

        :raises: Exception, AssertionError

        :returns: a point instance
        :rtype: Point
        """

        if latitude is None:
            msg = 'Argument latitude must be specified to Point constructor'
            raise Exception(msg)

        if longitude is None:
            msg = 'Argument longitude must be specified to Point constructor'
            raise Exception(msg)

        msg = 'Specified latitude %f was out of bounds' % latitude
        assert(-90 <= latitude <= 90.0), msg

        msg = 'Specified longitude %f was out of bounds' % longitude
        assert(-180 <= longitude <= 180.0), msg

        self.latitude = float(latitude)
        self.longitude = float(longitude)

        lat = latitude * self.degrees2radians    # Converted to radians
        lon = longitude * self.degrees2radians   # Converted to radians
        self.coslat = cos(lat)
        self.coslon = cos(lon)
        self.sinlat = sin(lat)
        self.sinlon = sin(lon)

    #---------------
    # Public methods
    #---------------
    def bearing_to(self, P):
        """Bearing (in degrees) to point P.

        :param P: A relative point
        :type P: Point

        :returns: bearing degrees
        :rtype: int
        """
        AZ = self.AZ(P)
        return int(round(AZ / self.degrees2radians))

    def distance_to(self, P):
        """Distance to point P.

        :param P: A relative point
        :type P: Point

        :returns: distance
        :rtype: float
        """
        GCA = self.GCA(P)
        return self.R * GCA

    def approximate_distance_to(self, P):
        """Very cheap and rough approximation to distance.

        :param P: A relative point
        :type P: Point

        :returns: distance
        :rtype: float
        """

        return max(abs(self.latitude - P.latitude),
                   abs(self.longitude - P.longitude))

    #-----------------
    # Internal methods
    #-----------------
    def __repr__(self):
        """Readable representation of point with two decimal places.

        :returns: point in human readable format
        :rtype: str
        """
        d = 2
        lat = round(self.latitude, d)
        lon = round(self.longitude, d)
        return ' (' + str(lat) + ', ' + str(lon) + ')'

    def GCA(self, P):
        """Compute the Creat Circle Angle (GCA) between current point and P.

        :param P: A relative point
        :type P: Point

        :returns: angle in radians
        :rtype: float
        """

        alpha = P.coslon * self.coslon + P.sinlon * self.sinlon
        # The original formula is alpha = cos(self.lon - P.lon)
        # but rewriting lets us make us of precomputed trigonometric values.

        x = alpha * self.coslat * P.coslat + self.sinlat * P.sinlat
        return acos(x)

    def AZ(self, P):
        """Compute Azimuth bearing (AZ) from current point to P.

        :param P: A relative point
        :type P: Point

        :returns: bearing in radians
        :rtype: float
        """

        # Compute cosine(AZ), where AZ is the azimuth angle
        GCA = self.GCA(P)
        c = P.sinlat - self.sinlat * cos(GCA)
        c = c / self.coslat / sin(GCA)

        AZ = acos(c)

        # Reverse direction if bearing is westward,
        # i.e. sin(self.lon - P.lon) > 0
        # Without this correction the bearing due west, say, will be 90 degrees
        # because the formulas work in the positive direction which is east.
        #
        # Precomputed trigonometric values are used to rewrite the formula:

        if self.sinlon * P.coslon - self.coslon * P.sinlon > 0:
            AZ = 2 * pi - AZ

        return AZ

    def generate_circle(self, radius, resolution=1):
        """Make a circle about this point.

        :param radius: The desired cirle radius [m]
        :type radius: float, int

        :param resolution: Radial distance (degrees) between
              points on circle. Default is 1 making the circle consist
              of 360 points. (optional)
        :type resolution: int, float

        :returns: list of lon, lat coordinates defining the circle
        :rtype: list

        ..note::
            The circle is defined in geographic coordinates so
            the distance in meters will be greater than the specified radius
            in the north south direction.
        """

        # Find first point in circle to the east of the center by bisecting
        # until desired radius is achieved

        # Go north until distance is greater than desired
        step = 0.001
        d = 0
        while d < radius:
            stepmin = step
            step *= 2
            p = Point(self.latitude + step, self.longitude)
            d = self.distance_to(p)

        # Then bisect until the correct distance is found in degrees
        stepmax = step
        while not numpy.allclose(d, radius, rtol=1.0e-6):
            step = (stepmax + stepmin) / 2
            p = Point(self.latitude + step, self.longitude)
            d = self.distance_to(p)

            if d > radius:
                stepmax = step
            else:
                stepmin = step

        #print
        #print ('Found geographical distance %f degrees yielding radius %f m'
        #       % (step, d))
        r = step

        # Generate circle with geographic radius = step (degrees)
        P = [[p.longitude, p.latitude]]

        angle = 0
        while angle < 360:
            theta = angle * self.degrees2radians
            #print angle, theta, self.bearing_to(p), self.distance_to(p)

            # Generate new point on circle
            lat = self.latitude + r * cos(theta)
            lon = self.longitude + r * sin(theta)

            p = Point(latitude=lat, longitude=lon)
            angle += resolution

            P.append([p.longitude, p.latitude])

        # Close polygon
        P.append(P[0])

        return numpy.array(P)
