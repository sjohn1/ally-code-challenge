# -*- coding: utf-8 -*-
'''
Created on 04.03.2016

@author: steffen
'''
import os
import sys
import json
import random
from math import trunc


from scipy.cluster.hierarchy import linkage, fcluster


import numpy as np

PATH_DATA='C:/Users/Steffen/workspace/busstops/data/'
FILE_POINTS='activity_points.geojson'
FILE_ROUTES='routes.geojson'



def loadData(filename):
    with open(filename) as f:
        data = json.load(f)
    return data

def appendToJsOutput(js, name, data):
    js = js + 'var '+ name +' = ' + json.dumps(data) + ';\n'
    return js

def writeOutputData(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f)
        
def getCentroid(pList):
    x = [p['geometry']['coordinates'][0] for p in pList]
    y = [p['geometry']['coordinates'][1] for p in pList]
    c_x = sum(x)/len(pList)
    c_y = sum(y)/len(pList)
    return [c_x, c_y]

def appendToOutput(busstops, centroid, nr_points, percentage):
    busstops['features'].append({  
         "type":"Feature",
         "properties":{  
            "nr_points":nr_points,
            "percentage":trunc(percentage*100)
         },
         "geometry":{  
            "type":"Point",
            "coordinates":[  
               centroid[0],
               centroid[1]
            ]
         }
      })

def getClusterColor(c_id, clusterColors):
    # get color of cluster; if cluster has no color yet, generate random color 
    if c_id not in clusterColors.keys():
        clusterColors[c_id] = "#%03x" % random.randint(0, 0xFFF)
    return clusterColors[c_id]



def main(args):
    
    # prepare js output
    js = ''
    # read activity points
    points = loadData(os.path.join(PATH_DATA,FILE_POINTS))
    
    # appand raw data to js output for visualization
    js = appendToJsOutput(js, 'raw', points)
    
    geom = []
    pointList = []
   
    for p in points['features']:
        # remove points which may introduce errors.
        if p['properties']['speed']>200 or p['properties']['accuracy']>80:
            points['features'].remove(p)
    
    # create numpy array of geometries for clustering
    for p in points['features']:
            geom.append(p['geometry']['coordinates'])       
    a = np.array(geom)

    # linkage matrix
    link = linkage(a, 'ward') # use Ward variance minimization algorithm

    max_d = 0.0005 # 0.001 degree is approximately 100m
    clusters = fcluster(link, max_d, criterion='distance')

    # Append cluster id to each point
    clusterDict = dict()
    clusterColors = dict()
    for i in range(0,len(points['features'])-1):
        c_id = clusters[i]
        #p = pointList[i]
        p = points['features'][i]
        p['properties']['cluster']= c_id
        p['properties']['color']=getClusterColor(c_id, clusterColors); #For visualization
        if c_id in clusterDict:
            clusterDict[c_id].append(p) 
        else:
            list_p = []
            list_p.append(p)
            clusterDict[c_id]=list_p


    # append cleaned data to js
    js = appendToJsOutput(js, 'clustered', points)
    
    # prepare busstop output
    busstops = dict()
    
    busstops = {"crs":{"type":"name", 
                       "properties":{  
                          "name":"urn:ogc:def:crs:OGC:1.3:CRS84"
                       }
                 },
                   "type":"FeatureCollection",
   "features": []}
    
    # check clusters if criteria for a bus stop are met
    '''
    criterion 1: minimum number of points
    criterion 2: minimum confidence
    criterion 3: speed below max speed
    criterion 4: previous activity must be one of the following
                a) on_foot
                b) on_bicycle
                c) still
    criterion 5: minimum percentage of points which meet criterion 2
    '''
    # Criterion 1: minimum number of points
    min_points=4
    min_confidence = 40
    min_percentage = 0.5
    max_speed = 50
    for c in clusterDict.keys():
        pList = clusterDict[c]
        nr_points=len(pList)
        if nr_points >= min_points:
            count = 0
            for p in pList:
                props=p['properties']
                speed=props['speed']
                prev=props['previous_dominating_activity']
                conf_prev = props['previous_dominating_activity_confidence']
                conf_cur =  props['current_dominating_activity_confidence']
                
                if (conf_prev >= min_confidence  and speed < max_speed and
                        (prev =='on_foot'
                        or prev == 'on_bicycle'
                        or prev == 'still'                      
                        )):
                    count = count + 1
            percentage = (count / float(nr_points))
            if  percentage > min_percentage: # criterion 5
                # calculate centroid of points
                centroid = getCentroid(pList)
                appendToOutput(busstops, centroid, nr_points, percentage )
              
           
           
    js = appendToJsOutput(js, 'busstops', busstops)
    
    jsfile = 'data.js'
    writer = open(os.path.join(PATH_DATA,jsfile), 'w')
    writer.write(js)        
    writer.close()
    
    writeOutputData(busstops,os.path.join(PATH_DATA,'busstops.geojson'))
    print 'task done...'
    
    
if __name__ == '__main__':
    main(sys.argv[1:])