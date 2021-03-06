# robot-catcher



<p align="center">
<img src="images/real-rl.gif" width="50%">
  <img src="images/sim-RL.png" width="35%">.
  </p>

How could a robot learn to catch a ball thrown in its direction? This was the main question we aimed to tackle for our senior design project. Our robot was a XY style plotter robot with a cup attached to a gantry plate. To create a controlled projectile, we constructed a wooden ramp to roll ping pong balls down. The robot's goal was to go to the landing position of the ball before it landed. It used Q-Learning with a state representation of (x,y,velocity) of the ping pong ball and received a reward based on the Euclidean distance between the ball and the gantry plate. The ball position was determined by a camera above the ramp and two laser pointers measured the velocity. A Unity simulation of our enviornment was used to train the agent then transfered to the real life robot.
