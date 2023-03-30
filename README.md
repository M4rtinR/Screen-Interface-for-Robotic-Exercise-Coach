# RehabInterface
This repo contains code for running both the squash coaching and stroke rehabilitation systems on Pepper. This is where the display on Pepper's tablet computer screen and interaction with the screen from the user is handled. Written in Python 3. The main code can be found here: https://github.com/M4rtinR/coachingPolicies.

## Downloading the Code
NOTE: For this component you will need to run Pycharm as an administrator. In a terminal, open the folder in which Pycharm is installed (for me this is ~/Programs/pycharm-community-2020.3.5/bin, but you may also find it in /snap/pycharm-community/current/bin) and use the following command:
  ```sudo ./pycharm.sh```
  and enter your password when prompted.
  
  Now clone the rehab interface repo into your admin-run Pycharm as you did for the main coaching policies code, and you should be able to select the required branch for the particular demo you wish to run. For me the cloning didn't work as administrator because it wouldn't log in to GitHub, so instead I had to clone in the regular PyCharm version and then open the project through administrator PyCharm once I had it downloaded onto my PC.
  
## Running the Demo
  1. Setup the Python Interpreter (Python3.8) and the configuration settings as you did for the main coaching policies program.
  
  2. Install the required packages as you did for the main coaching policies program. There is only one for this repo: "paramiko".
  
  3. Navigate to the correct branch (master for stroke rehabilitation demo or SquashScreen for squash demo).
  
  4. Click run.
