# ally-code-challenge

This is my solution for the gis-code-challenge.

## Instructions
1. install python module scipy, numpy
2. clone repository
	`git clone https://github.com/sjohn1/ally-code-challenge.git`
3. run script
	`python miningBusStops.py`
4. open `web/busstops.htm` to view results

## Algorithm

To derive the location of busstops out of the given activity points, following point properties have been considered:
- geometry
- speed
- accuracy
- previous_dominating_activity
- previous_dominating_activity_confidence

**_1. Step: Cleaning Data_**

First of all, the activity have been cleaned, to remove the influence of point which may introduce errors. All points were removed which 
- have a speed greater than 200km/h
- have an accuracy greater than 80 m

**_2. Step: Clustering_**

Points which are close to each other, are assigned to a cluster. The cluster id as well as a color (for visualization) is added to each point.

**_3. Step: Check properties of each cluster_**

For each cluster of activity different properties are checked in order to detect bus stops. Following criteria are checked:

    criterion 1: minimum number of points
    criterion 2: minimum confidence  
    criterion 3: speed below max speed    
    criterion 4: previous activity must be one of the following    
                a) on_foot
                b) on_bicycle
                c) still
    criterion 5: minimum percentage of points which meet criteria 2-4

**_4. Calculate Centroid_**

For each cluster which meets all criteria from Step 3 are considered to be bus stops. To get its location, the centroid of cluster points is calculated.

## Adjustable Parameters

The algorithm may be trained and improvement by adjusting following parameters:

- min_points
- min_confidence 
- min_percentage
- max_speed


## Layers in busstops.htm

**_Layer 'Bus Stops'_**

This Layer shows the derived bus stops. By clicking in the markers, the properties are displayed:

- percentage: shows the percentage from criterion 5 (see above) 
- nr_points: shows the number of points, which were members of the cluster of which this bus stop location was derived.

**_Layer 'Raw Data'_**

This Layer shows the original input data with its properties

**_Layer 'Clustered Raw Data'_**

This Layer shows the cleaned raw data (see above step 1), colorized by the cluster.
 