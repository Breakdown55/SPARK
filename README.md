## Inspiration
The recent LA wildfires that devastated Southern California inspired this project. The sheer proximity to our homes really moved us to create a program that lessens the probability of allowing wildfires to spread, as lightning is a direct contributor to wildfires in California, costing 1 billion dollars annually.  
## What it does
S.P.A.R.K. (Strike Prediction And Reconnaissance Kit) is an innovative system that detects the location of lightning strikes through AI models and quick calculations. The system then predicts the risk that lightning strikes pose to the area based on vegetation density and moisture. It relays this information to firefighters and a drone system that deploys drones if the predicted risk meets a certain threshold. 
## How we built it
We drafted our GUIs in QT Designer, which then converts them to PyQT5 code, which we progressively edited as we worked. We used Open Street Map's API to view the map, and place and label the pins. We trained a lightning detection model on Google's Teachable Machine, and then used brightness detection to locate the lightning once detected. Given the time it takes for the sound to reach the camera, the angle of the lightning strike relative to the camera, the camera's direction, and the camera's coordinates, we can predict the location of the lightning strike. Using Meteomatics' API, we can determine the area's fire risk where the lightning struck, ranking it from 0 to 1. Then, a drone with a video feed will be deployed to check out the coordinates to ensure a fire has not broken out. 
## Challenges we ran into
Opening a new window to display the "live video feed" was quite difficult, and arose several times throughout the project. Initially, the audio failed to play, as the library we used did not support it. We switched to VLC's Python library which worked. However, later on, we needed to switch to a different video player, which took a while to rework, but it eventually was successful. However, upon fixing some dependency conflicts, 

## Accomplishments that we're proud of
We're incredibly proud of building a functional and cohesive system that brings together AI, geolocation, environmental data, and real-time video analysis to help predict and respond to wildfire threats. Designing a UI that clearly communicates critical data and feels intuitive to use was a major success, especially given the technical complexity happening behind the scenes.
## What we learned
Throughout this project, we gather a greater understanding of PyQt GUI development and API integration. We gained valuable experience working with video processing, geolocation data, and deploying AI models in a real-world context. Additionally, we learned how to troubleshoot complex Python libraries, manage file paths across systems, and create a good user experience from input to response.
## What's next for S.P.A.R.K.
What we hope to accomplish next for S.P.A.R.K. is to integrate the program into homes and overall expand the program past just the fire department, and eventually allow emergency services to respond to all sorts of things, such as other natural disasters and various health emergencies some might be experiencing,  all through the use of camera analysis.



















#SOURCES:
