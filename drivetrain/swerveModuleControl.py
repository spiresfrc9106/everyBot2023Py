from wpimath.controller import SimpleMotorFeedforwardMeters
from wpimath.controller import PIDController
from wpimath.kinematics import SwerveModuleState
from wpimath.kinematics import SwerveModulePosition
from wpimath.geometry import Rotation2d
import wpilib

from wrappers.wrapperedSparkMax import WrapperedSparkMax
from dashboardWidgets.swerveState import getAzmthDesTopicName, getAzmthActTopicName
from dashboardWidgets.swerveState import getSpeedDesTopicName, getSpeedActTopicName
from utils.signalLogging import log
from utils.units import rad2Deg
from drivetrain.drivetrainPhysical import dtMotorRotToLinear
from drivetrain.drivetrainPhysical import dtLinearToMotorRot
from drivetrain.drivetrainPhysical import MAX_FWD_REV_SPEED_MPS
from drivetrain.drivetrainPhysical import INVERT_AZMTH_MOTOR
from drivetrain.drivetrainPhysical import wrapperedSwerveDriveAzmthEncoder

class SwerveModuleControl():
    """
    Control logic for one swerve drive module
    """
    def __init__(self, moduleName, wheelMotorCanID, azmthMotorCanID, azmthEncoderPortIdx, azmthOffset, invertWheel):
        """Instantiate one swerve drive module

        Args:
            moduleName (str): Name Prefix for the module (IE, "FL", or "BR"). For logging purposes mostly
            wheelMotorCanID (int): CAN Id for the wheel motor for this module
            azmthMotorCanID (int): CAN Id for the azimuth motor for this module
            azmthEncoderPortIdx (int): RIO Port for the azimuth absolute encoder for this module
            azmthOffset (float): Mounting offset of the azimuth encoder in Radians. 
            invertWheel (bool): Inverts the drive direction of the wheel - needed since left/right sides are mirrored
        """
        self.wheelMotor = WrapperedSparkMax(wheelMotorCanID, moduleName+"_wheel", False)
        self.azmthMotor = WrapperedSparkMax(azmthMotorCanID, moduleName+"_azmth", True)
        self.azmthEnc = wrapperedSwerveDriveAzmthEncoder(azmthEncoderPortIdx, moduleName + "_azmthEnc", azmthOffset)

        self.wheelMotor.setInverted(invertWheel)
        self.azmthMotor.setInverted(INVERT_AZMTH_MOTOR)
        
        self.wheelMotorFF = SimpleMotorFeedforwardMeters(0,0,0)

        self.desiredState = SwerveModuleState()
        self.optimizedDesiredState = SwerveModuleState()
        self.actualState = SwerveModuleState()

        self.azmthCtrl = PIDController(0,0,0)
        self.azmthCtrl.enableContinuousInput(-180.0, 180.0)

        self._prevMotorDesSpeed = 0

        self.moduleName = moduleName

    def _updateTelemetry(self):
        """
        Helper function to put all relevant data to logs and dashboards for this module
        """
        log(getAzmthDesTopicName(self.moduleName), 
            self.optimizedDesiredState.angle.degrees(), "deg")
        log(getAzmthActTopicName(self.moduleName), 
            rad2Deg(self.azmthEnc.getAngleRad()), "deg")
        log(getSpeedDesTopicName(self.moduleName), 
            self.optimizedDesiredState.speed/MAX_FWD_REV_SPEED_MPS, "frac")
        log(getSpeedActTopicName(self.moduleName), 
            dtMotorRotToLinear(self.wheelMotor.getMotorVelocityRadPerSec())/MAX_FWD_REV_SPEED_MPS, "frac")

    def getActualPosition(self):
        """
        Returns:
            SwerveModulePosition: The position of the module (azmth and wheel) as measured by sensors
        """
        wheelPosMeters = dtMotorRotToLinear(self.wheelMotor.getMotorPositionRad())
        return SwerveModulePosition(wheelPosMeters, Rotation2d(self.azmthEnc.getAngleRad()))

    def getActualState(self):
        """
        Returns:
            SwerveModuleState: The state of the module (azmth and wheel) as measured by sensors
        """
        return self.actualState

    def getDesiredState(self):
        """
        Returns:
            SwerveModuleState: The commanded, desired state of the module (azmth and wheel)
        """
        return self.desiredState

    def setClosedLoopGains(self, gains):
        """Set feed-forward and closed loop gains for the module

        Args:
            gains (SwerveModuleGainSet): The gains for this module
        """
        self.wheelMotor.setPID(gains.wheelP.get(), 
                               gains.wheelI.get(), 
                               gains.wheelD.get())
        self.wheelMotorFF = SimpleMotorFeedforwardMeters(gains.wheelS.get(), 
                                                         gains.wheelV.get(), 
                                                         gains.wheelA.get())
        self.azmthCtrl.setPID(gains.azmthP.get(), 
                              gains.azmthI.get(), 
                              gains.azmthD.get())

    def setDesiredState(self, desState):
        """Main command input - Call this to tell the module to go to a certian wheel speed and azimuth angle

        Args:
            desState (SwerveModuleState): The commanded state of the module
        """
        self.desiredState = desState


    def update(self):
        """Main update function, call every 20ms
        """

        # Read from the azimuth angle sensor (encoder)
        self.azmthEnc.update()

        # Optimize our incoming swerve command to minimize motion
        self.optimizedDesiredState = SwerveModuleState.optimize(self.desiredState, 
                                                                Rotation2d(self.azmthEnc.getAngleRad()))

        # Use a PID controller to calculate the voltage for the azimuth motor
        self.azmthCtrl.setSetpoint(self.optimizedDesiredState.angle.degrees()) # type: ignore
        azmthVoltage = self.azmthCtrl.calculate(rad2Deg(self.azmthEnc.getAngleRad()))
        self.azmthMotor.setVoltage(azmthVoltage)

        # Send voltage and speed commands to the wheel motor
        
        motorDesSpd = dtLinearToMotorRot(self.optimizedDesiredState.speed)
        motorDesAccel = (motorDesSpd - self._prevMotorDesSpeed)/ 0.02
        motorVoltageFF = self.wheelMotorFF.calculate(motorDesSpd, motorDesAccel)
        self.wheelMotor.setVelCmd(motorDesSpd, motorVoltageFF)
        
        self._prevMotorDesSpeed = motorDesSpd # save for next loop

        if(wpilib.TimedRobot.isSimulation()):
            # Simulation - assume module is perfect and goes to where we want it to
            self.actualState = self.optimizedDesiredState
        else:
            # Real Robot
            # Update this module's actual state with measurements from the sensors
            self.actualState.angle = Rotation2d(self.azmthEnc.getAngleRad())
            self.actualState.speed = dtMotorRotToLinear(self.wheelMotor.getMotorVelocityRadPerSec())

        self._updateTelemetry()
