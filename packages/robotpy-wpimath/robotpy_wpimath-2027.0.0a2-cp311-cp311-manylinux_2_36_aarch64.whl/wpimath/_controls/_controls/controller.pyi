from __future__ import annotations
import numpy
import numpy.typing
import typing
import wpimath._controls._controls.system
import wpimath._controls._controls.trajectory
import wpimath.geometry._geometry
import wpimath.kinematics._kinematics
import wpimath.units
import wpiutil._wpiutil
__all__ = ['ArmFeedforward', 'BangBangController', 'ControlAffinePlantInversionFeedforward_1_1', 'ControlAffinePlantInversionFeedforward_2_1', 'ControlAffinePlantInversionFeedforward_2_2', 'DifferentialDriveAccelerationLimiter', 'DifferentialDriveWheelVoltages', 'ElevatorFeedforward', 'HolonomicDriveController', 'ImplicitModelFollower_1_1', 'ImplicitModelFollower_2_1', 'ImplicitModelFollower_2_2', 'LTVDifferentialDriveController', 'LTVUnicycleController', 'LinearPlantInversionFeedforward_1_1', 'LinearPlantInversionFeedforward_2_1', 'LinearPlantInversionFeedforward_2_2', 'LinearPlantInversionFeedforward_3_2', 'LinearQuadraticRegulator_1_1', 'LinearQuadraticRegulator_2_1', 'LinearQuadraticRegulator_2_2', 'LinearQuadraticRegulator_3_2', 'PIDController', 'ProfiledPIDController', 'ProfiledPIDControllerRadians', 'SimpleMotorFeedforwardMeters', 'SimpleMotorFeedforwardRadians']
class ArmFeedforward:
    """
    A helper class that computes feedforward outputs for a simple arm (modeled as
    a motor acting against the force of gravity on a beam suspended at an angle).
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xffd41351c7e0>
    def __init__(self, kS: wpimath.units.volts, kG: wpimath.units.volts, kV: wpimath.units.volt_seconds_per_radian, kA: wpimath.units.volt_seconds_squared_per_radian = 0.0, dt: wpimath.units.seconds = 0.02) -> None:
        """
        Creates a new ArmFeedforward with the specified gains.
        
        :param kS: The static gain, in volts.
        :param kG: The gravity gain, in volts.
        :param kV: The velocity gain, in volt seconds per radian.
        :param kA: The acceleration gain, in volt seconds² per radian.
        :param dt: The period in seconds.
                   @throws IllegalArgumentException for kv &lt; zero.
                   @throws IllegalArgumentException for ka &lt; zero.
                   @throws IllegalArgumentException for period &le; zero.
        """
    @typing.overload
    def calculate(self, currentAngle: wpimath.units.radians, currentVelocity: wpimath.units.radians_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoint assuming discrete
        control. Use this method when the velocity does not change.
        
        :param currentAngle:    The current angle. This angle should be measured from
                                the horizontal (i.e. if the provided angle is 0, the arm should be parallel
                                to the floor). If your encoder does not follow this convention, an offset
                                should be added.
        :param currentVelocity: The current velocity.
        
        :returns: The computed feedforward in volts.
        """
    @typing.overload
    def calculate(self, currentAngle: wpimath.units.radians, currentVelocity: wpimath.units.radians_per_second, nextVelocity: wpimath.units.radians_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoints assuming discrete
        control.
        
        :param currentAngle:    The current angle. This angle should be measured from
                                the horizontal (i.e. if the provided angle is 0, the arm should be parallel
                                to the floor). If your encoder does not follow this convention, an offset
                                should be added.
        :param currentVelocity: The current velocity.
        :param nextVelocity:    The next velocity.
        
        :returns: The computed feedforward in volts.
        """
    def getKa(self) -> wpimath.units.volt_seconds_squared_per_radian:
        """
        Returns the acceleration gain.
        
        :returns: The acceleration gain.
        """
    def getKg(self) -> wpimath.units.volts:
        """
        Returns the gravity gain.
        
        :returns: The gravity gain.
        """
    def getKs(self) -> wpimath.units.volts:
        """
        Returns the static gain.
        
        :returns: The static gain.
        """
    def getKv(self) -> wpimath.units.volt_seconds_per_radian:
        """
        Returns the velocity gain.
        
        :returns: The velocity gain.
        """
    def maxAchievableAcceleration(self, maxVoltage: wpimath.units.volts, angle: wpimath.units.radians, velocity: wpimath.units.radians_per_second) -> wpimath.units.radians_per_second_squared:
        """
        Calculates the maximum achievable acceleration given a maximum voltage
        supply, a position, and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the arm.
        :param angle:      The angle of the arm. This angle should be measured
                           from the horizontal (i.e. if the provided angle is 0,
                           the arm should be parallel to the floor). If your
                           encoder does not follow this convention, an offset
                           should be added.
        :param velocity:   The velocity of the arm.
        
        :returns: The maximum possible acceleration at the given velocity and angle.
        """
    def maxAchievableVelocity(self, maxVoltage: wpimath.units.volts, angle: wpimath.units.radians, acceleration: wpimath.units.radians_per_second_squared) -> wpimath.units.radians_per_second:
        """
        Calculates the maximum achievable velocity given a maximum voltage supply,
        a position, and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the arm.
        :param angle:        The angle of the arm. This angle should be measured
                             from the horizontal (i.e. if the provided angle is 0,
                             the arm should be parallel to the floor). If your
                             encoder does not follow this convention, an offset
                             should be added.
        :param acceleration: The acceleration of the arm.
        
        :returns: The maximum possible velocity at the given acceleration and angle.
        """
    def minAchievableAcceleration(self, maxVoltage: wpimath.units.volts, angle: wpimath.units.radians, velocity: wpimath.units.radians_per_second) -> wpimath.units.radians_per_second_squared:
        """
        Calculates the minimum achievable acceleration given a maximum voltage
        supply, a position, and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the arm.
        :param angle:      The angle of the arm. This angle should be measured
                           from the horizontal (i.e. if the provided angle is 0,
                           the arm should be parallel to the floor). If your
                           encoder does not follow this convention, an offset
                           should be added.
        :param velocity:   The velocity of the arm.
        
        :returns: The minimum possible acceleration at the given velocity and angle.
        """
    def minAchievableVelocity(self, maxVoltage: wpimath.units.volts, angle: wpimath.units.radians, acceleration: wpimath.units.radians_per_second_squared) -> wpimath.units.radians_per_second:
        """
        Calculates the minimum achievable velocity given a maximum voltage supply,
        a position, and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the arm.
        :param angle:        The angle of the arm. This angle should be measured
                             from the horizontal (i.e. if the provided angle is 0,
                             the arm should be parallel to the floor). If your
                             encoder does not follow this convention, an offset
                             should be added.
        :param acceleration: The acceleration of the arm.
        
        :returns: The minimum possible velocity at the given acceleration and angle.
        """
    def setKa(self, kA: wpimath.units.volt_seconds_squared_per_radian) -> None:
        """
        Sets the acceleration gain.
        
        :param kA: The acceleration gain.
        """
    def setKg(self, kG: wpimath.units.volts) -> None:
        """
        Sets the gravity gain.
        
        :param kG: The gravity gain.
        """
    def setKs(self, kS: wpimath.units.volts) -> None:
        """
        Sets the static gain.
        
        :param kS: The static gain.
        """
    def setKv(self, kV: wpimath.units.volt_seconds_per_radian) -> None:
        """
        Sets the velocity gain.
        
        :param kV: The velocity gain.
        """
class BangBangController(wpiutil._wpiutil.Sendable):
    """
    Implements a bang-bang controller, which outputs either 0 or 1 depending on
    whether the measurement is less than the setpoint. This maximally-aggressive
    control approach works very well for velocity control of high-inertia
    mechanisms, and poorly on most other things.
    
    Note that this is an *asymmetric* bang-bang controller - it will not exert
    any control effort in the reverse direction (e.g. it won't try to slow down
    an over-speeding shooter wheel). This asymmetry is *extremely important.*
    Bang-bang control is extremely simple, but also potentially hazardous. Always
    ensure that your motor controllers are set to "coast" before attempting to
    control them with a bang-bang controller.
    """
    def __init__(self, tolerance: typing.SupportsFloat = ...) -> None:
        """
        Creates a new bang-bang controller.
        
        Always ensure that your motor controllers are set to "coast" before
        attempting to control them with a bang-bang controller.
        
        :param tolerance: Tolerance for atSetpoint.
        """
    def atSetpoint(self) -> bool:
        """
        Returns true if the error is within the tolerance of the setpoint.
        
        :returns: Whether the error is within the acceptable bounds.
        """
    @typing.overload
    def calculate(self, measurement: typing.SupportsFloat, setpoint: typing.SupportsFloat) -> float:
        """
        Returns the calculated control output.
        
        Always ensure that your motor controllers are set to "coast" before
        attempting to control them with a bang-bang controller.
        
        :param measurement: The most recent measurement of the process variable.
        :param setpoint:    The setpoint for the process variable.
        
        :returns: The calculated motor output (0 or 1).
        """
    @typing.overload
    def calculate(self, measurement: typing.SupportsFloat) -> float:
        """
        Returns the calculated control output.
        
        :param measurement: The most recent measurement of the process variable.
        
        :returns: The calculated motor output (0 or 1).
        """
    def getError(self) -> float:
        """
        Returns the current error.
        
        :returns: The current error.
        """
    def getMeasurement(self) -> float:
        """
        Returns the current measurement of the process variable.
        
        :returns: The current measurement of the process variable.
        """
    def getSetpoint(self) -> float:
        """
        Returns the current setpoint of the bang-bang controller.
        
        :returns: The current setpoint.
        """
    def getTolerance(self) -> float:
        """
        Returns the current tolerance of the controller.
        
        :returns: The current tolerance.
        """
    def initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    def setSetpoint(self, setpoint: typing.SupportsFloat) -> None:
        """
        Sets the setpoint for the bang-bang controller.
        
        :param setpoint: The desired setpoint.
        """
    def setTolerance(self, tolerance: typing.SupportsFloat) -> None:
        """
        Sets the error within which AtSetpoint will return true.
        
        :param tolerance: Position error which is tolerable.
        """
class ControlAffinePlantInversionFeedforward_1_1:
    """
    Constructs a control-affine plant inversion model-based feedforward from
    given model dynamics.
    
    If given the vector valued function as f(x, u) where x is the state
    vector and u is the input vector, the B matrix(continuous input matrix)
    is calculated through a NumericalJacobian. In this case f has to be
    control-affine (of the form f(x) + Bu).
    
    The feedforward is calculated as
    :strong:` u_ff = B:sup:`+` (rDot - f(x)) `, where :strong:`
    B:sup:`+` ` is the pseudoinverse of B.
    
    This feedforward does not account for a dynamic B matrix, B is either
    determined or supplied when the feedforward is created and remains constant.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function
        of state and input.
        
        :param f:  A vector-valued function of x, the state, and
                   u, the input, that returns the derivative of
                   the state vector. HAS to be control-affine
                   (of the form f(x) + Bu).
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function of state,
        and the plant's B matrix(continuous input matrix).
        
        :param f:  A vector-valued function of x, the state,
                   that returns the derivative of the state vector.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class ControlAffinePlantInversionFeedforward_2_1:
    """
    Constructs a control-affine plant inversion model-based feedforward from
    given model dynamics.
    
    If given the vector valued function as f(x, u) where x is the state
    vector and u is the input vector, the B matrix(continuous input matrix)
    is calculated through a NumericalJacobian. In this case f has to be
    control-affine (of the form f(x) + Bu).
    
    The feedforward is calculated as
    :strong:` u_ff = B:sup:`+` (rDot - f(x)) `, where :strong:`
    B:sup:`+` ` is the pseudoinverse of B.
    
    This feedforward does not account for a dynamic B matrix, B is either
    determined or supplied when the feedforward is created and remains constant.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function
        of state and input.
        
        :param f:  A vector-valued function of x, the state, and
                   u, the input, that returns the derivative of
                   the state vector. HAS to be control-affine
                   (of the form f(x) + Bu).
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function of state,
        and the plant's B matrix(continuous input matrix).
        
        :param f:  A vector-valued function of x, the state,
                   that returns the derivative of the state vector.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class ControlAffinePlantInversionFeedforward_2_2:
    """
    Constructs a control-affine plant inversion model-based feedforward from
    given model dynamics.
    
    If given the vector valued function as f(x, u) where x is the state
    vector and u is the input vector, the B matrix(continuous input matrix)
    is calculated through a NumericalJacobian. In this case f has to be
    control-affine (of the form f(x) + Bu).
    
    The feedforward is calculated as
    :strong:` u_ff = B:sup:`+` (rDot - f(x)) `, where :strong:`
    B:sup:`+` ` is the pseudoinverse of B.
    
    This feedforward does not account for a dynamic B matrix, B is either
    determined or supplied when the feedforward is created and remains constant.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function
        of state and input.
        
        :param f:  A vector-valued function of x, the state, and
                   u, the input, that returns the derivative of
                   the state vector. HAS to be control-affine
                   (of the form f(x) + Bu).
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def __init__(self, f: typing.Callable[[typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]], typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with given model dynamics as a function of state,
        and the plant's B matrix(continuous input matrix).
        
        :param f:  A vector-valued function of x, the state,
                   that returns the derivative of the state vector.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: The timestep between calls of calculate().
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class DifferentialDriveAccelerationLimiter:
    """
    Filters the provided voltages to limit a differential drive's linear and
    angular acceleration.
    
    The differential drive model can be created via the functions in
    LinearSystemId.
    """
    @typing.overload
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_2_2, trackwidth: wpimath.units.meters, maxLinearAccel: wpimath.units.meters_per_second_squared, maxAngularAccel: wpimath.units.radians_per_second_squared) -> None:
        """
        Constructs a DifferentialDriveAccelerationLimiter.
        
        :param system:          The differential drive dynamics.
        :param trackwidth:      The distance between the differential drive's left and
                                right wheels.
        :param maxLinearAccel:  The maximum linear acceleration.
        :param maxAngularAccel: The maximum angular acceleration.
        """
    @typing.overload
    def __init__(self, system: wpimath._controls._controls.system.LinearSystem_2_2_2, trackwidth: wpimath.units.meters, minLinearAccel: wpimath.units.meters_per_second_squared, maxLinearAccel: wpimath.units.meters_per_second_squared, maxAngularAccel: wpimath.units.radians_per_second_squared) -> None:
        """
        Constructs a DifferentialDriveAccelerationLimiter.
        
        :param system:          The differential drive dynamics.
        :param trackwidth:      The distance between the differential drive's left and
                                right wheels.
        :param minLinearAccel:  The minimum (most negative) linear acceleration.
        :param maxLinearAccel:  The maximum (most positive) linear acceleration.
        :param maxAngularAccel: The maximum angular acceleration.
                                @throws std::invalid_argument if minimum linear acceleration is greater
                                than maximum linear acceleration
        """
    def calculate(self, leftVelocity: wpimath.units.meters_per_second, rightVelocity: wpimath.units.meters_per_second, leftVoltage: wpimath.units.volts, rightVoltage: wpimath.units.volts) -> DifferentialDriveWheelVoltages:
        """
        Returns the next voltage pair subject to acceleration constraints.
        
        :param leftVelocity:  The left wheel velocity.
        :param rightVelocity: The right wheel velocity.
        :param leftVoltage:   The unconstrained left motor voltage.
        :param rightVoltage:  The unconstrained right motor voltage.
        
        :returns: The constrained wheel voltages.
        """
class DifferentialDriveWheelVoltages:
    """
    Motor voltages for a differential drive.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xffd41351e280>
    def __init__(self, left: wpimath.units.volts = 0, right: wpimath.units.volts = 0) -> None:
        ...
    def __repr__(self) -> str:
        ...
    @property
    def left(self) -> wpimath.units.volts:
        """
        Left wheel voltage.
        """
    @left.setter
    def left(self, arg0: wpimath.units.volts) -> None:
        ...
    @property
    def right(self) -> wpimath.units.volts:
        """
        Right wheel voltage.
        """
    @right.setter
    def right(self, arg0: wpimath.units.volts) -> None:
        ...
class ElevatorFeedforward:
    """
    A helper class that computes feedforward outputs for a simple elevator
    (modeled as a motor acting against the force of gravity).
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xffd41351e820>
    def __init__(self, kS: wpimath.units.volts, kG: wpimath.units.volts, kV: wpimath.units.volt_seconds_per_meter, kA: wpimath.units.volt_seconds_squared_per_meter = 0.0, dt: wpimath.units.seconds = 0.02) -> None:
        """
        Creates a new ElevatorFeedforward with the specified gains.
        
        :param kS: The static gain, in volts.
        :param kG: The gravity gain, in volts.
        :param kV: The velocity gain, in volt seconds per distance.
        :param kA: The acceleration gain, in volt seconds² per distance.
        :param dt: The period in seconds.
                   @throws IllegalArgumentException for kv &lt; zero.
                   @throws IllegalArgumentException for ka &lt; zero.
                   @throws IllegalArgumentException for period &le; zero.
        """
    @typing.overload
    def calculate(self, currentVelocity: wpimath.units.meters_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoint assuming discrete
        control. Use this method when the setpoint does not change.
        
        :param currentVelocity: The velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    @typing.overload
    def calculate(self, currentVelocity: wpimath.units.meters_per_second, nextVelocity: wpimath.units.meters_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoints assuming discrete
        control.
        
        Note this method is inaccurate when the velocity crosses 0.
        
        :param currentVelocity: The current velocity setpoint.
        :param nextVelocity:    The next velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    def getKa(self) -> wpimath.units.volt_seconds_squared_per_meter:
        """
        Returns the acceleration gain.
        
        :returns: The acceleration gain.
        """
    def getKg(self) -> wpimath.units.volts:
        """
        Returns the gravity gain.
        
        :returns: The gravity gain.
        """
    def getKs(self) -> wpimath.units.volts:
        """
        Returns the static gain.
        
        :returns: The static gain.
        """
    def getKv(self) -> wpimath.units.volt_seconds_per_meter:
        """
        Returns the velocity gain.
        
        :returns: The velocity gain.
        """
    def maxAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.meters_per_second) -> wpimath.units.meters_per_second_squared:
        """
        Calculates the maximum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the elevator.
        :param velocity:   The velocity of the elevator.
        
        :returns: The maximum possible acceleration at the given velocity.
        """
    def maxAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.meters_per_second_squared) -> wpimath.units.meters_per_second:
        """
        Calculates the maximum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the elevator.
        :param acceleration: The acceleration of the elevator.
        
        :returns: The maximum possible velocity at the given acceleration.
        """
    def minAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.meters_per_second) -> wpimath.units.meters_per_second_squared:
        """
        Calculates the minimum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the elevator.
        :param velocity:   The velocity of the elevator.
        
        :returns: The minimum possible acceleration at the given velocity.
        """
    def minAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.meters_per_second_squared) -> wpimath.units.meters_per_second:
        """
        Calculates the minimum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the elevator.
        :param acceleration: The acceleration of the elevator.
        
        :returns: The minimum possible velocity at the given acceleration.
        """
    def setKa(self, kA: wpimath.units.volt_seconds_squared_per_meter) -> None:
        """
        Sets the acceleration gain.
        
        :param kA: The acceleration gain.
        """
    def setKg(self, kG: wpimath.units.volts) -> None:
        """
        Sets the gravity gain.
        
        :param kG: The gravity gain.
        """
    def setKs(self, kS: wpimath.units.volts) -> None:
        """
        Sets the static gain.
        
        :param kS: The static gain.
        """
    def setKv(self, kV: wpimath.units.volt_seconds_per_meter) -> None:
        """
        Sets the velocity gain.
        
        :param kV: The velocity gain.
        """
class HolonomicDriveController:
    """
    This holonomic drive controller can be used to follow trajectories using a
    holonomic drivetrain (i.e. swerve or mecanum). Holonomic trajectory following
    is a much simpler problem to solve compared to skid-steer style drivetrains
    because it is possible to individually control field-relative x, y, and
    angular velocity.
    
    The holonomic drive controller takes in one PID controller for each
    direction, field-relative x and y, and one profiled PID controller for the
    angular direction. Because the heading dynamics are decoupled from
    translations, users can specify a custom heading that the drivetrain should
    point toward. This heading reference is profiled for smoothness.
    """
    def __init__(self, xController: PIDController, yController: PIDController, thetaController: ProfiledPIDControllerRadians) -> None:
        """
        Constructs a holonomic drive controller.
        
        :param xController:     A PID Controller to respond to error in the
                                field-relative x direction.
        :param yController:     A PID Controller to respond to error in the
                                field-relative y direction.
        :param thetaController: A profiled PID controller to respond to error in
                                angle.
        """
    def atReference(self) -> bool:
        """
        Returns true if the pose error is within tolerance of the reference.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, trajectoryPose: wpimath.geometry._geometry.Pose2d, desiredLinearVelocity: wpimath.units.meters_per_second, desiredHeading: wpimath.geometry._geometry.Rotation2d) -> wpimath.kinematics._kinematics.ChassisSpeeds:
        """
        Returns the next output of the holonomic drive controller.
        
        :param currentPose:           The current pose, as measured by odometry or pose
                                      estimator.
        :param trajectoryPose:        The desired trajectory pose, as sampled for the
                                      current timestep.
        :param desiredLinearVelocity: The desired linear velocity.
        :param desiredHeading:        The desired heading.
        
        :returns: The next output of the holonomic drive controller.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, desiredState: wpimath._controls._controls.trajectory.Trajectory.State, desiredHeading: wpimath.geometry._geometry.Rotation2d) -> wpimath.kinematics._kinematics.ChassisSpeeds:
        """
        Returns the next output of the holonomic drive controller.
        
        :param currentPose:    The current pose, as measured by odometry or pose
                               estimator.
        :param desiredState:   The desired trajectory pose, as sampled for the current
                               timestep.
        :param desiredHeading: The desired heading.
        
        :returns: The next output of the holonomic drive controller.
        """
    def getThetaController(self) -> ProfiledPIDControllerRadians:
        """
        Returns the rotation ProfiledPIDController
        """
    def getXController(self) -> PIDController:
        """
        Returns the X PIDController
        """
    def getYController(self) -> PIDController:
        """
        Returns the Y PIDController
        """
    def setEnabled(self, enabled: bool) -> None:
        """
        Enables and disables the controller for troubleshooting purposes. When
        Calculate() is called on a disabled controller, only feedforward values
        are returned.
        
        :param enabled: If the controller is enabled or not.
        """
    def setTolerance(self, tolerance: wpimath.geometry._geometry.Pose2d) -> None:
        """
        Sets the pose error which is considered tolerable for use with
        AtReference().
        
        :param tolerance: Pose error which is tolerable.
        """
class ImplicitModelFollower_1_1:
    """
    Contains the controller coefficients and logic for an implicit model
    follower.
    
    Implicit model following lets us design a feedback controller that erases the
    dynamics of our system and makes it behave like some other system. This can
    be used to make a drivetrain more controllable during teleop driving by
    making it behave like a slower or more benign drivetrain.
    
    For more on the underlying math, read appendix B.3 in
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], Aref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], Bref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:    Continuous system matrix of the plant being controlled.
        :param B:    Continuous input matrix of the plant being controlled.
        :param Aref: Continuous system matrix whose dynamics should be followed.
        :param Bref: Continuous input matrix whose dynamics should be followed.
        """
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_1, plantRef: wpimath._controls._controls.system.LinearSystem_1_1_1) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_2, plantRef: wpimath._controls._controls.system.LinearSystem_1_1_2) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_3, plantRef: wpimath._controls._controls.system.LinearSystem_1_1_3) -> None:
        ...
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        :param u: The current input for the original model.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class ImplicitModelFollower_2_1:
    """
    Contains the controller coefficients and logic for an implicit model
    follower.
    
    Implicit model following lets us design a feedback controller that erases the
    dynamics of our system and makes it behave like some other system. This can
    be used to make a drivetrain more controllable during teleop driving by
    making it behave like a slower or more benign drivetrain.
    
    For more on the underlying math, read appendix B.3 in
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], Aref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Bref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:    Continuous system matrix of the plant being controlled.
        :param B:    Continuous input matrix of the plant being controlled.
        :param Aref: Continuous system matrix whose dynamics should be followed.
        :param Bref: Continuous input matrix whose dynamics should be followed.
        """
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_1, plantRef: wpimath._controls._controls.system.LinearSystem_2_1_1) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_2, plantRef: wpimath._controls._controls.system.LinearSystem_2_1_2) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_3, plantRef: wpimath._controls._controls.system.LinearSystem_2_1_3) -> None:
        ...
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        :param u: The current input for the original model.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class ImplicitModelFollower_2_2:
    """
    Contains the controller coefficients and logic for an implicit model
    follower.
    
    Implicit model following lets us design a feedback controller that erases the
    dynamics of our system and makes it behave like some other system. This can
    be used to make a drivetrain more controllable during teleop driving by
    making it behave like a slower or more benign drivetrain.
    
    For more on the underlying math, read appendix B.3 in
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Aref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Bref: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"]) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:    Continuous system matrix of the plant being controlled.
        :param B:    Continuous input matrix of the plant being controlled.
        :param Aref: Continuous system matrix whose dynamics should be followed.
        :param Bref: Continuous input matrix whose dynamics should be followed.
        """
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_1, plantRef: wpimath._controls._controls.system.LinearSystem_2_2_1) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_2, plantRef: wpimath._controls._controls.system.LinearSystem_2_2_2) -> None:
        ...
    @typing.overload
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_3, plantRef: wpimath._controls._controls.system.LinearSystem_2_2_3) -> None:
        ...
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], u: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        :param u: The current input for the original model.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class LTVDifferentialDriveController:
    """
    The linear time-varying differential drive controller has a similar form to
    the LQR, but the model used to compute the controller gain is the nonlinear
    differential drive model linearized around the drivetrain's current state. We
    precompute gains for important places in our state-space, then interpolate
    between them with a lookup table to save computational resources.
    
    This controller has a flat hierarchy with pose and wheel velocity references
    and voltage outputs. This is different from a unicycle controller's nested
    hierarchy where the top-level controller has a pose reference and chassis
    velocity command outputs, and the low-level controller has wheel velocity
    references and voltage outputs. Flat hierarchies are easier to tune in one
    shot.
    
    See section 8.7 in Controls Engineering in FRC for a derivation of the
    control law we used shown in theorem 8.7.4.
    """
    def __init__(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_2, trackwidth: wpimath.units.meters, Qelems: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], Relems: tuple[typing.SupportsFloat, typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a linear time-varying differential drive controller.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param plant:      The differential drive velocity plant.
        :param trackwidth: The distance between the differential drive's left and
                           right wheels.
        :param Qelems:     The maximum desired error tolerance for each state.
        :param Relems:     The maximum desired control effort for each input.
        :param dt:         Discretization timestep.
        """
    def atReference(self) -> bool:
        """
        Returns true if the pose error is within tolerance of the reference.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, leftVelocity: wpimath.units.meters_per_second, rightVelocity: wpimath.units.meters_per_second, poseRef: wpimath.geometry._geometry.Pose2d, leftVelocityRef: wpimath.units.meters_per_second, rightVelocityRef: wpimath.units.meters_per_second) -> DifferentialDriveWheelVoltages:
        """
        Returns the left and right output voltages of the LTV controller.
        
        The reference pose, linear velocity, and angular velocity should come from
        a drivetrain trajectory.
        
        :param currentPose:      The current pose.
        :param leftVelocity:     The current left velocity.
        :param rightVelocity:    The current right velocity.
        :param poseRef:          The desired pose.
        :param leftVelocityRef:  The desired left velocity.
        :param rightVelocityRef: The desired right velocity.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, leftVelocity: wpimath.units.meters_per_second, rightVelocity: wpimath.units.meters_per_second, desiredState: wpimath._controls._controls.trajectory.Trajectory.State) -> DifferentialDriveWheelVoltages:
        """
        Returns the left and right output voltages of the LTV controller.
        
        The reference pose, linear velocity, and angular velocity should come from
        a drivetrain trajectory.
        
        :param currentPose:   The current pose.
        :param leftVelocity:  The left velocity.
        :param rightVelocity: The right velocity.
        :param desiredState:  The desired pose, linear velocity, and angular velocity
                              from a trajectory.
        """
    def setTolerance(self, poseTolerance: wpimath.geometry._geometry.Pose2d, leftVelocityTolerance: wpimath.units.meters_per_second, rightVelocityTolerance: wpimath.units.meters_per_second) -> None:
        """
        Sets the pose error which is considered tolerable for use with
        AtReference().
        
        :param poseTolerance:          Pose error which is tolerable.
        :param leftVelocityTolerance:  Left velocity error which is tolerable.
        :param rightVelocityTolerance: Right velocity error which is tolerable.
        """
class LTVUnicycleController:
    """
    The linear time-varying unicycle controller has a similar form to the LQR,
    but the model used to compute the controller gain is the nonlinear unicycle
    model linearized around the drivetrain's current state.
    
    See section 8.9 in Controls Engineering in FRC for a derivation of the
    control law we used shown in theorem 8.9.1.
    """
    @typing.overload
    def __init__(self, dt: wpimath.units.seconds) -> None:
        """
        Constructs a linear time-varying unicycle controller with default maximum
        desired error tolerances of (x = 0.0625 m, y = 0.125 m, heading = 2 rad)
        and default maximum desired control effort of (linear velocity = 1 m/s,
        angular velocity = 2 rad/s).
        
        :param dt: Discretization timestep.
        """
    @typing.overload
    def __init__(self, Qelems: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], Relems: tuple[typing.SupportsFloat, typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a linear time-varying unicycle controller.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param Qelems: The maximum desired error tolerance for each state (x, y,
                       heading).
        :param Relems: The maximum desired control effort for each input (linear
                       velocity, angular velocity).
        :param dt:     Discretization timestep.
        """
    def atReference(self) -> bool:
        """
        Returns true if the pose error is within tolerance of the reference.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, poseRef: wpimath.geometry._geometry.Pose2d, linearVelocityRef: wpimath.units.meters_per_second, angularVelocityRef: wpimath.units.radians_per_second) -> wpimath.kinematics._kinematics.ChassisSpeeds:
        """
        Returns the linear and angular velocity outputs of the LTV controller.
        
        The reference pose, linear velocity, and angular velocity should come from
        a drivetrain trajectory.
        
        :param currentPose:        The current pose.
        :param poseRef:            The desired pose.
        :param linearVelocityRef:  The desired linear velocity.
        :param angularVelocityRef: The desired angular velocity.
        """
    @typing.overload
    def calculate(self, currentPose: wpimath.geometry._geometry.Pose2d, desiredState: wpimath._controls._controls.trajectory.Trajectory.State) -> wpimath.kinematics._kinematics.ChassisSpeeds:
        """
        Returns the linear and angular velocity outputs of the LTV controller.
        
        The reference pose, linear velocity, and angular velocity should come from
        a drivetrain trajectory.
        
        :param currentPose:  The current pose.
        :param desiredState: The desired pose, linear velocity, and angular velocity
                             from a trajectory.
        """
    def setEnabled(self, enabled: bool) -> None:
        """
        Enables and disables the controller for troubleshooting purposes.
        
        :param enabled: If the controller is enabled or not.
        """
    def setTolerance(self, poseTolerance: wpimath.geometry._geometry.Pose2d) -> None:
        """
        Sets the pose error which is considered tolerable for use with
        AtReference().
        
        :param poseTolerance: Pose error which is tolerable.
        """
class LinearPlantInversionFeedforward_1_1:
    """
    Constructs a plant inversion model-based feedforward from a LinearSystem.
    
    The feedforward is calculated as :strong:` u_ff = B:sup:`+` (r_k+1 - A
    r_k) `, where :strong:` B:sup:`+` ` is the pseudoinverse
    of B.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with the given coefficients.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: Discretization timestep.
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class LinearPlantInversionFeedforward_2_1:
    """
    Constructs a plant inversion model-based feedforward from a LinearSystem.
    
    The feedforward is calculated as :strong:` u_ff = B:sup:`+` (r_k+1 - A
    r_k) `, where :strong:` B:sup:`+` ` is the pseudoinverse
    of B.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with the given coefficients.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: Discretization timestep.
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class LinearPlantInversionFeedforward_2_2:
    """
    Constructs a plant inversion model-based feedforward from a LinearSystem.
    
    The feedforward is calculated as :strong:` u_ff = B:sup:`+` (r_k+1 - A
    r_k) `, where :strong:` B:sup:`+` ` is the pseudoinverse
    of B.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with the given coefficients.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: Discretization timestep.
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class LinearPlantInversionFeedforward_3_2:
    """
    Constructs a plant inversion model-based feedforward from a LinearSystem.
    
    The feedforward is calculated as :strong:` u_ff = B:sup:`+` (r_k+1 - A
    r_k) `, where :strong:` B:sup:`+` ` is the pseudoinverse
    of B.
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns the current reference vector r.
        
        :returns: The current reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the current reference vector.
        """
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a feedforward with the given coefficients.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param dt: Discretization timestep.
        """
    @typing.overload
    def calculate(self, nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with only the desired
        future reference. This uses the internally stored "current"
        reference.
        
        If this method is used the initial state of the system is the one set using
        Reset(const StateVector&). If the initial state is not
        set it defaults to a zero vector.
        
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def calculate(self, r: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Calculate the feedforward with current and future reference vectors.
        
        :param r:     The reference state of the current timestep (k).
        :param nextR: The reference state of the future timestep (k + dt).
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def reset(self, initialState: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> None:
        """
        Resets the feedforward with a specified initial state vector.
        
        :param initialState: The initial state vector.
        """
    @typing.overload
    def reset(self) -> None:
        """
        Resets the feedforward with a zero initial state vector.
        """
    @typing.overload
    def uff(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the previously calculated feedforward as an input vector.
        
        :returns: The calculated feedforward.
        """
    @typing.overload
    def uff(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the previously calculated feedforward.
        
        :param i: Row of uff.
        
        :returns: The row of the calculated feedforward.
        """
class LinearQuadraticRegulator_1_1:
    """
    Contains the controller coefficients and logic for a linear-quadratic
    regulator (LQR).
    LQRs use the control law u = K(r - x).
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def K(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the controller matrix K.
        """
    @typing.overload
    def K(self, i: typing.SupportsInt, j: typing.SupportsInt) -> float:
        """
        Returns an element of the controller matrix K.
        
        :param i: Row of K.
        :param j: Column of K.
        """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the reference vector r.
        
        :returns: The reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the reference vector.
        """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], Qelems: tuple[typing.SupportsFloat], Relems: tuple[typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param A:      Continuous system matrix of the plant being controlled.
        :param B:      Continuous input matrix of the plant being controlled.
        :param Qelems: The maximum desired error tolerance for each state.
        :param Relems: The maximum desired control effort for each input.
        :param dt:     Discretization timestep.
                       @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], N: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param N:  The state-input cross-term cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_1_1_1, arg1: tuple[typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_1_1_2, arg1: tuple[typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_1_1_3, arg1: tuple[typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        """
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x:     The current state x.
        :param nextR: The next reference vector r.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_1, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_1_1_2, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class LinearQuadraticRegulator_2_1:
    """
    Contains the controller coefficients and logic for a linear-quadratic
    regulator (LQR).
    LQRs use the control law u = K(r - x).
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def K(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 2]"]:
        """
        Returns the controller matrix K.
        """
    @typing.overload
    def K(self, i: typing.SupportsInt, j: typing.SupportsInt) -> float:
        """
        Returns an element of the controller matrix K.
        
        :param i: Row of K.
        :param j: Column of K.
        """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the reference vector r.
        
        :returns: The reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the reference vector.
        """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], Qelems: tuple[typing.SupportsFloat, typing.SupportsFloat], Relems: tuple[typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param A:      Continuous system matrix of the plant being controlled.
        :param B:      Continuous input matrix of the plant being controlled.
        :param Qelems: The maximum desired error tolerance for each state.
        :param Relems: The maximum desired control effort for each input.
        :param dt:     Discretization timestep.
                       @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[1, 1]"], N: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param N:  The state-input cross-term cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_1_1, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_1_2, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_1_3, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        """
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[1, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x:     The current state x.
        :param nextR: The next reference vector r.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_1, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_2_1_2, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class LinearQuadraticRegulator_2_2:
    """
    Contains the controller coefficients and logic for a linear-quadratic
    regulator (LQR).
    LQRs use the control law u = K(r - x).
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def K(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 2]"]:
        """
        Returns the controller matrix K.
        """
    @typing.overload
    def K(self, i: typing.SupportsInt, j: typing.SupportsInt) -> float:
        """
        Returns an element of the controller matrix K.
        
        :param i: Row of K.
        :param j: Column of K.
        """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the reference vector r.
        
        :returns: The reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the reference vector.
        """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Qelems: tuple[typing.SupportsFloat, typing.SupportsFloat], Relems: tuple[typing.SupportsFloat, typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param A:      Continuous system matrix of the plant being controlled.
        :param B:      Continuous input matrix of the plant being controlled.
        :param Qelems: The maximum desired error tolerance for each state.
        :param Relems: The maximum desired control effort for each input.
        :param dt:     Discretization timestep.
                       @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], N: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param N:  The state-input cross-term cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_2_1, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_2_2, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_2_2_3, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        """
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x:     The current state x.
        :param nextR: The next reference vector r.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_1, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_2_2_2, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class LinearQuadraticRegulator_3_2:
    """
    Contains the controller coefficients and logic for a linear-quadratic
    regulator (LQR).
    LQRs use the control law u = K(r - x).
    
    For more on the underlying math, read
    https://file.tavsys.net/control/controls-engineering-in-frc.pdf.
    
    @tparam States Number of states.
    @tparam Inputs Number of inputs.
    """
    @typing.overload
    def K(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 3]"]:
        """
        Returns the controller matrix K.
        """
    @typing.overload
    def K(self, i: typing.SupportsInt, j: typing.SupportsInt) -> float:
        """
        Returns an element of the controller matrix K.
        
        :param i: Row of K.
        :param j: Column of K.
        """
    @typing.overload
    def R(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns the reference vector r.
        
        :returns: The reference vector.
        """
    @typing.overload
    def R(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the reference vector r.
        
        :param i: Row of r.
        
        :returns: The row of the reference vector.
        """
    @typing.overload
    def U(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the control input vector u.
        
        :returns: The control input.
        """
    @typing.overload
    def U(self, i: typing.SupportsInt) -> float:
        """
        Returns an element of the control input vector u.
        
        :param i: Row of u.
        
        :returns: The row of the control input vector.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 2]"], Qelems: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], Relems: tuple[typing.SupportsFloat, typing.SupportsFloat], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        See
        https://docs.wpilib.org/en/stable/docs/software/advanced-controls/state-space/state-space-intro.html#lqr-tuning
        for how to select the tolerances.
        
        :param A:      Continuous system matrix of the plant being controlled.
        :param B:      Continuous input matrix of the plant being controlled.
        :param Qelems: The maximum desired error tolerance for each state.
        :param Relems: The maximum desired control effort for each input.
        :param dt:     Discretization timestep.
                       @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 2]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, A: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], B: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 2]"], Q: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"], R: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"], N: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 2]"], dt: wpimath.units.seconds) -> None:
        """
        Constructs a controller with the given coefficients and plant.
        
        :param A:  Continuous system matrix of the plant being controlled.
        :param B:  Continuous input matrix of the plant being controlled.
        :param Q:  The state cost matrix.
        :param R:  The input cost matrix.
        :param N:  The state-input cross-term cost matrix.
        :param dt: Discretization timestep.
                   @throws std::invalid_argument If the system is unstabilizable.
        """
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_3_2_1, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_3_2_2, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def __init__(self, arg0: wpimath._controls._controls.system.LinearSystem_3_2_3, arg1: tuple[typing.SupportsFloat, typing.SupportsFloat, typing.SupportsFloat], arg2: tuple[typing.SupportsFloat, typing.SupportsFloat], arg3: wpimath.units.seconds) -> None:
        ...
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x: The current state x.
        """
    @typing.overload
    def calculate(self, x: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"], nextR: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns the next output of the controller.
        
        :param x:     The current state x.
        :param nextR: The next reference vector r.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_3_2_1, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    @typing.overload
    def latencyCompensate(self, plant: wpimath._controls._controls.system.LinearSystem_3_2_2, dt: wpimath.units.seconds, inputDelay: wpimath.units.seconds) -> None:
        """
        Adjusts LQR controller gain to compensate for a pure time delay in the
        input.
        
        Linear-Quadratic regulator controller gains tend to be aggressive. If
        sensor measurements are time-delayed too long, the LQR may be unstable.
        However, if we know the amount of delay, we can compute the control based
        on where the system will be after the time delay.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf
        appendix C.4 for a derivation.
        
        :param plant:      The plant being controlled.
        :param dt:         Discretization timestep.
        :param inputDelay: Input time delay.
        """
    def reset(self) -> None:
        """
        Resets the controller.
        """
class PIDController(wpiutil._wpiutil.Sendable):
    """
    Implements a PID control loop.
    """
    def __init__(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat, period: wpimath.units.seconds = 0.02) -> None:
        """
        Allocates a PIDController with the given constants for Kp, Ki, and Kd.
        
        :param Kp:     The proportional coefficient. Must be >= 0.
        :param Ki:     The integral coefficient. Must be >= 0.
        :param Kd:     The derivative coefficient. Must be >= 0.
        :param period: The period between controller updates in seconds. The
                       default is 20 milliseconds. Must be positive.
        """
    def atSetpoint(self) -> bool:
        """
        Returns true if the error is within the tolerance of the setpoint.
        The error tolerance defauls to 0.05, and the error derivative tolerance
        defaults to ∞.
        
        This will return false until at least one input value has been computed.
        """
    @typing.overload
    def calculate(self, measurement: typing.SupportsFloat) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        """
    @typing.overload
    def calculate(self, measurement: typing.SupportsFloat, setpoint: typing.SupportsFloat) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param setpoint:    The new setpoint of the controller.
        """
    def disableContinuousInput(self) -> None:
        """
        Disables continuous input.
        """
    def enableContinuousInput(self, minimumInput: typing.SupportsFloat, maximumInput: typing.SupportsFloat) -> None:
        """
        Enables continuous input.
        
        Rather then using the max and min input range as constraints, it considers
        them to be the same point and automatically calculates the shortest route
        to the setpoint.
        
        :param minimumInput: The minimum value expected from the input.
        :param maximumInput: The maximum value expected from the input.
        """
    def getAccumulatedError(self) -> float:
        """
        Gets the accumulated error used in the integral calculation of this
        controller.
        
        :returns: The accumulated error of this controller.
        """
    def getD(self) -> float:
        """
        Gets the differential coefficient.
        
        :returns: differential coefficient
        """
    def getError(self) -> float:
        """
        Returns the difference between the setpoint and the measurement.
        """
    def getErrorDerivative(self) -> float:
        """
        Returns the error derivative.
        """
    def getErrorDerivativeTolerance(self) -> float:
        """
        Gets the error derivative tolerance of this controller. Defaults to ∞.
        
        :returns: The error derivative tolerance of the controller.
        """
    def getErrorTolerance(self) -> float:
        """
        Gets the error tolerance of this controller. Defaults to 0.05.
        
        :returns: The error tolerance of the controller.
        """
    def getI(self) -> float:
        """
        Gets the integral coefficient.
        
        :returns: integral coefficient
        """
    def getIZone(self) -> float:
        """
        Get the IZone range.
        
        :returns: Maximum magnitude of error to allow integral control.
        """
    def getP(self) -> float:
        """
        Gets the proportional coefficient.
        
        :returns: proportional coefficient
        """
    def getPeriod(self) -> wpimath.units.seconds:
        """
        Gets the period of this controller.
        
        :returns: The period of the controller.
        """
    def getPositionError(self) -> float:
        """
        Returns the difference between the setpoint and the measurement.
        
        :deprecated: Use GetError() instead.
        """
    def getPositionTolerance(self) -> float:
        """
        Gets the position tolerance of this controller.
        
        :deprecated: Use GetErrorTolerance() instead.
        
        :returns: The position tolerance of the controller.
        """
    def getSetpoint(self) -> float:
        """
        Returns the current setpoint of the PIDController.
        
        :returns: The current setpoint.
        """
    def getVelocityError(self) -> float:
        """
        Returns the velocity error.
        
        :deprecated: Use GetErrorDerivative() instead.
        """
    def getVelocityTolerance(self) -> float:
        """
        Gets the velocity tolerance of this controller.
        
        :deprecated: Use GetErrorDerivativeTolerance() instead.
        
        :returns: The velocity tolerance of the controller.
        """
    def initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    def isContinuousInputEnabled(self) -> bool:
        """
        Returns true if continuous input is enabled.
        """
    def reset(self) -> None:
        """
        Reset the previous error, the integral term, and disable the controller.
        """
    def setD(self, Kd: typing.SupportsFloat) -> None:
        """
        Sets the differential coefficient of the PID controller gain.
        
        :param Kd: The differential coefficient. Must be >= 0.
        """
    def setI(self, Ki: typing.SupportsFloat) -> None:
        """
        Sets the integral coefficient of the PID controller gain.
        
        :param Ki: The integral coefficient. Must be >= 0.
        """
    def setIZone(self, iZone: typing.SupportsFloat) -> None:
        """
        Sets the IZone range. When the absolute value of the position error is
        greater than IZone, the total accumulated error will reset to zero,
        disabling integral gain until the absolute value of the position error is
        less than IZone. This is used to prevent integral windup. Must be
        non-negative. Passing a value of zero will effectively disable integral
        gain. Passing a value of infinity disables IZone functionality.
        
        :param iZone: Maximum magnitude of error to allow integral control. Must be
                      >= 0.
        """
    def setIntegratorRange(self, minimumIntegral: typing.SupportsFloat, maximumIntegral: typing.SupportsFloat) -> None:
        """
        Sets the minimum and maximum contributions of the integral term.
        
        The internal integrator is clamped so that the integral term's contribution
        to the output stays between minimumIntegral and maximumIntegral. This
        prevents integral windup.
        
        :param minimumIntegral: The minimum contribution of the integral term.
        :param maximumIntegral: The maximum contribution of the integral term.
        """
    def setP(self, Kp: typing.SupportsFloat) -> None:
        """
        Sets the proportional coefficient of the PID controller gain.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        """
    def setPID(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat) -> None:
        """
        Sets the PID Controller gain parameters.
        
        Sets the proportional, integral, and differential coefficients.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        :param Ki: The integral coefficient. Must be >= 0.
        :param Kd: The differential coefficient. Must be >= 0.
        """
    def setSetpoint(self, setpoint: typing.SupportsFloat) -> None:
        """
        Sets the setpoint for the PIDController.
        
        :param setpoint: The desired setpoint.
        """
    def setTolerance(self, errorTolerance: typing.SupportsFloat, errorDerivativeTolerance: typing.SupportsFloat = ...) -> None:
        """
        Sets the error which is considered tolerable for use with AtSetpoint().
        
        :param errorTolerance:           error which is tolerable.
        :param errorDerivativeTolerance: error derivative which is tolerable.
        """
class ProfiledPIDController(wpiutil._wpiutil.Sendable):
    """
    Implements a PID control loop whose setpoint is constrained by a trapezoid
    profile.
    """
    def __init__(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat, constraints: wpimath._controls._controls.trajectory.TrapezoidProfile.Constraints, period: wpimath.units.seconds = 0.02) -> None:
        """
        Allocates a ProfiledPIDController with the given constants for Kp, Ki, and
        Kd. Users should call reset() when they first start running the controller
        to avoid unwanted behavior.
        
        :param Kp:          The proportional coefficient. Must be >= 0.
        :param Ki:          The integral coefficient. Must be >= 0.
        :param Kd:          The derivative coefficient. Must be >= 0.
        :param constraints: Velocity and acceleration constraints for goal.
        :param period:      The period between controller updates in seconds. The
                            default is 20 milliseconds. Must be positive.
        """
    def atGoal(self) -> bool:
        """
        Returns true if the error is within the tolerance of the error.
        
        This will return false until at least one input value has been computed.
        """
    def atSetpoint(self) -> bool:
        """
        Returns true if the error is within the tolerance of the error.
        
        Currently this just reports on target as the actual value passes through
        the setpoint. Ideally it should be based on being within the tolerance for
        some period of time.
        
        This will return false until at least one input value has been computed.
        """
    @typing.overload
    def calculate(self, measurement: float) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        """
    @typing.overload
    def calculate(self, measurement: float, goal: wpimath._controls._controls.trajectory.TrapezoidProfile.State) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        """
    @typing.overload
    def calculate(self, measurement: float, goal: float) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        """
    @typing.overload
    def calculate(self, measurement: float, goal: float, constraints: wpimath._controls._controls.trajectory.TrapezoidProfile.Constraints) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        :param constraints: Velocity and acceleration constraints for goal.
        """
    def disableContinuousInput(self) -> None:
        """
        Disables continuous input.
        """
    def enableContinuousInput(self, minimumInput: float, maximumInput: float) -> None:
        """
        Enables continuous input.
        
        Rather then using the max and min input range as constraints, it considers
        them to be the same point and automatically calculates the shortest route
        to the setpoint.
        
        :param minimumInput: The minimum value expected from the input.
        :param maximumInput: The maximum value expected from the input.
        """
    def getAccumulatedError(self) -> float:
        """
        Gets the accumulated error used in the integral calculation of this
        controller.
        
        :returns: The accumulated error of this controller.
        """
    def getConstraints(self) -> wpimath._controls._controls.trajectory.TrapezoidProfile.Constraints:
        """
        Get the velocity and acceleration constraints for this controller.
        
        :returns: Velocity and acceleration constraints.
        """
    def getD(self) -> float:
        """
        Gets the differential coefficient.
        
        :returns: differential coefficient
        """
    def getGoal(self) -> wpimath._controls._controls.trajectory.TrapezoidProfile.State:
        """
        Gets the goal for the ProfiledPIDController.
        """
    def getI(self) -> float:
        """
        Gets the integral coefficient.
        
        :returns: integral coefficient
        """
    def getIZone(self) -> float:
        """
        Get the IZone range.
        
        :returns: Maximum magnitude of error to allow integral control.
        """
    def getP(self) -> float:
        """
        Gets the proportional coefficient.
        
        :returns: proportional coefficient
        """
    def getPeriod(self) -> wpimath.units.seconds:
        """
        Gets the period of this controller.
        
        :returns: The period of the controller.
        """
    def getPositionError(self) -> float:
        """
        Returns the difference between the setpoint and the measurement.
        
        :returns: The error.
        """
    def getPositionTolerance(self) -> float:
        """
        Gets the position tolerance of this controller.
        
        :returns: The position tolerance of the controller.
        """
    def getSetpoint(self) -> wpimath._controls._controls.trajectory.TrapezoidProfile.State:
        """
        Returns the current setpoint of the ProfiledPIDController.
        
        :returns: The current setpoint.
        """
    def getVelocityError(self) -> wpimath.units.units_per_second:
        """
        Returns the change in error per second.
        """
    def getVelocityTolerance(self) -> float:
        """
        Gets the velocity tolerance of this controller.
        
        :returns: The velocity tolerance of the controller.
        """
    def initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    @typing.overload
    def reset(self, measurement: wpimath._controls._controls.trajectory.TrapezoidProfile.State) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measurement: The current measured State of the system.
        """
    @typing.overload
    def reset(self, measuredPosition: float, measuredVelocity: wpimath.units.units_per_second) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measuredPosition: The current measured position of the system.
        :param measuredVelocity: The current measured velocity of the system.
        """
    @typing.overload
    def reset(self, measuredPosition: float) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measuredPosition: The current measured position of the system. The
                                 velocity is assumed to be zero.
        """
    def setConstraints(self, constraints: wpimath._controls._controls.trajectory.TrapezoidProfile.Constraints) -> None:
        """
        Set velocity and acceleration constraints for goal.
        
        :param constraints: Velocity and acceleration constraints for goal.
        """
    def setD(self, Kd: typing.SupportsFloat) -> None:
        """
        Sets the differential coefficient of the PID controller gain.
        
        :param Kd: The differential coefficient. Must be >= 0.
        """
    @typing.overload
    def setGoal(self, goal: wpimath._controls._controls.trajectory.TrapezoidProfile.State) -> None:
        """
        Sets the goal for the ProfiledPIDController.
        
        :param goal: The desired unprofiled setpoint.
        """
    @typing.overload
    def setGoal(self, goal: float) -> None:
        """
        Sets the goal for the ProfiledPIDController.
        
        :param goal: The desired unprofiled setpoint.
        """
    def setI(self, Ki: typing.SupportsFloat) -> None:
        """
        Sets the integral coefficient of the PID controller gain.
        
        :param Ki: The integral coefficient. Must be >= 0.
        """
    def setIZone(self, iZone: typing.SupportsFloat) -> None:
        """
        Sets the IZone range. When the absolute value of the position error is
        greater than IZone, the total accumulated error will reset to zero,
        disabling integral gain until the absolute value of the position error is
        less than IZone. This is used to prevent integral windup. Must be
        non-negative. Passing a value of zero will effectively disable integral
        gain. Passing a value of infinity disables IZone functionality.
        
        :param iZone: Maximum magnitude of error to allow integral control. Must be
                      >= 0.
        """
    def setIntegratorRange(self, minimumIntegral: typing.SupportsFloat, maximumIntegral: typing.SupportsFloat) -> None:
        """
        Sets the minimum and maximum contributions of the integral term.
        
        The internal integrator is clamped so that the integral term's contribution
        to the output stays between minimumIntegral and maximumIntegral. This
        prevents integral windup.
        
        :param minimumIntegral: The minimum contribution of the integral term.
        :param maximumIntegral: The maximum contribution of the integral term.
        """
    def setP(self, Kp: typing.SupportsFloat) -> None:
        """
        Sets the proportional coefficient of the PID controller gain.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        """
    def setPID(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat) -> None:
        """
        Sets the PID Controller gain parameters.
        
        Sets the proportional, integral, and differential coefficients.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        :param Ki: The integral coefficient. Must be >= 0.
        :param Kd: The differential coefficient. Must be >= 0.
        """
    def setTolerance(self, positionTolerance: float, velocityTolerance: wpimath.units.units_per_second = ...) -> None:
        """
        Sets the error which is considered tolerable for use with
        AtSetpoint().
        
        :param positionTolerance: Position error which is tolerable.
        :param velocityTolerance: Velocity error which is tolerable.
        """
class ProfiledPIDControllerRadians(wpiutil._wpiutil.Sendable):
    """
    Implements a PID control loop whose setpoint is constrained by a trapezoid
    profile.
    """
    def __init__(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat, constraints: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.Constraints, period: wpimath.units.seconds = 0.02) -> None:
        """
        Allocates a ProfiledPIDController with the given constants for Kp, Ki, and
        Kd. Users should call reset() when they first start running the controller
        to avoid unwanted behavior.
        
        :param Kp:          The proportional coefficient. Must be >= 0.
        :param Ki:          The integral coefficient. Must be >= 0.
        :param Kd:          The derivative coefficient. Must be >= 0.
        :param constraints: Velocity and acceleration constraints for goal.
        :param period:      The period between controller updates in seconds. The
                            default is 20 milliseconds. Must be positive.
        """
    def atGoal(self) -> bool:
        """
        Returns true if the error is within the tolerance of the error.
        
        This will return false until at least one input value has been computed.
        """
    def atSetpoint(self) -> bool:
        """
        Returns true if the error is within the tolerance of the error.
        
        Currently this just reports on target as the actual value passes through
        the setpoint. Ideally it should be based on being within the tolerance for
        some period of time.
        
        This will return false until at least one input value has been computed.
        """
    @typing.overload
    def calculate(self, measurement: wpimath.units.radians) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        """
    @typing.overload
    def calculate(self, measurement: wpimath.units.radians, goal: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.State) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        """
    @typing.overload
    def calculate(self, measurement: wpimath.units.radians, goal: wpimath.units.radians) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        """
    @typing.overload
    def calculate(self, measurement: wpimath.units.radians, goal: wpimath.units.radians, constraints: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.Constraints) -> float:
        """
        Returns the next output of the PID controller.
        
        :param measurement: The current measurement of the process variable.
        :param goal:        The new goal of the controller.
        :param constraints: Velocity and acceleration constraints for goal.
        """
    def disableContinuousInput(self) -> None:
        """
        Disables continuous input.
        """
    def enableContinuousInput(self, minimumInput: wpimath.units.radians, maximumInput: wpimath.units.radians) -> None:
        """
        Enables continuous input.
        
        Rather then using the max and min input range as constraints, it considers
        them to be the same point and automatically calculates the shortest route
        to the setpoint.
        
        :param minimumInput: The minimum value expected from the input.
        :param maximumInput: The maximum value expected from the input.
        """
    def getAccumulatedError(self) -> float:
        """
        Gets the accumulated error used in the integral calculation of this
        controller.
        
        :returns: The accumulated error of this controller.
        """
    def getConstraints(self) -> wpimath._controls._controls.trajectory.TrapezoidProfileRadians.Constraints:
        """
        Get the velocity and acceleration constraints for this controller.
        
        :returns: Velocity and acceleration constraints.
        """
    def getD(self) -> float:
        """
        Gets the differential coefficient.
        
        :returns: differential coefficient
        """
    def getGoal(self) -> wpimath._controls._controls.trajectory.TrapezoidProfileRadians.State:
        """
        Gets the goal for the ProfiledPIDController.
        """
    def getI(self) -> float:
        """
        Gets the integral coefficient.
        
        :returns: integral coefficient
        """
    def getIZone(self) -> float:
        """
        Get the IZone range.
        
        :returns: Maximum magnitude of error to allow integral control.
        """
    def getP(self) -> float:
        """
        Gets the proportional coefficient.
        
        :returns: proportional coefficient
        """
    def getPeriod(self) -> wpimath.units.seconds:
        """
        Gets the period of this controller.
        
        :returns: The period of the controller.
        """
    def getPositionError(self) -> wpimath.units.radians:
        """
        Returns the difference between the setpoint and the measurement.
        
        :returns: The error.
        """
    def getPositionTolerance(self) -> float:
        """
        Gets the position tolerance of this controller.
        
        :returns: The position tolerance of the controller.
        """
    def getSetpoint(self) -> wpimath._controls._controls.trajectory.TrapezoidProfileRadians.State:
        """
        Returns the current setpoint of the ProfiledPIDController.
        
        :returns: The current setpoint.
        """
    def getVelocityError(self) -> wpimath.units.radians_per_second:
        """
        Returns the change in error per second.
        """
    def getVelocityTolerance(self) -> float:
        """
        Gets the velocity tolerance of this controller.
        
        :returns: The velocity tolerance of the controller.
        """
    def initSendable(self, builder: wpiutil._wpiutil.SendableBuilder) -> None:
        ...
    @typing.overload
    def reset(self, measurement: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.State) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measurement: The current measured State of the system.
        """
    @typing.overload
    def reset(self, measuredPosition: wpimath.units.radians, measuredVelocity: wpimath.units.radians_per_second) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measuredPosition: The current measured position of the system.
        :param measuredVelocity: The current measured velocity of the system.
        """
    @typing.overload
    def reset(self, measuredPosition: wpimath.units.radians) -> None:
        """
        Reset the previous error and the integral term.
        
        :param measuredPosition: The current measured position of the system. The
                                 velocity is assumed to be zero.
        """
    def setConstraints(self, constraints: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.Constraints) -> None:
        """
        Set velocity and acceleration constraints for goal.
        
        :param constraints: Velocity and acceleration constraints for goal.
        """
    def setD(self, Kd: typing.SupportsFloat) -> None:
        """
        Sets the differential coefficient of the PID controller gain.
        
        :param Kd: The differential coefficient. Must be >= 0.
        """
    @typing.overload
    def setGoal(self, goal: wpimath._controls._controls.trajectory.TrapezoidProfileRadians.State) -> None:
        """
        Sets the goal for the ProfiledPIDController.
        
        :param goal: The desired unprofiled setpoint.
        """
    @typing.overload
    def setGoal(self, goal: wpimath.units.radians) -> None:
        """
        Sets the goal for the ProfiledPIDController.
        
        :param goal: The desired unprofiled setpoint.
        """
    def setI(self, Ki: typing.SupportsFloat) -> None:
        """
        Sets the integral coefficient of the PID controller gain.
        
        :param Ki: The integral coefficient. Must be >= 0.
        """
    def setIZone(self, iZone: typing.SupportsFloat) -> None:
        """
        Sets the IZone range. When the absolute value of the position error is
        greater than IZone, the total accumulated error will reset to zero,
        disabling integral gain until the absolute value of the position error is
        less than IZone. This is used to prevent integral windup. Must be
        non-negative. Passing a value of zero will effectively disable integral
        gain. Passing a value of infinity disables IZone functionality.
        
        :param iZone: Maximum magnitude of error to allow integral control. Must be
                      >= 0.
        """
    def setIntegratorRange(self, minimumIntegral: typing.SupportsFloat, maximumIntegral: typing.SupportsFloat) -> None:
        """
        Sets the minimum and maximum contributions of the integral term.
        
        The internal integrator is clamped so that the integral term's contribution
        to the output stays between minimumIntegral and maximumIntegral. This
        prevents integral windup.
        
        :param minimumIntegral: The minimum contribution of the integral term.
        :param maximumIntegral: The maximum contribution of the integral term.
        """
    def setP(self, Kp: typing.SupportsFloat) -> None:
        """
        Sets the proportional coefficient of the PID controller gain.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        """
    def setPID(self, Kp: typing.SupportsFloat, Ki: typing.SupportsFloat, Kd: typing.SupportsFloat) -> None:
        """
        Sets the PID Controller gain parameters.
        
        Sets the proportional, integral, and differential coefficients.
        
        :param Kp: The proportional coefficient. Must be >= 0.
        :param Ki: The integral coefficient. Must be >= 0.
        :param Kd: The differential coefficient. Must be >= 0.
        """
    def setTolerance(self, positionTolerance: wpimath.units.radians, velocityTolerance: wpimath.units.radians_per_second = ...) -> None:
        """
        Sets the error which is considered tolerable for use with
        AtSetpoint().
        
        :param positionTolerance: Position error which is tolerable.
        :param velocityTolerance: Velocity error which is tolerable.
        """
class SimpleMotorFeedforwardMeters:
    """
    A helper class that computes feedforward voltages for a simple
    permanent-magnet DC motor.
    """
    def __init__(self, kS: wpimath.units.volts, kV: wpimath.units.volt_seconds_per_meter, kA: wpimath.units.volt_seconds_squared_per_meter = 0.0, dt: wpimath.units.seconds = 0.02) -> None:
        """
        Creates a new SimpleMotorFeedforward with the specified gains.
        
        :param kS: The static gain, in volts.
        :param kV: The velocity gain, in volt seconds per distance.
        :param kA: The acceleration gain, in volt seconds² per distance.
        :param dt: The period in seconds.
                   @throws IllegalArgumentException for kv &lt; zero.
                   @throws IllegalArgumentException for ka &lt; zero.
                   @throws IllegalArgumentException for period &le; zero.
        """
    @typing.overload
    def calculate(self, velocity: wpimath.units.meters_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and velocity setpoint assuming
        discrete control. Use this method when the velocity setpoint does not
        change.
        
        :param velocity: The velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    @typing.overload
    def calculate(self, currentVelocity: wpimath.units.meters_per_second, nextVelocity: wpimath.units.meters_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoints assuming discrete
        control.
        
        Note this method is inaccurate when the velocity crosses 0.
        
        :param currentVelocity: The current velocity setpoint.
        :param nextVelocity:    The next velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    def getDt(self) -> wpimath.units.seconds:
        """
        Returns the period.
        
        :returns: The period.
        """
    def getKa(self) -> wpimath.units.volt_seconds_squared_per_meter:
        """
        Returns the acceleration gain.
        
        :returns: The acceleration gain.
        """
    def getKs(self) -> wpimath.units.volts:
        """
        Returns the static gain.
        
        :returns: The static gain.
        """
    def getKv(self) -> wpimath.units.volt_seconds_per_meter:
        """
        Returns the velocity gain.
        
        :returns: The velocity gain.
        """
    def maxAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.meters_per_second) -> wpimath.units.meters_per_second_squared:
        """
        Calculates the maximum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the motor.
        :param velocity:   The velocity of the motor.
        
        :returns: The maximum possible acceleration at the given velocity.
        """
    def maxAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.meters_per_second_squared) -> wpimath.units.meters_per_second:
        """
        Calculates the maximum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the motor.
        :param acceleration: The acceleration of the motor.
        
        :returns: The maximum possible velocity at the given acceleration.
        """
    def minAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.meters_per_second) -> wpimath.units.meters_per_second_squared:
        """
        Calculates the minimum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the motor.
        :param velocity:   The velocity of the motor.
        
        :returns: The minimum possible acceleration at the given velocity.
        """
    def minAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.meters_per_second_squared) -> wpimath.units.meters_per_second:
        """
        Calculates the minimum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the motor.
        :param acceleration: The acceleration of the motor.
        
        :returns: The minimum possible velocity at the given acceleration.
        """
    def setKa(self, kA: wpimath.units.volt_seconds_squared_per_meter) -> None:
        """
        Sets the acceleration gain.
        
        :param kA: The acceleration gain.
        """
    def setKs(self, kS: wpimath.units.volts) -> None:
        """
        Sets the static gain.
        
        :param kS: The static gain.
        """
    def setKv(self, kV: wpimath.units.volt_seconds_per_meter) -> None:
        """
        Sets the velocity gain.
        
        :param kV: The velocity gain.
        """
class SimpleMotorFeedforwardRadians:
    """
    A helper class that computes feedforward voltages for a simple
    permanent-magnet DC motor.
    """
    def __init__(self, kS: wpimath.units.volts, kV: wpimath.units.volt_seconds_per_radian, kA: wpimath.units.volt_seconds_squared_per_radian = 0.0, dt: wpimath.units.seconds = 0.02) -> None:
        """
        Creates a new SimpleMotorFeedforward with the specified gains.
        
        :param kS: The static gain, in volts.
        :param kV: The velocity gain, in volt seconds per distance.
        :param kA: The acceleration gain, in volt seconds² per distance.
        :param dt: The period in seconds.
                   @throws IllegalArgumentException for kv &lt; zero.
                   @throws IllegalArgumentException for ka &lt; zero.
                   @throws IllegalArgumentException for period &le; zero.
        """
    @typing.overload
    def calculate(self, velocity: wpimath.units.radians_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and velocity setpoint assuming
        discrete control. Use this method when the velocity setpoint does not
        change.
        
        :param velocity: The velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    @typing.overload
    def calculate(self, currentVelocity: wpimath.units.radians_per_second, nextVelocity: wpimath.units.radians_per_second) -> wpimath.units.volts:
        """
        Calculates the feedforward from the gains and setpoints assuming discrete
        control.
        
        Note this method is inaccurate when the velocity crosses 0.
        
        :param currentVelocity: The current velocity setpoint.
        :param nextVelocity:    The next velocity setpoint.
        
        :returns: The computed feedforward, in volts.
        """
    def getDt(self) -> wpimath.units.seconds:
        """
        Returns the period.
        
        :returns: The period.
        """
    def getKa(self) -> wpimath.units.volt_seconds_squared_per_radian:
        """
        Returns the acceleration gain.
        
        :returns: The acceleration gain.
        """
    def getKs(self) -> wpimath.units.volts:
        """
        Returns the static gain.
        
        :returns: The static gain.
        """
    def getKv(self) -> wpimath.units.volt_seconds_per_radian:
        """
        Returns the velocity gain.
        
        :returns: The velocity gain.
        """
    def maxAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.radians_per_second) -> wpimath.units.radians_per_second_squared:
        """
        Calculates the maximum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the motor.
        :param velocity:   The velocity of the motor.
        
        :returns: The maximum possible acceleration at the given velocity.
        """
    def maxAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.radians_per_second_squared) -> wpimath.units.radians_per_second:
        """
        Calculates the maximum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the motor.
        :param acceleration: The acceleration of the motor.
        
        :returns: The maximum possible velocity at the given acceleration.
        """
    def minAchievableAcceleration(self, maxVoltage: wpimath.units.volts, velocity: wpimath.units.radians_per_second) -> wpimath.units.radians_per_second_squared:
        """
        Calculates the minimum achievable acceleration given a maximum voltage
        supply and a velocity. Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the velocity constraint, and this will give you
        a simultaneously-achievable acceleration constraint.
        
        :param maxVoltage: The maximum voltage that can be supplied to the motor.
        :param velocity:   The velocity of the motor.
        
        :returns: The minimum possible acceleration at the given velocity.
        """
    def minAchievableVelocity(self, maxVoltage: wpimath.units.volts, acceleration: wpimath.units.radians_per_second_squared) -> wpimath.units.radians_per_second:
        """
        Calculates the minimum achievable velocity given a maximum voltage supply
        and an acceleration.  Useful for ensuring that velocity and
        acceleration constraints for a trapezoidal profile are simultaneously
        achievable - enter the acceleration constraint, and this will give you
        a simultaneously-achievable velocity constraint.
        
        :param maxVoltage:   The maximum voltage that can be supplied to the motor.
        :param acceleration: The acceleration of the motor.
        
        :returns: The minimum possible velocity at the given acceleration.
        """
    def setKa(self, kA: wpimath.units.volt_seconds_squared_per_radian) -> None:
        """
        Sets the acceleration gain.
        
        :param kA: The acceleration gain.
        """
    def setKs(self, kS: wpimath.units.volts) -> None:
        """
        Sets the static gain.
        
        :param kS: The static gain.
        """
    def setKv(self, kV: wpimath.units.volt_seconds_per_radian) -> None:
        """
        Sets the velocity gain.
        
        :param kV: The velocity gain.
        """
