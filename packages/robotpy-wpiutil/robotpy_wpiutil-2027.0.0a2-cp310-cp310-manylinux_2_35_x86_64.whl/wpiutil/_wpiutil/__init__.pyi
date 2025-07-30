from __future__ import annotations
import typing
import typing_extensions
from . import sync
from . import wpistruct
__all__ = ['Sendable', 'SendableBuilder', 'SendableRegistry', 'TimestampSource', 'getStackTrace', 'getStackTraceDefault', 'sync', 'wpistruct']
class Sendable:
    """
    Interface for Sendable objects.
    """
    def __init__(self) -> None:
        ...
    def initSendable(self, builder: SendableBuilder) -> None:
        """
        Initializes this Sendable object.
        
        :param builder: sendable builder
        """
class SendableBuilder:
    """
    Helper class for building Sendable dashboard representations.
    """
    class BackendKind:
        """
        The backend kinds used for the sendable builder.
        
        Members:
        
          kUnknown : Unknown.
        
          kNetworkTables : NetworkTables.
        """
        __members__: typing.ClassVar[dict[str, SendableBuilder.BackendKind]]  # value = {'kUnknown': <BackendKind.kUnknown: 0>, 'kNetworkTables': <BackendKind.kNetworkTables: 1>}
        kNetworkTables: typing.ClassVar[SendableBuilder.BackendKind]  # value = <BackendKind.kNetworkTables: 1>
        kUnknown: typing.ClassVar[SendableBuilder.BackendKind]  # value = <BackendKind.kUnknown: 0>
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
    def __init__(self) -> None:
        ...
    def addBooleanArrayProperty(self, key: str, getter: typing.Callable[[], list[int]], setter: typing.Callable[[list[typing.SupportsInt]], None]) -> None:
        """
        Add a boolean array property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addBooleanProperty(self, key: str, getter: typing.Callable[[], bool], setter: typing.Callable[[bool], None]) -> None:
        """
        Add a boolean property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addDoubleArrayProperty(self, key: str, getter: typing.Callable[[], list[float]], setter: typing.Callable[[list[typing.SupportsFloat]], None]) -> None:
        """
        Add a double array property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addDoubleProperty(self, key: str, getter: typing.Callable[[], float], setter: typing.Callable[[typing.SupportsFloat], None]) -> None:
        """
        Add a double property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addFloatArrayProperty(self, key: str, getter: typing.Callable[[], list[float]], setter: typing.Callable[[list[typing.SupportsFloat]], None]) -> None:
        """
        Add a float array property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addFloatProperty(self, key: str, getter: typing.Callable[[], float], setter: typing.Callable[[typing.SupportsFloat], None]) -> None:
        """
        Add a float property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addIntegerArrayProperty(self, key: str, getter: typing.Callable[[], list[int]], setter: typing.Callable[[list[typing.SupportsInt]], None]) -> None:
        """
        Add an integer array property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addIntegerProperty(self, key: str, getter: typing.Callable[[], int], setter: typing.Callable[[typing.SupportsInt], None]) -> None:
        """
        Add an integer property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addRawProperty(self, key: str, typeString: str, getter: typing.Callable[[], list[int]], setter: typing.Callable[[typing_extensions.Buffer], None]) -> None:
        """
        Add a raw property.
        
        :param key:        property name
        :param typeString: type string
        :param getter:     getter function (returns current value)
        :param setter:     setter function (sets new value)
        """
    def addSmallBooleanArrayProperty(self, key: str, getter: typing.Callable[[list[typing.SupportsInt]], list[int]], setter: typing.Callable[[list[typing.SupportsInt]], None]) -> None:
        """
        Add a boolean array property (SmallVector form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addSmallDoubleArrayProperty(self, key: str, getter: typing.Callable[[list[typing.SupportsFloat]], list[float]], setter: typing.Callable[[list[typing.SupportsFloat]], None]) -> None:
        """
        Add a double array property (SmallVector form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addSmallFloatArrayProperty(self, key: str, getter: typing.Callable[[list[typing.SupportsFloat]], list[float]], setter: typing.Callable[[list[typing.SupportsFloat]], None]) -> None:
        """
        Add a float array property (SmallVector form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addSmallIntegerArrayProperty(self, key: str, getter: typing.Callable[[list[typing.SupportsInt]], list[int]], setter: typing.Callable[[list[typing.SupportsInt]], None]) -> None:
        """
        Add an integer array property (SmallVector form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addSmallRawProperty(self, key: str, typeString: str, getter: typing.Callable[[list[typing.SupportsInt]], typing_extensions.Buffer], setter: typing.Callable[[typing_extensions.Buffer], None]) -> None:
        """
        Add a raw property (SmallVector form).
        
        :param key:        property name
        :param typeString: type string
        :param getter:     getter function (returns current value)
        :param setter:     setter function (sets new value)
        """
    def addSmallStringArrayProperty(self, key: str, getter: typing.Callable[[list[str]], list[str]], setter: typing.Callable[[list[str]], None]) -> None:
        """
        Add a string array property (SmallVector form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addSmallStringProperty(self, key: str, getter: typing.Callable[[list[str]], str], setter: typing.Callable[[str], None]) -> None:
        """
        Add a string property (SmallString form).
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addStringArrayProperty(self, key: str, getter: typing.Callable[[], list[str]], setter: typing.Callable[[list[str]], None]) -> None:
        """
        Add a string array property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def addStringProperty(self, key: str, getter: typing.Callable[[], str], setter: typing.Callable[[str], None]) -> None:
        """
        Add a string property.
        
        :param key:    property name
        :param getter: getter function (returns current value)
        :param setter: setter function (sets new value)
        """
    def clearProperties(self) -> None:
        """
        Clear properties.
        """
    def getBackendKind(self) -> SendableBuilder.BackendKind:
        """
        Gets the kind of backend being used.
        
        :returns: Backend kind
        """
    def isPublished(self) -> bool:
        """
        Return whether this sendable has been published.
        
        :returns: True if it has been published, false if not.
        """
    def publishConstBoolean(self, key: str, value: bool) -> None:
        """
        Add a constant boolean property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstBooleanArray(self, key: str, value: list[typing.SupportsInt]) -> None:
        """
        Add a constant boolean array property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstDouble(self, key: str, value: typing.SupportsFloat) -> None:
        """
        Add a constant double property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstDoubleArray(self, key: str, value: list[typing.SupportsFloat]) -> None:
        """
        Add a constant double array property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstFloat(self, key: str, value: typing.SupportsFloat) -> None:
        """
        Add a constant float property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstFloatArray(self, key: str, value: list[typing.SupportsFloat]) -> None:
        """
        Add a constant float array property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstInteger(self, key: str, value: typing.SupportsInt) -> None:
        """
        Add a constant integer property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstIntegerArray(self, key: str, value: list[typing.SupportsInt]) -> None:
        """
        Add a constant integer array property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstRaw(self, key: str, typeString: str, value: typing_extensions.Buffer) -> None:
        """
        Add a constant raw property.
        
        :param key:        property name
        :param typeString: type string
        :param value:      the value
        """
    def publishConstString(self, key: str, value: str) -> None:
        """
        Add a constant string property.
        
        :param key:   property name
        :param value: the value
        """
    def publishConstStringArray(self, key: str, value: list[str]) -> None:
        """
        Add a constant string array property.
        
        :param key:   property name
        :param value: the value
        """
    def setActuator(self, value: bool) -> None:
        """
        Set a flag indicating if this sendable should be treated as an actuator.
        By default this flag is false.
        
        :param value: true if actuator, false if not
        """
    def setSmartDashboardType(self, type: str) -> None:
        """
        Set the string representation of the named data type that will be used
        by the smart dashboard for this sendable.
        
        :param type: data type
        """
    def update(self) -> None:
        """
        Update the published values by calling the getters for all properties.
        """
class SendableRegistry:
    """
    The SendableRegistry class is the public interface for registering sensors
    and actuators for use on dashboards.
    """
    @staticmethod
    @typing.overload
    def add(sendable: Sendable, name: str) -> None:
        """
        Adds an object to the registry.
        
        :param sendable: object to add
        :param name:     component name
        """
    @staticmethod
    @typing.overload
    def add(sendable: Sendable, moduleType: str, channel: typing.SupportsInt) -> None:
        """
        Adds an object to the registry.
        
        :param sendable:   object to add
        :param moduleType: A string that defines the module name in the label for
                           the value
        :param channel:    The channel number the device is plugged into
        """
    @staticmethod
    @typing.overload
    def add(sendable: Sendable, moduleType: str, moduleNumber: typing.SupportsInt, channel: typing.SupportsInt) -> None:
        """
        Adds an object to the registry.
        
        :param sendable:     object to add
        :param moduleType:   A string that defines the module name in the label for
                             the value
        :param moduleNumber: The number of the particular module type
        :param channel:      The channel number the device is plugged into
        """
    @staticmethod
    @typing.overload
    def add(sendable: Sendable, subsystem: str, name: str) -> None:
        """
        Adds an object to the registry.
        
        :param sendable:  object to add
        :param subsystem: subsystem name
        :param name:      component name
        """
    @staticmethod
    def addChild(parent: Sendable, child: Sendable) -> None:
        """
        Adds a child object to an object.  Adds the child object to the registry
        if it's not already present.
        
        :param parent: parent object
        :param child:  child object
        """
    @staticmethod
    def contains(sendable: Sendable) -> bool:
        """
        Determines if an object is in the registry.
        
        :param sendable: object to check
        
        :returns: True if in registry, false if not.
        """
    @staticmethod
    def ensureInitialized() -> None:
        """
        Initializes the SendableRegistry. This is used to ensure initialization and
        destruction order relative to Sendables.
        """
    @staticmethod
    def getName(sendable: Sendable) -> str:
        """
        Gets the name of an object.
        
        :param sendable: object
        
        :returns: Name (empty if object is not in registry)
        """
    @staticmethod
    def getSendable(uid: typing.SupportsInt) -> Sendable:
        """
        Get sendable object for a given unique id.
        
        :param uid: unique id
        
        :returns: sendable object (may be null)
        """
    @staticmethod
    def getSubsystem(sendable: Sendable) -> str:
        """
        Gets the subsystem name of an object.
        
        :param sendable: object
        
        :returns: Subsystem name (empty if object is not in registry)
        """
    @staticmethod
    def getUniqueId(sendable: Sendable) -> int:
        """
        Get unique id for an object.  Since objects can move, use this instead
        of storing Sendable* directly if ownership is in question.
        
        :param sendable: object
        
        :returns: unique id
        """
    @staticmethod
    def publish(sendableUid: typing.SupportsInt, builder: SendableBuilder) -> None:
        """
        Publishes an object in the registry.
        
        :param sendableUid: sendable unique id
        :param builder:     publisher backend
        """
    @staticmethod
    def remove(sendable: Sendable) -> bool:
        """
        Removes an object from the registry.
        
        :param sendable: object to remove
        
        :returns: true if the object was removed; false if it was not present
        """
    @staticmethod
    @typing.overload
    def setName(sendable: Sendable, name: str) -> None:
        """
        Sets the name of an object.
        
        :param sendable: object
        :param name:     name
        """
    @staticmethod
    @typing.overload
    def setName(sendable: Sendable, moduleType: str, channel: typing.SupportsInt) -> None:
        """
        Sets the name of an object with a channel number.
        
        :param sendable:   object
        :param moduleType: A string that defines the module name in the label for
                           the value
        :param channel:    The channel number the device is plugged into
        """
    @staticmethod
    @typing.overload
    def setName(sendable: Sendable, moduleType: str, moduleNumber: typing.SupportsInt, channel: typing.SupportsInt) -> None:
        """
        Sets the name of an object with a module and channel number.
        
        :param sendable:     object
        :param moduleType:   A string that defines the module name in the label for
                             the value
        :param moduleNumber: The number of the particular module type
        :param channel:      The channel number the device is plugged into
        """
    @staticmethod
    @typing.overload
    def setName(sendable: Sendable, subsystem: str, name: str) -> None:
        """
        Sets both the subsystem name and device name of an object.
        
        :param sendable:  object
        :param subsystem: subsystem name
        :param name:      device name
        """
    @staticmethod
    def setSubsystem(sendable: Sendable, subsystem: str) -> None:
        """
        Sets the subsystem name of an object.
        
        :param sendable:  object
        :param subsystem: subsystem name
        """
    @staticmethod
    def update(sendableUid: typing.SupportsInt) -> None:
        """
        Updates published information from an object.
        
        :param sendableUid: sendable unique id
        """
class TimestampSource:
    """
    Timestamp metadata. Timebase is the same as wpi::Now
    
    Members:
    
      UNKNOWN
    
      FRAME_DEQUEUE
    
      V4L_EOF
    
      V4L_SOE
    """
    FRAME_DEQUEUE: typing.ClassVar[TimestampSource]  # value = <TimestampSource.FRAME_DEQUEUE: 1>
    UNKNOWN: typing.ClassVar[TimestampSource]  # value = <TimestampSource.UNKNOWN: 0>
    V4L_EOF: typing.ClassVar[TimestampSource]  # value = <TimestampSource.V4L_EOF: 2>
    V4L_SOE: typing.ClassVar[TimestampSource]  # value = <TimestampSource.V4L_SOE: 3>
    __members__: typing.ClassVar[dict[str, TimestampSource]]  # value = {'UNKNOWN': <TimestampSource.UNKNOWN: 0>, 'FRAME_DEQUEUE': <TimestampSource.FRAME_DEQUEUE: 1>, 'V4L_EOF': <TimestampSource.V4L_EOF: 2>, 'V4L_SOE': <TimestampSource.V4L_SOE: 3>}
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
def _setup_stack_trace_hook(arg0: typing.Any) -> None:
    ...
def getStackTrace(offset: typing.SupportsInt) -> str:
    """
    Get a stack trace, ignoring the first "offset" symbols.
    
    :param offset: The number of symbols at the top of the stack to ignore
    """
def getStackTraceDefault(offset: typing.SupportsInt) -> str:
    """
    The default implementation used for GetStackTrace().
    
    :param offset: The number of symbols at the top of the stack to ignore
    """
_st_cleanup: typing.Any  # value = <capsule object>
