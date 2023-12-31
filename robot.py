import os
import wpilib
from Autonomous.modes.drivePathTest1 import DrivePathTest1
from robotConfig import webserverConstructorOrNone
from robotConfig import dashboardOrNone
from humanInterface.driverInterface import DriverInterface
from drivetrain.drivetrainControl import DrivetrainControl
from utils.segmentTimeTracker import SegmentTimeTracker
from utils.signalLogging import SignalWrangler
from utils.calibration import CalibrationWrangler
from utils.faults import FaultWrangler
from utils.crashLogger import CrashLogger
from utils.rioMonitor import RIOMonitor
from utils.singleton import destroyAllSingletonInstances
from AutoSequencerV2.autoSequencer import AutoSequencer

class MyRobot(wpilib.TimedRobot):

    #########################################################
    ## Common init/update for all modes
    def robotInit(self): 
        # Since we're defining a bunch of new things here, tell pylint 
        # to ignore these instantiations in a method.
        # pylint: disable=attribute-defined-outside-init

        self.crashLogger = CrashLogger()
        wpilib.LiveWindow.disableAllTelemetry()
        self.webserver = webserverConstructorOrNone()


        self.driveTrain = DrivetrainControl()
                
        self.stt = SegmentTimeTracker()
        
        self.dInt = DriverInterface()

        self.autoSequencer = AutoSequencer()
        self.autoSequencer.addMode(DrivePathTest1())

        self.dashboard = dashboardOrNone()

        self.rioMonitor = RIOMonitor()

        
        # Uncomment this and simulate to update the code 
        # dependencies graph
        # from codeStructureReportGen import reportGen
        # reportGen.generate(self)


    def robotPeriodic(self):
        self.stt.start()
        self.crashLogger.update()
        
        if(self.dInt.getGyroResetCmd()):
            self.driveTrain.resetGyro()
        
        self.driveTrain.update()
        
        SignalWrangler().publishPeriodic()
        CalibrationWrangler().update()
        FaultWrangler().update()
        self.stt.end()
        
    #########################################################
    ## Autonomous-Specific init and update
    def autonomousInit(self):
        # Start up the autonomous sequencer
        self.autoSequencer.initiaize()
        
        # Use the autonomous rouines starting pose to init the pose estimator
        self.driveTrain.poseEst.setKnownPose(self.autoSequencer.getStartingPose())
        
    def autonomousPeriodic(self):
        self.autoSequencer.update()

    def autonomousExit(self):
        self.autoSequencer.end()

    #########################################################
    ## Teleop-Specific init and update
    def teleopInit(self):
        pass
        
    def teleopPeriodic(self):
        self.dInt.update()
        self.driveTrain.setCmdFieldRelative(
            self.dInt.getVxCmd(),
            self.dInt.getVyCmd(),
            self.dInt.getVtCmd())
    
    
    #########################################################
    ## Disabled-Specific init and update
    def disabledPeriodic(self):
        self.autoSequencer.updateMode()
        self.driveTrain.trajCtrl.updateCals()

    #########################################################
    ## Test-Specific init and update
    def testInit(self):
        # Induce a crash
        oopsie = (5/0.0) # pylint: disable=unused-variable

    #########################################################
    ## Cleanup
    def endCompetition(self):
        self.rioMonitor.stopThreads()
        destroyAllSingletonInstances()
        super().endCompetition()


if __name__ == '__main__':

    enableDebug = os.path.isfile("/home/lvuser/py/enableDebug")
    if(enableDebug):
        print("Starting Debug Support....")
        import debugpy 
        debugpy.listen(('0.0.0.0', 5678))
        debugpy.wait_for_client()

    wpilib.run(MyRobot)
