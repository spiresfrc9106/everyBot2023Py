from AutoSequencerV2.smartDashboardModeList import SmartDashboardModeList
from AutoSequencerV2.builtInModes.doNothingMode import DoNothingMode
from AutoSequencerV2.builtInModes.waitMode import WaitMode
from Autonomous.modes.drivePathTest1 import DrivePathTest1

# pylint: disable=R0801

def makeDelayModeList():
    # We are putting the autonomous delay mode list on the SmartDashboard
    delayModeList = SmartDashboardModeList("Delay")
    delayModeList.addMode(WaitMode(0.0))
    delayModeList.addMode(WaitMode(3.0))
    delayModeList.addMode(WaitMode(6.0))
    delayModeList.addMode(WaitMode(9.0))
    delayModeList.listIsComplete()
    return delayModeList

def makeMainModeList():
    # We are putting the autonomous main mode list on the SmartDashboard
    mainModeList = SmartDashboardModeList("Main")
    mainModeList.addMode(DoNothingMode())
    mainModeList.addMode(DrivePathTest1())
    mainModeList.listIsComplete()
    return mainModeList