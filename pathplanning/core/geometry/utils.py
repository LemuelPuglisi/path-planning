import math

from pathplanning.core.base import Point

def normalizeAngle(a):
    while a > math.pi:
        a = a - 2*math.pi
    while a < - math.pi:
        a = a + 2*math.pi
    return a


def pointsMatch(point1: Point, point2: Point):
    return point1.x == point2.x and point1.y == point2.y


def cellIntersectsObstacle(cell_TR, cell_BL, obs_TR, obs_BL):
    """ Separating axis theorem. """
    return not (
        cell_TR.x < obs_BL.x or 
        cell_BL.x > obs_TR.x or 
        cell_TR.y > obs_BL.y or # y axis checks are flipped
        cell_BL.y < obs_TR.y    # because we consider painting reference.
    )


#----------------------------------------------------------------------------
# The following code is taken from GeekForGeeks
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect
#----------------------------------------------------------------------------

def onSegment(p, q, r):
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False


def orientation(p, q, r):      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):   return 1    # Clockwise orientation
    elif (val < 0): return 2    # Counterclockwise orientation
    else: return 0              # Collinear orientation
        
        
def segmentsIntersects(p1,q1,p2,q2):
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
  
    # General case
    if ((o1 != o2) and (o3 != o4)): return True
  
    # Special Cases
    # p1 , q1 and p2 are collinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True
  
    # p1 , q1 and q2 are collinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True
  
    # p2 , q2 and p1 are collinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True
  
    # p2 , q2 and q1 are collinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True
  
    # If none of the cases
    return False
  