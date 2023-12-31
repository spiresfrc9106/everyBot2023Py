import os
import wpilib
from pathplannerlib import PathPlanner

from AutoSequencerV2.command import Command
from drivetrain.drivetrainControl import DrivetrainControl
from drivetrain.drivetrainPhysical import MAX_DT_LINEAR_SPEED
from drivetrain.drivetrainPhysical import MAX_TRANSLATE_ACCEL_MPS2

class DrivePathCommand(Command):
    
    def __init__(self, pathFile, speedScalar):
    
        self.name = pathFile

        # Hack around the fact that loadPath doesn't account for 
        # when the code is not running in the normal launch directory.
        # Critically, we have this issue while running unit tests on our code.
        # This shouldn't be necessary after PathPlanner is fixed internally
        absPath = os.path.abspath(os.path.join(os.path.dirname(__file__), 
                                               "..", 
                                               "..", 
                                               "deploy", 
                                               "pathplanner", 
                                               pathFile))

        self.path = PathPlanner.loadPath(absPath, 
                                         MAX_DT_LINEAR_SPEED * speedScalar,
                                         MAX_TRANSLATE_ACCEL_MPS2 * speedScalar)
        self.done = False
        self.startTime = -1 # we'll populate these for real later, just declare they'll exist
        self.duration = self.path.getTotalTime()
        self.drivetrain = DrivetrainControl()
        self.poseTelem = DrivetrainControl().poseEst.telemetry

    def initialize(self):
        self.startTime = wpilib.Timer.getFPGATimestamp()
        self.poseTelem.setTrajectory(self.path)

    def execute(self):
        curTime = wpilib.Timer.getFPGATimestamp() - self.startTime
        curState = self.path.sample(curTime)

        self.drivetrain.setCmdTrajectory(curState)

        self.done = curTime >= (self.duration)

        if(self.done):
            self.drivetrain.setCmdRobotRelative(0,0,0)
            self.poseTelem.setTrajectory(None)

    def isDone(self):
        return self.done
    
    def getName(self):
        return f"Drive Trajectory {self.name}"
