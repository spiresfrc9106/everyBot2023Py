from wpilib import XboxController
from wpimath import applyDeadband
from wpimath.filter import SlewRateLimiter
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_STRAFE_SPEED_MPS
from drivetrain.drivetrainPhysical import MAX_ROTATE_SPEED_RAD_PER_SEC
from drivetrain.drivetrainPhysical import MAX_ROTATE_ACCEL_RAD_PER_SEC_2
from drivetrain.drivetrainPhysical import MAX_TRANSLATE_ACCEL_MPS2
from utils.faults import Fault
from utils.signalLogging import log



class DriverInterface():
    """Class to gather input from the driver of the robot 
    """

    def __init__(self):
        ctrlIdx = 0
        self.ctrl = XboxController(ctrlIdx)
        self.velXCmd = 0
        self.velYCmd = 0
        self.velTCmd = 0
        self.gyroResetCmd = False
        self.connectedFault = Fault(f"Driver XBox Controller ({ctrlIdx}) Unplugged")
        
        self.velXSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velYSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_TRANSLATE_ACCEL_MPS2)
        self.velTSlewRateLimiter = SlewRateLimiter(rateLimit=MAX_ROTATE_ACCEL_RAD_PER_SEC_2)

    def update(self):
        """Main update - call this once every 20ms
        """
        
        if(self.ctrl.isConnected()):
            # Only attempt to read from the joystick if it's plugged in
            
            # Convert from joystic sign/axis conventions to robot velocity conventions
            vLJoyRaw = -1.0*self.ctrl.getLeftY()
            vRJoyRaw = -1.0*self.ctrl.getRightY()
            
            # Apply deadband to make sure letting go of the joystick actually stops the bot
            vLJoy = applyDeadband(vLJoyRaw,0.1)
            vRJoy = applyDeadband(vRJoyRaw,0.1)

            # okay so here's how this works
            #
            #          currently, we have:
            #
            #       +           -
            #
            # strafe u/d/l/r  rot l/r
            #

            #
            #   in reality, we need:
            #
            #    fwd/back  rot lr
            #
            #       |          |
            #
            #          fwd/b
            #
            #       |          -
            #
            #           l/r
            #

            #
            #     we find that the movement forward should be the average, 
            #     while the rotational should be the different between them
            #

            # Normally robot goes half speed - unlock full speed on 
            # sprint command being active
            sprintMult = 1.0 if(self.ctrl.getRightBumper()) else 0.5

            # Convert joystick fractions into physical units of velocity

            calcYCmd = (vRJoy + vLJoy) / 2
            calcTCmd = (vRJoy - vLJoy) / 2

            # not real: velXCmdRaw = vXJoy * MAX_FWD_REV_SPEED_MPS * sprintMult
            velYCmdRaw = calcYCmd * MAX_STRAFE_SPEED_MPS * sprintMult
            velTCmdRaw = calcTCmd * MAX_ROTATE_SPEED_RAD_PER_SEC * sprintMult
            
            # Slew-rate limit the velocity units to not change faster than
            # the robot can physically accomplish
            self.velXCmd = self.velXSlewRateLimiter.calculate(velXCmdRaw)
            self.velYCmd = self.velYSlewRateLimiter.calculate(velYCmdRaw)
            self.velTCmd = self.velTSlewRateLimiter.calculate(velTCmdRaw) 
            
            
            self.gyroResetCmd = self.ctrl.getAButtonPressed()
            
            self.connectedFault.setNoFault()
        else:
            # If the joystick is unplugged, pick safe-state commands and raise a fault
            self.velXCmd = 0.0
            self.velYCmd = 0.0
            self.velTCmd = 0.0
            self.gyroResetCmd = False
            self.connectedFault.setFaulted()

        log("DI FwdRev Cmd", self.velXCmd, "mps")
        log("DI Strafe Cmd", self.velYCmd, "mps")
        log("DI Rotate Cmd", self.velTCmd, "radPerSec")
        log("DI connected", self.ctrl.isConnected(), "bool")

    def getVxCmd(self):
        """
        Returns:
            float: Driver's current vX (downfield/upfield, or fwd/rev) command in meters per second
        """
        return self.velXCmd

    def getVyCmd(self):
        """
        Returns:
            float: Driver's current vY (side-to-side or strafe) command in meters per second
        """
        return self.velYCmd
    
    def getVtCmd(self):
        """
        Returns:
            float: Driver's current vT (rotation) command in radians per second
        """
        return self.velTCmd
    
    def getGyroResetCmd(self):
        """_summary_

        Returns:
            boolean: True if the driver wants to reset the gyro, false otherwise
        """
        return self.gyroResetCmd 
