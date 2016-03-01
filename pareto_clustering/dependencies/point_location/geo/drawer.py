import spatial
import matplotlib.pyplot as plt


def plotPoints(points, style='bo', alpha=1, linewidth=2, label=""):
    if not type(points) == list:
        points = [points]

    points = spatial.toNumpy(points)
    plt.plot(points[:, 0], points[:, 1], style, alpha=alpha, linewidth=linewidth, label=label)


def showPoints(points, style='bo'):
    plotPoints(points, style=style)
    plt.show()


def plot(polygons, style='g-', alpha=1, linewidth=2, label=""):
    if not type(polygons) == list:
        polygons = [polygons]
    for polygon in polygons:
        points = polygon.points + [polygon.points[0]]
        plotPoints(points, style=style, alpha=alpha, linewidth=linewidth, label=label)


def show(polygons, style='g-'):
    plot(polygons, style=style)
    plt.show()
