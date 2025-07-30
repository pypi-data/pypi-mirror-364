from __future__ import annotations
import typing
import typing_extensions
__all__ = ['AddressableLEDColorOrder', 'AddressableLEDData', 'AllianceStationID', 'CANDeviceType', 'CANFlags', 'CANManufacturer', 'CANMessage', 'CANReceiveMessage', 'CANStreamMessage', 'CAN_CloseStreamSession', 'CAN_GetCANStatus', 'CAN_OpenStreamSession', 'CAN_ReceiveMessage', 'CAN_SendMessage', 'ControlWord', 'EncoderEncodingType', 'EncoderIndexingType', 'HandleEnum', 'I2CPort', 'JoystickAxes', 'JoystickButtons', 'JoystickDescriptor', 'JoystickPOV', 'JoystickPOVs', 'MatchInfo', 'MatchType', 'PowerDistributionFaults', 'PowerDistributionStickyFaults', 'PowerDistributionType', 'PowerDistributionVersion', 'REVPHCompressorConfig', 'REVPHCompressorConfigType', 'REVPHFaults', 'REVPHStickyFaults', 'REVPHVersion', 'RuntimeType', 'SerialPort', 'SimBoolean', 'SimDevice', 'SimDouble', 'SimEnum', 'SimInt', 'SimLong', 'SimValue', 'SimValueDirection', 'Type', 'Value', 'allocateDigitalPWM', 'cancelNotifierAlarm', 'checkAnalogInputChannel', 'checkAnalogModule', 'checkCTREPCMSolenoidChannel', 'checkDIOChannel', 'checkPWMChannel', 'checkPowerDistributionChannel', 'checkPowerDistributionModule', 'checkREVPHModuleNumber', 'checkREVPHSolenoidChannel', 'cleanCAN', 'cleanNotifier', 'cleanPowerDistribution', 'clearAllCTREPCMStickyFaults', 'clearPowerDistributionStickyFaults', 'clearREVPHStickyFaults', 'clearSerial', 'closeI2C', 'closeSerial', 'createHandle', 'disableSerialTermination', 'enableSerialTermination', 'exitMain', 'expandFPGATime', 'fireCTREPCMOneShot', 'fireREVPHOneShot', 'flushSerial', 'format_as', 'freeAddressableLED', 'freeAnalogInputPort', 'freeCTREPCM', 'freeCounter', 'freeDIOPort', 'freeDigitalPWM', 'freeDutyCycle', 'freeEncoder', 'freePWMPort', 'freeREVPH', 'getAllJoystickData', 'getAllianceStation', 'getAnalogAverageBits', 'getAnalogAverageValue', 'getAnalogAverageVoltage', 'getAnalogLSBWeight', 'getAnalogOffset', 'getAnalogOversampleBits', 'getAnalogSampleRate', 'getAnalogValue', 'getAnalogValueToVolts', 'getAnalogVoltage', 'getAnalogVoltsToValue', 'getBrownedOut', 'getBrownoutVoltage', 'getCPUTemp', 'getCTREPCMClosedLoopControl', 'getCTREPCMCompressor', 'getCTREPCMCompressorCurrent', 'getCTREPCMCompressorCurrentTooHighFault', 'getCTREPCMCompressorCurrentTooHighStickyFault', 'getCTREPCMCompressorNotConnectedFault', 'getCTREPCMCompressorNotConnectedStickyFault', 'getCTREPCMCompressorShortedFault', 'getCTREPCMCompressorShortedStickyFault', 'getCTREPCMPressureSwitch', 'getCTREPCMSolenoidDisabledList', 'getCTREPCMSolenoidVoltageFault', 'getCTREPCMSolenoidVoltageStickyFault', 'getCTREPCMSolenoids', 'getComments', 'getCommsDisableCount', 'getControlWord', 'getCounter', 'getCounterPeriod', 'getCounterStopped', 'getCurrentThreadPriority', 'getDIO', 'getDIODirection', 'getDutyCycleFrequency', 'getDutyCycleHighTime', 'getDutyCycleOutput', 'getEncoder', 'getEncoderDecodingScaleFactor', 'getEncoderDirection', 'getEncoderDistance', 'getEncoderDistancePerPulse', 'getEncoderEncodingScale', 'getEncoderEncodingType', 'getEncoderFPGAIndex', 'getEncoderPeriod', 'getEncoderRate', 'getEncoderRaw', 'getEncoderSamplesToAverage', 'getEncoderStopped', 'getErrorMessage', 'getFPGARevision', 'getFPGATime', 'getFPGAVersion', 'getHandleIndex', 'getHandleType', 'getHandleTypedIndex', 'getJoystickAxes', 'getJoystickAxisType', 'getJoystickButtons', 'getJoystickDescriptor', 'getJoystickIsGamepad', 'getJoystickName', 'getJoystickPOVs', 'getJoystickType', 'getLastError', 'getMatchInfo', 'getMatchTime', 'getNumAddressableLEDs', 'getNumAnalogInputs', 'getNumCTREPCMModules', 'getNumCTREPDPChannels', 'getNumCTREPDPModules', 'getNumCTRESolenoidChannels', 'getNumCanBuses', 'getNumCounters', 'getNumDigitalChannels', 'getNumDigitalPWMOutputs', 'getNumDutyCycles', 'getNumEncoders', 'getNumInterrupts', 'getNumPWMChannels', 'getNumREVPDHChannels', 'getNumREVPDHModules', 'getNumREVPHChannels', 'getNumREVPHModules', 'getOutputsEnabled', 'getPWMPulseTimeMicroseconds', 'getPowerDistributionAllChannelCurrents', 'getPowerDistributionChannelCurrent', 'getPowerDistributionFaults', 'getPowerDistributionModuleNumber', 'getPowerDistributionNumChannels', 'getPowerDistributionStickyFaults', 'getPowerDistributionSwitchableChannel', 'getPowerDistributionTemperature', 'getPowerDistributionTotalCurrent', 'getPowerDistributionTotalEnergy', 'getPowerDistributionTotalPower', 'getPowerDistributionType', 'getPowerDistributionVersion', 'getPowerDistributionVoltage', 'getREVPH5VVoltage', 'getREVPHAnalogVoltage', 'getREVPHCompressor', 'getREVPHCompressorConfig', 'getREVPHCompressorCurrent', 'getREVPHFaults', 'getREVPHPressureSwitch', 'getREVPHSolenoidCurrent', 'getREVPHSolenoidDisabledList', 'getREVPHSolenoidVoltage', 'getREVPHSolenoids', 'getREVPHStickyFaults', 'getREVPHVersion', 'getREVPHVoltage', 'getRSLState', 'getRuntimeType', 'getSerialBytesReceived', 'getSerialFD', 'getSerialNumber', 'getSystemActive', 'getSystemClockTicksPerMicrosecond', 'getSystemTimeValid', 'getTeamNumber', 'getUserActive3V3', 'getUserCurrent3V3', 'getUserCurrentFaults3V3', 'getUserVoltage3V3', 'getVinVoltage', 'hasMain', 'initialize', 'initializeAddressableLED', 'initializeAnalogInputPort', 'initializeCAN', 'initializeCTREPCM', 'initializeCounter', 'initializeDIOPort', 'initializeDutyCycle', 'initializeEncoder', 'initializeI2C', 'initializeNotifier', 'initializePWMPort', 'initializePowerDistribution', 'initializeREVPH', 'initializeSerialPort', 'initializeSerialPortDirect', 'isAnyPulsing', 'isHandleCorrectVersion', 'isHandleType', 'isPulsing', 'loadExtensions', 'loadOneExtension', 'observeUserProgramAutonomous', 'observeUserProgramDisabled', 'observeUserProgramStarting', 'observeUserProgramTeleop', 'observeUserProgramTest', 'provideNewDataEventHandle', 'pulse', 'pulseMultiple', 'readCANPacketLatest', 'readCANPacketNew', 'readCANPacketTimeout', 'readI2C', 'readSerial', 'refreshDSData', 'removeNewDataEventHandle', 'reportUsage', 'resetCounter', 'resetEncoder', 'resetPowerDistributionTotalEnergy', 'resetUserCurrentFaults', 'runMain', 'sendConsoleLine', 'sendError', 'setAddressableLEDData', 'setAddressableLEDLength', 'setAddressableLEDStart', 'setAnalogAverageBits', 'setAnalogInputSimDevice', 'setAnalogOversampleBits', 'setAnalogSampleRate', 'setBrownoutVoltage', 'setCTREPCMClosedLoopControl', 'setCTREPCMOneShotDuration', 'setCTREPCMSolenoids', 'setCounterEdgeConfiguration', 'setCounterMaxPeriod', 'setCurrentThreadPriority', 'setDIO', 'setDIODirection', 'setDIOSimDevice', 'setDigitalPWMDutyCycle', 'setDigitalPWMOutputChannel', 'setDigitalPWMPPS', 'setDigitalPWMRate', 'setDutyCycleSimDevice', 'setEncoderDistancePerPulse', 'setEncoderMaxPeriod', 'setEncoderMinRate', 'setEncoderReverseDirection', 'setEncoderSamplesToAverage', 'setEncoderSimDevice', 'setJoystickOutputs', 'setNotifierName', 'setNotifierThreadPriority', 'setPWMOutputPeriod', 'setPWMPulseTimeMicroseconds', 'setPWMSimDevice', 'setPowerDistributionSwitchableChannel', 'setREVPHClosedLoopControlAnalog', 'setREVPHClosedLoopControlDigital', 'setREVPHClosedLoopControlDisabled', 'setREVPHClosedLoopControlHybrid', 'setREVPHCompressorConfig', 'setREVPHSolenoids', 'setSerialBaudRate', 'setSerialDataBits', 'setSerialFlowControl', 'setSerialParity', 'setSerialReadBufferSize', 'setSerialStopBits', 'setSerialTimeout', 'setSerialWriteBufferSize', 'setSerialWriteMode', 'setShowExtensionsNotFoundMessages', 'setUserRailEnabled3V3', 'shutdown', 'simPeriodicAfter', 'simPeriodicBefore', 'stopCANPacketRepeating', 'stopNotifier', 'transactionI2C', 'updateNotifierAlarm', 'waitForNotifierAlarm', 'writeCANPacket', 'writeCANPacketRepeating', 'writeCANRTRFrame', 'writeI2C', 'writeSerial']
class AddressableLEDColorOrder:
    """
    Order that color data is sent over the wire.
    
    Members:
    
      HAL_ALED_RGB
    
      HAL_ALED_RBG
    
      HAL_ALED_BGR
    
      HAL_ALED_BRG
    
      HAL_ALED_GBR
    
      HAL_ALED_GRB
    """
    HAL_ALED_BGR: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_BGR: 2>
    HAL_ALED_BRG: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_BRG: 3>
    HAL_ALED_GBR: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_GBR: 4>
    HAL_ALED_GRB: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_GRB: 5>
    HAL_ALED_RBG: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_RBG: 1>
    HAL_ALED_RGB: typing.ClassVar[AddressableLEDColorOrder]  # value = <AddressableLEDColorOrder.HAL_ALED_RGB: 0>
    __members__: typing.ClassVar[dict[str, AddressableLEDColorOrder]]  # value = {'HAL_ALED_RGB': <AddressableLEDColorOrder.HAL_ALED_RGB: 0>, 'HAL_ALED_RBG': <AddressableLEDColorOrder.HAL_ALED_RBG: 1>, 'HAL_ALED_BGR': <AddressableLEDColorOrder.HAL_ALED_BGR: 2>, 'HAL_ALED_BRG': <AddressableLEDColorOrder.HAL_ALED_BRG: 3>, 'HAL_ALED_GBR': <AddressableLEDColorOrder.HAL_ALED_GBR: 4>, 'HAL_ALED_GRB': <AddressableLEDColorOrder.HAL_ALED_GRB: 5>}
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
class AddressableLEDData:
    """
    structure for holding one LED's color data.
    """
    def __init__(self) -> None:
        ...
    @property
    def b(self) -> int:
        """
        ///< blue value
        """
    @b.setter
    def b(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def g(self) -> int:
        """
        ///< green value
        """
    @g.setter
    def g(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def r(self) -> int:
        """
        ///< red value
        """
    @r.setter
    def r(self, arg0: typing.SupportsInt) -> None:
        ...
class AllianceStationID:
    """
    Members:
    
      kUnknown : Unknown Alliance Station
    
      kRed1 : Red Alliance Station 1
    
      kRed2 : Red Alliance Station 2
    
      kRed3 : Red Alliance Station 3
    
      kBlue1 : Blue Alliance Station 1
    
      kBlue2 : Blue Alliance Station 2
    
      kBlue3 : Blue Alliance Station 3
    """
    __members__: typing.ClassVar[dict[str, AllianceStationID]]  # value = {'kUnknown': <AllianceStationID.kUnknown: 0>, 'kRed1': <AllianceStationID.kRed1: 1>, 'kRed2': <AllianceStationID.kRed2: 2>, 'kRed3': <AllianceStationID.kRed3: 3>, 'kBlue1': <AllianceStationID.kBlue1: 4>, 'kBlue2': <AllianceStationID.kBlue2: 5>, 'kBlue3': <AllianceStationID.kBlue3: 6>}
    kBlue1: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kBlue1: 4>
    kBlue2: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kBlue2: 5>
    kBlue3: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kBlue3: 6>
    kRed1: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kRed1: 1>
    kRed2: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kRed2: 2>
    kRed3: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kRed3: 3>
    kUnknown: typing.ClassVar[AllianceStationID]  # value = <AllianceStationID.kUnknown: 0>
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
class CANDeviceType:
    """
    The CAN device type.
    
    Teams should use HAL_CAN_Dev_kMiscellaneous
    
    Members:
    
      kBroadcast : Broadcast.
    
      kRobotController : Robot controller.
    
      kMotorController : Motor controller.
    
      kRelayController : Relay controller.
    
      kGyroSensor : Gyro sensor.
    
      kAccelerometer : Accelerometer.
    
      kUltrasonicSensor : Ultrasonic sensor.
    
      kGearToothSensor : Gear tooth sensor.
    
      kPowerDistribution : Power distribution.
    
      kPneumatics : Pneumatics.
    
      kMiscellaneous : Miscellaneous.
    
      kIOBreakout : IO breakout.
    
      kServoController
    
      kFirmwareUpdate : Firmware update.
    """
    __members__: typing.ClassVar[dict[str, CANDeviceType]]  # value = {'kBroadcast': <CANDeviceType.kBroadcast: 0>, 'kRobotController': <CANDeviceType.kRobotController: 1>, 'kMotorController': <CANDeviceType.kMotorController: 2>, 'kRelayController': <CANDeviceType.kRelayController: 3>, 'kGyroSensor': <CANDeviceType.kGyroSensor: 4>, 'kAccelerometer': <CANDeviceType.kAccelerometer: 5>, 'kUltrasonicSensor': <CANDeviceType.kUltrasonicSensor: 6>, 'kGearToothSensor': <CANDeviceType.kGearToothSensor: 7>, 'kPowerDistribution': <CANDeviceType.kPowerDistribution: 8>, 'kPneumatics': <CANDeviceType.kPneumatics: 9>, 'kMiscellaneous': <CANDeviceType.kMiscellaneous: 10>, 'kIOBreakout': <CANDeviceType.kIOBreakout: 11>, 'kServoController': <CANDeviceType.kServoController: 12>, 'kFirmwareUpdate': <CANDeviceType.kFirmwareUpdate: 31>}
    kAccelerometer: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kAccelerometer: 5>
    kBroadcast: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kBroadcast: 0>
    kFirmwareUpdate: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kFirmwareUpdate: 31>
    kGearToothSensor: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kGearToothSensor: 7>
    kGyroSensor: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kGyroSensor: 4>
    kIOBreakout: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kIOBreakout: 11>
    kMiscellaneous: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kMiscellaneous: 10>
    kMotorController: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kMotorController: 2>
    kPneumatics: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kPneumatics: 9>
    kPowerDistribution: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kPowerDistribution: 8>
    kRelayController: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kRelayController: 3>
    kRobotController: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kRobotController: 1>
    kServoController: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kServoController: 12>
    kUltrasonicSensor: typing.ClassVar[CANDeviceType]  # value = <CANDeviceType.kUltrasonicSensor: 6>
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
class CANFlags:
    """
    Members:
    
      HAL_CAN_NO_FLAGS : Placeholder for no flags
    
      HAL_CAN_FD_BITRATESWITCH : Mask for if frame will do FD bit rate switching.
    Only matters to send.
    
      HAL_CAN_FD_DATALENGTH : Mask for is frame will contain an FD length.
    """
    HAL_CAN_FD_BITRATESWITCH: typing.ClassVar[CANFlags]  # value = <CANFlags.HAL_CAN_FD_BITRATESWITCH: 1>
    HAL_CAN_FD_DATALENGTH: typing.ClassVar[CANFlags]  # value = <CANFlags.HAL_CAN_FD_DATALENGTH: 2>
    HAL_CAN_NO_FLAGS: typing.ClassVar[CANFlags]  # value = <CANFlags.HAL_CAN_NO_FLAGS: 0>
    __members__: typing.ClassVar[dict[str, CANFlags]]  # value = {'HAL_CAN_NO_FLAGS': <CANFlags.HAL_CAN_NO_FLAGS: 0>, 'HAL_CAN_FD_BITRATESWITCH': <CANFlags.HAL_CAN_FD_BITRATESWITCH: 1>, 'HAL_CAN_FD_DATALENGTH': <CANFlags.HAL_CAN_FD_DATALENGTH: 2>}
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
class CANManufacturer:
    """
    The CAN manufacturer ID.
    
    Teams should use HAL_CAN_Man_kTeamUse.
    
    Members:
    
      kBroadcast : Broadcast.
    
      kNI : National Instruments.
    
      kLM : Luminary Micro.
    
      kDEKA : DEKA Research and Development Corp.
    
      kCTRE : Cross the Road Electronics.
    
      kREV : REV robotics.
    
      kGrapple : Grapple.
    
      kMS : MindSensors.
    
      kTeamUse : Team use.
    
      kKauaiLabs : Kauai Labs.
    
      kCopperforge : Copperforge.
    
      kPWF : Playing With Fusion.
    
      kStudica : Studica.
    
      kTheThriftyBot : TheThriftyBot.
    
      kReduxRobotics : Redux Robotics.
    
      kAndyMark : AndyMark.
    
      kVividHosting : Vivid-Hosting.
    """
    __members__: typing.ClassVar[dict[str, CANManufacturer]]  # value = {'kBroadcast': <CANManufacturer.kBroadcast: 0>, 'kNI': <CANManufacturer.kNI: 1>, 'kLM': <CANManufacturer.kLM: 2>, 'kDEKA': <CANManufacturer.kDEKA: 3>, 'kCTRE': <CANManufacturer.kCTRE: 4>, 'kREV': <CANManufacturer.kREV: 5>, 'kGrapple': <CANManufacturer.kGrapple: 6>, 'kMS': <CANManufacturer.kMS: 7>, 'kTeamUse': <CANManufacturer.kTeamUse: 8>, 'kKauaiLabs': <CANManufacturer.kKauaiLabs: 9>, 'kCopperforge': <CANManufacturer.kCopperforge: 10>, 'kPWF': <CANManufacturer.kPWF: 11>, 'kStudica': <CANManufacturer.kStudica: 12>, 'kTheThriftyBot': <CANManufacturer.kTheThriftyBot: 13>, 'kReduxRobotics': <CANManufacturer.kReduxRobotics: 14>, 'kAndyMark': <CANManufacturer.kAndyMark: 15>, 'kVividHosting': <CANManufacturer.kVividHosting: 16>}
    kAndyMark: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kAndyMark: 15>
    kBroadcast: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kBroadcast: 0>
    kCTRE: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kCTRE: 4>
    kCopperforge: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kCopperforge: 10>
    kDEKA: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kDEKA: 3>
    kGrapple: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kGrapple: 6>
    kKauaiLabs: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kKauaiLabs: 9>
    kLM: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kLM: 2>
    kMS: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kMS: 7>
    kNI: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kNI: 1>
    kPWF: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kPWF: 11>
    kREV: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kREV: 5>
    kReduxRobotics: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kReduxRobotics: 14>
    kStudica: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kStudica: 12>
    kTeamUse: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kTeamUse: 8>
    kTheThriftyBot: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kTheThriftyBot: 13>
    kVividHosting: typing.ClassVar[CANManufacturer]  # value = <CANManufacturer.kVividHosting: 16>
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
class CANMessage:
    def __init__(self) -> None:
        ...
    @property
    def data(self) -> memoryview:
        """
        The message data
        """
    @property
    def dataSize(self) -> int:
        """
        The size of the data received (0-64 bytes)
        """
    @dataSize.setter
    def dataSize(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def flags(self) -> int:
        """
        Flags for the message (HAL_CANFlags)
        """
    @flags.setter
    def flags(self, arg0: typing.SupportsInt) -> None:
        ...
class CANReceiveMessage:
    def __init__(self) -> None:
        ...
    @property
    def message(self) -> CANMessage:
        """
        The received message
        """
    @message.setter
    def message(self, arg0: CANMessage) -> None:
        ...
    @property
    def timeStamp(self) -> int:
        """
        Receive timestamp (wpi time)
        """
    @timeStamp.setter
    def timeStamp(self, arg0: typing.SupportsInt) -> None:
        ...
class CANStreamMessage:
    """
    Storage for CAN Stream Messages.
    """
    def __init__(self) -> None:
        ...
    @property
    def message(self) -> CANReceiveMessage:
        """
        The message
        """
    @message.setter
    def message(self, arg0: CANReceiveMessage) -> None:
        ...
    @property
    def messageId(self) -> int:
        """
        The message ID
        """
    @messageId.setter
    def messageId(self, arg0: typing.SupportsInt) -> None:
        ...
class ControlWord:
    def __init__(self) -> None:
        ...
    @property
    def autonomous(self) -> int:
        ...
    @autonomous.setter
    def autonomous(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def control_reserved(self) -> int:
        ...
    @control_reserved.setter
    def control_reserved(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def dsAttached(self) -> int:
        ...
    @dsAttached.setter
    def dsAttached(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def eStop(self) -> int:
        ...
    @eStop.setter
    def eStop(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def enabled(self) -> int:
        ...
    @enabled.setter
    def enabled(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def fmsAttached(self) -> int:
        ...
    @fmsAttached.setter
    def fmsAttached(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def test(self) -> int:
        ...
    @test.setter
    def test(self, arg1: typing.SupportsInt) -> None:
        ...
class EncoderEncodingType:
    """
    The encoding scaling of the encoder.
    
    Members:
    
      Encoder_k1X
    
      Encoder_k2X
    
      Encoder_k4X
    """
    Encoder_k1X: typing.ClassVar[EncoderEncodingType]  # value = <EncoderEncodingType.Encoder_k1X: 0>
    Encoder_k2X: typing.ClassVar[EncoderEncodingType]  # value = <EncoderEncodingType.Encoder_k2X: 1>
    Encoder_k4X: typing.ClassVar[EncoderEncodingType]  # value = <EncoderEncodingType.Encoder_k4X: 2>
    __members__: typing.ClassVar[dict[str, EncoderEncodingType]]  # value = {'Encoder_k1X': <EncoderEncodingType.Encoder_k1X: 0>, 'Encoder_k2X': <EncoderEncodingType.Encoder_k2X: 1>, 'Encoder_k4X': <EncoderEncodingType.Encoder_k4X: 2>}
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
class EncoderIndexingType:
    """
    The type of index pulse for the encoder.
    
    Members:
    
      kResetWhileHigh
    
      kResetWhileLow
    
      kResetOnFallingEdge
    
      kResetOnRisingEdge
    """
    __members__: typing.ClassVar[dict[str, EncoderIndexingType]]  # value = {'kResetWhileHigh': <EncoderIndexingType.kResetWhileHigh: 0>, 'kResetWhileLow': <EncoderIndexingType.kResetWhileLow: 1>, 'kResetOnFallingEdge': <EncoderIndexingType.kResetOnFallingEdge: 2>, 'kResetOnRisingEdge': <EncoderIndexingType.kResetOnRisingEdge: 3>}
    kResetOnFallingEdge: typing.ClassVar[EncoderIndexingType]  # value = <EncoderIndexingType.kResetOnFallingEdge: 2>
    kResetOnRisingEdge: typing.ClassVar[EncoderIndexingType]  # value = <EncoderIndexingType.kResetOnRisingEdge: 3>
    kResetWhileHigh: typing.ClassVar[EncoderIndexingType]  # value = <EncoderIndexingType.kResetWhileHigh: 0>
    kResetWhileLow: typing.ClassVar[EncoderIndexingType]  # value = <EncoderIndexingType.kResetWhileLow: 1>
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
class HandleEnum:
    """
    Enum of HAL handle types. Vendors/Teams should use Vendor (17).
    
    Members:
    
      Undefined
    
      DIO
    
      Port
    
      Notifier
    
      Interrupt
    
      AnalogOutput
    
      AnalogInput
    
      AnalogTrigger
    
      Relay
    
      PWM
    
      DigitalPWM
    
      Counter
    
      FPGAEncoder
    
      Encoder
    
      Compressor
    
      Solenoid
    
      AnalogGyro
    
      Vendor
    
      SimulationJni
    
      CAN
    
      SerialPort
    
      DutyCycle
    
      DMA
    
      AddressableLED
    
      CTREPCM
    
      CTREPDP
    
      REVPDH
    
      REVPH
    
      CANStream
    """
    AddressableLED: typing.ClassVar[HandleEnum]  # value = <HandleEnum.AddressableLED: 23>
    AnalogGyro: typing.ClassVar[HandleEnum]  # value = <HandleEnum.AnalogGyro: 16>
    AnalogInput: typing.ClassVar[HandleEnum]  # value = <HandleEnum.AnalogInput: 6>
    AnalogOutput: typing.ClassVar[HandleEnum]  # value = <HandleEnum.AnalogOutput: 5>
    AnalogTrigger: typing.ClassVar[HandleEnum]  # value = <HandleEnum.AnalogTrigger: 7>
    CAN: typing.ClassVar[HandleEnum]  # value = <HandleEnum.CAN: 19>
    CANStream: typing.ClassVar[HandleEnum]  # value = <HandleEnum.CANStream: 28>
    CTREPCM: typing.ClassVar[HandleEnum]  # value = <HandleEnum.CTREPCM: 24>
    CTREPDP: typing.ClassVar[HandleEnum]  # value = <HandleEnum.CTREPDP: 25>
    Compressor: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Compressor: 14>
    Counter: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Counter: 11>
    DIO: typing.ClassVar[HandleEnum]  # value = <HandleEnum.DIO: 48>
    DMA: typing.ClassVar[HandleEnum]  # value = <HandleEnum.DMA: 22>
    DigitalPWM: typing.ClassVar[HandleEnum]  # value = <HandleEnum.DigitalPWM: 10>
    DutyCycle: typing.ClassVar[HandleEnum]  # value = <HandleEnum.DutyCycle: 21>
    Encoder: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Encoder: 13>
    FPGAEncoder: typing.ClassVar[HandleEnum]  # value = <HandleEnum.FPGAEncoder: 12>
    Interrupt: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Interrupt: 4>
    Notifier: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Notifier: 3>
    PWM: typing.ClassVar[HandleEnum]  # value = <HandleEnum.PWM: 9>
    Port: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Port: 2>
    REVPDH: typing.ClassVar[HandleEnum]  # value = <HandleEnum.REVPDH: 26>
    REVPH: typing.ClassVar[HandleEnum]  # value = <HandleEnum.REVPH: 27>
    Relay: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Relay: 8>
    SerialPort: typing.ClassVar[HandleEnum]  # value = <HandleEnum.SerialPort: 20>
    SimulationJni: typing.ClassVar[HandleEnum]  # value = <HandleEnum.SimulationJni: 18>
    Solenoid: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Solenoid: 15>
    Undefined: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Undefined: 0>
    Vendor: typing.ClassVar[HandleEnum]  # value = <HandleEnum.Vendor: 17>
    __members__: typing.ClassVar[dict[str, HandleEnum]]  # value = {'Undefined': <HandleEnum.Undefined: 0>, 'DIO': <HandleEnum.DIO: 48>, 'Port': <HandleEnum.Port: 2>, 'Notifier': <HandleEnum.Notifier: 3>, 'Interrupt': <HandleEnum.Interrupt: 4>, 'AnalogOutput': <HandleEnum.AnalogOutput: 5>, 'AnalogInput': <HandleEnum.AnalogInput: 6>, 'AnalogTrigger': <HandleEnum.AnalogTrigger: 7>, 'Relay': <HandleEnum.Relay: 8>, 'PWM': <HandleEnum.PWM: 9>, 'DigitalPWM': <HandleEnum.DigitalPWM: 10>, 'Counter': <HandleEnum.Counter: 11>, 'FPGAEncoder': <HandleEnum.FPGAEncoder: 12>, 'Encoder': <HandleEnum.Encoder: 13>, 'Compressor': <HandleEnum.Compressor: 14>, 'Solenoid': <HandleEnum.Solenoid: 15>, 'AnalogGyro': <HandleEnum.AnalogGyro: 16>, 'Vendor': <HandleEnum.Vendor: 17>, 'SimulationJni': <HandleEnum.SimulationJni: 18>, 'CAN': <HandleEnum.CAN: 19>, 'SerialPort': <HandleEnum.SerialPort: 20>, 'DutyCycle': <HandleEnum.DutyCycle: 21>, 'DMA': <HandleEnum.DMA: 22>, 'AddressableLED': <HandleEnum.AddressableLED: 23>, 'CTREPCM': <HandleEnum.CTREPCM: 24>, 'CTREPDP': <HandleEnum.CTREPDP: 25>, 'REVPDH': <HandleEnum.REVPDH: 26>, 'REVPH': <HandleEnum.REVPH: 27>, 'CANStream': <HandleEnum.CANStream: 28>}
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
class I2CPort:
    """
    Members:
    
      kInvalid
    
      kPort0
    
      kPort1
    """
    __members__: typing.ClassVar[dict[str, I2CPort]]  # value = {'kInvalid': <I2CPort.kInvalid: -1>, 'kPort0': <I2CPort.kPort0: 0>, 'kPort1': <I2CPort.kPort1: 1>}
    kInvalid: typing.ClassVar[I2CPort]  # value = <I2CPort.kInvalid: -1>
    kPort0: typing.ClassVar[I2CPort]  # value = <I2CPort.kPort0: 0>
    kPort1: typing.ClassVar[I2CPort]  # value = <I2CPort.kPort1: 1>
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
class JoystickAxes:
    def __init__(self) -> None:
        ...
    @property
    def axes(self) -> memoryview:
        ...
    @property
    def count(self) -> int:
        ...
    @count.setter
    def count(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def raw(self) -> memoryview:
        ...
class JoystickButtons:
    def __init__(self) -> None:
        ...
    @property
    def buttons(self) -> int:
        ...
    @buttons.setter
    def buttons(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def count(self) -> int:
        ...
    @count.setter
    def count(self, arg0: typing.SupportsInt) -> None:
        ...
class JoystickDescriptor:
    def __init__(self) -> None:
        ...
    @property
    def axisCount(self) -> int:
        ...
    @axisCount.setter
    def axisCount(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def axisTypes(self) -> memoryview:
        ...
    @property
    def buttonCount(self) -> int:
        ...
    @buttonCount.setter
    def buttonCount(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def isGamepad(self) -> int:
        ...
    @isGamepad.setter
    def isGamepad(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def name(self) -> memoryview:
        ...
    @property
    def povCount(self) -> int:
        ...
    @povCount.setter
    def povCount(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def type(self) -> int:
        ...
    @type.setter
    def type(self, arg0: typing.SupportsInt) -> None:
        ...
class JoystickPOV:
    """
    Members:
    
      kCentered : Centered
    
      kUp : Up
    
      kRight : Right
    
      kDown : Down
    
      kLeft : Left
    
      kRightUp : Right-Up
    
      kRightDown : Right-Down
    
      kLeftUp : Left-Up
    
      kLeftDown : Left-Down
    """
    __members__: typing.ClassVar[dict[str, JoystickPOV]]  # value = {'kCentered': <JoystickPOV.kCentered: 0>, 'kUp': <JoystickPOV.kUp: 1>, 'kRight': <JoystickPOV.kRight: 2>, 'kDown': <JoystickPOV.kDown: 4>, 'kLeft': <JoystickPOV.kLeft: 8>, 'kRightUp': <JoystickPOV.kRightUp: 3>, 'kRightDown': <JoystickPOV.kRightDown: 6>, 'kLeftUp': <JoystickPOV.kLeftUp: 9>, 'kLeftDown': <JoystickPOV.kLeftDown: 12>}
    kCentered: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kCentered: 0>
    kDown: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kDown: 4>
    kLeft: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kLeft: 8>
    kLeftDown: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kLeftDown: 12>
    kLeftUp: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kLeftUp: 9>
    kRight: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kRight: 2>
    kRightDown: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kRightDown: 6>
    kRightUp: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kRightUp: 3>
    kUp: typing.ClassVar[JoystickPOV]  # value = <JoystickPOV.kUp: 1>
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
class JoystickPOVs:
    def __init__(self) -> None:
        ...
    @property
    def count(self) -> int:
        ...
    @count.setter
    def count(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def povs(self) -> memoryview:
        ...
class MatchInfo:
    matchType: MatchType
    def __init__(self) -> None:
        ...
    @property
    def eventName(self) -> memoryview:
        ...
    @property
    def gameSpecificMessage(self) -> memoryview:
        ...
    @property
    def gameSpecificMessageSize(self) -> int:
        ...
    @gameSpecificMessageSize.setter
    def gameSpecificMessageSize(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def matchNumber(self) -> int:
        ...
    @matchNumber.setter
    def matchNumber(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def replayNumber(self) -> int:
        ...
    @replayNumber.setter
    def replayNumber(self, arg0: typing.SupportsInt) -> None:
        ...
class MatchType:
    """
    Members:
    
      none
    
      practice
    
      qualification
    
      elimination
    """
    __members__: typing.ClassVar[dict[str, MatchType]]  # value = {'none': <MatchType.none: 0>, 'practice': <MatchType.practice: 1>, 'qualification': <MatchType.qualification: 2>, 'elimination': <MatchType.elimination: 3>}
    elimination: typing.ClassVar[MatchType]  # value = <MatchType.elimination: 3>
    none: typing.ClassVar[MatchType]  # value = <MatchType.none: 0>
    practice: typing.ClassVar[MatchType]  # value = <MatchType.practice: 1>
    qualification: typing.ClassVar[MatchType]  # value = <MatchType.qualification: 2>
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
class PowerDistributionFaults:
    def __init__(self) -> None:
        ...
    @property
    def brownout(self) -> int:
        """
        The input voltage is below the minimum voltage.
        """
    @brownout.setter
    def brownout(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canWarning(self) -> int:
        """
        A warning was raised by the device's CAN controller.
        """
    @canWarning.setter
    def canWarning(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel0BreakerFault(self) -> int:
        """
        Breaker fault on channel 0.
        """
    @channel0BreakerFault.setter
    def channel0BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel10BreakerFault(self) -> int:
        """
        Breaker fault on channel 10.
        """
    @channel10BreakerFault.setter
    def channel10BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel11BreakerFault(self) -> int:
        """
        Breaker fault on channel 12.
        """
    @channel11BreakerFault.setter
    def channel11BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel12BreakerFault(self) -> int:
        """
        Breaker fault on channel 13.
        """
    @channel12BreakerFault.setter
    def channel12BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel13BreakerFault(self) -> int:
        """
        Breaker fault on channel 14.
        """
    @channel13BreakerFault.setter
    def channel13BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel14BreakerFault(self) -> int:
        """
        Breaker fault on channel 15.
        """
    @channel14BreakerFault.setter
    def channel14BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel15BreakerFault(self) -> int:
        """
        Breaker fault on channel 16.
        """
    @channel15BreakerFault.setter
    def channel15BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel16BreakerFault(self) -> int:
        """
        Breaker fault on channel 17.
        """
    @channel16BreakerFault.setter
    def channel16BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel17BreakerFault(self) -> int:
        """
        Breaker fault on channel 18.
        """
    @channel17BreakerFault.setter
    def channel17BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel18BreakerFault(self) -> int:
        """
        Breaker fault on channel 19.
        """
    @channel18BreakerFault.setter
    def channel18BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel19BreakerFault(self) -> int:
        """
        Breaker fault on channel 20.
        """
    @channel19BreakerFault.setter
    def channel19BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel1BreakerFault(self) -> int:
        """
        Breaker fault on channel 1.
        """
    @channel1BreakerFault.setter
    def channel1BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel20BreakerFault(self) -> int:
        """
        Breaker fault on channel 21.
        """
    @channel20BreakerFault.setter
    def channel20BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel21BreakerFault(self) -> int:
        """
        Breaker fault on channel 22.
        """
    @channel21BreakerFault.setter
    def channel21BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel22BreakerFault(self) -> int:
        """
        Breaker fault on channel 23.
        """
    @channel22BreakerFault.setter
    def channel22BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel23BreakerFault(self) -> int:
        """
        Breaker fault on channel 24.
        """
    @channel23BreakerFault.setter
    def channel23BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel2BreakerFault(self) -> int:
        """
        Breaker fault on channel 2.
        """
    @channel2BreakerFault.setter
    def channel2BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel3BreakerFault(self) -> int:
        """
        Breaker fault on channel 3.
        """
    @channel3BreakerFault.setter
    def channel3BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel4BreakerFault(self) -> int:
        """
        Breaker fault on channel 4.
        """
    @channel4BreakerFault.setter
    def channel4BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel5BreakerFault(self) -> int:
        """
        Breaker fault on channel 5.
        """
    @channel5BreakerFault.setter
    def channel5BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel6BreakerFault(self) -> int:
        """
        Breaker fault on channel 6.
        """
    @channel6BreakerFault.setter
    def channel6BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel7BreakerFault(self) -> int:
        """
        Breaker fault on channel 7.
        """
    @channel7BreakerFault.setter
    def channel7BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel8BreakerFault(self) -> int:
        """
        Breaker fault on channel 8.
        """
    @channel8BreakerFault.setter
    def channel8BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel9BreakerFault(self) -> int:
        """
        Breaker fault on channel 9.
        """
    @channel9BreakerFault.setter
    def channel9BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareFault(self) -> int:
        """
        The hardware on the device has malfunctioned.
        """
    @hardwareFault.setter
    def hardwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
class PowerDistributionStickyFaults:
    """
    Storage for REV PDH Sticky Faults
    """
    def __init__(self) -> None:
        ...
    @property
    def brownout(self) -> int:
        """
        The input voltage is below the minimum voltage.
        """
    @brownout.setter
    def brownout(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canBusOff(self) -> int:
        """
        The device's CAN controller experienced a "Bus Off" event.
        """
    @canBusOff.setter
    def canBusOff(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canWarning(self) -> int:
        """
        A warning was raised by the device's CAN controller.
        """
    @canWarning.setter
    def canWarning(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel0BreakerFault(self) -> int:
        """
        Breaker fault on channel 0.
        """
    @channel0BreakerFault.setter
    def channel0BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel10BreakerFault(self) -> int:
        """
        Breaker fault on channel 10.
        """
    @channel10BreakerFault.setter
    def channel10BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel11BreakerFault(self) -> int:
        """
        Breaker fault on channel 12.
        """
    @channel11BreakerFault.setter
    def channel11BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel12BreakerFault(self) -> int:
        """
        Breaker fault on channel 13.
        """
    @channel12BreakerFault.setter
    def channel12BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel13BreakerFault(self) -> int:
        """
        Breaker fault on channel 14.
        """
    @channel13BreakerFault.setter
    def channel13BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel14BreakerFault(self) -> int:
        """
        Breaker fault on channel 15.
        """
    @channel14BreakerFault.setter
    def channel14BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel15BreakerFault(self) -> int:
        """
        Breaker fault on channel 16.
        """
    @channel15BreakerFault.setter
    def channel15BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel16BreakerFault(self) -> int:
        """
        Breaker fault on channel 17.
        """
    @channel16BreakerFault.setter
    def channel16BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel17BreakerFault(self) -> int:
        """
        Breaker fault on channel 18.
        """
    @channel17BreakerFault.setter
    def channel17BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel18BreakerFault(self) -> int:
        """
        Breaker fault on channel 19.
        """
    @channel18BreakerFault.setter
    def channel18BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel19BreakerFault(self) -> int:
        """
        Breaker fault on channel 20.
        """
    @channel19BreakerFault.setter
    def channel19BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel1BreakerFault(self) -> int:
        """
        Breaker fault on channel 1.
        """
    @channel1BreakerFault.setter
    def channel1BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel20BreakerFault(self) -> int:
        """
        Breaker fault on channel 21.
        """
    @channel20BreakerFault.setter
    def channel20BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel21BreakerFault(self) -> int:
        """
        Breaker fault on channel 22.
        """
    @channel21BreakerFault.setter
    def channel21BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel22BreakerFault(self) -> int:
        """
        Breaker fault on channel 23.
        """
    @channel22BreakerFault.setter
    def channel22BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel23BreakerFault(self) -> int:
        """
        Breaker fault on channel 24.
        """
    @channel23BreakerFault.setter
    def channel23BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel2BreakerFault(self) -> int:
        """
        Breaker fault on channel 2.
        """
    @channel2BreakerFault.setter
    def channel2BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel3BreakerFault(self) -> int:
        """
        Breaker fault on channel 3.
        """
    @channel3BreakerFault.setter
    def channel3BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel4BreakerFault(self) -> int:
        """
        Breaker fault on channel 4.
        """
    @channel4BreakerFault.setter
    def channel4BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel5BreakerFault(self) -> int:
        """
        Breaker fault on channel 5.
        """
    @channel5BreakerFault.setter
    def channel5BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel6BreakerFault(self) -> int:
        """
        Breaker fault on channel 6.
        """
    @channel6BreakerFault.setter
    def channel6BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel7BreakerFault(self) -> int:
        """
        Breaker fault on channel 7.
        """
    @channel7BreakerFault.setter
    def channel7BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel8BreakerFault(self) -> int:
        """
        Breaker fault on channel 8.
        """
    @channel8BreakerFault.setter
    def channel8BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel9BreakerFault(self) -> int:
        """
        Breaker fault on channel 9.
        """
    @channel9BreakerFault.setter
    def channel9BreakerFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareFault(self) -> int:
        """
        The firmware on the device has malfunctioned.
        """
    @firmwareFault.setter
    def firmwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareFault(self) -> int:
        """
        The hardware on the device has malfunctioned.
        """
    @hardwareFault.setter
    def hardwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hasReset(self) -> int:
        """
        The device has rebooted.
        """
    @hasReset.setter
    def hasReset(self, arg1: typing.SupportsInt) -> None:
        ...
class PowerDistributionType:
    """
    The types of power distribution devices.
    
    Members:
    
      kAutomatic : Automatically determines the module type
    
      kCTRE : CTRE (Cross The Road Electronics) Power Distribution Panel (PDP).
    
      kRev : REV Power Distribution Hub (PDH).
    """
    __members__: typing.ClassVar[dict[str, PowerDistributionType]]  # value = {'kAutomatic': <PowerDistributionType.kAutomatic: 0>, 'kCTRE': <PowerDistributionType.kCTRE: 1>, 'kRev': <PowerDistributionType.kRev: 2>}
    kAutomatic: typing.ClassVar[PowerDistributionType]  # value = <PowerDistributionType.kAutomatic: 0>
    kCTRE: typing.ClassVar[PowerDistributionType]  # value = <PowerDistributionType.kCTRE: 1>
    kRev: typing.ClassVar[PowerDistributionType]  # value = <PowerDistributionType.kRev: 2>
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
class PowerDistributionVersion:
    """
    Power distribution version.
    """
    def __init__(self) -> None:
        ...
    @property
    def firmwareFix(self) -> int:
        """
        Firmware fix version number.
        """
    @firmwareFix.setter
    def firmwareFix(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareMajor(self) -> int:
        """
        Firmware major version number.
        """
    @firmwareMajor.setter
    def firmwareMajor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareMinor(self) -> int:
        """
        Firmware minor version number.
        """
    @firmwareMinor.setter
    def firmwareMinor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareMajor(self) -> int:
        """
        Hardware major version number.
        """
    @hardwareMajor.setter
    def hardwareMajor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareMinor(self) -> int:
        """
        Hardware minor version number.
        """
    @hardwareMinor.setter
    def hardwareMinor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def uniqueId(self) -> int:
        """
        Unique ID.
        """
    @uniqueId.setter
    def uniqueId(self, arg0: typing.SupportsInt) -> None:
        ...
class REVPHCompressorConfig:
    """
    Storage for compressor config
    """
    def __init__(self) -> None:
        ...
    @property
    def forceDisable(self) -> int:
        ...
    @forceDisable.setter
    def forceDisable(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def maxAnalogVoltage(self) -> float:
        ...
    @maxAnalogVoltage.setter
    def maxAnalogVoltage(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def minAnalogVoltage(self) -> float:
        ...
    @minAnalogVoltage.setter
    def minAnalogVoltage(self, arg0: typing.SupportsFloat) -> None:
        ...
    @property
    def useDigital(self) -> int:
        ...
    @useDigital.setter
    def useDigital(self, arg0: typing.SupportsInt) -> None:
        ...
class REVPHCompressorConfigType:
    """
    The compressor configuration type
    
    Members:
    
      kDisabled : Disabled.
    
      kDigital : Digital.
    
      kAnalog : Analog.
    
      kHybrid : Hybrid.
    """
    __members__: typing.ClassVar[dict[str, REVPHCompressorConfigType]]  # value = {'kDisabled': <REVPHCompressorConfigType.kDisabled: 0>, 'kDigital': <REVPHCompressorConfigType.kDigital: 1>, 'kAnalog': <REVPHCompressorConfigType.kAnalog: 2>, 'kHybrid': <REVPHCompressorConfigType.kHybrid: 3>}
    kAnalog: typing.ClassVar[REVPHCompressorConfigType]  # value = <REVPHCompressorConfigType.kAnalog: 2>
    kDigital: typing.ClassVar[REVPHCompressorConfigType]  # value = <REVPHCompressorConfigType.kDigital: 1>
    kDisabled: typing.ClassVar[REVPHCompressorConfigType]  # value = <REVPHCompressorConfigType.kDisabled: 0>
    kHybrid: typing.ClassVar[REVPHCompressorConfigType]  # value = <REVPHCompressorConfigType.kHybrid: 3>
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
class REVPHFaults:
    """
    Storage for REV PH Faults
    """
    def __init__(self) -> None:
        ...
    @property
    def brownout(self) -> int:
        """
        The input voltage is below the minimum voltage.
        """
    @brownout.setter
    def brownout(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canWarning(self) -> int:
        """
        A warning was raised by the device's CAN controller.
        """
    @canWarning.setter
    def canWarning(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel0Fault(self) -> int:
        """
        Fault on channel 0.
        """
    @channel0Fault.setter
    def channel0Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel10Fault(self) -> int:
        """
        Fault on channel 10.
        """
    @channel10Fault.setter
    def channel10Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel11Fault(self) -> int:
        """
        Fault on channel 11.
        """
    @channel11Fault.setter
    def channel11Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel12Fault(self) -> int:
        """
        Fault on channel 12.
        """
    @channel12Fault.setter
    def channel12Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel13Fault(self) -> int:
        """
        Fault on channel 13.
        """
    @channel13Fault.setter
    def channel13Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel14Fault(self) -> int:
        """
        Fault on channel 14.
        """
    @channel14Fault.setter
    def channel14Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel15Fault(self) -> int:
        """
        Fault on channel 15.
        """
    @channel15Fault.setter
    def channel15Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel1Fault(self) -> int:
        """
        Fault on channel 1.
        """
    @channel1Fault.setter
    def channel1Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel2Fault(self) -> int:
        """
        Fault on channel 2.
        """
    @channel2Fault.setter
    def channel2Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel3Fault(self) -> int:
        """
        Fault on channel 3.
        """
    @channel3Fault.setter
    def channel3Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel4Fault(self) -> int:
        """
        Fault on channel 4.
        """
    @channel4Fault.setter
    def channel4Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel5Fault(self) -> int:
        """
        Fault on channel 5.
        """
    @channel5Fault.setter
    def channel5Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel6Fault(self) -> int:
        """
        Fault on channel 6.
        """
    @channel6Fault.setter
    def channel6Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel7Fault(self) -> int:
        """
        Fault on channel 7.
        """
    @channel7Fault.setter
    def channel7Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel8Fault(self) -> int:
        """
        Fault on channel 8.
        """
    @channel8Fault.setter
    def channel8Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def channel9Fault(self) -> int:
        """
        Fault on channel 9.
        """
    @channel9Fault.setter
    def channel9Fault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def compressorOpen(self) -> int:
        """
        The compressor output has an open circuit.
        """
    @compressorOpen.setter
    def compressorOpen(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def compressorOverCurrent(self) -> int:
        """
        An overcurrent event occurred on the compressor output.
        """
    @compressorOverCurrent.setter
    def compressorOverCurrent(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareFault(self) -> int:
        """
        The hardware on the device has malfunctioned.
        """
    @hardwareFault.setter
    def hardwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def solenoidOverCurrent(self) -> int:
        """
        An overcurrent event occurred on a solenoid output.
        """
    @solenoidOverCurrent.setter
    def solenoidOverCurrent(self, arg1: typing.SupportsInt) -> None:
        ...
class REVPHStickyFaults:
    """
    Storage for REV PH Sticky Faults
    """
    def __init__(self) -> None:
        ...
    @property
    def brownout(self) -> int:
        """
        The input voltage is below the minimum voltage.
        """
    @brownout.setter
    def brownout(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canBusOff(self) -> int:
        """
        The device's CAN controller experienced a "Bus Off" event.
        """
    @canBusOff.setter
    def canBusOff(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def canWarning(self) -> int:
        """
        A warning was raised by the device's CAN controller.
        """
    @canWarning.setter
    def canWarning(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def compressorOpen(self) -> int:
        """
        The compressor output has an open circuit.
        """
    @compressorOpen.setter
    def compressorOpen(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def compressorOverCurrent(self) -> int:
        """
        An overcurrent event occurred on the compressor output.
        """
    @compressorOverCurrent.setter
    def compressorOverCurrent(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareFault(self) -> int:
        """
        The firmware on the device has malfunctioned.
        """
    @firmwareFault.setter
    def firmwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareFault(self) -> int:
        """
        The hardware on the device has malfunctioned.
        """
    @hardwareFault.setter
    def hardwareFault(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def hasReset(self) -> int:
        """
        The device has rebooted.
        """
    @hasReset.setter
    def hasReset(self, arg1: typing.SupportsInt) -> None:
        ...
    @property
    def solenoidOverCurrent(self) -> int:
        """
        An overcurrent event occurred on a solenoid output.
        """
    @solenoidOverCurrent.setter
    def solenoidOverCurrent(self, arg1: typing.SupportsInt) -> None:
        ...
class REVPHVersion:
    """
    Storage for REV PH Version
    """
    def __init__(self) -> None:
        ...
    @property
    def firmwareFix(self) -> int:
        """
        The firmware fix version.
        """
    @firmwareFix.setter
    def firmwareFix(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareMajor(self) -> int:
        """
        The firmware major version.
        """
    @firmwareMajor.setter
    def firmwareMajor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def firmwareMinor(self) -> int:
        """
        The firmware minor version.
        """
    @firmwareMinor.setter
    def firmwareMinor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareMajor(self) -> int:
        """
        The hardware major version.
        """
    @hardwareMajor.setter
    def hardwareMajor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def hardwareMinor(self) -> int:
        """
        The hardware minor version.
        """
    @hardwareMinor.setter
    def hardwareMinor(self, arg0: typing.SupportsInt) -> None:
        ...
    @property
    def uniqueId(self) -> int:
        """
        The device's unique ID.
        """
    @uniqueId.setter
    def uniqueId(self, arg0: typing.SupportsInt) -> None:
        ...
class RuntimeType:
    """
    Runtime type.
    
    Members:
    
      HAL_Runtime_RoboRIO : roboRIO 1.0
    
      HAL_Runtime_RoboRIO2 : roboRIO 2.0
    
      HAL_Runtime_Simulation : Simulation runtime
    
      HAL_Runtime_SystemCore : SystemCore
    """
    HAL_Runtime_RoboRIO: typing.ClassVar[RuntimeType]  # value = <RuntimeType.HAL_Runtime_RoboRIO: 0>
    HAL_Runtime_RoboRIO2: typing.ClassVar[RuntimeType]  # value = <RuntimeType.HAL_Runtime_RoboRIO2: 1>
    HAL_Runtime_Simulation: typing.ClassVar[RuntimeType]  # value = <RuntimeType.HAL_Runtime_Simulation: 2>
    HAL_Runtime_SystemCore: typing.ClassVar[RuntimeType]  # value = <RuntimeType.HAL_Runtime_SystemCore: 3>
    __members__: typing.ClassVar[dict[str, RuntimeType]]  # value = {'HAL_Runtime_RoboRIO': <RuntimeType.HAL_Runtime_RoboRIO: 0>, 'HAL_Runtime_RoboRIO2': <RuntimeType.HAL_Runtime_RoboRIO2: 1>, 'HAL_Runtime_Simulation': <RuntimeType.HAL_Runtime_Simulation: 2>, 'HAL_Runtime_SystemCore': <RuntimeType.HAL_Runtime_SystemCore: 3>}
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
class SerialPort:
    """
    Members:
    
      Onboard
    
      MXP
    
      USB1
    
      USB2
    """
    MXP: typing.ClassVar[SerialPort]  # value = <SerialPort.MXP: 1>
    Onboard: typing.ClassVar[SerialPort]  # value = <SerialPort.Onboard: 0>
    USB1: typing.ClassVar[SerialPort]  # value = <SerialPort.USB1: 2>
    USB2: typing.ClassVar[SerialPort]  # value = <SerialPort.USB2: 3>
    __members__: typing.ClassVar[dict[str, SerialPort]]  # value = {'Onboard': <SerialPort.Onboard: 0>, 'MXP': <SerialPort.MXP: 1>, 'USB1': <SerialPort.USB1: 2>, 'USB2': <SerialPort.USB2: 3>}
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
class SimBoolean(SimValue):
    """
    Wrapper around a HAL simulator boolean value.
    
    It is not useful to construct these directly -- they are returned from
    :meth:`.SimDeviceSim.getBoolean` or :meth:`.SimDevice.createBoolean`.
    """
    value: bool
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValueBoolean().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    def get(self) -> bool:
        """
        Gets the simulated value.
        
        :returns: The current value
        """
    def set(self, value: bool) -> None:
        """
        Sets the simulated value.
        
        :param value: the value to set
        """
class SimDevice:
    """
    Wrapper around a HAL simulation 'device'
    
    This creates a simulated 'device' object that can be interacted with
    from user SimDeviceSim objects or via the Simulation GUI.
    
    .. note:: To interact with an existing device use
              :class:`hal.simulation.SimDeviceSim` instead.
    """
    class Direction:
        """
        Direction of a simulated value (from the perspective of user code).
        
        Members:
        
          kInput
        
          kOutput
        
          kBidir
        """
        __members__: typing.ClassVar[dict[str, SimDevice.Direction]]  # value = {'kInput': <Direction.kInput: 0>, 'kOutput': <Direction.kOutput: 1>, 'kBidir': <Direction.kBidir: 2>}
        kBidir: typing.ClassVar[SimDevice.Direction]  # value = <Direction.kBidir: 2>
        kInput: typing.ClassVar[SimDevice.Direction]  # value = <Direction.kInput: 0>
        kOutput: typing.ClassVar[SimDevice.Direction]  # value = <Direction.kOutput: 1>
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
    def __bool__(self) -> bool:
        ...
    @typing.overload
    def __init__(self, name: str) -> None:
        """
        Creates a simulated device.
        
        The device name must be unique.  Returns null if the device name
        already exists.  If multiple instances of the same device are desired,
        recommend appending the instance/unique identifier in brackets to the base
        name, e.g. "device[1]".
        
        Using a device name of the form "Type:Name" will create a WebSockets node
        with a type value of "Type" and a device value of "Name"
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name: device name
        """
    @typing.overload
    def __init__(self, name: str, index: typing.SupportsInt) -> None:
        """
        Creates a simulated device.
        
        The device name must be unique.  Returns null if the device name
        already exists.  This is a convenience method that appends index in
        brackets to the device name, e.g. passing index=1 results in "device[1]"
        for the device name.
        
        Using a device name of the form "Type:Name" will create a WebSockets node
        with a type value of "Type" and a device value of "Name"
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:  device name
        :param index: device index number to append to name
        """
    @typing.overload
    def __init__(self, name: str, index: typing.SupportsInt, channel: typing.SupportsInt) -> None:
        """
        Creates a simulated device.
        
        The device name must be unique.  Returns null if the device name
        already exists.  This is a convenience method that appends index and
        channel in brackets to the device name, e.g. passing index=1 and channel=2
        results in "device[1,2]" for the device name.
        
        Using a device name of the form "Type:Name" will create a WebSockets node
        with a type value of "Type" and a device value of "Name"
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:    device name
        :param index:   device index number to append to name
        :param channel: device channel number to append to name
        """
    def __repr__(self) -> str:
        ...
    def createBoolean(self, name: str, direction: typing.SupportsInt, initialValue: bool) -> SimBoolean:
        """
        Creates a boolean value on the simulated device.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param initialValue: initial value
        
        :returns: simulated boolean value object
        """
    def createDouble(self, name: str, direction: typing.SupportsInt, initialValue: typing.SupportsFloat) -> SimDouble:
        """
        Creates a double value on the simulated device.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param initialValue: initial value
        
        :returns: simulated double value object
        """
    def createEnum(self, name: str, direction: typing.SupportsInt, options: list[str], initialValue: typing.SupportsInt) -> SimEnum:
        """
        Creates an enumerated value on the simulated device.
        
        Enumerated values are always in the range 0 to numOptions-1.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param options:      array of option descriptions
        :param initialValue: initial value (selection)
        
        :returns: simulated enum value object
        """
    def createEnumDouble(self, name: str, direction: typing.SupportsInt, options: list[str], optionValues: list[typing.SupportsFloat], initialValue: typing.SupportsInt) -> SimEnum:
        """
        Creates an enumerated value on the simulated device with double values.
        
        Enumerated values are always in the range 0 to numOptions-1.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param options:      array of option descriptions
        :param optionValues: array of option values (must be the same size as
                             options)
        :param initialValue: initial value (selection)
        
        :returns: simulated enum value object
        """
    def createInt(self, name: str, direction: typing.SupportsInt, initialValue: typing.SupportsInt) -> SimInt:
        """
        Creates an int value on the simulated device.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param initialValue: initial value
        
        :returns: simulated double value object
        """
    def createLong(self, name: str, direction: typing.SupportsInt, initialValue: typing.SupportsInt) -> SimLong:
        """
        Creates a long value on the simulated device.
        
        If not in simulation, results in an "empty" object that evaluates to false
        in a boolean context.
        
        :param name:         value name
        :param direction:    input/output/bidir (from perspective of user code)
        :param initialValue: initial value
        
        :returns: simulated double value object
        """
    def getName(self) -> str:
        """
        Get the name of the simulated device.
        
        :returns: name
        """
    @property
    def name(self) -> str:
        ...
class SimDouble(SimValue):
    """
    Wrapper around a HAL simulator double value.
    
    It is not useful to construct these directly -- they are returned from
    :meth:`.SimDeviceSim.getDouble` or :meth:`.SimDevice.createDouble`.
    """
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValueDouble().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    def get(self) -> float:
        """
        Gets the simulated value.
        
        :returns: The current value
        """
    def reset(self) -> None:
        """
        Resets the simulated value to 0. Use this instead of Set(0) for resetting
        incremental sensor values like encoder counts or gyro accumulated angle
        to ensure correct behavior in a distributed system (e.g. WebSockets).
        """
    def set(self, value: typing.SupportsFloat) -> None:
        """
        Sets the simulated value.
        
        :param value: the value to set
        """
    @property
    def value(self) -> float:
        ...
    @value.setter
    def value(self, arg1: typing.SupportsFloat) -> None:
        ...
class SimEnum(SimValue):
    """
    Wrapper around a HAL simulator enum value.
    
    It is not useful to construct these directly -- they are returned from
    :meth:`.SimDeviceSim.getEnum` or :meth:`.SimDevice.createEnum`.
    """
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValueEnum().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    def get(self) -> int:
        """
        Gets the simulated value.
        
        :returns: The current value
        """
    def set(self, value: typing.SupportsInt) -> None:
        """
        Sets the simulated value.
        
        :param value: the value to set
        """
    @property
    def value(self) -> int:
        ...
    @value.setter
    def value(self, arg1: typing.SupportsInt) -> None:
        ...
class SimInt(SimValue):
    """
    Wrapper around a HAL simulator int value handle.
    
    It is not useful to construct these directly, they are returned
    from various functions.
    """
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValueInt().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    def get(self) -> int:
        """
        Gets the simulated value.
        
        :returns: The current value
        """
    def reset(self) -> None:
        """
        Resets the simulated value to 0. Use this instead of Set(0) for resetting
        incremental sensor values like encoder counts or gyro accumulated angle
        to ensure correct behavior in a distributed system (e.g. WebSockets).
        """
    def set(self, value: typing.SupportsInt) -> None:
        """
        Sets the simulated value.
        
        :param value: the value to set
        """
    @property
    def value(self) -> int:
        ...
    @value.setter
    def value(self, arg1: typing.SupportsInt) -> None:
        ...
class SimLong(SimValue):
    """
    Wrapper around a HAL simulator long value handle.
    
    It is not useful to construct these directly, they are returned
    from various functions.
    """
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValueLong().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    def get(self) -> int:
        """
        Gets the simulated value.
        
        :returns: The current value
        """
    def reset(self) -> None:
        """
        Resets the simulated value to 0. Use this instead of Set(0) for resetting
        incremental sensor values like encoder counts or gyro accumulated angle
        to ensure correct behavior in a distributed system (e.g. WebSockets).
        """
    def set(self, value: typing.SupportsInt) -> None:
        """
        Sets the simulated value.
        
        :param value: the value to set
        """
    @property
    def value(self) -> int:
        ...
    @value.setter
    def value(self, arg1: typing.SupportsInt) -> None:
        ...
class SimValue:
    """
    Readonly wrapper around a HAL simulator value.
    
    It is not useful to construct these directly -- they are returned from
    :meth:`.SimDeviceSim.getValue` or :meth:`.SimDevice.createValue`.
    """
    def __bool__(self) -> bool:
        ...
    def __init__(self, handle: typing.SupportsInt) -> None:
        """
        Wraps a simulated value handle as returned by HAL_CreateSimValue().
        
        :param handle: simulated value handle
        """
    def __repr__(self) -> str:
        ...
    @property
    def type(self) -> Type:
        ...
    @property
    def value(self) -> typing.Any:
        ...
class SimValueDirection:
    """
    Direction of a simulated value (from the perspective of user code).
    
    Members:
    
      HAL_SimValueInput : input to user code from the simulator
    
      HAL_SimValueOutput : output from user code to the simulator
    
      HAL_SimValueBidir : bidirectional between user code and simulator
    """
    HAL_SimValueBidir: typing.ClassVar[SimValueDirection]  # value = <SimValueDirection.HAL_SimValueBidir: 2>
    HAL_SimValueInput: typing.ClassVar[SimValueDirection]  # value = <SimValueDirection.HAL_SimValueInput: 0>
    HAL_SimValueOutput: typing.ClassVar[SimValueDirection]  # value = <SimValueDirection.HAL_SimValueOutput: 1>
    __members__: typing.ClassVar[dict[str, SimValueDirection]]  # value = {'HAL_SimValueInput': <SimValueDirection.HAL_SimValueInput: 0>, 'HAL_SimValueOutput': <SimValueDirection.HAL_SimValueOutput: 1>, 'HAL_SimValueBidir': <SimValueDirection.HAL_SimValueBidir: 2>}
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
class Type:
    """
    Members:
    
      UNASSIGNED
    
      BOOLEAN
    
      DOUBLE
    
      ENUM
    
      INT
    
      LONG
    """
    BOOLEAN: typing.ClassVar[Type]  # value = <Type.BOOLEAN: 1>
    DOUBLE: typing.ClassVar[Type]  # value = <Type.DOUBLE: 2>
    ENUM: typing.ClassVar[Type]  # value = <Type.ENUM: 4>
    INT: typing.ClassVar[Type]  # value = <Type.INT: 8>
    LONG: typing.ClassVar[Type]  # value = <Type.LONG: 16>
    UNASSIGNED: typing.ClassVar[Type]  # value = <Type.UNASSIGNED: 0>
    __members__: typing.ClassVar[dict[str, Type]]  # value = {'UNASSIGNED': <Type.UNASSIGNED: 0>, 'BOOLEAN': <Type.BOOLEAN: 1>, 'DOUBLE': <Type.DOUBLE: 2>, 'ENUM': <Type.ENUM: 4>, 'INT': <Type.INT: 8>, 'LONG': <Type.LONG: 16>}
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
class Value:
    def __repr__(self) -> str:
        ...
    @property
    def type(self) -> Type:
        ...
    @property
    def value(self) -> typing.Any:
        ...
def CAN_CloseStreamSession(sessionHandle: typing.SupportsInt) -> None:
    """
    Closes a CAN stream.
    
    :param sessionHandle: the session to close
    """
def CAN_GetCANStatus(busId: typing.SupportsInt) -> tuple[float, int, int, int, int, int]:
    """
    Gets CAN status information.
    
    :param in:  busId                 the bus number
    :param out: percentBusUtilization the bus utilization
    :param out: busOffCount           the number of bus off errors
    :param out: txFullCount           the number of tx full errors
    :param out: receiveErrorCount     the number of receive errors
    :param out: transmitErrorCount    the number of transmit errors
    :param out: status                Error status variable. 0 on success.
    """
def CAN_OpenStreamSession(busId: typing.SupportsInt, messageId: typing.SupportsInt, messageIDMask: typing.SupportsInt, maxMessages: typing.SupportsInt) -> tuple[int, int]:
    """
    Opens a CAN stream.
    
    :param in:  busId                   the bus number
    :param in:  messageId     the message ID to read
    :param in:  messageIDMask the message ID mask
    :param in:  maxMessages   the maximum number of messages to stream
    :param out: status        Error status variable. 0 on success.
    
    :returns: the stream handle
    """
def CAN_ReceiveMessage(busId: typing.SupportsInt, messageId: typing.SupportsInt, message: CANReceiveMessage) -> int:
    """
    Receives a CAN message.
    
    :param in:  busId       The CAN bus number
    :param in:  messageId the message id
    :param out: message  The CAN message
    :param out: status     Error status variable. 0 on success.
    """
def CAN_SendMessage(busId: typing.SupportsInt, messageId: typing.SupportsInt, message: CANMessage, periodMs: typing.SupportsInt) -> int:
    """
    Sends a CAN message.
    
    :param in:  busId     the CAN bus number
    :param in:  messageId the message id
    :param in:  message   the CAN message
    :param in:  periodMs  the repeat period
    :param out: status   Error status variable. 0 on success.
    """
def __test_senderr() -> None:
    ...
def allocateDigitalPWM() -> tuple[int, int]:
    """
    Allocates a DO PWM Generator.
    
    :param out: status Error status variable. 0 on success.
    
    :returns: the allocated digital PWM handle
    """
def cancelNotifierAlarm(notifierHandle: typing.SupportsInt) -> int:
    """
    Cancels the next notifier alarm.
    
    This does not cause HAL_WaitForNotifierAlarm to return.
    
    :param in:  notifierHandle the notifier handle
    :param out: status Error status variable. 0 on success.
    """
def checkAnalogInputChannel(channel: typing.SupportsInt) -> int:
    """
    Checks that the analog output channel number is valid.
    Verifies that the analog channel number is one of the legal channel numbers.
    Channel numbers are 0-based.
    
    :param in: channel The analog output channel number.
    
    :returns: Analog channel is valid
    """
def checkAnalogModule(module: typing.SupportsInt) -> int:
    """
    Checks that the analog module number is valid.
    
    :param in: module The analog module number.
    
    :returns: Analog module is valid and present
    """
def checkCTREPCMSolenoidChannel(channel: typing.SupportsInt) -> int:
    """
    Checks if a solenoid channel number is valid.
    
    :param in: channel the channel to check
    
    :returns: true if the channel is valid, otherwise false
    """
def checkDIOChannel(channel: typing.SupportsInt) -> int:
    """
    Checks if a DIO channel is valid.
    
    :param channel: the channel number to check
    
    :returns: true if the channel is valid, otherwise false
    """
def checkPWMChannel(channel: typing.SupportsInt) -> int:
    """
    Checks if a pwm channel is valid.
    
    :param channel: the channel to check
    
    :returns: true if the channel is valid, otherwise false
    """
def checkPowerDistributionChannel(handle: typing.SupportsInt, channel: typing.SupportsInt) -> int:
    """
    Checks if a PowerDistribution channel is valid.
    
    :param handle:  the module handle
    :param channel: the channel to check
    
    :returns: true if the channel is valid, otherwise false
    """
def checkPowerDistributionModule(module: typing.SupportsInt, type: PowerDistributionType) -> int:
    """
    Checks if a PowerDistribution module is valid.
    
    :param module: the module to check
    :param type:   the type of module
    
    :returns: true if the module is valid, otherwise false
    """
def checkREVPHModuleNumber(module: typing.SupportsInt) -> int:
    """
    Checks if a PH module (CAN ID) is valid.
    
    :param in: module the module to check
    
    :returns: true if the module is valid, otherwise false
    """
def checkREVPHSolenoidChannel(channel: typing.SupportsInt) -> int:
    """
    Checks if a solenoid channel number is valid.
    
    :param in: channel the channel to check
    
    :returns: true if the channel is valid, otherwise false
    """
def cleanCAN(handle: typing.SupportsInt) -> None:
    """
    Frees a CAN device
    
    :param handle: the CAN handle
    """
def cleanNotifier(notifierHandle: typing.SupportsInt) -> None:
    """
    Cleans a notifier.
    
    Note this also stops a notifier if it is already running.
    
    :param in: notifierHandle the notifier handle
    """
def cleanPowerDistribution(handle: typing.SupportsInt) -> None:
    """
    Cleans a PowerDistribution module.
    
    :param handle: the module handle
    """
def clearAllCTREPCMStickyFaults(handle: typing.SupportsInt) -> int:
    """
    Clears all sticky faults on this device.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    """
def clearPowerDistributionStickyFaults(handle: typing.SupportsInt) -> int:
    """
    Clears any PowerDistribution sticky faults.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    """
def clearREVPHStickyFaults(handle: typing.SupportsInt) -> int:
    """
    Clears the sticky faults.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    """
def clearSerial(handle: typing.SupportsInt) -> int:
    """
    Clears the receive buffer of the serial port.
    
    :param in:  handle  the serial port handle
    :param out: status the error code, or 0 for success
    """
def closeI2C(port: I2CPort) -> None:
    """
    Closes an I2C port
    
    :param port: The I2C port, 0 for the on-board, 1 for the MXP.
    """
def closeSerial(handle: typing.SupportsInt) -> None:
    """
    Closes a serial port.
    
    :param in: handle  the serial port handle to close
    """
def createHandle(index: typing.SupportsInt, handleType: HandleEnum, version: typing.SupportsInt) -> int:
    """
    Create a handle for a specific index, type and version.
    
    Note the version is not checked on the roboRIO.
    
    :param index:      the index
    :param handleType: the handle type
    :param version:    the handle version
    
    :returns: the created handle
    """
def disableSerialTermination(handle: typing.SupportsInt) -> int:
    """
    Disables a termination character for reads.
    
    :param in:  handle  the serial port handle
    :param out: status the error code, or 0 for success
    """
def enableSerialTermination(handle: typing.SupportsInt, terminator: str) -> int:
    """
    Sets the termination character that terminates a read.
    
    By default this is disabled.
    
    :param in:  handle      the serial port handle
    :param in:  terminator  the termination character to set
    :param out: status     the error code, or 0 for success
    """
def exitMain() -> None:
    """
    Causes HAL_RunMain() to exit.
    
    If HAL_SetMain() has been called, this calls the exit function provided
    to that function.
    """
def expandFPGATime(unexpandedLower: typing.SupportsInt) -> tuple[int, int]:
    """
    Given an 32 bit FPGA time, expand it to the nearest likely 64 bit FPGA time.
    
    Note: This is making the assumption that the timestamp being converted is
    always in the past.  If you call this with a future timestamp, it probably
    will make it in the past.  If you wait over 70 minutes between capturing the
    bottom 32 bits of the timestamp and expanding it, you will be off by
    multiples of 1<<32 microseconds.
    
    :param in:  unexpandedLower 32 bit FPGA time
    :param out: status the error code, or 0 for success
    
    :returns: The current time in microseconds according to the FPGA (since FPGA
              reset) as a 64 bit number.
    """
def fireCTREPCMOneShot(handle: typing.SupportsInt, index: typing.SupportsInt) -> int:
    """
    Fire a single solenoid shot.
    
    :param in:  handle  the PCM handle
    :param in:  index solenoid index
    :param out: status Error status variable. 0 on success.
    """
def fireREVPHOneShot(handle: typing.SupportsInt, index: typing.SupportsInt, durMs: typing.SupportsInt) -> int:
    """
    Fire a single solenoid shot for the specified duration.
    
    :param in:  handle  the PH handle
    :param in:  index solenoid index
    :param in:  durMs shot duration in ms
    :param out: status Error status variable. 0 on success.
    """
def flushSerial(handle: typing.SupportsInt) -> int:
    """
    Flushes the serial write buffer out to the port.
    
    :param in:  handle  the serial port handle
    :param out: status the error code, or 0 for success
    """
def format_as(order: AddressableLEDColorOrder) -> int:
    ...
def freeAddressableLED(handle: typing.SupportsInt) -> None:
    """
    Free the Addressable LED Handle.
    
    :param in: handle the Addressable LED handle to free
    """
def freeAnalogInputPort(analogPortHandle: typing.SupportsInt) -> None:
    """
    Frees an analog input port.
    
    :param analogPortHandle: Handle to the analog port.
    """
def freeCTREPCM(handle: typing.SupportsInt) -> None:
    """
    Frees a PCM handle.
    
    :param in: handle the PCMhandle
    """
def freeCounter(counterHandle: typing.SupportsInt) -> None:
    """
    Frees a counter.
    
    :param in: counterHandle the counter handle
    """
def freeDIOPort(dioPortHandle: typing.SupportsInt) -> None:
    """
    Frees a DIO port.
    
    :param dioPortHandle: the DIO channel handle
    """
def freeDigitalPWM(pwmGenerator: typing.SupportsInt) -> None:
    """
    Frees the resource associated with a DO PWM generator.
    
    :param in: pwmGenerator the digital PWM handle
    """
def freeDutyCycle(dutyCycleHandle: typing.SupportsInt) -> None:
    """
    Free a DutyCycle.
    
    :param dutyCycleHandle: the duty cycle handle
    """
def freeEncoder(encoderHandle: typing.SupportsInt) -> None:
    """
    Frees an encoder.
    
    :param in: encoderHandle the encoder handle
    """
def freePWMPort(pwmPortHandle: typing.SupportsInt) -> None:
    """
    Frees a PWM port.
    
    :param in: pwmPortHandle the pwm handle
    """
def freeREVPH(handle: typing.SupportsInt) -> None:
    """
    Frees a PH handle.
    
    :param in: handle the PH handle
    """
def getAllJoystickData(axes: JoystickAxes, povs: JoystickPOVs, buttons: JoystickButtons) -> None:
    ...
def getAllianceStation() -> tuple[AllianceStationID, int]:
    """
    Gets the current alliance station ID.
    
    :param out: status the error code, or 0 for success
    
    :returns: the alliance station ID
    """
def getAnalogAverageBits(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the number of averaging bits.
    
    This gets the number of averaging bits from the FPGA. The actual number of
    averaged samples is 2**bits. The averaging is done automatically in the FPGA.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: Bits to average.
    """
def getAnalogAverageValue(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets a sample from the output of the oversample and average engine for the
    channel.
    
    The sample is 12-bit + the value configured in SetOversampleBits().
    The value configured in SetAverageBits() will cause this value to be averaged
    2**bits number of samples. This is not a sliding window.  The sample will not
    change until 2**(OversampleBits + AverageBits) samples have been acquired
    from the module on this channel. Use GetAverageVoltage() to get the analog
    value in calibrated units.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: A sample from the oversample and average engine for the channel.
    """
def getAnalogAverageVoltage(analogPortHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets a scaled sample from the output of the oversample and average engine for
    the channel.
    
    The value is scaled to units of Volts using the calibrated scaling data from
    GetLSBWeight() and GetOffset(). Using oversampling will cause this value to
    be higher resolution, but it will update more slowly. Using averaging will
    cause this value to be more stable, but it will update more slowly.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: A scaled sample from the output of the oversample and average engine
              for the channel.
    """
def getAnalogLSBWeight(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the factory scaling least significant bit weight constant.
    The least significant bit weight constant for the channel that was calibrated
    in manufacturing and stored in an eeprom in the module.
    
    Volts = ((LSB_Weight * 1e-9) * raw) - (Offset * 1e-9)
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: Least significant bit weight.
    """
def getAnalogOffset(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the factory scaling offset constant.
    The offset constant for the channel that was calibrated in manufacturing and
    stored in an eeprom in the module.
    
    Volts = ((LSB_Weight * 1e-9) * raw) - (Offset * 1e-9)
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status Error status variable. 0 on success.
    
    :returns: Offset constant.
    """
def getAnalogOversampleBits(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the number of oversample bits.
    
    This gets the number of oversample bits from the FPGA. The actual number of
    oversampled values is 2**bits. The oversampling is done automatically in the
    FPGA.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status          the error code, or 0 for success
    
    :returns: Bits to oversample.
    """
def getAnalogSampleRate() -> tuple[float, int]:
    """
    Gets the current sample rate.
    
    This assumes one entry in the scan list.
    This is a global setting for the Athena and effects all channels.
    
    :param out: status the error code, or 0 for success
    
    :returns: Sample rate.
    """
def getAnalogValue(analogPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets a sample straight from the channel on this module.
    
    The sample is a 12-bit value representing the 0V to 3.3V range of the A/D
    converter in the module. The units are in A/D converter codes.  Use
    GetVoltage() to get the analog value in calibrated units.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: A sample straight from the channel on this module.
    """
def getAnalogValueToVolts(analogPortHandle: typing.SupportsInt, rawValue: typing.SupportsInt) -> tuple[float, int]:
    """
    Get the analog voltage from a raw value.
    
    :param in:  analogPortHandle  Handle to the analog port the values were read
                from.
    :param in:  rawValue          The raw analog value
    :param out: status           Error status variable. 0 on success.
    
    :returns: The voltage relating to the value
    """
def getAnalogVoltage(analogPortHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets a scaled sample straight from the channel on this module.
    
    The value is scaled to units of Volts using the calibrated scaling data from
    GetLSBWeight() and GetOffset().
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param out: status the error code, or 0 for success
    
    :returns: A scaled sample straight from the channel on this module.
    """
def getAnalogVoltsToValue(analogPortHandle: typing.SupportsInt, voltage: typing.SupportsFloat) -> tuple[int, int]:
    """
    Converts a voltage to a raw value for a specified channel.
    
    This process depends on the calibration of each channel, so the channel must
    be specified.
    
    @todo This assumes raw values.  Oversampling not supported as is.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param in:  voltage The voltage to convert.
    :param out: status the error code, or 0 for success
    
    :returns: The raw value for the channel.
    """
def getBrownedOut() -> tuple[int, int]:
    """
    Gets if the system is in a browned out state.
    
    :param out: status the error code, or 0 for success
    
    :returns: true if the system is in a low voltage brown out, false otherwise
    """
def getBrownoutVoltage() -> tuple[float, int]:
    """
    Get the current brownout voltage setting.
    
    :param out: status the error code, or 0 for success
    
    :returns: The brownout voltage
    """
def getCPUTemp() -> tuple[float, int]:
    """
    Get the current CPU temperature in degrees Celsius
    
    :param out: status the error code, or 0 for success
    
    :returns: current CPU temperature in degrees Celsius
    """
def getCTREPCMClosedLoopControl(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get whether the PCM closed loop control is enabled.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if closed loop control is enabled, otherwise false.
    """
def getCTREPCMCompressor(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get whether compressor is turned on.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: true if the compressor is turned on
    """
def getCTREPCMCompressorCurrent(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the current drawn by the compressor.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: The current drawn by the compressor in amps.
    """
def getCTREPCMCompressorCurrentTooHighFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Return whether the compressor current is currently too high.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if the compressor current is too high, otherwise false.
              @see HAL_GetCTREPCMCompressorShortedStickyFault
    """
def getCTREPCMCompressorCurrentTooHighStickyFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the compressor current has been too high since sticky
    faults were last cleared. This fault is persistent and can be cleared by
    HAL_ClearAllCTREPCMStickyFaults()
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if the compressor current has been too high since sticky
              faults were last cleared.
              @see HAL_GetCTREPCMCompressorCurrentTooHighFault()
    """
def getCTREPCMCompressorNotConnectedFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the compressor is currently disconnected.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if compressor is currently disconnected, otherwise false.
              @see HAL_GetCTREPCMCompressorNotConnectedStickyFault()
    """
def getCTREPCMCompressorNotConnectedStickyFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the compressor has been disconnected since sticky faults
    were last cleared. This fault is persistent and can be cleared by
    HAL_ClearAllCTREPCMStickyFaults()
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if the compressor has been disconnected since sticky faults
              were last cleared, otherwise false.
              @see HAL_GetCTREPCMCompressorShortedFault()
    """
def getCTREPCMCompressorShortedFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the compressor is currently shorted.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if the compressor is currently shorted, otherwise false.
              @see HAL_GetCTREPCMCompressorShortedStickyFault
    """
def getCTREPCMCompressorShortedStickyFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the compressor has been shorted since sticky faults were
    last cleared. This fault is persistent and can be cleared by
    HAL_ClearAllCTREPCMStickyFaults()
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if the compressor has been shorted since sticky faults were
              last cleared, otherwise false.
              @see HAL_GetCTREPCMCompressorShortedFault()
    """
def getCTREPCMPressureSwitch(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns the state of the pressure switch.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if pressure switch indicates that the system is full,
              otherwise false.
    """
def getCTREPCMSolenoidDisabledList(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get a bitmask of disabled solenoids.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: Bitmask indicating disabled solenoids. The LSB represents solenoid 0.
    """
def getCTREPCMSolenoidVoltageFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the solenoid is currently reporting a voltage fault.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if solenoid is reporting a fault, otherwise false.
              @see HAL_GetCTREPCMSolenoidVoltageStickyFault()
    """
def getCTREPCMSolenoidVoltageStickyFault(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns whether the solenoid has reported a voltage fault since sticky faults
    were last cleared. This fault is persistent and can be cleared by
    HAL_ClearAllCTREPCMStickyFaults()
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if solenoid is reporting a fault, otherwise false.
              @see HAL_GetCTREPCMSolenoidVoltageFault()
    """
def getCTREPCMSolenoids(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets a bitmask of solenoid values.
    
    :param in:  handle  the PCM handle
    :param out: status Error status variable. 0 on success.
    
    :returns: Bitmask containing the state of the solenoids. The LSB represents
              solenoid 0.
    """
def getComments() -> str:
    """
    Returns the comments from the roboRIO web interface.
    
    :param out: comments The comments string. Free with WPI_FreeString
    """
def getCommsDisableCount() -> tuple[int, int]:
    """
    Gets the number of times the system has been disabled due to communication
    errors with the Driver Station.
    
    :returns: number of disables due to communication errors.
    """
def getControlWord(controlWord: ControlWord) -> int:
    """
    Gets the current control word of the driver station.
    
    The control word contains the robot state.
    
    :param controlWord: the control word (out)
    
    :returns: the error code, or 0 for success
    """
def getCounter(counterHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Reads the current counter value.
    
    Reads the value at this instant. It may still be running, so it reflects the
    current value. Next time it is read, it might have a different value.
    
    :param in:  counterHandle the counter handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the current counter value
    """
def getCounterPeriod(counterHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the Period of the most recent count.
    
    Returns the time interval of the most recent count. This can be used for
    velocity calculations to determine shaft speed.
    
    :param in:  counterHandle the counter handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the period of the last two pulses in units of seconds
    """
def getCounterStopped(counterHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Determines if the clock is stopped.
    
    Determine if the clocked input is stopped based on the MaxPeriod value set
    using the SetMaxPeriod method. If the clock exceeds the MaxPeriod, then the
    device (and counter) are assumed to be stopped and it returns true.
    
    :param in:  counterHandle the counter handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: true if the most recent counter period exceeds the MaxPeriod value
              set by SetMaxPeriod
    """
def getCurrentThreadPriority(isRealTime: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the thread priority for the current thread.
    
    :param out: isRealTime Set to true if thread is real-time, otherwise false.
    :param out: status     Error status variable. 0 on success.
    
    :returns: The current thread priority. For real-time, this is 1-99 with 99
              being highest. For non-real-time, this is 0. See "man 7 sched" for
              details.
    """
def getDIO(dioPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Reads a digital value from a DIO channel.
    
    :param in:  dioPortHandle the digital port handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the state of the specified channel
    """
def getDIODirection(dioPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Reads the direction of a DIO channel.
    
    :param in:  dioPortHandle the digital port handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: true for input, false for output
    """
def getDutyCycleFrequency(dutyCycleHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Get the frequency of the duty cycle signal.
    
    :param in:  dutyCycleHandle the duty cycle handle
    :param out: status Error status variable. 0 on success.
    
    :returns: frequency in Hertz
    """
def getDutyCycleHighTime(dutyCycleHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get the raw high time of the duty cycle signal.
    
    :param in:  dutyCycleHandle the duty cycle handle
    :param out: status Error status variable. 0 on success.
    
    :returns: high time of last pulse in nanoseconds
    """
def getDutyCycleOutput(dutyCycleHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Get the output ratio of the duty cycle signal.
    
    0 means always low, 1 means always high.
    
    :param in:  dutyCycleHandle the duty cycle handle
    :param out: status Error status variable. 0 on success.
    
    :returns: output ratio between 0 and 1
    """
def getEncoder(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the current counts of the encoder after encoding type scaling.
    
    This is scaled by the value passed during initialization to encodingType.
    
    :param in:  encoderHandle the encoder handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the current scaled count
    """
def getEncoderDecodingScaleFactor(encoderHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the decoding scale factor of the encoder.
    
    This is used to perform the scaling from raw to type scaled values.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the scale value for the encoder
    """
def getEncoderDirection(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the last direction the encoder value changed.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the last direction the encoder value changed
    """
def getEncoderDistance(encoderHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the current distance traveled by the encoder.
    
    This is the encoder count scaled by the distance per pulse set for the
    encoder.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the encoder distance (units are determined by the units
              passed to HAL_SetEncoderDistancePerPulse)
    """
def getEncoderDistancePerPulse(encoderHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the user set distance per pulse of the encoder.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the set distance per pulse
    """
def getEncoderEncodingScale(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the encoder scale value.
    
    This is set by the value passed during initialization to encodingType.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the encoder scale value
    """
def getEncoderEncodingType(encoderHandle: typing.SupportsInt) -> tuple[EncoderEncodingType, int]:
    """
    Gets the encoding type of the encoder.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the encoding type
    """
def getEncoderFPGAIndex(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the FPGA index of the encoder.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the FPGA index of the encoder
    """
def getEncoderPeriod(encoderHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the Period of the most recent count.
    
    Returns the time interval of the most recent count. This can be used for
    velocity calculations to determine shaft speed.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the period of the last two pulses in units of seconds
    """
def getEncoderRate(encoderHandle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the current rate of the encoder.
    
    This is the encoder period scaled by the distance per pulse set for the
    encoder.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the encoder rate (units are determined by the units passed to
              HAL_SetEncoderDistancePerPulse, time value is seconds)
    """
def getEncoderRaw(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the raw counts of the encoder.
    
    This is not scaled by any values.
    
    :param in:  encoderHandle the encoder handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the raw encoder count
    """
def getEncoderSamplesToAverage(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the current samples to average value.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the current samples to average value
    """
def getEncoderStopped(encoderHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Determines if the clock is stopped.
    
    Determines if the clocked input is stopped based on the MaxPeriod value set
    using the SetMaxPeriod method. If the clock exceeds the MaxPeriod, then the
    device (and encoder) are assumed to be stopped and it returns true.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: true if the most recent encoder period exceeds the MaxPeriod value
              set by SetMaxPeriod
    """
def getErrorMessage(code: typing.SupportsInt) -> str:
    """
    Gets the error message for a specific status code.
    
    :param code: the status code
    
    :returns: the error message for the code. This does not need to be freed.
    """
def getFPGARevision() -> tuple[int, int]:
    """
    Returns the FPGA Revision number.
    
    The format of the revision is 3 numbers.
    The 12 most significant bits are the Major Revision.
    the next 8 bits are the Minor Revision.
    The 12 least significant bits are the Build Number.
    
    :param out: status the error code, or 0 for success
    
    :returns: FPGA Revision number.
    """
def getFPGATime() -> tuple[int, int]:
    """
    Reads the microsecond-resolution timer on the FPGA.
    
    :param out: status the error code, or 0 for success
    
    :returns: The current time in microseconds according to the FPGA (since FPGA
              reset).
    """
def getFPGAVersion() -> tuple[int, int]:
    """
    Returns the FPGA Version number.
    
    For now, expect this to be competition year.
    
    :param out: status the error code, or 0 for success
    
    :returns: FPGA Version number.
    """
def getHandleIndex(handle: typing.SupportsInt) -> int:
    """
    Get the handle index from a handle.
    
    :param handle: the handle
    
    :returns: the index
    """
def getHandleType(handle: typing.SupportsInt) -> HandleEnum:
    """
    Get the handle type from a handle.
    
    :param handle: the handle
    
    :returns: the type
    """
def getHandleTypedIndex(handle: typing.SupportsInt, enumType: HandleEnum, version: typing.SupportsInt) -> int:
    """
    Get if the handle is a correct type and version.
    
    Note the version is not checked on the roboRIO.
    
    :param handle:   the handle
    :param enumType: the type to check
    :param version:  the handle version to check
    
    :returns: true if the handle is proper version and type, otherwise
              false.
    """
def getJoystickAxes(joystickNum: typing.SupportsInt, axes: JoystickAxes) -> int:
    """
    Gets the axes of a specific joystick.
    
    :param joystickNum: the joystick number
    :param axes:        the axes values (output)
    
    :returns: the error code, or 0 for success
    """
def getJoystickAxisType(joystickNum: typing.SupportsInt, axis: typing.SupportsInt) -> int:
    """
    Gets the type of a specific joystick axis.
    
    This is device specific, and different depending on what system input type
    the joystick uses.
    
    :param joystickNum: the joystick number
    :param axis:        the axis number
    
    :returns: the enumerated axis type
    """
def getJoystickButtons(joystickNum: typing.SupportsInt, buttons: JoystickButtons) -> int:
    """
    Gets the buttons of a specific joystick.
    
    :param joystickNum: the joystick number
    :param buttons:     the button values (output)
    
    :returns: the error code, or 0 for success
    """
def getJoystickDescriptor(joystickNum: typing.SupportsInt, desc: JoystickDescriptor) -> int:
    """
    Retrieves the Joystick Descriptor for particular slot.
    
    :param joystickNum: the joystick number
    :param out:         desc   descriptor (data transfer object) to fill in. desc is
                        filled in regardless of success. In other words, if
                        descriptor is not available, desc is filled in with
                        default values matching the init-values in Java and C++
                        Driver Station for when caller requests a too-large
                        joystick index.
    
    :returns: error code reported from Network Comm back-end.  Zero is good,
              nonzero is bad.
    """
def getJoystickIsGamepad(joystickNum: typing.SupportsInt) -> int:
    """
    Gets whether a specific joystick is considered to be an Gamepad.
    
    :param joystickNum: the joystick number
    
    :returns: true if gamepad, false otherwise
    """
def getJoystickName(joystickNum: typing.SupportsInt) -> str:
    """
    Gets the name of a joystick.
    
    The returned string must be freed with WPI_FreeString
    
    :param name:        the joystick name string
    :param joystickNum: the joystick number
    """
def getJoystickPOVs(joystickNum: typing.SupportsInt, povs: JoystickPOVs) -> int:
    """
    Gets the POVs of a specific joystick.
    
    :param joystickNum: the joystick number
    :param povs:        the POV values (output)
    
    :returns: the error code, or 0 for success
    """
def getJoystickType(joystickNum: typing.SupportsInt) -> int:
    """
    Gets the type of joystick connected.
    
    This is device specific, and different depending on what system input type
    the joystick uses.
    
    :param joystickNum: the joystick number
    
    :returns: the enumerated joystick type
    """
def getLastError() -> tuple[str, int]:
    """
    Gets the last error set on this thread, or the message for the status code.
    
    If passed HAL_USE_LAST_ERROR, the last error set on the thread will be
    returned.
    
    :param out: status the status code, set to the error status code if input is
                HAL_USE_LAST_ERROR
    
    :returns: the error message for the code. This does not need to be freed,
              but can be overwritten by another hal call on the same thread.
    """
def getMatchInfo(info: MatchInfo) -> int:
    """
    Gets info about a specific match.
    
    :param in: info the match info (output)
    
    :returns: the error code, or 0 for success
    """
def getMatchTime() -> tuple[float, int]:
    """
    Return the approximate match time. The FMS does not send an official match
    time to the robots, but does send an approximate match time. The value will
    count down the time remaining in the current period (auto or teleop).
    Warning: This is not an official time (so it cannot be used to dispute ref
    calls or guarantee that a function will trigger before the match ends).
    
    When connected to the real field, this number only changes in full integer
    increments, and always counts down.
    
    When the DS is in practice mode, this number is a floating point number,
    and counts down.
    
    When the DS is in teleop or autonomous mode, this number is a floating
    point number, and counts up.
    
    Simulation matches DS behavior without an FMS connected.
    
    :param out: status the error code, or 0 for success
    
    :returns: Time remaining in current match period (auto or teleop) in seconds
    """
def getNumAddressableLEDs() -> int:
    """
    Gets the number of addressable LED generators in the current system.
    
    :returns: the number of Addressable LED generators
    """
def getNumAnalogInputs() -> int:
    """
    Gets the number of analog inputs in the current system.
    
    :returns: the number of analog inputs
    """
def getNumCTREPCMModules() -> int:
    """
    Gets the number of PCM modules in the current system.
    
    :returns: the number of PCM modules
    """
def getNumCTREPDPChannels() -> int:
    """
    Gets the number of PDP channels in the current system.
    
    :returns: the number of PDP channels
    """
def getNumCTREPDPModules() -> int:
    """
    Gets the number of PDP modules in the current system.
    
    :returns: the number of PDP modules
    """
def getNumCTRESolenoidChannels() -> int:
    """
    Gets the number of solenoid channels in the current system.
    
    :returns: the number of solenoid channels
    """
def getNumCanBuses() -> int:
    """
    Gets the number of can buses in the current system.
    
    :returns: the number of can buses
    """
def getNumCounters() -> int:
    """
    Gets the number of counters in the current system.
    
    :returns: the number of counters
    """
def getNumDigitalChannels() -> int:
    """
    Gets the number of digital channels in the current system.
    
    :returns: the number of digital channels
    """
def getNumDigitalPWMOutputs() -> int:
    """
    Gets the number of digital IO PWM outputs in the current system.
    
    :returns: the number of digital IO PWM outputs
    """
def getNumDutyCycles() -> int:
    """
    Gets the number of duty cycle inputs in the current system.
    
    :returns: the number of Duty Cycle inputs
    """
def getNumEncoders() -> int:
    """
    Gets the number of quadrature encoders in the current system.
    
    :returns: the number of quadrature encoders
    """
def getNumInterrupts() -> int:
    """
    Gets the number of interrupts in the current system.
    
    :returns: the number of interrupts
    """
def getNumPWMChannels() -> int:
    """
    Gets the number of PWM channels in the current system.
    
    :returns: the number of PWM channels
    """
def getNumREVPDHChannels() -> int:
    """
    Gets the number of PDH channels in the current system.
    
    :returns: the number of PDH channels
    """
def getNumREVPDHModules() -> int:
    """
    Gets the number of PDH modules in the current system.
    
    :returns: the number of PDH modules
    """
def getNumREVPHChannels() -> int:
    """
    Gets the number of PH channels in the current system.
    
    :returns: the number of PH channels
    """
def getNumREVPHModules() -> int:
    """
    Gets the number of PH modules in the current system.
    
    :returns: the number of PH modules
    """
def getOutputsEnabled() -> int:
    """
    Gets if outputs are enabled by the control system.
    
    :returns: true if outputs are enabled
    """
def getPWMPulseTimeMicroseconds(pwmPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the current microsecond pulse time from a PWM channel.
    
    :param in:  pwmPortHandle the PWM handle
    :param out: status       Error status variable. 0 on success.
    
    :returns: the current PWM microsecond pulse time
    """
def getPowerDistributionAllChannelCurrents(handle: typing.SupportsInt, currentsLength: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the current of all channels on the PowerDistribution.
    
    The array must be large enough to hold all channels.
    
    :param in:  handle         the module handle
    :param out: currents      the currents
    :param in:  currentsLength the length of the currents array
    :param out: status        Error status variable. 0 on success.
    """
def getPowerDistributionChannelCurrent(handle: typing.SupportsInt, channel: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the current of a specific PowerDistribution channel.
    
    :param in:  handle   the module handle
    :param in:  channel  the channel
    :param out: status  Error status variable. 0 on success.
    
    :returns: the channel current (amps)
    """
def getPowerDistributionFaults(handle: typing.SupportsInt, faults: PowerDistributionFaults) -> int:
    """
    Get the current faults of the PowerDistribution.
    
    On a CTRE PDP, this will return an object with no faults active.
    
    :param in:  handle the module handle
    :param out: faults the HAL_PowerDistributionFaults to populate
    :param out: status Error status variable. 0 on success.
    """
def getPowerDistributionModuleNumber(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the module number for a specific handle.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the module number
    """
def getPowerDistributionNumChannels(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the number of channels for this handle.
    
    :param in:  handle the handle
    :param out: status Error status variable. 0 on success.
    
    :returns: number of channels
    """
def getPowerDistributionStickyFaults(handle: typing.SupportsInt, stickyFaults: PowerDistributionStickyFaults) -> int:
    """
    Gets the sticky faults of the PowerDistribution.
    
    On a CTRE PDP, this will return an object with no faults active.
    
    :param in:  handle the module handle
    :param out: stickyFaults the HAL_PowerDistributionStickyFaults to populate
    :param out: status Error status variable. 0 on success.
    """
def getPowerDistributionSwitchableChannel(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns true if switchable channel is powered on.
    
    This is a REV PDH-specific function. This function will no-op on CTRE PDP.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the state of the switchable channel
    """
def getPowerDistributionTemperature(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the temperature of the Power Distribution Panel.
    
    Not supported on the Rev PDH and returns 0.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the module temperature (celsius)
    """
def getPowerDistributionTotalCurrent(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the total current of the PowerDistribution.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the total current (amps)
    """
def getPowerDistributionTotalEnergy(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the total energy of the Power Distribution Panel.
    
    Not supported on the Rev PDH and returns 0.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the total energy (joules)
    """
def getPowerDistributionTotalPower(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the total power of the Power Distribution Panel.
    
    Not supported on the Rev PDH and returns 0.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the total power (watts)
    """
def getPowerDistributionType(handle: typing.SupportsInt) -> tuple[PowerDistributionType, int]:
    """
    Gets the type of PowerDistribution module.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the type of module
    """
def getPowerDistributionVersion(handle: typing.SupportsInt, version: PowerDistributionVersion) -> int:
    """
    Get the version of the PowerDistribution.
    
    :param in:  handle the module handle
    :param out: version the HAL_PowerDistributionVersion to populate
    :param out: status Error status variable. 0 on success.
    """
def getPowerDistributionVoltage(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Gets the PowerDistribution input voltage.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    
    :returns: the input voltage (volts)
    """
def getREVPH5VVoltage(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the current voltage of the regulated 5v supply.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: The current voltage of the 5v supply in volts.
    """
def getREVPHAnalogVoltage(handle: typing.SupportsInt, channel: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the raw voltage of the specified analog
    input channel.
    
    :param in:  handle  the PH handle
    :param in:  channel The analog input channel to read voltage from.
    :param out: status Error status variable. 0 on success.
    
    :returns: The voltage of the specified analog input channel in volts.
    """
def getREVPHCompressor(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get whether compressor is turned on.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: true if the compressor is turned on
    """
def getREVPHCompressorConfig(handle: typing.SupportsInt) -> tuple[REVPHCompressorConfigType, int]:
    """
    Get compressor configuration from the PH.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: compressor configuration
    """
def getREVPHCompressorCurrent(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the current drawn by the compressor.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: The current drawn by the compressor in amps.
    """
def getREVPHFaults(handle: typing.SupportsInt, faults: REVPHFaults) -> int:
    """
    Returns the faults currently active on the PH.
    
    :param in:  handle  the PH handle
    :param out: faults The faults.
    :param out: status Error status variable. 0 on success.
    """
def getREVPHPressureSwitch(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Returns the state of the digital pressure switch.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: True if pressure switch indicates that the system is full,
              otherwise false.
    """
def getREVPHSolenoidCurrent(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the total current drawn by all solenoids.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: Total current drawn by all solenoids in amps.
    """
def getREVPHSolenoidDisabledList(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Get a bitmask of disabled solenoids.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: Bitmask indicating disabled solenoids. The LSB represents solenoid 0.
    """
def getREVPHSolenoidVoltage(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the current voltage of the solenoid power supply.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: The current voltage of the solenoid power supply in volts.
    """
def getREVPHSolenoids(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets a bitmask of solenoid values.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: Bitmask containing the state of the solenoids. The LSB represents
              solenoid 0.
    """
def getREVPHStickyFaults(handle: typing.SupportsInt, stickyFaults: REVPHStickyFaults) -> int:
    """
    Returns the sticky faults currently active on this device.
    
    :param in:  handle  the PH handle
    :param out: stickyFaults The sticky faults.
    :param out: status Error status variable. 0 on success.
    """
def getREVPHVersion(handle: typing.SupportsInt, version: REVPHVersion) -> int:
    """
    Returns the hardware and firmware versions of the PH.
    
    :param in:  handle  the PH handle
    :param out: version The hardware and firmware versions.
    :param out: status Error status variable. 0 on success.
    """
def getREVPHVoltage(handle: typing.SupportsInt) -> tuple[float, int]:
    """
    Returns the current input voltage for the PH.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    
    :returns: The input voltage in volts.
    """
def getRSLState() -> tuple[int, int]:
    """
    Gets the current state of the Robot Signal Light (RSL).
    
    :param out: status the error code, or 0 for success
    
    :returns: The current state of the RSL- true if on, false if off
    """
def getRuntimeType() -> RuntimeType:
    """
    Returns the runtime type of the HAL.
    
    :returns: HAL Runtime Type
    """
def getSerialBytesReceived(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the number of bytes currently in the read buffer.
    
    :param in:  handle  the serial port handle
    :param out: status the error code, or 0 for success
    
    :returns: the number of bytes in the read buffer
    """
def getSerialFD(handle: typing.SupportsInt) -> tuple[int, int]:
    """
    Gets the raw serial port file descriptor from a handle.
    
    :param in:  handle the serial port handle
    :param out: status the error code, or 0 for success
    
    :returns: the raw port descriptor
    """
def getSerialNumber() -> str:
    """
    Returns the roboRIO serial number.
    
    :param out: serialNumber The roboRIO serial number. Free with WPI_FreeString
    """
def getSystemActive() -> tuple[int, int]:
    """
    Gets if the system outputs are currently active.
    
    :param out: status the error code, or 0 for success
    
    :returns: true if the system outputs are active, false if disabled
    """
def getSystemClockTicksPerMicrosecond() -> int:
    """
    Gets the number of FPGA system clock ticks per microsecond.
    
    :returns: the number of clock ticks per microsecond
    """
def getSystemTimeValid() -> tuple[int, int]:
    """
    Gets if the system time is valid.
    
    :param out: status the error code, or 0 for success
    
    :returns: True if the system time is valid, false otherwise
    """
def getTeamNumber() -> int:
    """
    Returns the team number configured for the robot controller.
    
    :returns: team number, or 0 if not found.
    """
def getUserActive3V3() -> tuple[int, int]:
    """
    Gets the active state of the 3V3 rail.
    
    :param out: status the error code, or 0 for success
    
    :returns: true if the rail is active, otherwise false
    """
def getUserCurrent3V3() -> tuple[float, int]:
    """
    Gets the 3V3 rail current.
    
    :param out: status the error code, or 0 for success
    
    :returns: the 3V3 rail current (amps)
    """
def getUserCurrentFaults3V3() -> tuple[int, int]:
    """
    Gets the fault count for the 3V3 rail. Capped at 255.
    
    :param out: status the error code, or 0 for success
    
    :returns: the number of 3V3 fault counts
    """
def getUserVoltage3V3() -> tuple[float, int]:
    """
    Gets the 3V3 rail voltage.
    
    :param out: status the error code, or 0 for success
    
    :returns: the 3V3 rail voltage (volts)
    """
def getVinVoltage() -> tuple[float, int]:
    """
    Gets the roboRIO input voltage.
    
    :param out: status the error code, or 0 for success
    
    :returns: the input voltage (volts)
    """
def hasMain() -> int:
    """
    Returns true if HAL_SetMain() has been called.
    
    :returns: True if HAL_SetMain() has been called, false otherwise.
    """
def initialize(timeout: typing.SupportsInt, mode: typing.SupportsInt) -> int:
    """
    Call this to start up HAL. This is required for robot programs.
    
    This must be called before any other HAL functions. Failure to do so will
    result in undefined behavior, and likely segmentation faults. This means that
    any statically initialized variables in a program MUST call this function in
    their constructors if they want to use other HAL calls.
    
    The common parameters are 500 for timeout and 0 for mode.
    
    This function is safe to call from any thread, and as many times as you wish.
    It internally guards from any reentrancy.
    
    The applicable modes are:
    0: Try to kill an existing HAL from another program, if not successful,
    error.
    1: Force kill a HAL from another program.
    2: Just warn if another hal exists and cannot be killed. Will likely result
    in undefined behavior.
    
    :param timeout: the initialization timeout (ms)
    :param mode:    the initialization mode (see remarks)
    
    :returns: true if initialization was successful, otherwise false.
    """
def initializeAddressableLED(channel: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Creates a new instance of an addressable LED.
    
    :param in:  channel            the smartio channel
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status the error code, or 0 for success
    
    :returns: Addressable LED handle
    """
def initializeAnalogInputPort(channel: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes the analog input port using the given port object.
    
    :param in:  channel the smartio channel.
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status the error code, or 0 for success
    
    :returns: the created analog input handle
    """
def initializeCAN(busId: typing.SupportsInt, manufacturer: CANManufacturer, deviceId: typing.SupportsInt, deviceType: CANDeviceType) -> tuple[int, int]:
    """
    Initializes a CAN device.
    
    These follow the FIRST standard CAN layout.
    https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html
    
    :param in:  busId        the bus id
    :param in:  manufacturer the can manufacturer
    :param in:  deviceId     the device ID (0-63)
    :param in:  deviceType   the device type
    :param out: status      Error status variable. 0 on success.
    
    :returns: the created CAN handle
    """
def initializeCTREPCM(busId: typing.SupportsInt, module: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes a PCM.
    
    :param in:  busId              the CAN bus ID
    :param in:  module             the CAN ID to initialize
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status            Error status variable. 0 on success.
    
    :returns: the created PH handle
    """
def initializeCounter(channel: typing.SupportsInt, risingEdge: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes a counter.
    
    :param in:  channel               the dio channel
    :param in:  risingEdge            true to count on rising edge, false for
                falling
    :param in:  allocationLocation    the location where the allocation is
                occurring (can be null)
    :param out: status     Error status variable. 0 on success.
    
    :returns: the created handle
    """
def initializeDIOPort(channel: typing.SupportsInt, input: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Creates a new instance of a digital port.
    
    :param in:  channel            the smartio channel
    :param in:  input              true for input, false for output
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status            Error status variable. 0 on success.
    
    :returns: the created digital handle
    """
def initializeDutyCycle(channel: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initialize a DutyCycle input.
    
    :param in:  channel            the smartio channel
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status Error status variable. 0 on success.
    
    :returns: the created duty cycle handle
    """
def initializeEncoder(aChannel: typing.SupportsInt, bChannel: typing.SupportsInt, reverseDirection: typing.SupportsInt, encodingType: EncoderEncodingType) -> tuple[int, int]:
    """
    Initializes an encoder.
    
    :param in:  aChannel             the A channel
    :param in:  bChannel             the B channel
    :param in:  reverseDirection     true to reverse the counting direction from
                standard, otherwise false
    :param in:  encodingType         the encoding type
    :param out: status              Error status variable. 0 on success.
    
    :returns: the created encoder handle
    """
def initializeI2C(port: I2CPort) -> int:
    """
    Initializes the I2C port.
    
    Opens the port if necessary and saves the handle.
    If opening the MXP port, also sets up the channel functions appropriately.
    
    :param in:  port    The port to open, 0 for the on-board, 1 for the MXP.
    :param out: status Error status variable. 0 on success.
    """
def initializeNotifier() -> tuple[int, int]:
    """
    Initializes a notifier.
    
    A notifier is an FPGA controller timer that triggers at requested intervals
    based on the FPGA time. This can be used to make precise control loops.
    
    :param out: status Error status variable. 0 on success.
    
    :returns: the created notifier
    """
def initializePWMPort(channel: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes a PWM port.
    
    :param in:  channel the smartio channel
    :param in:  allocationLocation  the location where the allocation is occurring
                (can be null)
    :param out: status             Error status variable. 0 on success.
    
    :returns: the created pwm handle
    """
def initializePowerDistribution(busId: typing.SupportsInt, moduleNumber: typing.SupportsInt, type: PowerDistributionType, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes a Power Distribution Panel.
    
    :param in:  busId              the bus id
    :param in:  moduleNumber       the module number to initialize
    :param in:  type               the type of module to initialize
    :param in:  allocationLocation the location where the allocation is occurring
    :param out: status            Error status variable. 0 on success.
    
    :returns: the created PowerDistribution handle
    """
def initializeREVPH(busId: typing.SupportsInt, module: typing.SupportsInt, allocationLocation: str) -> tuple[int, int]:
    """
    Initializes a PH.
    
    :param in:  busId              the bus id
    :param in:  module             the CAN ID to initialize
    :param in:  allocationLocation the location where the allocation is occurring
                (can be null)
    :param out: status            Error status variable. 0 on success.
    
    :returns: the created PH handle
    """
def initializeSerialPort(port: SerialPort) -> tuple[int, int]:
    """
    Initializes a serial port.
    
    The channels are either the onboard RS232, the MXP UART, or 2 USB ports. The
    top port is USB1, the bottom port is USB2.
    
    :param in:  port the serial port to initialize
    :param out: status the error code, or 0 for success
    
    :returns: Serial Port Handle
    """
def initializeSerialPortDirect(port: SerialPort, portName: str) -> tuple[int, int]:
    """
    Initializes a serial port with a direct name.
    
    This name is the /dev name for a specific port.
    Note these are not always consistent between roboRIO reboots.
    
    :param in:  port     the serial port to initialize
    :param in:  portName the dev port name
    :param out: status  the error code, or 0 for success
    
    :returns: Serial Port Handle
    """
def isAnyPulsing() -> tuple[int, int]:
    """
    Checks if any DIO line is currently generating a pulse.
    
    :param out: status Error status variable. 0 on success.
    
    :returns: true if a pulse on some line is in progress
    """
def isHandleCorrectVersion(handle: typing.SupportsInt, version: typing.SupportsInt) -> bool:
    """
    Get if the version of the handle is correct.
    
    Do not use on the roboRIO, used specifically for the sim to handle resets.
    
    :param handle:  the handle
    :param version: the handle version to check
    
    :returns: true if the handle is the right version, otherwise false
    """
def isHandleType(handle: typing.SupportsInt, handleType: HandleEnum) -> bool:
    """
    Get if the handle is a specific type.
    
    :param handle:     the handle
    :param handleType: the type to check
    
    :returns: true if the type is correct, otherwise false
    """
def isPulsing(dioPortHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Checks a DIO line to see if it is currently generating a pulse.
    
    :param in:  dioPortHandle the digital port handle
    :param out: status Error status variable. 0 on success.
    
    :returns: true if a pulse is in progress, otherwise false
    """
def loadExtensions() -> int:
    """
    Loads any extra halsim libraries provided in the HALSIM_EXTENSIONS
    environment variable.
    
    :returns: the success state of the initialization
    """
def loadOneExtension(library: str) -> int:
    """
    Loads a single extension from a direct path.
    
    Expected to be called internally, not by users.
    
    :param library: the library path
    
    :returns: the success state of the initialization
    """
def observeUserProgramAutonomous() -> None:
    """
    Sets the autonomous enabled flag in the DS.
    
    This is used for the DS to ensure the robot is properly responding to its
    state request. Ensure this gets called about every 50ms, or the robot will be
    disabled by the DS.
    """
def observeUserProgramDisabled() -> None:
    """
    Sets the disabled flag in the DS.
    
    This is used for the DS to ensure the robot is properly responding to its
    state request. Ensure this gets called about every 50ms, or the robot will be
    disabled by the DS.
    """
def observeUserProgramStarting() -> None:
    """
    Sets the program starting flag in the DS.
    
    This is what changes the DS to showing robot code ready.
    """
def observeUserProgramTeleop() -> None:
    """
    Sets the teleoperated enabled flag in the DS.
    
    This is used for the DS to ensure the robot is properly responding to its
    state request. Ensure this gets called about every 50ms, or the robot will be
    disabled by the DS.
    """
def observeUserProgramTest() -> None:
    """
    Sets the test mode flag in the DS.
    
    This is used for the DS to ensure the robot is properly responding to its
    state request. Ensure this gets called about every 50ms, or the robot will be
    disabled by the DS.
    """
def provideNewDataEventHandle(handle: typing.SupportsInt) -> None:
    """
    Adds an event handle to be signalled when new data arrives.
    
    :param handle: the event handle to be signalled
    """
def pulse(dioPortHandle: typing.SupportsInt, pulseLength: typing.SupportsFloat) -> int:
    """
    Generates a single digital pulse.
    
    Write a pulse to the specified digital output channel. There can only be a
    single pulse going at any time.
    
    :param in:  dioPortHandle the digital port handle
    :param in:  pulseLength   the active length of the pulse in seconds
    :param out: status       Error status variable. 0 on success.
    """
def pulseMultiple(channelMask: typing.SupportsInt, pulseLength: typing.SupportsFloat) -> int:
    """
    Generates a single digital pulse on multiple channels.
    
    Write a pulse to the channels enabled by the mask. There can only be a
    single pulse going at any time.
    
    :param in:  channelMask the channel mask
    :param in:  pulseLength the active length of the pulse in seconds
    :param out: status     Error status variable. 0 on success.
    """
def readCANPacketLatest(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANReceiveMessage) -> int:
    """
    Reads a CAN packet. The will continuously return the last packet received,
    without accounting for packet age.
    
    :param in:  handle    the CAN handle
    :param in:  apiId     the ID to read (0-1023)
    :param out: message  the message received.
    :param out: status   Error status variable. 0 on success.
    """
def readCANPacketNew(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANReceiveMessage) -> int:
    """
    Reads a new CAN packet.
    
    This will only return properly once per packet received. Multiple calls
    without receiving another packet will return an error code.
    
    :param in:  handle    the CAN handle
    :param in:  apiId     the ID to read (0-1023)
    :param out: message  the message received.
    :param out: status   Error status variable. 0 on success.
    """
def readCANPacketTimeout(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANReceiveMessage, timeoutMs: typing.SupportsInt) -> int:
    """
    Reads a CAN packet. The will return the last packet received until the
    packet is older then the requested timeout. Then it will return an error
    code.
    
    :param in:  handle        the CAN handle
    :param in:  apiId         the ID to read (0-1023)
    :param out: message      the message received.
    :param out: timeoutMs    the timeout time for the packet
    :param out: status       Error status variable. 0 on success.
    """
def readI2C(port: I2CPort, deviceAddress: typing.SupportsInt, buffer: typing_extensions.Buffer) -> int:
    """
    Executes a read transaction with the device.
    
    Reads bytes from a device.
    Most I2C devices will auto-increment the register pointer internally allowing
    you to read consecutive registers on a device in a single transaction.
    
    :param port:          The I2C port, 0 for the on-board, 1 for the MXP.
    :param deviceAddress: The register to read first in the transaction.
    :param count:         The number of bytes to read in the transaction.
    :param buffer:        A pointer to the array of bytes to store the data read from the
                          device.
    
    :returns: 0 on success or -1 on transfer abort.
    """
def readSerial(handle: typing.SupportsInt, buffer: typing_extensions.Buffer) -> tuple[int, int]:
    """
    Reads data from the serial port.
    
    Will wait for either timeout (if set), the termination char (if set), or the
    count to be full. Whichever one comes first.
    
    :param in:  handle  the serial port handle
    :param out: buffer the buffer in which to store bytes read
    :param in:  count   the number of bytes maximum to read
    :param out: status the error code, or 0 for success
    
    :returns: the number of bytes actually read
    """
def refreshDSData() -> int:
    """
    Refresh the DS control word.
    
    :returns: true if updated
    """
def removeNewDataEventHandle(handle: typing.SupportsInt) -> None:
    """
    Removes the event handle from being signalled when new data arrives.
    
    :param handle: the event handle to remove
    """
@typing.overload
def reportUsage(resource: str, data: str) -> int:
    """
    Reports usage of a resource of interest.  Repeated calls for the same
    resource name replace the previous report.
    
    :param resource: the used resource name; convention is to suffix with
                     "[instanceNum]" for multiple instances of the same
                     resource
    :param data:     arbitrary associated data string
    
    :returns: a handle
    """
@typing.overload
def reportUsage(resource: str, instanceNumber: typing.SupportsInt, data: str) -> int:
    """
    Reports usage of a resource of interest.  Repeated calls for the same
    resource name replace the previous report.
    
    :param resource:       the used resource name
    :param instanceNumber: an index that identifies the resource instance
    :param data:           arbitrary associated data string
    
    :returns: a handle
    """
def resetCounter(counterHandle: typing.SupportsInt) -> int:
    """
    Resets the Counter to zero.
    
    Sets the counter value to zero. This does not effect the running state of the
    counter, just sets the current value to zero.
    
    :param in:  counterHandle the counter handle
    :param out: status       Error status variable. 0 on success.
    """
def resetEncoder(encoderHandle: typing.SupportsInt) -> int:
    """
    Reads the current encoder value.
    
    Read the value at this instant. It may still be running, so it reflects the
    current value. Next time it is read, it might have a different value.
    
    :param in:  encoderHandle the encoder handle
    :param out: status       Error status variable. 0 on success.
    """
def resetPowerDistributionTotalEnergy(handle: typing.SupportsInt) -> int:
    """
    Resets the PowerDistribution accumulated energy.
    
    Not supported on the Rev PDH and does nothing.
    
    :param in:  handle the module handle
    :param out: status Error status variable. 0 on success.
    """
def resetUserCurrentFaults() -> int:
    """
    Resets the overcurrent fault counters for all user rails to 0.
    
    :param out: status the error code, or 0 for success
    """
def runMain() -> None:
    """
    Runs the main function provided to HAL_SetMain().
    
    If HAL_SetMain() has not been called, simply sleeps until HAL_ExitMain()
    is called.
    """
def sendConsoleLine(line: str) -> int:
    """
    Sends a line to the driver station console.
    
    :param line: the line to send (null terminated)
    
    :returns: the error code, or 0 for success
    """
def sendError(isError: typing.SupportsInt, errorCode: typing.SupportsInt, isLVCode: typing.SupportsInt, details: str, location: str, callStack: str, printMsg: typing.SupportsInt) -> int:
    """
    Sends an error to the driver station.
    
    :param isError:   true for error, false for warning
    :param errorCode: the error code
    :param isLVCode:  true for a LV error code, false for a standard error code
    :param details:   the details of the error
    :param location:  the file location of the error
    :param callStack: the callstack of the error
    :param printMsg:  true to print the error message to stdout as well as to the
                      DS
    
    :returns: the error code, or 0 for success
    """
def setAddressableLEDData(start: typing.SupportsInt, length: typing.SupportsInt, colorOrder: AddressableLEDColorOrder, data: AddressableLEDData) -> int:
    """
    Sets the led output data.
    
    All addressable LEDs use a single backing buffer 1024 LEDs in size.
    This function may be used to set part of or all of the buffer.
    
    :param in:  start the strip start, in LEDs
    :param in:  length the strip length, in LEDs
    :param in:  colorOrder the color order
    :param in:  data the buffer to write
    :param out: status the error code, or 0 for success
    """
def setAddressableLEDLength(handle: typing.SupportsInt, length: typing.SupportsInt) -> int:
    """
    Sets the length of the LED strip.
    
    All addressable LEDs use a single backing buffer 1024 LEDs in size.
    The max length for a single output is 1024 LEDs (with an offset of zero).
    
    :param in:  handle the Addressable LED handle
    :param in:  length the strip length, in LEDs
    :param out: status the error code, or 0 for success
    """
def setAddressableLEDStart(handle: typing.SupportsInt, start: typing.SupportsInt) -> int:
    """
    Sets the start buffer location used for the LED strip.
    
    All addressable LEDs use a single backing buffer 1024 LEDs in size.
    The max length for a single output is 1024 LEDs (with an offset of zero).
    
    :param in:  handle the Addressable LED handle
    :param in:  start the strip start, in LEDs
    :param out: status the error code, or 0 for success
    """
def setAnalogAverageBits(analogPortHandle: typing.SupportsInt, bits: typing.SupportsInt) -> int:
    """
    Sets the number of averaging bits.
    
    This sets the number of averaging bits. The actual number of averaged samples
    is 2**bits. Use averaging to improve the stability of your measurement at the
    expense of sampling rate. The averaging is done automatically in the FPGA.
    
    :param in:  analogPortHandle Handle to the analog port to configure.
    :param in:  bits Number of bits to average.
    :param out: status the error code, or 0 for success
    """
def setAnalogInputSimDevice(handle: typing.SupportsInt, device: typing.SupportsInt) -> None:
    """
    Indicates the analog input is used by a simulated device.
    
    :param handle: the analog input handle
    :param device: simulated device handle
    """
def setAnalogOversampleBits(analogPortHandle: typing.SupportsInt, bits: typing.SupportsInt) -> int:
    """
    Sets the number of oversample bits.
    
    This sets the number of oversample bits. The actual number of oversampled
    values is 2**bits. Use oversampling to improve the resolution of your
    measurements at the expense of sampling rate. The oversampling is done
    automatically in the FPGA.
    
    :param in:  analogPortHandle Handle to the analog port to use.
    :param in:  bits Number of bits to oversample.
    :param out: status the error code, or 0 for success
    """
def setAnalogSampleRate(samplesPerSecond: typing.SupportsFloat) -> int:
    """
    Sets the sample rate.
    
    This is a global setting for the Athena and effects all channels.
    
    :param in:  samplesPerSecond The number of samples per channel per second.
    :param out: status          the error code, or 0 for success
    """
def setBrownoutVoltage(voltage: typing.SupportsFloat) -> int:
    """
    Set the voltage the roboRIO will brownout and disable all outputs.
    
    Note that this only does anything on the roboRIO 2.
    On the roboRIO it is a no-op.
    
    :param in:  voltage The brownout voltage
    :param out: status the error code, or 0 for success
    """
def setCTREPCMClosedLoopControl(handle: typing.SupportsInt, enabled: typing.SupportsInt) -> int:
    """
    Enables the compressor closed loop control using the digital pressure switch.
    The compressor will turn on when the pressure switch indicates that the
    system is not full, and will turn off when the pressure switch indicates that
    the system is full.
    
    :param in:  handle  the PCM handle
    :param in:  enabled true to enable closed loop control
    :param out: status Error status variable. 0 on success.
    """
def setCTREPCMOneShotDuration(handle: typing.SupportsInt, index: typing.SupportsInt, durMs: typing.SupportsInt) -> int:
    """
    Set the duration for a single solenoid shot.
    
    :param in:  handle  the PCM handle
    :param in:  index solenoid index
    :param in:  durMs shot duration in ms
    :param out: status Error status variable. 0 on success.
    """
def setCTREPCMSolenoids(handle: typing.SupportsInt, mask: typing.SupportsInt, values: typing.SupportsInt) -> int:
    """
    Sets solenoids on a pneumatics module.
    
    :param in:  handle  the PCM handle
    :param in:  mask Bitmask indicating which solenoids to set. The LSB represents
                solenoid 0.
    :param in:  values Bitmask indicating the desired states of the solenoids. The
                LSB represents solenoid 0.
    :param out: status Error status variable. 0 on success.
    """
def setCounterEdgeConfiguration(counterHandle: typing.SupportsInt, risingEdge: typing.SupportsInt) -> int:
    """
    Sets the up source to either detect rising edges or falling edges.
    
    Note that both are allowed to be set true at the same time without issues.
    
    :param in:  counterHandle  the counter handle
    :param in:  risingEdge     true to trigger on rising
    :param out: status        Error status variable. 0 on success.
    """
def setCounterMaxPeriod(counterHandle: typing.SupportsInt, maxPeriod: typing.SupportsFloat) -> int:
    """
    Sets the maximum period where the device is still considered "moving".
    
    Sets the maximum period where the device is considered moving. This value is
    used to determine the "stopped" state of the counter using the
    HAL_GetCounterStopped method.
    
    :param in:  counterHandle the counter handle
    :param in:  maxPeriod     the maximum period where the counted device is
                considered moving in seconds
    :param out: status       Error status variable. 0 on success.
    """
def setCurrentThreadPriority(realTime: typing.SupportsInt, priority: typing.SupportsInt) -> tuple[int, int]:
    """
    Sets the thread priority for the current thread.
    
    :param in:  realTime Set to true to set a real-time priority, false for
                standard priority.
    :param in:  priority Priority to set the thread to. For real-time, this is
                1-99 with 99 being highest. For non-real-time, this is
                forced to 0. See "man 7 sched" for more details.
    :param out: status  Error status variable. 0 on success.
    
    :returns: True on success.
    """
def setDIO(dioPortHandle: typing.SupportsInt, value: typing.SupportsInt) -> int:
    """
    Writes a digital value to a DIO channel.
    
    :param in:  dioPortHandle the digital port handle
    :param in:  value         the state to set the digital channel (if it is
                configured as an output)
    :param out: status       Error status variable. 0 on success.
    """
def setDIODirection(dioPortHandle: typing.SupportsInt, input: typing.SupportsInt) -> int:
    """
    Sets the direction of a DIO channel.
    
    :param in:  dioPortHandle the digital port handle
    :param in:  input         true to set input, false for output
    :param out: status       Error status variable. 0 on success.
    """
def setDIOSimDevice(handle: typing.SupportsInt, device: typing.SupportsInt) -> None:
    """
    Indicates the DIO channel is used by a simulated device.
    
    :param handle: the DIO channel handle
    :param device: simulated device handle
    """
def setDigitalPWMDutyCycle(pwmGenerator: typing.SupportsInt, dutyCycle: typing.SupportsFloat) -> int:
    """
    Configures the duty-cycle of the PWM generator.
    
    :param in:  pwmGenerator the digital PWM handle
    :param in:  dutyCycle    the percent duty cycle to output [0..1]
    :param out: status      Error status variable. 0 on success.
    """
def setDigitalPWMOutputChannel(pwmGenerator: typing.SupportsInt, channel: typing.SupportsInt) -> int:
    """
    Configures which DO channel the PWM signal is output on.
    
    :param in:  pwmGenerator the digital PWM handle
    :param in:  channel      the channel to output on
    :param out: status      Error status variable. 0 on success.
    """
def setDigitalPWMPPS(pwmGenerator: typing.SupportsInt, dutyCycle: typing.SupportsFloat) -> int:
    """
    Configures the digital PWM to be a PPS signal with specified duty cycle.
    
    :param in:  pwmGenerator the digital PWM handle
    :param in:  dutyCycle    the percent duty cycle to output [0..1]
    :param out: status      Error status variable. 0 on success.
    """
def setDigitalPWMRate(rate: typing.SupportsFloat) -> int:
    """
    Changes the frequency of the DO PWM generator.
    
    The valid range is from 0.6 Hz to 19 kHz.
    
    The frequency resolution is logarithmic.
    
    :param in:  rate the frequency to output all digital output PWM signals
    :param out: status Error status variable. 0 on success.
    """
def setDutyCycleSimDevice(handle: typing.SupportsInt, device: typing.SupportsInt) -> None:
    """
    Indicates the duty cycle is used by a simulated device.
    
    :param handle: the duty cycle handle
    :param device: simulated device handle
    """
def setEncoderDistancePerPulse(encoderHandle: typing.SupportsInt, distancePerPulse: typing.SupportsFloat) -> int:
    """
    Sets the distance traveled per encoder pulse. This is used as a scaling
    factor for the rate and distance calls.
    
    :param in:  encoderHandle    the encoder handle
    :param in:  distancePerPulse the distance traveled per encoder pulse (units
                user defined)
    :param out: status          Error status variable. 0 on success.
    """
def setEncoderMaxPeriod(encoderHandle: typing.SupportsInt, maxPeriod: typing.SupportsFloat) -> int:
    """
    Sets the maximum period where the device is still considered "moving".
    
    Sets the maximum period where the device is considered moving. This value is
    used to determine the "stopped" state of the encoder using the
    HAL_GetEncoderStopped method.
    
    :param in:  encoderHandle the encoder handle
    :param in:  maxPeriod     the maximum period where the counted device is
                considered moving in seconds
    :param out: status       Error status variable. 0 on success.
    """
def setEncoderMinRate(encoderHandle: typing.SupportsInt, minRate: typing.SupportsFloat) -> int:
    """
    Sets the minimum rate to be considered moving by the encoder.
    
    Units need to match what is set by HAL_SetEncoderDistancePerPulse, with time
    as seconds.
    
    :param in:  encoderHandle the encoder handle
    :param in:  minRate       the minimum rate to be considered moving (units are
                determined by the units passed to
                HAL_SetEncoderDistancePerPulse, time value is
                seconds)
    :param out: status       Error status variable. 0 on success.
    """
def setEncoderReverseDirection(encoderHandle: typing.SupportsInt, reverseDirection: typing.SupportsInt) -> int:
    """
    Sets if to reverse the direction of the encoder.
    
    Note that this is not a toggle. It is an absolute set.
    
    :param in:  encoderHandle    the encoder handle
    :param in:  reverseDirection true to reverse the direction, false to not.
    :param out: status          Error status variable. 0 on success.
    """
def setEncoderSamplesToAverage(encoderHandle: typing.SupportsInt, samplesToAverage: typing.SupportsInt) -> int:
    """
    Sets the number of encoder samples to average when calculating encoder rate.
    
    :param in:  encoderHandle    the encoder handle
    :param in:  samplesToAverage the number of samples to average
    :param out: status          Error status variable. 0 on success.
    """
def setEncoderSimDevice(handle: typing.SupportsInt, device: typing.SupportsInt) -> None:
    """
    Indicates the encoder is used by a simulated device.
    
    :param handle: the encoder handle
    :param device: simulated device handle
    """
def setJoystickOutputs(joystickNum: typing.SupportsInt, outputs: typing.SupportsInt, leftRumble: typing.SupportsInt, rightRumble: typing.SupportsInt) -> int:
    """
    Set joystick outputs.
    
    :param joystickNum: the joystick number
    :param outputs:     bitmask of outputs, 1 for on 0 for off
    :param leftRumble:  the left rumble value (0-FFFF)
    :param rightRumble: the right rumble value (0-FFFF)
    
    :returns: the error code, or 0 for success
    """
def setNotifierName(notifierHandle: typing.SupportsInt, name: str) -> int:
    """
    Sets the name of a notifier.
    
    :param in:  notifierHandle the notifier handle
    :param in:  name name
    :param out: status Error status variable. 0 on success.
    """
def setNotifierThreadPriority(realTime: typing.SupportsInt, priority: typing.SupportsInt) -> tuple[int, int]:
    """
    Sets the HAL notifier thread priority.
    
    The HAL notifier thread is responsible for managing the FPGA's notifier
    interrupt and waking up user's Notifiers when it's their time to run.
    Giving the HAL notifier thread real-time priority helps ensure the user's
    real-time Notifiers, if any, are notified to run in a timely manner.
    
    :param in:  realTime Set to true to set a real-time priority, false for
                standard priority.
    :param in:  priority Priority to set the thread to. For real-time, this is
                1-99 with 99 being highest. For non-real-time, this is
                forced to 0. See "man 7 sched" for more details.
    :param out: status  Error status variable. 0 on success.
    
    :returns: True on success.
    """
def setPWMOutputPeriod(pwmPortHandle: typing.SupportsInt, period: typing.SupportsInt) -> int:
    """
    Sets the PWM output period.
    
    :param in:  pwmPortHandle the PWM handle.
    :param in:  period   0 for 5ms, 1 or 2 for 10ms, 3 for 20ms
    :param out: status       Error status variable. 0 on success.
    """
def setPWMPulseTimeMicroseconds(pwmPortHandle: typing.SupportsInt, microsecondPulseTime: typing.SupportsInt) -> int:
    """
    Sets a PWM channel to the desired pulse width in microseconds.
    
    :param in:  pwmPortHandle the PWM handle
    :param in:  microsecondPulseTime  the PWM value to set
    :param out: status       Error status variable. 0 on success.
    """
def setPWMSimDevice(handle: typing.SupportsInt, device: typing.SupportsInt) -> None:
    """
    Indicates the pwm is used by a simulated device.
    
    :param handle: the pwm handle
    :param device: simulated device handle
    """
def setPowerDistributionSwitchableChannel(handle: typing.SupportsInt, enabled: typing.SupportsInt) -> int:
    """
    Power on/off switchable channel.
    
    This is a REV PDH-specific function. This function will no-op on CTRE PDP.
    
    :param in:  handle the module handle
    :param in:  enabled true to turn on switchable channel
    :param out: status Error status variable. 0 on success.
    """
def setREVPHClosedLoopControlAnalog(handle: typing.SupportsInt, minAnalogVoltage: typing.SupportsFloat, maxAnalogVoltage: typing.SupportsFloat) -> int:
    """
    Enables the compressor in analog mode. This mode uses an analog
    pressure sensor connected to analog channel 0 to cycle the compressor. The
    compressor will turn on when the pressure drops below minAnalogVoltage and
    will turn off when the pressure reaches maxAnalogVoltage. This mode is only
    supported by the REV PH with the REV Analog Pressure Sensor connected to
    analog channel 0.
    
    :param in:  handle  the PH handle
    :param in:  minAnalogVoltage The compressor will turn on when the analog
                pressure sensor voltage drops below this value
    :param in:  maxAnalogVoltage The compressor will turn off when the analog
                pressure sensor reaches this value.
    :param out: status Error status variable. 0 on success.
    """
def setREVPHClosedLoopControlDigital(handle: typing.SupportsInt) -> int:
    """
    Enables the compressor in digital mode using the digital pressure switch. The
    compressor will turn on when the pressure switch indicates that the system is
    not full, and will turn off when the pressure switch indicates that the
    system is full.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    """
def setREVPHClosedLoopControlDisabled(handle: typing.SupportsInt) -> int:
    """
    Disable Compressor.
    
    :param in:  handle  the PH handle
    :param out: status Error status variable. 0 on success.
    """
def setREVPHClosedLoopControlHybrid(handle: typing.SupportsInt, minAnalogVoltage: typing.SupportsFloat, maxAnalogVoltage: typing.SupportsFloat) -> int:
    """
    Enables the compressor in hybrid mode. This mode uses both a digital
    pressure switch and an analog pressure sensor connected to analog channel 0
    to cycle the compressor.
    
    The compressor will turn on when \\a both:
    
    - The digital pressure switch indicates the system is not full AND
    - The analog pressure sensor indicates that the pressure in the system is
    below the specified minimum pressure.
    
    The compressor will turn off when \\a either:
    
    - The digital pressure switch is disconnected or indicates that the system
    is full OR
    - The pressure detected by the analog sensor is greater than the specified
    maximum pressure.
    
    :param in:  handle  the PH handle
    :param in:  minAnalogVoltage The compressor will turn on when the analog
                pressure sensor voltage drops below this value and the pressure switch
                indicates that the system is not full.
    :param in:  maxAnalogVoltage The compressor will turn off when the analog
                pressure sensor reaches this value or the pressure switch is disconnected or
                indicates that the system is full.
    :param out: status Error status variable. 0 on success.
    """
def setREVPHCompressorConfig(handle: typing.SupportsInt, config: REVPHCompressorConfig) -> int:
    """
    Send compressor configuration to the PH.
    
    :param in:  handle  the PH handle
    :param in:  config  compressor configuration
    :param out: status Error status variable. 0 on success.
    """
def setREVPHSolenoids(handle: typing.SupportsInt, mask: typing.SupportsInt, values: typing.SupportsInt) -> int:
    """
    Sets solenoids on a PH.
    
    :param in:  handle  the PH handle
    :param in:  mask Bitmask indicating which solenoids to set. The LSB represents
                solenoid 0.
    :param in:  values Bitmask indicating the desired states of the solenoids. The
                LSB represents solenoid 0.
    :param out: status Error status variable. 0 on success.
    """
def setSerialBaudRate(handle: typing.SupportsInt, baud: typing.SupportsInt) -> int:
    """
    Sets the baud rate of a serial port.
    
    Any value between 0 and 0xFFFFFFFF may be used. Default is 9600.
    
    :param in:  handle  the serial port handle
    :param in:  baud    the baud rate to set
    :param out: status the error code, or 0 for success
    """
def setSerialDataBits(handle: typing.SupportsInt, bits: typing.SupportsInt) -> int:
    """
    Sets the number of data bits on a serial port.
    
    Defaults to 8.
    
    :param in:  handle  the serial port handle
    :param in:  bits    the number of data bits (5-8)
    :param out: status the error code, or 0 for success
    """
def setSerialFlowControl(handle: typing.SupportsInt, flow: typing.SupportsInt) -> int:
    """
    Sets the flow control mode of a serial port.
    
    Valid values are:
    0: None (default)
    1: XON-XOFF
    2: RTS-CTS
    3: DTR-DSR
    
    :param in:  handle  the serial port handle
    :param in:  flow    the mode to set (see remarks for valid values)
    :param out: status the error code, or 0 for success
    """
def setSerialParity(handle: typing.SupportsInt, parity: typing.SupportsInt) -> int:
    """
    Sets the number of parity bits on a serial port.
    
    Valid values are:
    0: None (default)
    1: Odd
    2: Even
    3: Mark - Means exists and always 1
    4: Space - Means exists and always 0
    
    :param in:  handle  the serial port handle
    :param in:  parity  the parity bit mode (see remarks for valid values)
    :param out: status the error code, or 0 for success
    """
def setSerialReadBufferSize(handle: typing.SupportsInt, size: typing.SupportsInt) -> int:
    """
    Sets the size of the read buffer.
    
    :param in:  handle  the serial port handle
    :param in:  size    the read buffer size
    :param out: status the error code, or 0 for success
    """
def setSerialStopBits(handle: typing.SupportsInt, stopBits: typing.SupportsInt) -> int:
    """
    Sets the number of stop bits on a serial port.
    
    Valid values are:
    10: One stop bit (default)
    15: One and a half stop bits
    20: Two stop bits
    
    :param in:  handle    the serial port handle
    :param in:  stopBits  the stop bit value (see remarks for valid values)
    :param out: status   the error code, or 0 for success
    """
def setSerialTimeout(handle: typing.SupportsInt, timeout: typing.SupportsFloat) -> int:
    """
    Sets the minimum serial read timeout of a port.
    
    :param in:  handle   the serial port handle
    :param in:  timeout  the timeout in milliseconds
    :param out: status  the error code, or 0 for success
    """
def setSerialWriteBufferSize(handle: typing.SupportsInt, size: typing.SupportsInt) -> int:
    """
    Sets the size of the write buffer.
    
    :param in:  handle  the serial port handle
    :param in:  size    the write buffer size
    :param out: status the error code, or 0 for success
    """
def setSerialWriteMode(handle: typing.SupportsInt, mode: typing.SupportsInt) -> int:
    """
    Sets the write mode on a serial port.
    
    Valid values are:
    1: Flush on access
    2: Flush when full (default)
    
    :param in:  handle  the serial port handle
    :param in:  mode    the mode to set (see remarks for valid values)
    :param out: status the error code, or 0 for success
    """
def setShowExtensionsNotFoundMessages(showMessage: typing.SupportsInt) -> None:
    """
    Enables or disables the message saying no HAL extensions were found.
    
    Some apps don't care, and the message create clutter. For general team code,
    we want it.
    
    This must be called before HAL_Initialize is called.
    
    This defaults to true.
    
    :param showMessage: true to show message, false to not.
    """
def setUserRailEnabled3V3(enabled: typing.SupportsInt) -> int:
    """
    Enables or disables the 3V3 rail.
    
    :param enabled: whether the rail should be enabled
    :param out:     status the error code, or 0 for success
    """
def shutdown() -> None:
    """
    Call this to shut down HAL.
    
    This must be called at termination of the robot program to avoid potential
    segmentation faults with simulation extensions at exit.
    """
def simPeriodicAfter() -> None:
    """
    Calls registered SimPeriodic "after" callbacks (only in simulation mode).
    This should be called after user code periodic simulation functions.
    """
def simPeriodicBefore() -> None:
    """
    Calls registered SimPeriodic "before" callbacks (only in simulation mode).
    This should be called prior to user code periodic simulation functions.
    """
def stopCANPacketRepeating(handle: typing.SupportsInt, apiId: typing.SupportsInt) -> int:
    """
    Stops a repeating packet with a specific ID.
    
    This ID is 10 bits.
    
    :param in:  handle  the CAN handle
    :param in:  apiId   the ID to stop repeating (0-1023)
    :param out: status Error status variable. 0 on success.
    """
def stopNotifier(notifierHandle: typing.SupportsInt) -> int:
    """
    Stops a notifier from running.
    
    This will cause any call into HAL_WaitForNotifierAlarm to return with time =
    0.
    
    :param in:  notifierHandle the notifier handle
    :param out: status Error status variable. 0 on success.
    """
def transactionI2C(port: I2CPort, deviceAddress: typing.SupportsInt, dataToSend: typing_extensions.Buffer, dataReceived: typing_extensions.Buffer) -> int:
    """
    Generic I2C read/write transaction.
    
    This is a lower-level interface to the I2C hardware giving you more control
    over each transaction.
    
    :param port:          The I2C port, 0 for the on-board, 1 for the MXP.
    :param deviceAddress: The address of the register on the device to be
                          read/written.
    :param dataToSend:    Buffer of data to send as part of the transaction.
    :param sendSize:      Number of bytes to send as part of the transaction.
    :param dataReceived:  Buffer to read data into.
    :param receiveSize:   Number of bytes to read from the device.
    
    :returns: 0 on success or -1 on transfer abort.
    """
def updateNotifierAlarm(notifierHandle: typing.SupportsInt, triggerTime: typing.SupportsInt) -> int:
    """
    Updates the trigger time for a notifier.
    
    Note that this time is an absolute time relative to HAL_GetFPGATime()
    
    :param in:  notifierHandle the notifier handle
    :param in:  triggerTime    the updated trigger time
    :param out: status        Error status variable. 0 on success.
    """
def waitForNotifierAlarm(notifierHandle: typing.SupportsInt) -> tuple[int, int]:
    """
    Waits for the next alarm for the specific notifier.
    
    This is a blocking call until either the time elapses or HAL_StopNotifier
    gets called. If the latter occurs, this function will return zero and any
    loops using this function should exit. Failing to do so can lead to
    use-after-frees.
    
    :param in:  notifierHandle the notifier handle
    :param out: status        Error status variable. 0 on success.
    
    :returns: the FPGA time the notifier returned
    """
def writeCANPacket(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANMessage) -> int:
    """
    Writes a packet to the CAN device with a specific ID.
    
    This ID is 10 bits.
    
    :param in:  handle  the CAN handle
    :param in:  apiId   the ID to write (0-1023)
    :param in:  message the message
    :param out: status Error status variable. 0 on success.
    """
def writeCANPacketRepeating(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANMessage, repeatMs: typing.SupportsInt) -> int:
    """
    Writes a repeating packet to the CAN device with a specific ID.
    
    This ID is 10 bits.
    
    The device will automatically repeat the packet at the specified interval
    
    :param in:  handle   the CAN handle
    :param in:  apiId    the ID to write (0-1023)
    :param in:  message  the message
    :param in:  repeatMs the period to repeat in ms
    :param out: status  Error status variable. 0 on success.
    """
def writeCANRTRFrame(handle: typing.SupportsInt, apiId: typing.SupportsInt, message: CANMessage) -> int:
    """
    Writes an RTR frame of the specified length to the CAN device with the
    specific ID.
    
    By spec, the length must be equal to the length sent by the other device,
    otherwise behavior is unspecified.
    
    :param in:  handle   the CAN handle
    :param in:  apiId    the ID to write (0-1023)
    :param in:  message  the message
    :param out: status  Error status variable. 0 on success.
    """
def writeI2C(port: I2CPort, deviceAddress: typing.SupportsInt, dataToSend: typing_extensions.Buffer) -> int:
    """
    Executes a write transaction with the device.
    
    Writes a single byte to a register on a device and wait until the
    transaction is complete.
    
    :param port:          The I2C port, 0 for the on-board, 1 for the MXP.
    :param deviceAddress: The address of the register on the device to be
                          written.
    :param dataToSend:    The byte to write to the register on the device.
    :param sendSize:      Number of bytes to send.
    
    :returns: 0 on success or -1 on transfer abort.
    """
def writeSerial(handle: typing.SupportsInt, buffer: typing_extensions.Buffer) -> tuple[int, int]:
    """
    Writes data to the serial port.
    
    :param in:  handle  the serial port handle
    :param in:  buffer  the buffer to write
    :param in:  count   the number of bytes to write from the buffer
    :param out: status the error code, or 0 for success
    
    :returns: the number of bytes actually written
    """
__hal_simulation__: bool = True
__halplatform__: str = 'sim'
_cleanup: typing.Any  # value = <capsule object>
