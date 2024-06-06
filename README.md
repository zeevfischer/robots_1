### Dron simulation 
In this assignment, we are provided with a simulation of a Tello drone. Five maps are given, and the main objective is to create an algorithm for the drone to explore as much of each map as it can.   
[Assiment link](https://docs.google.com/document/d/1eo34T_M7jfduRZm_oevy94YY2LkGLzRT/edit#heading=h.2g3tsmea07xv)   
[Tello sensors](https://docs.google.com/spreadsheets/d/1kEa58v7qfw0noEKWtmUCC2BKMSIQ96JJTwXRhNLZrWc/edit#gid=0)   
## authorers
zeev fischer: 318960242   
eden mor: 316160332   
daniel musai: 206684755   

## Drone and Map characteristics
**Note: all sensors have a rate of 10 times per second **   
**Note: all distance sensors have a typical error if 2% +-**   
1. Each pixel on the map represents 2.5 cm
2. on the map WHITE pixel is a path BLACK pixel is an obstacle
3. Drone radius is 10 cm
4. six distace secsers up,down,front,back,left,right
5. speed 1-3 meters per second with an acceleration of 1 meter per second
6. battery life up to 8 minits
7. orientation sensor (IMU)
8. pitch +- 10 degrees (100 degrees per second)
9. roll +- 10 degrees (100 degrees per second)
10. yaw (100 degrees per second)

## Code Explanation
The drone will first detect the closest wall and move in its direction. If it cannot detect a wall, it will move in a random direction. Then, it will begin to map the room by following along the wall.   
The drone is represented by a red dot, and every space the drone detects gets colored yellow.   

### Pros and cons
This algorithm is excellent for maze-like maps; however, if there are empty spaces or objects in the middle of the map, the drone may miss some or even most of the map. Ideally, this will be fixed along the road as this assignment progresses.   
Moreover, the initial location of the drone is also important. With this algorithm in mind, the drone should ideally start at the edge of the map. If it starts in the middle and there are detached areas in the map, the drone may be caught in an endless loop around that space.   
However, if we start at an edge, the drone can follow a maze superbly.    
If you examine our code, you will see that we did not change the rotation of the drone. Instead, we found it easier to work with left, right, forward, and backward movements. However, this too may change in the future as the project progresses.   
For the drone movement, there are two main variables: one is for the wall direction that we are following, and the second is the main movement direction if we are close enough to the wall.    

## How To Run
**Noat: Basic understanding of running code is required. There are no special downloads needed; however, keep in mind that some workspaces may differ from others.**
1. for this project we used PyCharm you are encouraged to do the same.
2. Open a workspace that can run Python code.
3. Download the repository and insert the main.py file and the maps directory into your Python workspace.
4. In the main.py file, in the function main, there is a variable called "image_path" that you need to update to the correct path to the map in your system. This should be the path to the Maps directory included in this repository.
