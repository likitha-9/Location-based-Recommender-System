import pandas as pd,matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
import numpy as np
from geopy.distance import great_circle
import random
from shapely.geometry import MultiPoint
import webbrowser

x=open("C:/Python27/new_abboip.txt",'r')
arr=[]
lines=list(x)
for i in range(0,len(lines)):
    a=lines[i].split()
    b=[float(a[0]),float(a[1])]
    arr.append(b)
x.close()

df = pd.DataFrame(arr, columns = ['lat','lon'])

coord = df.as_matrix(columns=['lat','lon'])

c=[]
c=coord

# CLUSTERING THE HISTORICAL PICK-UP POINTS

kms_per_radian = 6371.0088
epsilon = 1.5/kms_per_radian
db = DBSCAN(eps=epsilon, min_samples=20, algorithm='ball_tree', metric='haversine').fit(np.radians(c))
core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
core_samples_mask[db.core_sample_indices_] = True
cluster_labels = db.labels_
print ("No. of all points:",len(cluster_labels))
num_clusters = len(set(cluster_labels))
clusters = pd.Series([c[cluster_labels == i] for i in range(num_clusters)])

for i in range(0,len(clusters)):
    clusters[i]=clusters[i].tolist()
    

print ("Number of clusters: ",num_clusters)
print ("Clusters are: ",clusters)

# FINDING THE CENTROID OF THE CLUSTERS FOR POTENTIAL PICK-UP POINT

centermost_points=[]
for i in range(num_clusters-1):
    centroid = (MultiPoint(clusters[i]).centroid.x, MultiPoint(clusters[i]).centroid.y)
    centermost_point = min(clusters[i], key=lambda point: great_circle(point, centroid).m)
    centermost_points.append(tuple(centermost_point))

print ("Centroids of each cluster: ",centermost_points)

# CALCULATING THE PICK-UP PROBABILITY FOR EACH CLUSTER

pick={}
empty_cabs={}

for i in range(num_clusters-1):
    pick[i]=0
    empty_cabs[i]=0

x=open("C:/Python27/preprocessing_1.txt",'r')
line=list(x)
for j in range(0,len(line)-1):
        l=line[j].split()
        m=line[j+1].split()
        check=0
        if(m[3]=='0'):
            p=[float(l[1]),float(l[2])]
            if(l[3]=='1'):
                check=1
            for k in range(len(clusters)):
                if(p in clusters[k]):
                    empty_cabs[k]=empty_cabs[k]+1
                    if(check==1):
                        pick[k]=pick[k]+1
       
x.close()

print (pick)
print (empty_cabs)

prob=[]

for i in range(len(clusters)-1):
    prob.append(float(format((pick[i]/empty_cabs[i]),'.7f')))
                    
print (prob)


# GETTING THE DRIVING DISTANCE FROM THE GOOGLE API

import googlemaps
from datetime import datetime

gmaps = googlemaps.Client(key='AIzaSyDQDdQQpHoW-krnw1pSD07eg3-1p_QWXxk')

dist_matrix = []

for i in range(0,len(centermost_points)):
    dist_matrix.append([])
    origin=str(centermost_points[i][0])+", "+str(centermost_points[i][1])
    for j in range(0,len(centermost_points)):
            destination=str(centermost_points[j][0])+", "+str(centermost_points[j][1])
            if(i is not j):
                directions_result = gmaps.distance_matrix(origin,destination,mode="driving")
                dis=directions_result['rows'][0]['elements'][0]['distance']['text'].split()
                dist_matrix[i].append(float(dis[0]))
            else:
                dist_matrix[i].append(0)

print (dist_matrix)


# POTENTIAL SEQUENCE CANDIDATES GENERATION

"""
INPUT:      SET OF POTENTIAL PICK-UP POINTS (centermost_points),
            PROBABILITY SET (prob[]) FOR ALL PICK-UP POINTS,
            THE PAIRWISE DRIVING DISTANCE MATRIX (dist_matrix) OF PICK-UP POINTS
OUTPUT:     SET OF POTENTIAL SEQUENCE CANDIDATES R

"""

R=[]
R.append([])
F1=[]
F1.append({})
PE=[]
PE.append({})
for i in range(0,len(centermost_points)):
    r=[centermost_points[i]]
    F1[0][str(r)]=0
    PE[0][str(r)]=prob[i]
    R[0].append(r)

#print (F1,PE)
h={}
for l in range(1,len(centermost_points)):
    R.append([])
    F1.append({})
    PE.append({})
    for k in range(0,len(R[l-1])):
        r=R[l-1][k]
        if(l==1):
            rem_c=list(set(centermost_points)-set([r[0]]))
        else:
            rem_c=centermost_points
            for i in range(0,len(r)):
                rem_c=list(set(rem_c)-set(r[i]))
        for j in range(0,len(rem_c)):
            p=[]
            if(r[0] in centermost_points):
                p=[[rem_c[j]],r]
            else:
                p.append([rem_c[j]])
                if(r not in p):
                    p=p+r
            #print ("p:",p)
            if(p in R[l]):
                continue
            if(r[0] in centermost_points):
                source=r[0]
            else:
                source=r[0][0]

            F1[l][str(p)]=F1[l-1][str(r)]*(1-prob[centermost_points.index(source)])+dist_matrix[centermost_points.index(rem_c[j])][(centermost_points.index(source))]*PE[l-1][str(r)]
            PE[l][str(p)]=PE[l-1][str(r)]*(1-prob[centermost_points.index(rem_c[j])])+prob[centermost_points.index(rem_c[j])]

            prun=[]
            for x in range(0,len(R[l])):
                q=R[l][x]
                if(q[0]==p[0] and sorted(p)==sorted(q)):
                    prun.append(q)

            if(prun==[]):
                R[l].append(p)
            else:
                #print ("F1[p]",F1[l][str(p)])
                w1=0
                for m in range(0,len(prun)):
                    q=prun[m]
                    if(F1[l][str(p)]==F1[l][str(q)]):
                        w1+=1
                if(w1==len(prun)):
                    R[l].append(p)
                w2=0
                for m in range(0,len(prun)):
                    q=prun[m]
                    if(F1[l][str(p)]<F1[l][str(q)]):
                        w2+=1
                if(w2==len(prun)):
                    for ab in range(0,len(prun)):
                        R[l].remove(prun[ab])
                    R[l].append(p)
                    
print ("-------Potential sequence candidates:-------")
print ("Sequence candidates of length 1:")
print (R[0])
print ("Sequence candidates of length 2:")
print (R[1])
print ("Sequence candidates of length 3:")
print (R[2])
print ("Sequence candidates of length 4:")
print (R[3])
print ("Sequence candidates of length 5:")
print (R[4])


# BATCH PRUNING

X=[]
count=0
for i in range(0,len(centermost_points)):
    X.append([])
    for k in range(0,len(centermost_points)):
        X[i].append([])
    cnt=0
    for j in range(0,len(R[i])):
        r=R[i][j]
        if(r[0] in centermost_points):
                source=r[0]
                X[i][centermost_points.index(source)].append(r)
        else:
                source=r[0][0]
                X[i][centermost_points.index(source)].append(r)
        #print (source,centermost_points.index(source),X[i][centermost_points.index(source)])       
        for l in range(len(X[i][centermost_points.index(source)])):
            #print (l)
            q=X[i][centermost_points.index(source)][l]
            if(q != r and q!=-1):
                if(F1[i][str(q)]<F1[i][str(r)]):
                    y=X[i][centermost_points.index(source)].index(q)
                    X[i][centermost_points.index(source)][y]=-1
                    cnt+=1
                    break
                else:
                    if(F1[i][str(r)]<F1[i][str(q)]):
                        y=X[i][centermost_points.index(source)].index(r)
                        X[i][centermost_points.index(source)][y]=-1
                        cnt+=1
    count+=cnt  #count denotes the total number of rejected sequences from R.

for i in range(0,len(centermost_points)):
    for j in range(0,len(X[i])):
        while(-1 in X[i][j]):
            X[i][j].remove(-1)

res=[]
for i in range(0,len(X)):
	res.append([])
	for j in range(0,len(X[i])):
		for k in range(0,len(X[i][j])):
			res[i].append(X[i][j][k])

			
# ONLINE PROCESSING

c0=(37.67548, -122.54681)
D=[]
F={}
F_min=0.0
Di=999
minl=3
maxl=5
for i in range(minl,maxl):
    for j in range(0,len(res[i])):
        r=res[i][j]
        if(r[0] in centermost_points):
                source=r[0]
        else:
                source=r[0][0]
        d=[]
        if(r[0] in centermost_points):
            d=[[c0],r]
        else:
            d.append([c0])
            if(r not in d):
                d=d+r

        origin=str(c0[0])+", "+str(c0[1])
        destination=str(source[0])+", "+str(source[1])
        
        directions_result = gmaps.distance_matrix(origin,destination,mode="driving")
        dist=(directions_result['rows'][0]['elements'][0]['distance']['text']).split()

        F[str(d)]=F1[i][str(r)]*(1-prob[centermost_points.index(source)])+float(dist[0])*PE[i][str(r)]+Di*(1-PE[i][str(r)])
        if(D==[] or F[str(d)]==F_min):
            D=D+d
        else:
            if(F[str(d)]<F_min):
                D.append(d)
                F_min=F[str(d)]

print ("-----RECOMMENDED OPTIMAL PATH-----")
print (D)


# PLOTTING THE CLUSTERS ON GMAPS

from gmplot import gmplot
import webbrowser

rec=[]
for i in range(len(D)):
    rec.append(D[i][0])

lat=[]
lon=[]

for i in range(len(centermost_points)):
    lat.append(centermost_points[i][0])

for i in range(len(centermost_points)):
    lon.append(centermost_points[i][1])

gmap=gmplot.GoogleMapPlotter(centermost_points[1][0],centermost_points[1][1],13)

color=['orange','blue','maroon','red','green']
for i in range(0,len(clusters)-1):
    latit=[]
    long=[]
    for j in range(0,len(clusters[i])):
        latit.append(clusters[i][j][0])
        long.append(clusters[i][j][1])
    gmap.scatter(latit,long,color[i],size=80,marker=False)


gmap.scatter(lat,lon,'black',size=500,marker=False)

# Draw

#directions_result = gmaps.distance_matrix(rec[0],rec[len(rec)-1],mode="driving")
        
gmap.draw("my_map.html")

webbrowser.open("my_map.html")


# PLOTTING OF CLUSTERS OF GEOGRAPHICAL POINTS

import matplotlib.pyplot as plt

unique_labels = set(cluster_labels)
colors = [plt.cm.Spectral(each)
          for each in np.linspace(0, 1, len(unique_labels))]
for k, col in zip(unique_labels, colors):
    if k == -1:
        # Black used for noise.
        col = [0, 0, 0, 1]

    class_member_mask = (cluster_labels == k)

    xy = c[class_member_mask & core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=14)

    xy = c[class_member_mask & ~core_samples_mask]
    plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
             markeredgecolor='k', markersize=6)

    #plt.plot(centermost_points[k],'o',markerfacecolor=tuple(col),markeredgecolor='k', markersize=18)

plt.title('Estimated number of clusters: %d' % num_clusters)
plt.show()
