"""Validate whether geographical coordinate point is on DTU campus.
Planar approximation test of whether a point is inside the polygon
(geofence) that encloses DTU. Complex geofence does not include Skylab, or
any of the kollegiums, because it is meant to encompas study-related
geospacial areas.

Algorithm from http://www.ariel.com.au/a/python-point-int-poly.html
"""

def validate(point, poly="complex"):
    """Validate if point is inside campus.
    
    Parameters
    ----------
    point : (float, float)
    poly : str
        Specify whether to use a complex fence that in very cunning 
        fashion encapsulates only study-related campus areas, or simple
        fence that uses whole campus area. If using simple an extra
        condition should be added to check whether point is in kollegium.
    
    Returns
    -------
    inside : bool
        If True, point is inside campus, else False.
    """
    
    complex_fence = [(55.79201, 12.52896), (55.78497, 12.52634),
                     (55.78516, 12.52454), (55.7793, 12.52128),
                     (55.77843, 12.51643), (55.78118, 12.51224),
                     (55.78299, 12.51327), (55.78331, 12.5116),
                     (55.79245, 12.52014)]
    
    simple_fence = [(55.79201, 12.52896), (55.78002, 12.52462),
                    (55.77843, 12.51643), (55.78185, 12.50977), 
                    (55.79249, 12.5205)]
    
    if poly == "simple": 
        poly = simple_fence; 
        print "Warning: Using simple fence! Check if location is home."
    elif poly == "complex": 
        poly = complex_fence
    else:
        print "Warning: Invalid fence option specified; using complex."
    
    x, y = point

    n = len(poly)
    inside = False

    p1x,p1y = poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xints = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside