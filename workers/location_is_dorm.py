"""Validate whether geographical coordinate point is at known dorm.
Validate fences using https://www.mapcustomizer.com/.

Algorithm from http://www.ariel.com.au/a/python-point-int-poly.html
"""

def validate(point):
    """Validate if point is in known dorm location.
    
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
    
    andels = [(55.780256, 12.522057), (55.780491, 12.523003),
              (55.781299, 12.523452), (55.781163, 12.524386),
              (55.780184, 12.523924), (55.779916, 12.521987)]
    kampsa = [(55.781501, 12.522751), (55.783411, 12.523814), 
              (55.783813, 12.524533), (55.783649, 12.525473),
              (55.781190, 12.524554)]
    villum = [(55.784784, 12.524647), (55.784633, 12.525645), 
              (55.784013, 12.525447), (55.784209, 12.524351)]
    willia = [(55.782516, 12.511908), (55.782425, 12.512409),
              (55.781365, 12.511568), (55.781450, 12.511026)]
    ostenf = [(55.788685, 12.531732), (55.788689, 12.533580),
              (55.787745, 12.533572), (55.787780, 12.531605)]
    viggoj = [(55.799586, 12.491374), (55.800299, 12.493603),
              (55.799319, 12.493867), (55.799090, 12.491979)]
    troero = [(55.847144, 12.526772), (55.847267, 12.530204),
              (55.846379, 12.530299), (55.846287, 12.526854)]
    nybrog = [(55.773445, 12.471626), (55.774310, 12.474543),
              (55.772307, 12.477018), (55.771529, 12.475360)]
    hjorte = [(55.740727, 12.435091), (55.740907, 12.436595),
              (55.739276, 12.437189), (55.738757, 12.435537)]
    paulbe = [(55.811511, 12.512745), (55.811238, 12.515996),
              (55.810111, 12.515977), (55.810192, 12.511739)]
    popede = [(55.764040, 12.476051), (55.764064, 12.477994),
              (55.762321, 12.477835), (55.762309, 12.476876)]
    gahage = [(55.694281, 12.586961), (55.694553, 12.587367),
              (55.694427, 12.587562), (55.694170, 12.587173)]
    lautru = [(55.730406, 12.404633), (55.730682, 12.405655),
              (55.729430, 12.406903), (55.728875, 12.404911)]
    
    
    fences = {"andels": andels, "kampsa": kampsa, "villum": villum, 
              "willia": willia, "ostenf": ostenf, "viggoj": viggoj, 
              "troero": troero, "nybrog": nybrog, "hjorte": hjorte, 
              "paulbe": paulbe, "popede": popede, "gahage": gahage, 
              "lautru": lautru}
    
    for name, poly in fences.items():
        if inside_polygon(poly): return name
        
    return False
    
    
    
    
    