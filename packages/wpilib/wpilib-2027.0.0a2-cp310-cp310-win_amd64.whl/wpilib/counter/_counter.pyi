from __future__ import annotations
import typing
import wpimath.units
import wpiutil._wpiutil
__all__ = ['EdgeConfiguration', 'Tachometer', 'UpDownCounter']
class EdgeConfiguration:
    """
    Edge configuration.
    
    Members:
    
      kRisingEdge : Rising edge configuration.
    
      kFallingEdge : Falling edge configuration.
    """
    __members__: typing.ClassVar[dict[str, EdgeConfiguration]]  # value = {'kRisingEdge': <EdgeConfiguration.kRisingEdge: 0>, 'kFallingEdge': <EdgeConfiguration.kFallingEdge: 1>}
    kFallingEdge: typing.ClassVar[EdgeConfiguration]  # value = <EdgeConfiguration.kFallingEdge: 1>
    kRisingEdge: typing.ClassVar[EdgeConfiguration]  # value = <EdgeConfiguration.kRisingEdge: 0>
    def __eq__(self, other: typing.Any) -> bool:
        ...
    def __getstate__(self) -> int:
        ...
    def __hash__(self) -> int:
        ...
    def __index__(self) -> int:
        ...
    def __init__(self, value: typing.SupportsInt) -> None:
        ...
    def __int__(self) -> int:
        ...
    def __ne__(self, other: typing.Any) -> bool:
        ...
    def __repr__(self) -> str:
        ...
    def __setstate__(self, state: typing.SupportsInt) -> None:
        ...
    def __str__(self) -> str:
        ...
    @property
    def name(self) -> str:
        ...
    @property
    def value(self) -> int:
        ...
class Tachometer(wpiutil._wpiutil.Sendable):
    """
    Tachometer for getting rotational speed from a device.
    
    The Tachometer class measures the time between digital pulses to
    determine the rotation speed of a mechanism. Examples of devices that could
    be used with the tachometer class are a hall effect sensor, break beam
    sensor, or optical sensor detecting tape on a shooter wheel. Unlike
    encoders, this class only needs a single digital input.
    """
    def __init__(self, channel: typing.SupportsInt, configuration: EdgeConfiguration) -> None:
        """
        Constructs a new tachometer.
        
        :param channel:       The DIO Channel.
        :param configuration: Edge configuration
        """
    def _initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    def getEdgesPerRevolution(self) -> int:
        """
        Gets the number of edges per revolution.
        
        :returns: Edges per revolution.
        """
    def getFrequency(self) -> wpimath.units.hertz:
        """
        Gets the tachometer frequency.
        
        :returns: Current frequency.
        """
    def getPeriod(self) -> wpimath.units.seconds:
        """
        Gets the tachometer period.
        
        :returns: Current period.
        """
    def getRevolutionsPerMinute(self) -> wpimath.units.revolutions_per_minute:
        """
        Gets the current tachometer revolutions per minute.
        
        SetEdgesPerRevolution must be set with a non 0 value for this to work.
        
        :returns: Current RPM.
        """
    def getRevolutionsPerSecond(self) -> wpimath.units.turns_per_second:
        """
        Gets the current tachometer revolutions per second.
        
        SetEdgesPerRevolution must be set with a non 0 value for this to work.
        
        :returns: Current RPS.
        """
    def getStopped(self) -> bool:
        """
        Gets if the tachometer is stopped.
        
        :returns: True if the tachometer is stopped.
        """
    def setEdgeConfiguration(self, configuration: EdgeConfiguration) -> None:
        """
        Sets the configuration for the channel.
        
        :param configuration: The channel configuration.
        """
    def setEdgesPerRevolution(self, edges: typing.SupportsInt) -> None:
        """
        Sets the number of edges per revolution.
        
        :param edges: Edges per revolution.
        """
    def setMaxPeriod(self, maxPeriod: wpimath.units.seconds) -> None:
        """
        Sets the maximum period before the tachometer is considered stopped.
        
        :param maxPeriod: The max period.
        """
class UpDownCounter(wpiutil._wpiutil.Sendable):
    """
    Up Down Counter.
    
    This class can count edges on a single digital input or count up based on an
    edge from one digital input and down on an edge from another digital input.
    """
    def __init__(self, channel: typing.SupportsInt, configuration: EdgeConfiguration) -> None:
        """
        Constructs a new UpDown Counter.
        
        :param channel:       The DIO channel
        :param configuration: Edge configuration
        """
    def _initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    def getCount(self) -> int:
        """
        Gets the current count.
        
        :returns: The current count.
        """
    def reset(self) -> None:
        """
        Resets the current count.
        """
    def setEdgeConfiguration(self, configuration: EdgeConfiguration) -> None:
        """
        Sets the configuration for the channel.
        
        :param configuration: The channel configuration.
        """
