def validate(point, timestamp=None):
    """Return first polygon in which point is found, else return False

    Validate whether geographical coordinate point is at known friday bar.
    Validate fences using https://www.mapcustomizer.com/.
    
    Parameters
    ----------
    point : (float, float)
    
    Returns
    -------
    name/bool : str/bool
        If True, return name of kollegium point is inside,
        if False, return False
    """
    def inside_polygon(poly):
        """Valide if point is in polygon
        
        Source: http://www.ariel.com.au/a/python-point-int-poly.html
        """
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
    
    diaman = [(55.783017, 12.520569), (55.782780, 12.521862),
              (55.782273, 12.521631), (55.782477, 12.520349)]
    diagon = [(55.790038, 12.524303), (55.789637, 12.526174),
              (55.788925, 12.525812), (55.789183, 12.524014)]
    ethere = [(55.787810, 12.517801), (55.787520, 12.519421),
              (55.787165, 12.519260), (55.787466, 12.517576)]
    maskin = [(55.780649, 12.516041), (55.780293, 12.518005),
              (55.779744, 12.517790), (55.780097, 12.515773)]
    hegnet = [(55.782815, 12.516577), (55.782583, 12.517815),
              (55.782138, 12.517299), (55.782317, 12.516362)]
    shuset = [(55.786680, 12.525446), (55.786544, 12.526239),
              (55.786265, 12.526094), (55.786397, 12.525315)]
    
    
    fences = {"diaman": diaman, "diagon": diagon, "ethere": ethere, 
              "maskin": maskin, "hegnet": hegnet, "shuset": shuset}
        
    for name, poly in fences.items():
        if inside_polygon(poly): 
            if timestamp is None:
                #print "Warning: Timestamp not provided, activity not guaranteed social/friday bar"
                return name
            else:
                from datetime import datetime as dt
                datetime = dt.fromtimestamp(timestamp)
                if datetime.hour >= 16:
                    if datetime.weekday() == 4:
                        return True
                    if name == "shuset" and datetime.weekday() in range(5):
                        return True
                return False
        
    return False
    
    
    
    
    