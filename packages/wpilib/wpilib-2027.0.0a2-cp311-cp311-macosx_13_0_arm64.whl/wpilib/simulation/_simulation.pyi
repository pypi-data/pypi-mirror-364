from __future__ import annotations
import hal._wpiHal
import ntcore._ntcore
import numpy
import numpy.typing
import pybind11_stubgen.typing_ext
import typing
import wpilib._wpilib
import wpilib._wpilib.interfaces
import wpimath._controls._controls.plant
import wpimath._controls._controls.system
import wpimath.geometry._geometry
import wpimath.units
__all__ = ['ADXL345Sim', 'AddressableLEDSim', 'AnalogEncoderSim', 'AnalogInputSim', 'BatterySim', 'CTREPCMSim', 'CallbackStore', 'DCMotorSim', 'DIOSim', 'DifferentialDrivetrainSim', 'DigitalPWMSim', 'DoubleSolenoidSim', 'DriverStationSim', 'DutyCycleEncoderSim', 'DutyCycleSim', 'ElevatorSim', 'EncoderSim', 'FlywheelSim', 'GenericHIDSim', 'JoystickSim', 'LinearSystemSim_1_1_1', 'LinearSystemSim_1_1_2', 'LinearSystemSim_2_1_1', 'LinearSystemSim_2_1_2', 'LinearSystemSim_2_2_1', 'LinearSystemSim_2_2_2', 'PS4ControllerSim', 'PS5ControllerSim', 'PWMMotorControllerSim', 'PWMSim', 'PneumaticsBaseSim', 'PowerDistributionSim', 'REVPHSim', 'RoboRioSim', 'SendableChooserSim', 'ServoSim', 'SharpIRSim', 'SimDeviceSim', 'SingleJointedArmSim', 'SolenoidSim', 'StadiaControllerSim', 'XboxControllerSim', 'getProgramStarted', 'isTimingPaused', 'pauseTiming', 'restartTiming', 'resumeTiming', 'setProgramStarted', 'setRuntimeType', 'stepTiming', 'stepTimingAsync', 'waitForProgramStart']
class ADXL345Sim:
    """
    Class to control a simulated ADXL345.
    """
    def __init__(self, accel: wpilib._wpilib.ADXL345_I2C) -> None:
        """
        Constructs from a ADXL345_I2C object.
        
        :param accel: ADXL345 accel to simulate
        """
    def setX(self, accel: typing.SupportsFloat) -> None:
        """
        Sets the X acceleration.
        
        :param accel: The X acceleration.
        """
    def setY(self, accel: typing.SupportsFloat) -> None:
        """
        Sets the Y acceleration.
        
        :param accel: The Y acceleration.
        """
    def setZ(self, accel: typing.SupportsFloat) -> None:
        """
        Sets the Z acceleration.
        
        :param accel: The Z acceleration.
        """
class AddressableLEDSim:
    """
    Class to control a simulated addressable LED.
    """
    @staticmethod
    def getGlobalData(start: typing.SupportsInt, length: typing.SupportsInt, data: hal._wpiHal.AddressableLEDData) -> int:
        """
        Get the global LED data.
        
        :param start:  the start of the LED data
        :param length: the length of the LED data
        :param data:   output parameter to fill with LED data
        
        :returns: the length of the LED data
        """
    @staticmethod
    def registerDataCallback(callback: typing.Callable[[str, typing.SupportsInt, typing.SupportsInt], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the LED data.
        
        :param callback:      the callback that will be called whenever the LED data is
                              changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def setGlobalData(start: typing.SupportsInt, length: typing.SupportsInt, data: hal._wpiHal.AddressableLEDData) -> None:
        """
        Change the global LED data.
        
        :param start:  the start of the LED data
        :param length: the length of the LED data
        :param data:   the new data
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructs an addressable LED for a specific channel.
        
        :param channel: output channel
        """
    @typing.overload
    def __init__(self, addressableLED: wpilib._wpilib.AddressableLED) -> None:
        """
        Constructs from an AddressableLED object.
        
        :param addressableLED: AddressableLED to simulate
        """
    def getData(self, data: hal._wpiHal.AddressableLEDData) -> int:
        """
        Get the LED data.
        
        :param data: output parameter to fill with LED data
        
        :returns: the length of the LED data
        """
    def getInitialized(self) -> bool:
        """
        Check if initialized.
        
        :returns: true if initialized
        """
    def getLength(self) -> int:
        """
        Get the length of the LED strip.
        
        :returns: the length
        """
    def getStart(self) -> int:
        """
        Get the start.
        
        :returns: the start
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the Initialized property.
        
        :param callback:      the callback that will be called whenever the Initialized
                              property is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object storing this callback
        """
    def registerLengthCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the length.
        
        :param callback:      the callback that will be called whenever the length is
                              changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerStartCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the start.
        
        :param callback:      the callback that will be called whenever the start
                              is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def setData(self, data: hal._wpiHal.AddressableLEDData) -> None:
        """
        Change the LED data.
        
        :param data: the new data
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Change the Initialized value of the LED strip.
        
        :param initialized: the new value
        """
    def setLength(self, length: typing.SupportsInt) -> None:
        """
        Change the length of the LED strip.
        
        :param length: the new value
        """
    def setStart(self, start: typing.SupportsInt) -> None:
        """
        Change the start.
        
        :param start: the new start
        """
class AnalogEncoderSim:
    """
    Class to control a simulated analog encoder.
    """
    def __init__(self, encoder: wpilib._wpilib.AnalogEncoder) -> None:
        """
        Constructs from an AnalogEncoder object.
        
        :param encoder: AnalogEncoder to simulate
        """
    def get(self) -> float:
        """
        Get the simulated position.
        """
    def set(self, value: typing.SupportsFloat) -> None:
        """
        Set the position.
        
        :param value: The position.
        """
class AnalogInputSim:
    """
    Class to control a simulated analog input.
    """
    @typing.overload
    def __init__(self, analogInput: wpilib._wpilib.AnalogInput) -> None:
        """
        Constructs from an AnalogInput object.
        
        :param analogInput: AnalogInput to simulate
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructs from an analog input channel number.
        
        :param channel: Channel number
        """
    def getAverageBits(self) -> int:
        """
        Get the number of average bits.
        
        :returns: the number of average bits
        """
    def getInitialized(self) -> bool:
        """
        Check if this analog input has been initialized.
        
        :returns: true if initialized
        """
    def getOversampleBits(self) -> int:
        """
        Get the amount of oversampling bits.
        
        :returns: the amount of oversampling bits
        """
    def getVoltage(self) -> float:
        """
        Get the voltage.
        
        :returns: the voltage
        """
    def registerAverageBitsCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the number of average bits.
        
        :param callback:      the callback that will be called whenever the number of
                              average bits is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the analog input is initialized.
        
        :param callback:      the callback that will be called whenever the analog input
                              is initialized
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerOversampleBitsCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the amount of oversampling bits.
        
        :param callback:      the callback that will be called whenever the oversampling
                              bits are changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerVoltageCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the voltage.
        
        :param callback:      the callback that will be called whenever the voltage is
                              changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all simulation data for this object.
        """
    def setAverageBits(self, averageBits: typing.SupportsInt) -> None:
        """
        Change the number of average bits.
        
        :param averageBits: the new value
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Change whether this analog input has been initialized.
        
        :param initialized: the new value
        """
    def setOversampleBits(self, oversampleBits: typing.SupportsInt) -> None:
        """
        Change the amount of oversampling bits.
        
        :param oversampleBits: the new value
        """
    def setVoltage(self, voltage: typing.SupportsFloat) -> None:
        """
        Change the voltage.
        
        :param voltage: the new value
        """
class BatterySim:
    """
    A utility class to simulate the robot battery.
    """
    @staticmethod
    @typing.overload
    def calculate(nominalVoltage: wpimath.units.volts, resistance: wpimath.units.ohms, currents: list[wpimath.units.amperes]) -> wpimath.units.volts:
        """
        Calculate the loaded battery voltage. Use this with
        RoboRioSim::SetVInVoltage(double) to set the simulated battery voltage,
        which can then be retrieved with the RobotController::GetBatteryVoltage()
        method.
        
        :param nominalVoltage: The nominal battery voltage. Usually 12v.
        :param resistance:     The forward resistance of the battery. Most batteries
                               are at or below 20 milliohms.
        :param currents:       The currents drawn from the battery.
        
        :returns: The battery's voltage under load.
        """
    @staticmethod
    @typing.overload
    def calculate(currents: list[wpimath.units.amperes]) -> wpimath.units.volts:
        """
        Calculate the loaded battery voltage. Use this with
        RoboRioSimSetVInVoltage(double) to set the simulated battery voltage, which
        can then be retrieved with the RobotController::GetBatteryVoltage() method.
        This function assumes a nominal voltage of 12V and a resistance of 20
        milliohms (0.020 ohms).
        
        :param currents: The currents drawn from the battery.
        
        :returns: The battery's voltage under load.
        """
    def __init__(self) -> None:
        ...
class CTREPCMSim(PneumaticsBaseSim):
    """
    Class to control a simulated Pneumatic Control Module (PCM).
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs with the default PCM module number (CAN ID).
        """
    @typing.overload
    def __init__(self, module: typing.SupportsInt) -> None:
        """
        Constructs from a PCM module number (CAN ID).
        
        :param module: module number
        """
    @typing.overload
    def __init__(self, pneumatics: wpilib._wpilib.PneumaticsBase) -> None:
        ...
    def getAllSolenoidOutputs(self) -> int:
        ...
    def getClosedLoopEnabled(self) -> bool:
        """
        Check whether the closed loop compressor control is active.
        
        :returns: true if active
        """
    def getCompressorCurrent(self) -> float:
        """
        Read the compressor current.
        
        :returns: the current of the compressor connected to this module
        """
    def getCompressorOn(self) -> bool:
        ...
    def getInitialized(self) -> bool:
        ...
    def getPressureSwitch(self) -> bool:
        """
        Check the value of the pressure switch.
        
        :returns: the pressure switch value
        """
    def getSolenoidOutput(self, channel: typing.SupportsInt) -> bool:
        ...
    def registerClosedLoopEnabledCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the closed loop state changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerCompressorCurrentCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the compressor current changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerCompressorOnCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerPressureSwitchCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the pressure switch value changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerSolenoidOutputCallback(self, channel: typing.SupportsInt, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def resetData(self) -> None:
        ...
    def setAllSolenoidOutputs(self, outputs: typing.SupportsInt) -> None:
        ...
    def setClosedLoopEnabled(self, closedLoopEnabled: bool) -> None:
        """
        Turn on/off the closed loop control of the compressor.
        
        :param closedLoopEnabled: whether the control loop is active
        """
    def setCompressorCurrent(self, compressorCurrent: typing.SupportsFloat) -> None:
        """
        Set the compressor current.
        
        :param compressorCurrent: the new compressor current
        """
    def setCompressorOn(self, compressorOn: bool) -> None:
        ...
    def setInitialized(self, initialized: bool) -> None:
        ...
    def setPressureSwitch(self, pressureSwitch: bool) -> None:
        """
        Set the value of the pressure switch.
        
        :param pressureSwitch: the new value
        """
    def setSolenoidOutput(self, channel: typing.SupportsInt, solenoidOutput: bool) -> None:
        ...
class CallbackStore:
    """
    Manages simulation callbacks; each object is associated with a callback.
    """
    def setUid(self, uid: typing.SupportsInt) -> None:
        ...
class DCMotorSim(LinearSystemSim_2_1_2):
    """
    Represents a simulated DC motor mechanism.
    """
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_2, gearbox: wpimath._controls._controls.plant.DCMotor, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated DC motor mechanism.
        
        :param plant:              The linear system representing the DC motor. This
                                   system can be created with LinearSystemId::DCMotorSystem(). If
                                   LinearSystemId::DCMotorSystem(kV, kA) is used, the distance unit must be
                                   radians.
        :param gearbox:            The type of and number of motors in the DC motor
                                   gearbox.
        :param measurementStdDevs: The standard deviation of the measurement noise.
        """
    def getAngularAcceleration(self) -> wpimath.units.radians_per_second_squared:
        """
        Returns the DC motor acceleration.
        
        :returns: The DC motor acceleration
        """
    def getAngularPosition(self) -> wpimath.units.radians:
        """
        Returns the DC motor position.
        
        :returns: The DC motor position.
        """
    def getAngularPositionRotations(self) -> wpimath.units.turns:
        """
        Returns the DC motor position in rotations
        """
    def getAngularVelocity(self) -> wpimath.units.radians_per_second:
        """
        Returns the DC motor velocity.
        
        :returns: The DC motor velocity.
        """
    def getAngularVelocityRPM(self) -> wpimath.units.revolutions_per_minute:
        """
        Returns the DC motor velocity in revolutions per minute
        """
    def getCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the DC motor current draw.
        
        :returns: The DC motor current draw.
        """
    def getGearbox(self) -> wpimath._controls._controls.plant.DCMotor:
        """
        Returns the gearbox.
        """
    def getGearing(self) -> float:
        """
        Returns the gearing;
        """
    def getInputVoltage(self) -> wpimath.units.volts:
        """
        Gets the input voltage for the DC motor.
        
        :returns: The DC motor input voltage.
        """
    def getJ(self) -> wpimath.units.kilogram_square_meters:
        """
        Returns the moment of inertia
        """
    def getTorque(self) -> wpimath.units.newton_meters:
        """
        Returns the DC motor torque.
        
        :returns: The DC motor torque
        """
    def setAngle(self, angularPosition: wpimath.units.radians) -> None:
        """
        Sets the DC motor's angular position.
        
        :param angularPosition: The new position in radians.
        """
    def setAngularVelocity(self, angularVelocity: wpimath.units.radians_per_second) -> None:
        """
        Sets the DC motor's angular velocity.
        
        :param angularVelocity: The new velocity in radians per second.
        """
    def setInputVoltage(self, voltage: wpimath.units.volts) -> None:
        """
        Sets the input voltage for the DC motor.
        
        :param voltage: The input voltage.
        """
    def setState(self, angularPosition: wpimath.units.radians, angularVelocity: wpimath.units.radians_per_second) -> None:
        """
        Sets the state of the DC motor.
        
        :param angularPosition: The new position
        :param angularVelocity: The new velocity
        """
class DIOSim:
    """
    Class to control a simulated digital input or output.
    """
    @typing.overload
    def __init__(self, input: wpilib._wpilib.DigitalInput) -> None:
        """
        Constructs from a DigitalInput object.
        
        :param input: DigitalInput to simulate
        """
    @typing.overload
    def __init__(self, output: wpilib._wpilib.DigitalOutput) -> None:
        """
        Constructs from a DigitalOutput object.
        
        :param output: DigitalOutput to simulate
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructs from an digital I/O channel number.
        
        :param channel: Channel number
        """
    def getFilterIndex(self) -> int:
        """
        Read the filter index.
        
        :returns: the filter index of this DIO port
        """
    def getInitialized(self) -> bool:
        """
        Check whether this DIO has been initialized.
        
        :returns: true if initialized
        """
    def getIsInput(self) -> bool:
        """
        Check whether this DIO port is currently an Input.
        
        :returns: true if Input
        """
    def getPulseLength(self) -> float:
        """
        Read the pulse length.
        
        :returns: the pulse length of this DIO port
        """
    def getValue(self) -> bool:
        """
        Read the value of the DIO port.
        
        :returns: the DIO value
        """
    def registerFilterIndexCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the filter index changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when this DIO is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerIsInputCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever this DIO changes to be an input.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerPulseLengthCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the pulse length changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerValueCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the DIO value changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all simulation data of this object.
        """
    def setFilterIndex(self, filterIndex: typing.SupportsInt) -> None:
        """
        Change the filter index of this DIO port.
        
        :param filterIndex: the new filter index
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether this DIO has been initialized.
        
        :param initialized: whether this object is initialized
        """
    def setIsInput(self, isInput: bool) -> None:
        """
        Define whether this DIO port is an Input.
        
        :param isInput: whether this DIO should be an Input
        """
    def setPulseLength(self, pulseLength: typing.SupportsFloat) -> None:
        """
        Change the pulse length of this DIO port.
        
        :param pulseLength: the new pulse length
        """
    def setValue(self, value: bool) -> None:
        """
        Change the DIO value.
        
        :param value: the new value
        """
class DifferentialDrivetrainSim:
    class KitbotGearing:
        """
        Represents a gearing option of the Toughbox mini.
        12.75:1 -- 14:50 and 14:50
        10.71:1 -- 14:50 and 16:48
        8.45:1 -- 14:50 and 19:45
        7.31:1 -- 14:50 and 21:43
        5.95:1 -- 14:50 and 24:40
        """
        k10p71: typing.ClassVar[float] = 10.71
        k12p75: typing.ClassVar[float] = 12.75
        k5p95: typing.ClassVar[float] = 5.95
        k7p31: typing.ClassVar[float] = 7.31
        k8p45: typing.ClassVar[float] = 8.45
        def __init__(self) -> None:
            ...
    class KitbotMotor:
        """
        Represents common motor layouts of the kit drivetrain.
        """
        DualCIMPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        DualFalcon500PerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        DualMiniCIMPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        DualNEOPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        SingleCIMPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        SingleFalcon500PerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        SingleMiniCIMPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        SingleNEOPerSide: typing.ClassVar[wpimath._controls._controls.plant.DCMotor]  # value = <wpimath._controls._controls.plant.DCMotor object>
        def __init__(self) -> None:
            ...
    class KitbotWheelSize:
        """
        Represents common wheel sizes of the kit drivetrain.
        """
        kEightInch: typing.ClassVar[float] = 0.2032
        kSixInch: typing.ClassVar[float] = 0.1524
        kTenInch: typing.ClassVar[float] = 0.254
        def __init__(self) -> None:
            ...
    class State:
        kHeading: typing.ClassVar[int] = 2
        kLeftPosition: typing.ClassVar[int] = 5
        kLeftVelocity: typing.ClassVar[int] = 3
        kRightPosition: typing.ClassVar[int] = 6
        kRightVelocity: typing.ClassVar[int] = 4
        kX: typing.ClassVar[int] = 0
        kY: typing.ClassVar[int] = 1
        def __init__(self) -> None:
            ...
    @staticmethod
    @typing.overload
    def createKitbotSim(motor: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, wheelSize: wpimath.units.meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(7)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) -> DifferentialDrivetrainSim:
        """
        Create a sim for the standard FRC kitbot.
        
        :param motor:              The motors installed in the bot.
        :param gearing:            The gearing reduction used.
        :param wheelSize:          The wheel size.
        :param measurementStdDevs: Standard deviations for measurements, in the form
                                   [x, y, heading, left velocity, right velocity, left distance, right
                                   distance]ᵀ. Can be omitted if no noise is desired. Gyro standard
                                   deviations of 0.0001 radians, velocity standard deviations of 0.05 m/s, and
                                   position measurement standard deviations of 0.005 meters are a reasonable
                                   starting point.
        """
    @staticmethod
    @typing.overload
    def createKitbotSim(motor: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, wheelSize: wpimath.units.meters, J: wpimath.units.kilogram_square_meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(7)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) -> DifferentialDrivetrainSim:
        """
        Create a sim for the standard FRC kitbot.
        
        :param motor:              The motors installed in the bot.
        :param gearing:            The gearing reduction used.
        :param wheelSize:          The wheel size.
        :param J:                  The moment of inertia of the drivebase. This can be
                                   calculated using SysId.
        :param measurementStdDevs: Standard deviations for measurements, in the form
                                   [x, y, heading, left velocity, right velocity, left distance, right
                                   distance]ᵀ. Can be omitted if no noise is desired. Gyro standard
                                   deviations of 0.0001 radians, velocity standard deviations of 0.05 m/s, and
                                   position measurement standard deviations of 0.005 meters are a reasonable
                                   starting point.
        """
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_2, trackwidth: wpimath.units.meters, driveMotor: wpimath._controls._controls.plant.DCMotor, gearingRatio: typing.SupportsFloat, wheelRadius: wpimath.units.meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(7)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) -> None:
        """
        Creates a simulated differential drivetrain.
        
        :param plant:              The LinearSystem representing the robot's drivetrain. This
                                   system can be created with
                                   LinearSystemId::DrivetrainVelocitySystem() or
                                   LinearSystemId::IdentifyDrivetrainSystem().
        :param trackwidth:         The robot's trackwidth.
        :param driveMotor:         A DCMotor representing the left side of the drivetrain.
        :param gearingRatio:       The gearingRatio ratio of the left side, as output over
                                   input. This must be the same ratio as the ratio used to
                                   identify or create the plant.
        :param wheelRadius:        The radius of the wheels on the drivetrain, in meters.
        :param measurementStdDevs: Standard deviations for measurements, in the form
                                   [x, y, heading, left velocity, right velocity,
                                   left distance, right distance]ᵀ. Can be omitted
                                   if no noise is desired. Gyro standard deviations
                                   of 0.0001 radians, velocity standard deviations
                                   of 0.05 m/s, and position measurement standard
                                   deviations of 0.005 meters are a reasonable
                                   starting point.
        """
    @typing.overload
    def __init__(self, driveMotor: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, J: wpimath.units.kilogram_square_meters, mass: wpimath.units.kilograms, wheelRadius: wpimath.units.meters, trackwidth: wpimath.units.meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(7)] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]) -> None:
        """
        Creates a simulated differential drivetrain.
        
        :param driveMotor:         A DCMotor representing the left side of the drivetrain.
        :param gearing:            The gearing on the drive between motor and wheel, as
                                   output over input. This must be the same ratio as the
                                   ratio used to identify or create the plant.
        :param J:                  The moment of inertia of the drivetrain about its
                                   center.
        :param mass:               The mass of the drivebase.
        :param wheelRadius:        The radius of the wheels on the drivetrain.
        :param trackwidth:         The robot's trackwidth, or distance between left and
                                   right wheels.
        :param measurementStdDevs: Standard deviations for measurements, in the form
                                   [x, y, heading, left velocity, right velocity,
                                   left distance, right distance]ᵀ. Can be omitted
                                   if no noise is desired. Gyro standard deviations
                                   of 0.0001 radians, velocity standard deviations
                                   of 0.05 m/s, and position measurement standard
                                   deviations of 0.005 meters are a reasonable
                                   starting point.
        """
    def clampInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Clamp the input vector such that no element exceeds the battery voltage.
        If any does, the relative magnitudes of the input will be maintained.
        
        :param u: The input vector.
        
        :returns: The normalized input.
        """
    def dynamics(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[7, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[7, 1]"]:
        """
        The differential drive dynamics function.
        
        :param x: The state.
        :param u: The input.
        
        :returns: The state derivative with respect to time.
        """
    def getCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the currently drawn current.
        """
    def getGearing(self) -> float:
        """
        Returns the current gearing reduction of the drivetrain, as output over
        input.
        """
    def getHeading(self) -> wpimath.geometry._geometry.Rotation2d:
        """
        Returns the direction the robot is pointing.
        
        Note that this angle is counterclockwise-positive, while most gyros are
        clockwise positive.
        """
    def getLeftCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the currently drawn current for the left side.
        """
    def getLeftPosition(self) -> wpimath.units.meters:
        """
        Get the left encoder position in meters.
        
        :returns: The encoder position.
        """
    def getLeftPositionFeet(self) -> wpimath.units.feet:
        ...
    def getLeftPositionInches(self) -> wpimath.units.inches:
        ...
    def getLeftVelocity(self) -> wpimath.units.meters_per_second:
        """
        Get the left encoder velocity in meters per second.
        
        :returns: The encoder velocity.
        """
    def getLeftVelocityFps(self) -> wpimath.units.feet_per_second:
        ...
    def getPose(self) -> wpimath.geometry._geometry.Pose2d:
        """
        Returns the current pose.
        """
    def getRightCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the currently drawn current for the right side.
        """
    def getRightPosition(self) -> wpimath.units.meters:
        """
        Get the right encoder position in meters.
        
        :returns: The encoder position.
        """
    def getRightPositionFeet(self) -> wpimath.units.feet:
        ...
    def getRightPositionInches(self) -> wpimath.units.inches:
        ...
    def getRightVelocity(self) -> wpimath.units.meters_per_second:
        """
        Get the right encoder velocity in meters per second.
        
        :returns: The encoder velocity.
        """
    def getRightVelocityFps(self) -> wpimath.units.feet_per_second:
        ...
    def setGearing(self, newGearing: typing.SupportsFloat) -> None:
        """
        Sets the gearing reduction on the drivetrain. This is commonly used for
        shifting drivetrains.
        
        :param newGearing: The new gear ratio, as output over input.
        """
    def setInputs(self, leftVoltage: wpimath.units.volts, rightVoltage: wpimath.units.volts) -> None:
        """
        Sets the applied voltage to the drivetrain. Note that positive voltage must
        make that side of the drivetrain travel forward (+X).
        
        :param leftVoltage:  The left voltage.
        :param rightVoltage: The right voltage.
        """
    def setPose(self, pose: wpimath.geometry._geometry.Pose2d) -> None:
        """
        Sets the system pose.
        
        :param pose: The pose.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[7, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time that's passed since the last Update(units::second_t)
                   call.
        """
class DigitalPWMSim:
    """
    Class to control a simulated digital PWM output.
    
    This is for duty cycle PWM outputs on a DigitalOutput, not for the servo
    style PWM outputs on a PWM channel.
    """
    @staticmethod
    def createForChannel(channel: typing.SupportsInt) -> DigitalPWMSim:
        """
        Creates an DigitalPWMSim for a digital I/O channel.
        
        :param channel: DIO channel
        
        :returns: Simulated object
                  @throws std::out_of_range if no Digital PWM is configured for that channel
        """
    @staticmethod
    def createForIndex(index: typing.SupportsInt) -> DigitalPWMSim:
        """
        Creates an DigitalPWMSim for a simulated index.
        The index is incremented for each simulated DigitalPWM.
        
        :param index: simulator index
        
        :returns: Simulated object
        """
    def __init__(self, digitalOutput: wpilib._wpilib.DigitalOutput) -> None:
        """
        Constructs from a DigitalOutput object.
        
        :param digitalOutput: DigitalOutput to simulate
        """
    def getDutyCycle(self) -> float:
        """
        Read the duty cycle value.
        
        :returns: the duty cycle value of this PWM output
        """
    def getInitialized(self) -> bool:
        """
        Check whether this PWM output has been initialized.
        
        :returns: true if initialized
        """
    def getPin(self) -> int:
        """
        Check the pin number.
        
        :returns: the pin number
        """
    def registerDutyCycleCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the duty cycle value changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when this PWM output is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerPinCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the pin changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all simulation data.
        """
    def setDutyCycle(self, dutyCycle: typing.SupportsFloat) -> None:
        """
        Set the duty cycle value of this PWM output.
        
        :param dutyCycle: the new value
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether this PWM output has been initialized.
        
        :param initialized: whether this object is initialized
        """
    def setPin(self, pin: typing.SupportsInt) -> None:
        """
        Change the pin number.
        
        :param pin: the new pin number
        """
class DoubleSolenoidSim:
    @typing.overload
    def __init__(self, moduleSim: PneumaticsBaseSim, fwd: typing.SupportsInt, rev: typing.SupportsInt) -> None:
        ...
    @typing.overload
    def __init__(self, module: typing.SupportsInt, type: wpilib._wpilib.PneumaticsModuleType, fwd: typing.SupportsInt, rev: typing.SupportsInt) -> None:
        ...
    @typing.overload
    def __init__(self, type: wpilib._wpilib.PneumaticsModuleType, fwd: typing.SupportsInt, rev: typing.SupportsInt) -> None:
        ...
    def get(self) -> wpilib._wpilib.DoubleSolenoid.Value:
        ...
    def getModuleSim(self) -> PneumaticsBaseSim:
        ...
    def set(self, output: wpilib._wpilib.DoubleSolenoid.Value) -> None:
        ...
class DriverStationSim:
    """
    Class to control a simulated driver station.
    """
    @staticmethod
    def getAllianceStationId() -> hal._wpiHal.AllianceStationID:
        """
        Get the alliance station ID (color + number).
        
        :returns: the alliance station color and number
        """
    @staticmethod
    def getAutonomous() -> bool:
        """
        Check if the DS is in autonomous.
        
        :returns: true if autonomous
        """
    @staticmethod
    def getDsAttached() -> bool:
        """
        Check if the DS is attached.
        
        :returns: true if attached
        """
    @staticmethod
    def getEStop() -> bool:
        """
        Check if eStop has been activated.
        
        :returns: true if eStopped
        """
    @staticmethod
    def getEnabled() -> bool:
        """
        Check if the DS is enabled.
        
        :returns: true if enabled
        """
    @staticmethod
    def getFmsAttached() -> bool:
        """
        Check if the FMS is connected.
        
        :returns: true if FMS is connected
        """
    @staticmethod
    def getJoystickOutputs(stick: typing.SupportsInt) -> int:
        """
        Gets the joystick outputs.
        
        :param stick: The joystick number
        
        :returns: The joystick outputs
        """
    @staticmethod
    def getJoystickRumble(stick: typing.SupportsInt, rumbleNum: typing.SupportsInt) -> int:
        """
        Gets the joystick rumble.
        
        :param stick:     The joystick number
        :param rumbleNum: Rumble to get (0=left, 1=right)
        
        :returns: The joystick rumble value
        """
    @staticmethod
    def getMatchTime() -> float:
        """
        Get the current value of the match timer.
        
        :returns: the current match time
        """
    @staticmethod
    def getTest() -> bool:
        """
        Check if the DS is in test.
        
        :returns: true if test
        """
    @staticmethod
    def notifyNewData() -> None:
        """
        Updates DriverStation data so that new values are visible to the user
        program.
        """
    @staticmethod
    def registerAllianceStationIdCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the alliance station ID.
        
        :param callback:      the callback that will be called whenever the alliance
                              station changes
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerAutonomousCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the DS is in autonomous mode.
        
        :param callback:      the callback that will be called on autonomous mode
                              entrance/exit
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerDsAttachedCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the DS is connected.
        
        :param callback:      the callback that will be called whenever the DS
                              connection changes
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerEStopCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the eStop state.
        
        :param callback:      the callback that will be called whenever the eStop state
                              changes
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerEnabledCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the DS is enabled.
        
        :param callback:      the callback that will be called whenever the enabled
                              state is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerFmsAttachedCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the FMS is connected.
        
        :param callback:      the callback that will be called whenever the FMS
                              connection changes
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerMatchTimeCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on match time.
        
        :param callback:      the callback that will be called whenever match time
                              changes
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerTestCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on whether the DS is in test mode.
        
        :param callback:      the callback that will be called whenever the test mode
                              is entered or left
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def resetData() -> None:
        """
        Reset all simulation data for the Driver Station.
        """
    @staticmethod
    def setAllianceStationId(allianceStationId: hal._wpiHal.AllianceStationID) -> None:
        """
        Change the alliance station.
        
        :param allianceStationId: the new alliance station
        """
    @staticmethod
    def setAutonomous(autonomous: bool) -> None:
        """
        Change whether the DS is in autonomous.
        
        :param autonomous: the new value
        """
    @staticmethod
    def setDsAttached(dsAttached: bool) -> None:
        """
        Change whether the DS is attached.
        
        :param dsAttached: the new value
        """
    @staticmethod
    def setEStop(eStop: bool) -> None:
        """
        Set whether eStop is active.
        
        :param eStop: true to activate
        """
    @staticmethod
    def setEnabled(enabled: bool) -> None:
        """
        Change whether the DS is enabled.
        
        :param enabled: the new value
        """
    @staticmethod
    def setEventName(name: str) -> None:
        """
        Sets the event name.
        
        :param name: the event name
        """
    @staticmethod
    def setFmsAttached(fmsAttached: bool) -> None:
        """
        Change whether the FMS is connected.
        
        :param fmsAttached: the new value
        """
    @staticmethod
    def setGameSpecificMessage(message: str) -> None:
        """
        Sets the game specific message.
        
        :param message: the game specific message
        """
    @staticmethod
    def setJoystickAxis(stick: typing.SupportsInt, axis: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Gets the value of the axis on a joystick.
        
        :param stick: The joystick number
        :param axis:  The analog axis number
        :param value: The value of the axis on the joystick
        """
    @staticmethod
    def setJoystickAxisCount(stick: typing.SupportsInt, count: typing.SupportsInt) -> None:
        """
        Sets the number of axes for a joystick.
        
        :param stick: The joystick number
        :param count: The number of axes on the indicated joystick
        """
    @staticmethod
    def setJoystickAxisType(stick: typing.SupportsInt, axis: typing.SupportsInt, type: typing.SupportsInt) -> None:
        """
        Sets the types of Axes for a joystick.
        
        :param stick: The joystick number
        :param axis:  The target axis
        :param type:  The type of axis
        """
    @staticmethod
    def setJoystickButton(stick: typing.SupportsInt, button: typing.SupportsInt, state: bool) -> None:
        """
        Sets the state of one joystick button. %Button indexes begin at 1.
        
        :param stick:  The joystick number
        :param button: The button index, beginning at 1
        :param state:  The state of the joystick button
        """
    @staticmethod
    def setJoystickButtonCount(stick: typing.SupportsInt, count: typing.SupportsInt) -> None:
        """
        Sets the number of buttons for a joystick.
        
        :param stick: The joystick number
        :param count: The number of buttons on the indicated joystick
        """
    @staticmethod
    def setJoystickButtons(stick: typing.SupportsInt, buttons: typing.SupportsInt) -> None:
        """
        Sets the state of all the buttons on a joystick.
        
        :param stick:   The joystick number
        :param buttons: The bitmap state of the buttons on the joystick
        """
    @staticmethod
    def setJoystickIsGamepad(stick: typing.SupportsInt, isGamepad: bool) -> None:
        """
        Sets the value of isGamepad for a joystick.
        
        :param stick:     The joystick number
        :param isGamepad: The value of isGamepad
        """
    @staticmethod
    def setJoystickName(stick: typing.SupportsInt, name: str) -> None:
        """
        Sets the name of a joystick.
        
        :param stick: The joystick number
        :param name:  The value of name
        """
    @staticmethod
    def setJoystickPOV(stick: typing.SupportsInt, pov: typing.SupportsInt, value: wpilib._wpilib.DriverStation.POVDirection) -> None:
        """
        Gets the state of a POV on a joystick.
        
        :param stick: The joystick number
        :param pov:   The POV number
        :param value: the angle of the POV
        """
    @staticmethod
    def setJoystickPOVCount(stick: typing.SupportsInt, count: typing.SupportsInt) -> None:
        """
        Sets the number of POVs for a joystick.
        
        :param stick: The joystick number
        :param count: The number of POVs on the indicated joystick
        """
    @staticmethod
    def setJoystickType(stick: typing.SupportsInt, type: typing.SupportsInt) -> None:
        """
        Sets the value of type for a joystick.
        
        :param stick: The joystick number
        :param type:  The value of type
        """
    @staticmethod
    def setMatchNumber(matchNumber: typing.SupportsInt) -> None:
        """
        Sets the match number.
        
        :param matchNumber: the match number
        """
    @staticmethod
    def setMatchTime(matchTime: typing.SupportsFloat) -> None:
        """
        Sets the match timer.
        
        :param matchTime: the new match time
        """
    @staticmethod
    def setMatchType(type: wpilib._wpilib.DriverStation.MatchType) -> None:
        """
        Sets the match type.
        
        :param type: the match type
        """
    @staticmethod
    def setReplayNumber(replayNumber: typing.SupportsInt) -> None:
        """
        Sets the replay number.
        
        :param replayNumber: the replay number
        """
    @staticmethod
    def setSendConsoleLine(shouldSend: bool) -> None:
        """
        Sets suppression of DriverStation::SendConsoleLine messages.
        
        :param shouldSend: If false then messages will be suppressed.
        """
    @staticmethod
    def setSendError(shouldSend: bool) -> None:
        """
        Sets suppression of DriverStation::ReportError and ReportWarning messages.
        
        :param shouldSend: If false then messages will be suppressed.
        """
    @staticmethod
    def setTest(test: bool) -> None:
        """
        Change whether the DS is in test.
        
        :param test: the new value
        """
    def __init__(self) -> None:
        ...
class DutyCycleEncoderSim:
    """
    Class to control a simulated duty cycle encoder.
    """
    @typing.overload
    def __init__(self, encoder: wpilib._wpilib.DutyCycleEncoder) -> None:
        """
        Constructs from a DutyCycleEncoder object.
        
        :param encoder: DutyCycleEncoder to simulate
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructs from a digital input channel.
        
        :param channel: digital input channel
        """
    def get(self) -> float:
        """
        Get the position.
        
        :returns: The position.
        """
    def isConnected(self) -> bool:
        """
        Get if the encoder is connected.
        
        :returns: true if the encoder is connected.
        """
    def set(self, value: typing.SupportsFloat) -> None:
        """
        Set the position.
        
        :param value: The position.
        """
    def setConnected(self, isConnected: bool) -> None:
        """
        Set if the encoder is connected.
        
        :param isConnected: Whether or not the sensor is connected.
        """
class DutyCycleSim:
    """
    Class to control a simulated duty cycle digital input.
    """
    @staticmethod
    def createForChannel(channel: typing.SupportsInt) -> DutyCycleSim:
        """
        Creates a DutyCycleSim for a SmartIO channel.
        
        :param channel: SmartIO channel
        
        :returns: Simulated object
        """
    def __init__(self, dutyCycle: wpilib._wpilib.DutyCycle) -> None:
        """
        Constructs from a DutyCycle object.
        
        :param dutyCycle: DutyCycle to simulate
        """
    def getFrequency(self) -> wpimath.units.hertz:
        """
        Measure the frequency.
        
        :returns: the duty cycle frequency
        """
    def getInitialized(self) -> bool:
        """
        Check whether this duty cycle input has been initialized.
        
        :returns: true if initialized
        """
    def getOutput(self) -> float:
        """
        Measure the output from this duty cycle port.
        
        :returns: the output value
        """
    def registerFrequencyCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the frequency changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when this duty cycle input is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerOutputCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the output changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all simulation data for the duty cycle output.
        """
    def setFrequency(self, frequency: wpimath.units.hertz) -> None:
        """
        Change the duty cycle frequency.
        
        :param frequency: the new frequency
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether this duty cycle input has been initialized.
        
        :param initialized: whether this object is initialized
        """
    def setOutput(self, output: typing.SupportsFloat) -> None:
        """
        Change the duty cycle output.
        
        :param output: the new output value
        """
class ElevatorSim(LinearSystemSim_2_1_2):
    """
    Represents a simulated elevator mechanism.
    """
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_2, gearbox: wpimath._controls._controls.plant.DCMotor, minHeight: wpimath.units.meters, maxHeight: wpimath.units.meters, simulateGravity: bool, startingHeight: wpimath.units.meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Constructs a simulated elevator mechanism.
        
        :param plant:              The linear system that represents the elevator.
                                   This system can be created with
                                   LinearSystemId::ElevatorSystem().
        :param gearbox:            The type of and number of motors in your
                                   elevator gearbox.
        :param minHeight:          The minimum allowed height of the elevator.
        :param maxHeight:          The maximum allowed height of the elevator.
        :param simulateGravity:    Whether gravity should be simulated or not.
        :param startingHeight:     The starting height of the elevator.
        :param measurementStdDevs: The standard deviation of the measurements.
        """
    @typing.overload
    def __init__(self, gearbox: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, carriageMass: wpimath.units.kilograms, drumRadius: wpimath.units.meters, minHeight: wpimath.units.meters, maxHeight: wpimath.units.meters, simulateGravity: bool, startingHeight: wpimath.units.meters, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Constructs a simulated elevator mechanism.
        
        :param gearbox:            The type of and number of motors in your
                                   elevator gearbox.
        :param gearing:            The gearing of the elevator (numbers greater
                                   than 1 represent reductions).
        :param carriageMass:       The mass of the elevator carriage.
        :param drumRadius:         The radius of the drum that your cable is
                                   wrapped around.
        :param minHeight:          The minimum allowed height of the elevator.
        :param maxHeight:          The maximum allowed height of the elevator.
        :param simulateGravity:    Whether gravity should be simulated or not.
        :param startingHeight:     The starting height of the elevator.
        :param measurementStdDevs: The standard deviation of the measurements.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the elevator.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (voltage).
        :param dt:          The time difference between controller updates.
        """
    def getCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the elevator current draw.
        
        :returns: The elevator current draw.
        """
    def getPosition(self) -> wpimath.units.meters:
        """
        Returns the position of the elevator.
        
        :returns: The position of the elevator.
        """
    def getPositionFeet(self) -> wpimath.units.feet:
        ...
    def getPositionInches(self) -> wpimath.units.inches:
        ...
    def getVelocity(self) -> wpimath.units.meters_per_second:
        """
        Returns the velocity of the elevator.
        
        :returns: The velocity of the elevator.
        """
    def getVelocityFps(self) -> wpimath.units.feet_per_second:
        ...
    def hasHitLowerLimit(self) -> bool:
        """
        Returns whether the elevator has hit the lower limit.
        
        :returns: Whether the elevator has hit the lower limit.
        """
    def hasHitUpperLimit(self) -> bool:
        """
        Returns whether the elevator has hit the upper limit.
        
        :returns: Whether the elevator has hit the upper limit.
        """
    def setInputVoltage(self, voltage: wpimath.units.volts) -> None:
        """
        Sets the input voltage for the elevator.
        
        :param voltage: The input voltage.
        """
    def setState(self, position: wpimath.units.meters, velocity: wpimath.units.meters_per_second) -> None:
        """
        Sets the elevator's state. The new position will be limited between the
        minimum and maximum allowed heights.
        
        :param position: The new position
        :param velocity: The new velocity
        """
    def wouldHitLowerLimit(self, elevatorHeight: wpimath.units.meters) -> bool:
        """
        Returns whether the elevator would hit the lower limit.
        
        :param elevatorHeight: The elevator height.
        
        :returns: Whether the elevator would hit the lower limit.
        """
    def wouldHitUpperLimit(self, elevatorHeight: wpimath.units.meters) -> bool:
        """
        Returns whether the elevator would hit the upper limit.
        
        :param elevatorHeight: The elevator height.
        
        :returns: Whether the elevator would hit the upper limit.
        """
class EncoderSim:
    """
    Class to control a simulated encoder.
    """
    @staticmethod
    def createForChannel(channel: typing.SupportsInt) -> EncoderSim:
        """
        Creates an EncoderSim for a digital input channel.  Encoders take two
        channels, so either one may be specified.
        
        :param channel: digital input channel
        
        :returns: Simulated object
                  @throws NoSuchElementException if no Encoder is configured for that channel
        """
    @staticmethod
    def createForIndex(index: typing.SupportsInt) -> EncoderSim:
        """
        Creates an EncoderSim for a simulated index.
        The index is incremented for each simulated Encoder.
        
        :param index: simulator index
        
        :returns: Simulated object
        """
    def __init__(self, encoder: wpilib._wpilib.Encoder) -> None:
        """
        Constructs from an Encoder object.
        
        :param encoder: Encoder to simulate
        """
    def getCount(self) -> int:
        """
        Read the count of the encoder.
        
        :returns: the count
        """
    def getDirection(self) -> bool:
        """
        Get the direction of the encoder.
        
        :returns: the direction of the encoder
        """
    def getDistance(self) -> float:
        """
        Read the distance of the encoder.
        
        :returns: the encoder distance
        """
    def getDistancePerPulse(self) -> float:
        """
        Read the distance per pulse of the encoder.
        
        :returns: the encoder distance per pulse
        """
    def getInitialized(self) -> bool:
        """
        Read the Initialized value of the encoder.
        
        :returns: true if initialized
        """
    def getMaxPeriod(self) -> float:
        """
        Get the max period of the encoder.
        
        :returns: the max period of the encoder
        """
    def getPeriod(self) -> float:
        """
        Read the period of the encoder.
        
        :returns: the encoder period
        """
    def getRate(self) -> float:
        """
        Get the rate of the encoder.
        
        :returns: the rate of change
        """
    def getReset(self) -> bool:
        """
        Check if the encoder has been reset.
        
        :returns: true if reset
        """
    def getReverseDirection(self) -> bool:
        """
        Get the reverse direction of the encoder.
        
        :returns: the reverse direction of the encoder
        """
    def getSamplesToAverage(self) -> int:
        """
        Get the samples-to-average value.
        
        :returns: the samples-to-average value
        """
    def registerCountCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the count property of the encoder.
        
        :param callback:      the callback that will be called whenever the count
                              property is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerDirectionCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the direction of the encoder.
        
        :param callback:      the callback that will be called whenever the direction
                              is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerDistancePerPulseCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the distance per pulse value of this encoder.
        
        :param callback:      the callback that will be called whenever the
                              distance per pulse is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the Initialized property of the encoder.
        
        :param callback:      the callback that will be called whenever the Initialized
                              property is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerMaxPeriodCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the max period of the encoder is
        changed.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerPeriodCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the period of the encoder.
        
        :param callback:      the callback that will be called whenever the period is
                              changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerResetCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be called whenever the encoder is reset.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerReverseDirectionCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the reverse direction.
        
        :param callback:      the callback that will be called whenever the reverse
                              direction is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerSamplesToAverageCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback on the samples-to-average value of this encoder.
        
        :param callback:      the callback that will be called whenever the
                              samples-to-average is changed
        :param initialNotify: if true, the callback will be run on the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Resets all simulation data for this encoder.
        """
    def setCount(self, count: typing.SupportsInt) -> None:
        """
        Change the count of the encoder.
        
        :param count: the new count
        """
    def setDirection(self, direction: bool) -> None:
        """
        Set the direction of the encoder.
        
        :param direction: the new direction
        """
    def setDistance(self, distance: typing.SupportsFloat) -> None:
        """
        Change the encoder distance.
        
        :param distance: the new distance
        """
    def setDistancePerPulse(self, distancePerPulse: typing.SupportsFloat) -> None:
        """
        Change the encoder distance per pulse.
        
        :param distancePerPulse: the new distance per pulse
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Change the Initialized value of the encoder.
        
        :param initialized: the new value
        """
    def setMaxPeriod(self, maxPeriod: typing.SupportsFloat) -> None:
        """
        Change the max period of the encoder.
        
        :param maxPeriod: the new value
        """
    def setPeriod(self, period: typing.SupportsFloat) -> None:
        """
        Change the encoder period.
        
        :param period: the new period
        """
    def setRate(self, rate: typing.SupportsFloat) -> None:
        """
        Change the rate of the encoder.
        
        :param rate: the new rate
        """
    def setReset(self, reset: bool) -> None:
        """
        Change the reset property of the encoder.
        
        :param reset: the new value
        """
    def setReverseDirection(self, reverseDirection: bool) -> None:
        """
        Set the reverse direction.
        
        :param reverseDirection: the new value
        """
    def setSamplesToAverage(self, samplesToAverage: typing.SupportsInt) -> None:
        """
        Set the samples-to-average value.
        
        :param samplesToAverage: the new value
        """
class FlywheelSim(LinearSystemSim_1_1_1):
    """
    Represents a simulated flywheel mechanism.
    """
    def J(self) -> wpimath.units.kilogram_square_meters:
        """
        Returns the moment of inertia
        """
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_1, gearbox: wpimath._controls._controls.plant.DCMotor, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(1)] = [0.0]) -> None:
        """
        Creates a simulated flywheel mechanism.
        
        :param plant:              The linear system representing the flywheel. This
                                   system can be created with
                                   LinearSystemId::FlywheelSystem() or
                                   LinearSystemId::IdentifyVelocitySystem().
        :param gearbox:            The type of and number of motors in the flywheel
                                   gearbox.
        :param measurementStdDevs: The standard deviation of the measurement noise.
        """
    def gearbox(self) -> wpimath._controls._controls.plant.DCMotor:
        """
        Returns the gearbox.
        """
    def gearing(self) -> float:
        """
        Returns the gearing;
        """
    def getAngularAcceleration(self) -> wpimath.units.radians_per_second_squared:
        """
        Returns the flywheel's acceleration.
        
        :returns: The flywheel's acceleration
        """
    def getAngularVelocity(self) -> wpimath.units.radians_per_second:
        """
        Returns the flywheel's velocity.
        
        :returns: The flywheel's velocity.
        """
    def getCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the flywheel's current draw.
        
        :returns: The flywheel's current draw.
        """
    def getInputVoltage(self) -> wpimath.units.volts:
        """
        Gets the input voltage for the flywheel.
        
        :returns: The flywheel input voltage.
        """
    def getTorque(self) -> wpimath.units.newton_meters:
        """
        Returns the flywheel's torque.
        
        :returns: The flywheel's torque
        """
    def setInputVoltage(self, voltage: wpimath.units.volts) -> None:
        """
        Sets the input voltage for the flywheel.
        
        :param voltage: The input voltage.
        """
    def setVelocity(self, velocity: wpimath.units.radians_per_second) -> None:
        """
        Sets the flywheel's angular velocity.
        
        :param velocity: The new velocity
        """
class GenericHIDSim:
    """
    Class to control a simulated generic joystick.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.interfaces.GenericHID) -> None:
        """
        Constructs from a GenericHID object.
        
        :param joystick: joystick to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def getOutput(self, outputNumber: typing.SupportsInt) -> bool:
        """
        Read the output of a button.
        
        :param outputNumber: the button number
        
        :returns: the value of the button (true = pressed)
        """
    def getOutputs(self) -> int:
        """
        Get the encoded 16-bit integer that passes button values.
        
        :returns: the button values
        """
    def getRumble(self, type: wpilib._wpilib.interfaces.GenericHID.RumbleType) -> float:
        """
        Get the joystick rumble.
        
        :param type: the rumble to read
        
        :returns: the rumble value
        """
    def notifyNewData(self) -> None:
        """
        Updates joystick data so that new values are visible to the user program.
        """
    def setAxisCount(self, count: typing.SupportsInt) -> None:
        """
        Set the axis count of this device.
        
        :param count: the new axis count
        """
    def setAxisType(self, axis: typing.SupportsInt, type: typing.SupportsInt) -> None:
        """
        Set the type of an axis.
        
        :param axis: the axis
        :param type: the type
        """
    def setButtonCount(self, count: typing.SupportsInt) -> None:
        """
        Set the button count of this device.
        
        :param count: the new button count
        """
    def setName(self, name: str) -> None:
        """
        Set the name of this device.
        
        :param name: the new device name
        """
    @typing.overload
    def setPOV(self, pov: typing.SupportsInt, value: wpilib._wpilib.DriverStation.POVDirection) -> None:
        """
        Set the value of a given POV.
        
        :param pov:   the POV to set
        :param value: the new value
        """
    @typing.overload
    def setPOV(self, value: wpilib._wpilib.DriverStation.POVDirection) -> None:
        """
        Set the value of the default POV (port 0).
        
        :param value: the new value
        """
    def setPOVCount(self, count: typing.SupportsInt) -> None:
        """
        Set the POV count of this device.
        
        :param count: the new POV count
        """
    def setRawAxis(self, axis: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Set the value of a given axis.
        
        :param axis:  the axis to set
        :param value: the new value
        """
    def setRawButton(self, button: typing.SupportsInt, value: bool) -> None:
        """
        Set the value of a given button.
        
        :param button: the button to set
        :param value:  the new value
        """
    def setType(self, type: wpilib._wpilib.interfaces.GenericHID.HIDType) -> None:
        """
        Set the type of this device.
        
        :param type: the new device type
        """
class JoystickSim(GenericHIDSim):
    """
    Class to control a simulated joystick.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.Joystick) -> None:
        """
        Constructs from a Joystick object.
        
        :param joystick: joystick to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def setThrottle(self, value: typing.SupportsFloat) -> None:
        """
        Set the throttle value of the joystick.
        
        :param value: the new throttle value
        """
    def setTop(self, state: bool) -> None:
        """
        Set the top state of the joystick.
        
        :param state: the new state
        """
    def setTrigger(self, state: bool) -> None:
        """
        Set the trigger value of the joystick.
        
        :param state: the new value
        """
    def setTwist(self, value: typing.SupportsFloat) -> None:
        """
        Set the twist value of the joystick.
        
        :param value: the new twist value
        """
    def setX(self, value: typing.SupportsFloat) -> None:
        """
        Set the X value of the joystick.
        
        :param value: the new X value
        """
    def setY(self, value: typing.SupportsFloat) -> None:
        """
        Set the Y value of the joystick.
        
        :param value: the new Y value
        """
    def setZ(self, value: typing.SupportsFloat) -> None:
        """
        Set the Z value of the joystick.
        
        :param value: the new Z value
        """
class LinearSystemSim_1_1_1:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_1_1_1, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(1)] = [0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(1)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_1_1_1:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Output vector.
        """
class LinearSystemSim_1_1_2:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_1_1_2, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(2)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_1_1_2:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Output vector.
        """
class LinearSystemSim_2_1_1:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_1_1, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(1)] = [0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(1)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_2_1_1:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Output vector.
        """
class LinearSystemSim_2_1_2:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_1_2, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(2)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_2_1_2:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Output vector.
        """
class LinearSystemSim_2_2_1:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_2_1, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(1)] = [0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(1)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_2_2_1:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Output vector.
        """
class LinearSystemSim_2_2_2:
    """
    This class helps simulate linear systems. To use this class, do the following
    in the simulationPeriodic() method.
    
    Call the SetInput() method with the inputs to your system (generally
    voltage). Call the Update() method to update the simulation. Set simulated
    sensor readings with the simulated positions in the GetOutput() method.
    
    @tparam States  Number of states of the system.
    @tparam Inputs  Number of inputs to the system.
    @tparam Outputs Number of outputs of the system.
    """
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_2_2, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated generic linear system.
        
        :param system:             The system to simulate.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    def _clampInput(self, maxInput: typing.SupportsFloat) -> None:
        """
        Clamp the input vector such that no element exceeds the given voltage. If
        any does, the relative magnitudes of the input will be maintained.
        
        :param maxInput: The maximum magnitude of the input vector after clamping.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the system.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (usually voltage).
        :param dt:          The time difference between controller updates.
        """
    @typing.overload
    def getInput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current input of the plant.
        
        :returns: The current input of the plant.
        """
    @typing.overload
    def getInput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current input of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current input of the plant.
        """
    @typing.overload
    def getOutput(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current output of the plant.
        
        :returns: The current output of the plant.
        """
    @typing.overload
    def getOutput(self, row: typing.SupportsInt) -> float:
        """
        Returns an element of the current output of the plant.
        
        :param row: The row to return.
        
        :returns: An element of the current output of the plant.
        """
    @typing.overload
    def setInput(self, u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system inputs (usually voltages).
        
        :param u: The system inputs.
        """
    @typing.overload
    def setInput(self, row: typing.SupportsInt, value: typing.SupportsFloat) -> None:
        """
        Sets the system inputs.
        
        :param row:   The row in the input matrix to set.
        :param value: The value to set the row to.
        """
    def setState(self, state: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Sets the system state.
        
        :param state: The new state.
        """
    def update(self, dt: wpimath.units.seconds) -> None:
        """
        Updates the simulation.
        
        :param dt: The time between updates.
        """
    @property
    def _m_measurementStdDevs(self) -> typing.Annotated[list[float], pybind11_stubgen.typing_ext.FixedSize(2)]:
        """
        The standard deviations of measurements, used for adding noise to the
        measurements.
        """
    @property
    def _m_plant(self) -> wpimath._controls._controls.system.LinearSystem_2_2_2:
        """
        The plant that represents the linear system.
        """
    @property
    def _m_u(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Input vector.
        """
    @property
    def _m_x(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        State vector.
        """
    @property
    def _m_y(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Output vector.
        """
class PS4ControllerSim(GenericHIDSim):
    """
    Class to control a simulated PS4 controller.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.PS4Controller) -> None:
        """
        Constructs from a PS4Controller object.
        
        :param joystick: controller to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def setCircleButton(self, value: bool) -> None:
        """
        Change the value of the circle button on the controller.
        
        :param value: the new value
        """
    def setCrossButton(self, value: bool) -> None:
        """
        Change the value of the cross button on the controller.
        
        :param value: the new value
        """
    def setL1Button(self, value: bool) -> None:
        """
        Change the value of the left trigger 1 button on the controller.
        
        :param value: the new value
        """
    def setL2Axis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the left trigger 2 axis on the controller.
        
        :param value: the new value
        """
    def setL2Button(self, value: bool) -> None:
        """
        Change the value of the left trigger 2 button on the controller.
        
        :param value: the new value
        """
    def setL3Button(self, value: bool) -> None:
        """
        Change the value of the L3 (left stick) button on the controller.
        
        :param value: the new value
        """
    def setLeftX(self, value: typing.SupportsFloat) -> None:
        """
        Change the left X value of the controller's joystick.
        
        :param value: the new value
        """
    def setLeftY(self, value: typing.SupportsFloat) -> None:
        """
        Change the left Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setOptionsButton(self, value: bool) -> None:
        """
        Change the value of the options button on the controller.
        
        :param value: the new value
        """
    def setPSButton(self, value: bool) -> None:
        """
        Change the value of the PlayStation button on the controller.
        
        :param value: the new value
        """
    def setR1Button(self, value: bool) -> None:
        """
        Change the value of the right trigger 1 button on the controller.
        
        :param value: the new value
        """
    def setR2Axis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the right trigger 2 axis on the controller.
        
        :param value: the new value
        """
    def setR2Button(self, value: bool) -> None:
        """
        Change the value of the right trigger 2 button on the controller.
        
        :param value: the new value
        """
    def setR3Button(self, value: bool) -> None:
        """
        Change the value of the R3 (right stick) button on the controller.
        
        :param value: the new value
        """
    def setRightX(self, value: typing.SupportsFloat) -> None:
        """
        Change the right X value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightY(self, value: typing.SupportsFloat) -> None:
        """
        Change the right Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setShareButton(self, value: bool) -> None:
        """
        Change the value of the share button on the controller.
        
        :param value: the new value
        """
    def setSquareButton(self, value: bool) -> None:
        """
        Change the value of the square button on the controller.
        
        :param value: the new value
        """
    def setTouchpadButton(self, value: bool) -> None:
        """
        Change the value of the touchpad button on the controller.
        
        :param value: the new value
        """
    def setTriangleButton(self, value: bool) -> None:
        """
        Change the value of the triangle button on the controller.
        
        :param value: the new value
        """
class PS5ControllerSim(GenericHIDSim):
    """
    Class to control a simulated PS5 controller.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.PS5Controller) -> None:
        """
        Constructs from a PS5Controller object.
        
        :param joystick: controller to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def setCircleButton(self, value: bool) -> None:
        """
        Change the value of the circle button on the controller.
        
        :param value: the new value
        """
    def setCreateButton(self, value: bool) -> None:
        """
        Change the value of the create button on the controller.
        
        :param value: the new value
        """
    def setCrossButton(self, value: bool) -> None:
        """
        Change the value of the cross button on the controller.
        
        :param value: the new value
        """
    def setL1Button(self, value: bool) -> None:
        """
        Change the value of the left trigger 1 button on the controller.
        
        :param value: the new value
        """
    def setL2Axis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the left trigger 2 axis on the controller.
        
        :param value: the new value
        """
    def setL2Button(self, value: bool) -> None:
        """
        Change the value of the left trigger 2 button on the controller.
        
        :param value: the new value
        """
    def setL3Button(self, value: bool) -> None:
        """
        Change the value of the L3 (left stick) button on the controller.
        
        :param value: the new value
        """
    def setLeftX(self, value: typing.SupportsFloat) -> None:
        """
        Change the left X value of the controller's joystick.
        
        :param value: the new value
        """
    def setLeftY(self, value: typing.SupportsFloat) -> None:
        """
        Change the left Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setOptionsButton(self, value: bool) -> None:
        """
        Change the value of the options button on the controller.
        
        :param value: the new value
        """
    def setPSButton(self, value: bool) -> None:
        """
        Change the value of the PlayStation button on the controller.
        
        :param value: the new value
        """
    def setR1Button(self, value: bool) -> None:
        """
        Change the value of the right trigger 1 button on the controller.
        
        :param value: the new value
        """
    def setR2Axis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the right trigger 2 axis on the controller.
        
        :param value: the new value
        """
    def setR2Button(self, value: bool) -> None:
        """
        Change the value of the right trigger 2 button on the controller.
        
        :param value: the new value
        """
    def setR3Button(self, value: bool) -> None:
        """
        Change the value of the R3 (right stick) button on the controller.
        
        :param value: the new value
        """
    def setRightX(self, value: typing.SupportsFloat) -> None:
        """
        Change the right X value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightY(self, value: typing.SupportsFloat) -> None:
        """
        Change the right Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setSquareButton(self, value: bool) -> None:
        """
        Change the value of the square button on the controller.
        
        :param value: the new value
        """
    def setTouchpadButton(self, value: bool) -> None:
        """
        Change the value of the touchpad button on the controller.
        
        :param value: the new value
        """
    def setTriangleButton(self, value: bool) -> None:
        """
        Change the value of the triangle button on the controller.
        
        :param value: the new value
        """
class PWMMotorControllerSim:
    @typing.overload
    def __init__(self, motorctrl: wpilib._wpilib.PWMMotorController) -> None:
        ...
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        ...
    def getSpeed(self) -> float:
        ...
class PWMSim:
    """
    Class to control a simulated PWM output.
    """
    @typing.overload
    def __init__(self, pwm: wpilib._wpilib.PWM) -> None:
        """
        Constructs from a PWM object.
        
        :param pwm: PWM to simulate
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructs from a PWM channel number.
        
        :param channel: Channel number
        """
    def getInitialized(self) -> bool:
        """
        Check whether the PWM has been initialized.
        
        :returns: true if initialized
        """
    def getOutputPeriod(self) -> int:
        """
        Get the PWM period scale.
        
        :returns: the PWM period scale
        """
    def getPulseMicrosecond(self) -> int:
        """
        Get the PWM pulse microsecond value.
        
        :returns: the PWM pulse microsecond value
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the PWM is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerOutputPeriodCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the PWM period scale changes.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerPulseMicrosecondCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the PWM pulse microsecond value changes.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all simulation data.
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether the PWM has been initialized.
        
        :param initialized: whether this object is initialized
        """
    def setOutputPeriod(self, period: typing.SupportsInt) -> None:
        """
        Set the PWM period scale.
        
        :param period: the PWM period scale
        """
    def setPulseMicrosecond(self, microsecondPulseTime: typing.SupportsInt) -> None:
        """
        Set the PWM pulse microsecond value.
        
        :param microsecondPulseTime: the PWM pulse microsecond value
        """
class PneumaticsBaseSim:
    @staticmethod
    def getForType(module: typing.SupportsInt, type: wpilib._wpilib.PneumaticsModuleType) -> PneumaticsBaseSim:
        ...
    @typing.overload
    def __init__(self, index: typing.SupportsInt) -> None:
        """
        Constructs a PneumaticsBaseSim with the given index.
        
        :param index: The index.
        """
    @typing.overload
    def __init__(self, module: wpilib._wpilib.PneumaticsBase) -> None:
        """
        Constructs a PneumaticsBaseSim for the given module.
        
        :param module: The module.
        """
    def getAllSolenoidOutputs(self) -> int:
        """
        Get the current value of all solenoid outputs.
        
        :returns: the solenoid outputs (1 bit per output)
        """
    def getCompressorCurrent(self) -> float:
        """
        Read the compressor current.
        
        :returns: the current of the compressor connected to this module
        """
    def getCompressorOn(self) -> bool:
        """
        Check if the compressor is on.
        
        :returns: true if the compressor is active
        """
    def getInitialized(self) -> bool:
        """
        Check whether the PCM/PH has been initialized.
        
        :returns: true if initialized
        """
    def getPressureSwitch(self) -> bool:
        """
        Check the value of the pressure switch.
        
        :returns: the pressure switch value
        """
    def getSolenoidOutput(self, channel: typing.SupportsInt) -> bool:
        """
        Check the solenoid output on a specific channel.
        
        :param channel: the channel to check
        
        :returns: the solenoid output
        """
    def registerCompressorCurrentCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the compressor current changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def registerCompressorOnCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the compressor activates.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the PCM/PH is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def registerPressureSwitchCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the pressure switch value changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the initial
                              value
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def registerSolenoidOutputCallback(self, channel: typing.SupportsInt, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the solenoid output on a channel
        changes.
        
        :param channel:       the channel to monitor
        :param callback:      the callback
        :param initialNotify: should the callback be run with the initial value
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def resetData(self) -> None:
        """
        Reset all simulation data for this object.
        """
    def setAllSolenoidOutputs(self, outputs: typing.SupportsInt) -> None:
        """
        Change all of the solenoid outputs.
        
        :param outputs: the new solenoid outputs (1 bit per output)
        """
    def setCompressorCurrent(self, compressorCurrent: typing.SupportsFloat) -> None:
        """
        Set the compressor current.
        
        :param compressorCurrent: the new compressor current
        """
    def setCompressorOn(self, compressorOn: bool) -> None:
        """
        Set whether the compressor is active.
        
        :param compressorOn: the new value
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether the PCM/PH has been initialized.
        
        :param initialized: true for initialized
        """
    def setPressureSwitch(self, pressureSwitch: bool) -> None:
        """
        Set the value of the pressure switch.
        
        :param pressureSwitch: the new value
        """
    def setSolenoidOutput(self, channel: typing.SupportsInt, solenoidOutput: bool) -> None:
        """
        Change the solenoid output on a specific channel.
        
        :param channel:        the channel to check
        :param solenoidOutput: the new solenoid output
        """
    @property
    def _m_index(self) -> int:
        """
        PneumaticsBase index.
        """
class PowerDistributionSim:
    """
    Class to control a simulated Power Distribution Panel (PowerDistribution).
    """
    @typing.overload
    def __init__(self, module: typing.SupportsInt = 0) -> None:
        """
        Constructs from a PowerDistribution module number (CAN ID).
        
        :param module: module number
        """
    @typing.overload
    def __init__(self, pdp: wpilib._wpilib.PowerDistribution) -> None:
        """
        Constructs from a PowerDistribution object.
        
        :param pdp: PowerDistribution to simulate
        """
    def getAllCurrents(self, length: typing.SupportsInt) -> float:
        """
        Read the current of all of the PowerDistribution channels.
        
        :param currents: output array; set to the current in each channel. The
                         array must be big enough to hold all the PowerDistribution
                         channels
        :param length:   length of output array
        """
    def getCurrent(self, channel: typing.SupportsInt) -> float:
        """
        Read the current in one of the PowerDistribution channels.
        
        :param channel: the channel to check
        
        :returns: the current in the given channel
        """
    def getInitialized(self) -> bool:
        """
        Check whether the PowerDistribution has been initialized.
        
        :returns: true if initialized
        """
    def getTemperature(self) -> float:
        """
        Check the temperature of the PowerDistribution.
        
        :returns: the PowerDistribution temperature
        """
    def getVoltage(self) -> float:
        """
        Check the PowerDistribution voltage.
        
        :returns: the PowerDistribution voltage.
        """
    def registerCurrentCallback(self, channel: typing.SupportsInt, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the current of a specific channel
        changes.
        
        :param channel:       the channel
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the PowerDistribution is initialized.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerTemperatureCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the PowerDistribution temperature
        changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerVoltageCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the PowerDistribution voltage
        changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    def resetData(self) -> None:
        """
        Reset all PowerDistribution simulation data.
        """
    def setAllCurrents(self, currents: typing.SupportsFloat, length: typing.SupportsInt) -> None:
        """
        Change the current in all of the PowerDistribution channels.
        
        :param currents: array containing the current values for each channel. The
                         array must be big enough to hold all the PowerDistribution
                         channels
        :param length:   length of array
        """
    def setCurrent(self, channel: typing.SupportsInt, current: typing.SupportsFloat) -> None:
        """
        Change the current in the given channel.
        
        :param channel: the channel to edit
        :param current: the new current for the channel
        """
    def setInitialized(self, initialized: bool) -> None:
        """
        Define whether the PowerDistribution has been initialized.
        
        :param initialized: whether this object is initialized
        """
    def setTemperature(self, temperature: typing.SupportsFloat) -> None:
        """
        Define the PowerDistribution temperature.
        
        :param temperature: the new PowerDistribution temperature
        """
    def setVoltage(self, voltage: typing.SupportsFloat) -> None:
        """
        Set the PowerDistribution voltage.
        
        :param voltage: the new PowerDistribution voltage
        """
class REVPHSim(PneumaticsBaseSim):
    """
    Class to control a simulated Pneumatic Control Module (PCM).
    """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs with the default PCM module number (CAN ID).
        """
    @typing.overload
    def __init__(self, module: typing.SupportsInt) -> None:
        """
        Constructs from a PCM module number (CAN ID).
        
        :param module: module number
        """
    @typing.overload
    def __init__(self, pneumatics: wpilib._wpilib.PneumaticsBase) -> None:
        ...
    def getAllSolenoidOutputs(self) -> int:
        ...
    def getCompressorConfigType(self) -> int:
        """
        Check whether the closed loop compressor control is active.
        
        :returns: compressor config type
        """
    def getCompressorCurrent(self) -> float:
        ...
    def getCompressorOn(self) -> bool:
        """
        Check if the compressor is on.
        
        :returns: true if the compressor is active
        """
    def getInitialized(self) -> bool:
        ...
    def getPressureSwitch(self) -> bool:
        ...
    def getSolenoidOutput(self, channel: typing.SupportsInt) -> bool:
        ...
    def registerCompressorConfigTypeCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the closed loop state changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    def registerCompressorCurrentCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerCompressorOnCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerInitializedCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerPressureSwitchCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def registerSolenoidOutputCallback(self, channel: typing.SupportsInt, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        ...
    def resetData(self) -> None:
        ...
    def setAllSolenoidOutputs(self, outputs: typing.SupportsInt) -> None:
        ...
    def setCompressorConfigType(self, compressorConfigType: typing.SupportsInt) -> None:
        """
        Turn on/off the closed loop control of the compressor.
        
        :param compressorConfigType: compressor config type
        """
    def setCompressorCurrent(self, compressorCurrent: typing.SupportsFloat) -> None:
        ...
    def setCompressorOn(self, compressorOn: bool) -> None:
        """
        Set whether the compressor is active.
        
        :param compressorOn: the new value
        """
    def setInitialized(self, solenoidInitialized: bool) -> None:
        ...
    def setPressureSwitch(self, pressureSwitch: bool) -> None:
        ...
    def setSolenoidOutput(self, channel: typing.SupportsInt, solenoidOutput: bool) -> None:
        ...
class RoboRioSim:
    """
    A utility class to control a simulated RoboRIO.
    """
    @staticmethod
    def getBrownoutVoltage() -> wpimath.units.volts:
        """
        Measure the brownout voltage.
        
        :returns: the brownout voltage
        """
    @staticmethod
    def getCPUTemp() -> wpimath.units.celsius:
        """
        Get the cpu temp.
        
        :returns: the cpu temp.
        """
    @staticmethod
    def getComments() -> str:
        """
        Get the comments.
        
        :returns: The comments.
        """
    @staticmethod
    def getSerialNumber() -> str:
        """
        Get the serial number.
        
        :returns: The serial number.
        """
    @staticmethod
    def getTeamNumber() -> int:
        """
        Get the team number.
        
        :returns: the team number.
        """
    @staticmethod
    def getUserActive3V3() -> bool:
        """
        Get the 3.3V rail active state.
        
        :returns: true if the 3.3V rail is active
        """
    @staticmethod
    def getUserCurrent3V3() -> wpimath.units.amperes:
        """
        Measure the 3.3V rail current.
        
        :returns: the 3.3V rail current
        """
    @staticmethod
    def getUserFaults3V3() -> int:
        """
        Get the 3.3V rail number of faults.
        
        :returns: number of faults
        """
    @staticmethod
    def getUserVoltage3V3() -> wpimath.units.volts:
        """
        Measure the 3.3V rail voltage.
        
        :returns: the 3.3V rail voltage
        """
    @staticmethod
    def getVInVoltage() -> wpimath.units.volts:
        """
        Measure the Vin voltage.
        
        :returns: the Vin voltage
        """
    @staticmethod
    def registerBrownoutVoltageCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the brownout voltage changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerCPUTempCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the cpu temp changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerTeamNumberCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the team number changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerUserActive3V3Callback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the 3.3V rail active state changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerUserCurrent3V3Callback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the 3.3V rail current changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerUserFaults3V3Callback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the 3.3V rail number of faults
        changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerUserVoltage3V3Callback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the 3.3V rail voltage changes.
        
        :param callback:      the callback
        :param initialNotify: whether the callback should be called with the
                              initial value
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def registerVInVoltageCallback(callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run whenever the Vin voltage changes.
        
        :param callback:      the callback
        :param initialNotify: whether to call the callback with the initial state
        
        :returns: the CallbackStore object associated with this callback
        """
    @staticmethod
    def resetData() -> None:
        """
        Reset all simulation data.
        """
    @staticmethod
    def setBrownoutVoltage(brownoutVoltage: wpimath.units.volts) -> None:
        """
        Define the brownout voltage.
        
        :param brownoutVoltage: the new voltage
        """
    @staticmethod
    def setCPUTemp(cpuTemp: wpimath.units.celsius) -> None:
        """
        Define the cpu temp.
        
        :param cpuTemp: the new cpu temp.
        """
    @staticmethod
    def setComments(comments: str) -> None:
        """
        Set the comments.
        
        :param comments: The comments.
        """
    @staticmethod
    def setSerialNumber(serialNumber: str) -> None:
        """
        Set the serial number.
        
        :param serialNumber: The serial number.
        """
    @staticmethod
    def setTeamNumber(teamNumber: typing.SupportsInt) -> None:
        """
        Set the team number.
        
        :param teamNumber: the new team number.
        """
    @staticmethod
    def setUserActive3V3(userActive3V3: bool) -> None:
        """
        Set the 3.3V rail active state.
        
        :param userActive3V3: true to make rail active
        """
    @staticmethod
    def setUserCurrent3V3(userCurrent3V3: wpimath.units.amperes) -> None:
        """
        Define the 3.3V rail current.
        
        :param userCurrent3V3: the new current
        """
    @staticmethod
    def setUserFaults3V3(userFaults3V3: typing.SupportsInt) -> None:
        """
        Set the 3.3V rail number of faults.
        
        :param userFaults3V3: number of faults
        """
    @staticmethod
    def setUserVoltage3V3(userVoltage3V3: wpimath.units.volts) -> None:
        """
        Define the 3.3V rail voltage.
        
        :param userVoltage3V3: the new voltage
        """
    @staticmethod
    def setVInVoltage(vInVoltage: wpimath.units.volts) -> None:
        """
        Define the Vin voltage.
        
        :param vInVoltage: the new voltage
        """
    def __init__(self) -> None:
        ...
class SendableChooserSim:
    """
    Class that facilitates control of a SendableChooser's selected option in
    simulation.
    """
    @typing.overload
    def __init__(self, path: str) -> None:
        """
        Constructs a SendableChooserSim.
        
        :param path: The path where the SendableChooser is published.
        """
    @typing.overload
    def __init__(self, inst: ntcore._ntcore.NetworkTableInstance, path: str) -> None:
        """
        Constructs a SendableChooserSim.
        
        :param inst: The NetworkTables instance.
        :param path: The path where the SendableChooser is published.
        """
    def setSelected(self, option: str) -> None:
        """
        Set the selected option.
        
        :param option: The option.
        """
class ServoSim:
    @typing.overload
    def __init__(self, servo: wpilib._wpilib.Servo) -> None:
        ...
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        ...
    def getAngle(self) -> float:
        ...
    def getPosition(self) -> float:
        ...
class SharpIRSim:
    """
    Simulation class for Sharp IR sensors.
    """
    @typing.overload
    def __init__(self, sharpIR: wpilib._wpilib.SharpIR) -> None:
        """
        Constructor.
        
        :param sharpIR: The real sensor to simulate
        """
    @typing.overload
    def __init__(self, channel: typing.SupportsInt) -> None:
        """
        Constructor.
        
        :param channel: Analog channel for this sensor
        """
    def setRange(self, range: wpimath.units.meters) -> None:
        """
        Set the range returned by the distance sensor.
        
        :param range: range of the target returned by the sensor
        """
class SimDeviceSim:
    """
    Interact with a generic simulated device
    
    Any devices that support simulation but don't have a dedicated sim
    object associated with it can be interacted with via this object.
    You just need to know the name of the associated object.
    
    Here are two ways to find the names of available devices:
    
    * The static function :meth:`.enumerateDevices` can give you a list of
      all available devices -- note that the device must be created first
      before this will return any results!
    * When running the WPILib simulation GUI, the names of the 'Other Devices'
      panel are names of devices that you can interact with via this class.
    
    Once you've created a simulated device, you can use the :meth:`.enumerateValues`
    method to determine what values you can interact with.
    
    
    .. note:: WPILib has simulation support for all of its devices. Some
              vendors may only have limited support for simulation -- read
              the vendor's documentation or contact them for more information.
    """
    @staticmethod
    def enumerateDevices(prefix: str = '') -> list[str]:
        """
        Returns a list of available device names
        """
    @staticmethod
    def getEnumOptions(val: hal._wpiHal.SimEnum) -> list[str]:
        """
        Get all options for the given enum.
        
        :param val: the enum
        
        :returns: names of the different values for that enum
        """
    @staticmethod
    def resetData() -> None:
        """
        Reset all SimDevice data.
        """
    @typing.overload
    def __init__(self, name: str) -> None:
        """
        Constructs a SimDeviceSim.
        
        :param name: name of the SimDevice
        """
    @typing.overload
    def __init__(self, name: str, index: typing.SupportsInt) -> None:
        """
        Constructs a SimDeviceSim.
        
        :param name:  name of the SimDevice
        :param index: device index number to append to name
        """
    @typing.overload
    def __init__(self, name: str, index: typing.SupportsInt, channel: typing.SupportsInt) -> None:
        """
        Constructs a SimDeviceSim.
        
        :param name:    name of the SimDevice
        :param index:   device index number to append to name
        :param channel: device channel number to append to name
        """
    @typing.overload
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Constructs a SimDeviceSim.
        
        :param handle: the low level handle for the corresponding SimDevice.
        """
    def enumerateValues(self) -> list[tuple[str, bool]]:
        """
        Returns a list of (name, readonly) tuples of available values for this device
        """
    def getBoolean(self, name: str) -> hal._wpiHal.SimBoolean:
        """
        Retrieves an object that allows you to interact with simulated values
        represented as a boolean.
        """
    def getDouble(self, name: str) -> hal._wpiHal.SimDouble:
        """
        Retrieves an object that allows you to interact with simulated values
        represented as a double.
        """
    def getEnum(self, name: str) -> hal._wpiHal.SimEnum:
        """
        Get the property object with the given name.
        
        :param name: the property name
        
        :returns: the property object
        """
    def getInt(self, name: str) -> hal._wpiHal.SimInt:
        """
        Retrieves an object that allows you to interact with simulated values
        represented as an integer.
        """
    def getLong(self, name: str) -> hal._wpiHal.SimLong:
        """
        Retrieves an object that allows you to interact with simulated values
        represented as a long.
        """
    def getName(self) -> str:
        """
        Get the name of this object.
        
        :returns: name
        """
    def getValue(self, name: str) -> hal._wpiHal.SimValue:
        """
        Provides a readonly mechanism to retrieve all types of device values
        """
class SingleJointedArmSim(LinearSystemSim_2_1_2):
    """
    Represents a simulated arm mechanism.
    """
    @staticmethod
    def estimateMOI(length: wpimath.units.meters, mass: wpimath.units.kilograms) -> wpimath.units.kilogram_square_meters:
        """
        Calculates a rough estimate of the moment of inertia of an arm given its
        length and mass.
        
        :param length: The length of the arm.
        :param mass:   The mass of the arm.
        
        :returns: The calculated moment of inertia.
        """
    @typing.overload
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_1_2, gearbox: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, armLength: wpimath.units.meters, minAngle: wpimath.units.radians, maxAngle: wpimath.units.radians, simulateGravity: bool, startingAngle: wpimath.units.radians, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated arm mechanism.
        
        :param system:             The system representing this arm. This system can
                                   be created with
                                   LinearSystemId::SingleJointedArmSystem().
        :param gearbox:            The type and number of motors on the arm gearbox.
        :param gearing:            The gear ratio of the arm (numbers greater than 1
                                   represent reductions).
        :param armLength:          The length of the arm.
        :param minAngle:           The minimum angle that the arm is capable of.
        :param maxAngle:           The maximum angle that the arm is capable of.
        :param simulateGravity:    Whether gravity should be simulated or not.
        :param startingAngle:      The initial position of the arm.
        :param measurementStdDevs: The standard deviations of the measurements.
        """
    @typing.overload
    def __init__(self, gearbox: wpimath._controls._controls.plant.DCMotor, gearing: typing.SupportsFloat, moi: wpimath.units.kilogram_square_meters, armLength: wpimath.units.meters, minAngle: wpimath.units.radians, maxAngle: wpimath.units.radians, simulateGravity: bool, startingAngle: wpimath.units.radians, measurementStdDevs: typing.Annotated[list[typing.SupportsFloat], pybind11_stubgen.typing_ext.FixedSize(2)] = [0.0, 0.0]) -> None:
        """
        Creates a simulated arm mechanism.
        
        :param gearbox:            The type and number of motors on the arm gearbox.
        :param gearing:            The gear ratio of the arm (numbers greater than 1
                                   represent reductions).
        :param moi:                The moment of inertia of the arm. This can be
                                   calculated from CAD software.
        :param armLength:          The length of the arm.
        :param minAngle:           The minimum angle that the arm is capable of.
        :param maxAngle:           The maximum angle that the arm is capable of.
        :param simulateGravity:    Whether gravity should be simulated or not.
        :param startingAngle:      The initial position of the arm.
        :param measurementStdDevs: The standard deviation of the measurement noise.
        """
    def _updateX(self, currentXhat: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Updates the state estimate of the arm.
        
        :param currentXhat: The current state estimate.
        :param u:           The system inputs (voltage).
        :param dt:          The time difference between controller updates.
        """
    def getAngle(self) -> wpimath.units.radians:
        """
        Returns the current arm angle.
        
        :returns: The current arm angle.
        """
    def getAngleDegrees(self) -> wpimath.units.degrees:
        ...
    def getCurrentDraw(self) -> wpimath.units.amperes:
        """
        Returns the arm current draw.
        
        :returns: The arm current draw.
        """
    def getVelocity(self) -> wpimath.units.radians_per_second:
        """
        Returns the current arm velocity.
        
        :returns: The current arm velocity.
        """
    def getVelocityDps(self) -> wpimath.units.degrees_per_second:
        ...
    def hasHitLowerLimit(self) -> bool:
        """
        Returns whether the arm has hit the lower limit.
        
        :returns: Whether the arm has hit the lower limit.
        """
    def hasHitUpperLimit(self) -> bool:
        """
        Returns whether the arm has hit the upper limit.
        
        :returns: Whether the arm has hit the upper limit.
        """
    def setInputVoltage(self, voltage: wpimath.units.volts) -> None:
        """
        Sets the input voltage for the arm.
        
        :param voltage: The input voltage.
        """
    def setState(self, angle: wpimath.units.radians, velocity: wpimath.units.radians_per_second) -> None:
        """
        Sets the arm's state. The new angle will be limited between the minimum and
        maximum allowed limits.
        
        :param angle:    The new angle.
        :param velocity: The new angular velocity.
        """
    def wouldHitLowerLimit(self, armAngle: wpimath.units.radians) -> bool:
        """
        Returns whether the arm would hit the lower limit.
        
        :param armAngle: The arm height.
        
        :returns: Whether the arm would hit the lower limit.
        """
    def wouldHitUpperLimit(self, armAngle: wpimath.units.radians) -> bool:
        """
        Returns whether the arm would hit the upper limit.
        
        :param armAngle: The arm height.
        
        :returns: Whether the arm would hit the upper limit.
        """
class SolenoidSim:
    @typing.overload
    def __init__(self, moduleSim: PneumaticsBaseSim, channel: typing.SupportsInt) -> None:
        ...
    @typing.overload
    def __init__(self, module: typing.SupportsInt, type: wpilib._wpilib.PneumaticsModuleType, channel: typing.SupportsInt) -> None:
        ...
    @typing.overload
    def __init__(self, type: wpilib._wpilib.PneumaticsModuleType, channel: typing.SupportsInt) -> None:
        ...
    def getModuleSim(self) -> PneumaticsBaseSim:
        ...
    def getOutput(self) -> bool:
        ...
    def registerOutputCallback(self, callback: typing.Callable[[str, hal._wpiHal.Value], None], initialNotify: bool) -> CallbackStore:
        """
        Register a callback to be run when the output of this solenoid has changed.
        
        :param callback:      the callback
        :param initialNotify: whether to run the callback with the initial state
        
        :returns: the :class:`.CallbackStore` object associated with this callback.
                  Save a reference to this object; it being deconstructed cancels the
                  callback.
        """
    def setOutput(self, output: bool) -> None:
        ...
class StadiaControllerSim(GenericHIDSim):
    """
    Class to control a simulated Stadia controller.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.StadiaController) -> None:
        """
        Constructs from a StadiaController object.
        
        :param joystick: controller to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def setAButton(self, value: bool) -> None:
        """
        Change the value of the A button on the controller.
        
        :param value: the new value
        """
    def setBButton(self, value: bool) -> None:
        """
        Change the value of the B button on the controller.
        
        :param value: the new value
        """
    def setEllipsesButton(self, value: bool) -> None:
        """
        Change the value of the ellipses button on the controller.
        
        :param value: the new value
        """
    def setFrameButton(self, value: bool) -> None:
        """
        Change the value of the frame button on the controller.
        
        :param value: the new value
        """
    def setGoogleButton(self, value: bool) -> None:
        """
        Change the value of the google button on the controller.
        
        :param value: the new value
        """
    def setHamburgerButton(self, value: bool) -> None:
        """
        Change the value of the hamburger button on the controller.
        
        :param value: the new value
        """
    def setLeftBumperButton(self, value: bool) -> None:
        """
        Change the value of the left bumper button on the controller.
        
        :param value: the new value
        """
    def setLeftStickButton(self, value: bool) -> None:
        """
        Change the value of the left stick button on the controller.
        
        :param value: the new value
        """
    def setLeftTriggerButton(self, value: bool) -> None:
        """
        Change the value of the left trigger button on the controller.
        
        :param value: the new value
        """
    def setLeftX(self, value: typing.SupportsFloat) -> None:
        """
        Change the left X value of the controller's joystick.
        
        :param value: the new value
        """
    def setLeftY(self, value: typing.SupportsFloat) -> None:
        """
        Change the left Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightBumperButton(self, value: bool) -> None:
        """
        Change the value of the right bumper button on the controller.
        
        :param value: the new value
        """
    def setRightStickButton(self, value: bool) -> None:
        """
        Change the value of the right stick button on the controller.
        
        :param value: the new value
        """
    def setRightTriggerButton(self, value: bool) -> None:
        """
        Change the value of the right trigger button on the controller.
        
        :param value: the new value
        """
    def setRightX(self, value: typing.SupportsFloat) -> None:
        """
        Change the right X value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightY(self, value: typing.SupportsFloat) -> None:
        """
        Change the right Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setStadiaButton(self, value: bool) -> None:
        """
        Change the value of the stadia button on the controller.
        
        :param value: the new value
        """
    def setXButton(self, value: bool) -> None:
        """
        Change the value of the X button on the controller.
        
        :param value: the new value
        """
    def setYButton(self, value: bool) -> None:
        """
        Change the value of the Y button on the controller.
        
        :param value: the new value
        """
class XboxControllerSim(GenericHIDSim):
    """
    Class to control a simulated Xbox controller.
    """
    @typing.overload
    def __init__(self, joystick: wpilib._wpilib.XboxController) -> None:
        """
        Constructs from a XboxController object.
        
        :param joystick: controller to simulate
        """
    @typing.overload
    def __init__(self, port: typing.SupportsInt) -> None:
        """
        Constructs from a joystick port number.
        
        :param port: port number
        """
    def setAButton(self, value: bool) -> None:
        """
        Change the value of the A button on the controller.
        
        :param value: the new value
        """
    def setBButton(self, value: bool) -> None:
        """
        Change the value of the B button on the controller.
        
        :param value: the new value
        """
    def setBackButton(self, value: bool) -> None:
        """
        Change the value of the back button on the controller.
        
        :param value: the new value
        """
    def setLeftBumperButton(self, value: bool) -> None:
        """
        Change the value of the left bumper button on the controller.
        
        :param value: the new value
        """
    def setLeftStickButton(self, value: bool) -> None:
        """
        Change the value of the left stick button on the controller.
        
        :param value: the new value
        """
    def setLeftTriggerAxis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the left trigger axis on the controller.
        
        :param value: the new value
        """
    def setLeftX(self, value: typing.SupportsFloat) -> None:
        """
        Change the left X value of the controller's joystick.
        
        :param value: the new value
        """
    def setLeftY(self, value: typing.SupportsFloat) -> None:
        """
        Change the left Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightBumperButton(self, value: bool) -> None:
        """
        Change the value of the right bumper button on the controller.
        
        :param value: the new value
        """
    def setRightStickButton(self, value: bool) -> None:
        """
        Change the value of the right stick button on the controller.
        
        :param value: the new value
        """
    def setRightTriggerAxis(self, value: typing.SupportsFloat) -> None:
        """
        Change the value of the right trigger axis on the controller.
        
        :param value: the new value
        """
    def setRightX(self, value: typing.SupportsFloat) -> None:
        """
        Change the right X value of the controller's joystick.
        
        :param value: the new value
        """
    def setRightY(self, value: typing.SupportsFloat) -> None:
        """
        Change the right Y value of the controller's joystick.
        
        :param value: the new value
        """
    def setStartButton(self, value: bool) -> None:
        """
        Change the value of the start button on the controller.
        
        :param value: the new value
        """
    def setXButton(self, value: bool) -> None:
        """
        Change the value of the X button on the controller.
        
        :param value: the new value
        """
    def setYButton(self, value: bool) -> None:
        """
        Change the value of the Y button on the controller.
        
        :param value: the new value
        """
def _resetMotorSafety() -> None:
    ...
def _resetWpilibSimulationData() -> None:
    ...
def getProgramStarted() -> bool:
    ...
def isTimingPaused() -> bool:
    """
    Check if the simulator time is paused.
    
    :returns: true if paused
    """
def pauseTiming() -> None:
    """
    Pause the simulator time.
    """
def restartTiming() -> None:
    """
    Restart the simulator time.
    """
def resumeTiming() -> None:
    """
    Resume the simulator time.
    """
def setProgramStarted() -> None:
    ...
def setRuntimeType(type: hal._wpiHal.RuntimeType) -> None:
    """
    Override the HAL runtime type (simulated/real).
    
    :param type: runtime type
    """
def stepTiming(delta: wpimath.units.seconds) -> None:
    """
    Advance the simulator time and wait for all notifiers to run.
    
    :param delta: the amount to advance (in seconds)
    """
def stepTimingAsync(delta: wpimath.units.seconds) -> None:
    """
    Advance the simulator time and return immediately.
    
    :param delta: the amount to advance (in seconds)
    """
def waitForProgramStart() -> None:
    ...
