df = {}
f=open('tweet_features.txt','r')
lines=f.readlines()
f.close()
j=0
for line in lines:
    target=line.strip()
    features=target.split(' ')
    df[j]=(float(features[0]),float(features[1]))
    j+=1
for i in range(10):
    print(df.get(i,"None"))

import pylab, random
import matplotlib.pyplot as plt

def distance(x,y,p=2):
    dist=0
    for i in range(len(x)):
        dist+=(abs(x[i]-y[i]))**p
    return dist**(1/p)

class point(object):
    def __init__(self, name, coordinates, label= None):
        self.name=name
        self.coordinates=coordinates[:]
        self.dim=len(coordinates)
        self.label=label
    def getcoordinates(self):
        return self.coordinates
    def getdim(self):
        return self.dim
    def __add__(self,other):
        f=[]
        for i in range(self.dim):
            f.append(self.coordinates[i]+other.coordinates[i])
        return point(self.name+'+'+other.name,f)
    def __truediv__(self,n):
        f=[]
        for i in self.getcoordinates():
            f.append(i/float(n))
        return point(self.name+'/'+str(n),f)
    def __sub__(self,other):
        f=[]
        for i in range(self.dim):
            f.append(self.coordinates[i]-other.coordinates[i])
        return point(self.name+'-'+other.name,f)
    

class cluster(object):
    def __init__(self, points):
        self.points=points
        self.center=self.computecenter()
    
    def computecenter(self):
        dim=self.points[0].getdim()
        centerpoint=point('center',[0.0]*dim)
        for item in self.points:
            centerpoint+=item
        centerpoint/=len(self.points)
        return centerpoint
    
    def getcenter(self):
        return self.center
    
    def update(self,otherpoints):
        self.points=otherpoints
        converged=True
        oldcenter=self.center
        if distance(oldcenter.coordinates,self.computecenter().coordinates)>0:
            converged=False
            self.center=self.computecenter()
        return converged, self.center
        
        
def plotSamples(samples, marker='o', verbose = False):
    xVals, yVals = [], []
    for s in samples:
        x = s.coordinates[0]
        y = s.coordinates[1]
        if verbose:
            pylab.annotate(s.name, xy = (x, y),
                           xytext = (x+0.13, y-0.07),
                           fontsize = 'x-large')
        xVals.append(x)
        yVals.append(y)
    plt.plot(xVals, yVals, marker)

# MATLAB formatting strings
def make_cmarkers():
    markers = ('o', 'v', '^', '<', '>', '8', 
                   's', 'p', '*', 'h', 'H', 'D', 'd')
    colors = ('b', 'g', 'r', 'c', 'm', 'y', 'k')
    return [c + m for m in markers for c in colors]

def plot_cluster(clusters, verbose = False):
    color_markers = iter(make_cmarkers())
    for c in clusters:
        cm = next(color_markers)
        plotSamples(c.points, cm, verbose)
        plotSamples([c.center], 'sk')
    plt.show()
    
def settingup(j,df):
    points = []
    for s in range(j):
        x = df[s][0]
        y = df[s][1]
        points.append(point(''+str(s), [x, y]))
    return points

def main():    
    points = settingup(j,df)
    samples=points
    k=2
    print("before clustering")
    plot_cluster([cluster(points)])
    
    startingpoints=random.sample(points,k)
    clusterlst=[]
    for i in range(k):
        clusterlst.append(cluster([startingpoints[i]]))
    convergence=False
    while convergence==False:
        newclusterlst=[]
        for i in range(k):
            newclusterlst.append([])
        for point in samples:
            index=0
            smallestdistance=distance(clusterlst[0].getcenter().coordinates,point.coordinates)
            for i in range(1,k):
                distancenow=distance(clusterlst[i].getcenter().coordinates,point.coordinates)
                if distancenow<smallestdistance:
                    smallestdistance=distancenow
                    index=i
            newclusterlst[index].append(point)
        convergence=True
        for i in range(k):
            converged, newcenter=clusterlst[i].update(newclusterlst[i])
            if converged==False:
                convergence=False
    print("after clustering")
    plot_cluster(clusterlst)

main()
