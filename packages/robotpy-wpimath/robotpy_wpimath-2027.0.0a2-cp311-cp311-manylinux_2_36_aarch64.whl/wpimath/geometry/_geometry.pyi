from __future__ import annotations
import numpy
import numpy.typing
import typing
import wpimath.units
__all__ = ['CoordinateAxis', 'CoordinateSystem', 'Ellipse2d', 'Pose2d', 'Pose3d', 'Quaternion', 'Rectangle2d', 'Rotation2d', 'Rotation3d', 'Transform2d', 'Transform3d', 'Translation2d', 'Translation3d', 'Twist2d', 'Twist3d', 'rotationVectorToMatrix']
class CoordinateAxis:
    """
    A class representing a coordinate system axis within the NWU coordinate
    system.
    """
    @staticmethod
    def D() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to -Z in the NWU coordinate system.
        """
    @staticmethod
    def E() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to -Y in the NWU coordinate system.
        """
    @staticmethod
    def N() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to +X in the NWU coordinate system.
        """
    @staticmethod
    def S() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to -X in the NWU coordinate system.
        """
    @staticmethod
    def U() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to +Z in the NWU coordinate system.
        """
    @staticmethod
    def W() -> CoordinateAxis:
        """
        Returns a coordinate axis corresponding to +Y in the NWU coordinate system.
        """
    def __init__(self, x: typing.SupportsFloat, y: typing.SupportsFloat, z: typing.SupportsFloat) -> None:
        """
        Constructs a coordinate system axis within the NWU coordinate system and
        normalizes it.
        
        :param x: The x component.
        :param y: The y component.
        :param z: The z component.
        """
class CoordinateSystem:
    """
    A helper class that converts Pose3d objects between different standard
    coordinate frames.
    """
    @staticmethod
    def EDN() -> CoordinateSystem:
        """
        Returns an instance of the East-Down-North (EDN) coordinate system.
        
        The +X axis is east, the +Y axis is down, and the +Z axis is north.
        """
    @staticmethod
    def NED() -> CoordinateSystem:
        """
        Returns an instance of the NED coordinate system.
        
        The +X axis is north, the +Y axis is east, and the +Z axis is down.
        """
    @staticmethod
    def NWU() -> CoordinateSystem:
        """
        Returns an instance of the North-West-Up (NWU) coordinate system.
        
        The +X axis is north, the +Y axis is west, and the +Z axis is up.
        """
    @staticmethod
    @typing.overload
    def convert(translation: Translation3d, from_: CoordinateSystem, to: CoordinateSystem) -> Translation3d:
        """
        Converts the given translation from one coordinate system to another.
        
        :param translation: The translation to convert.
        :param from_:       The coordinate system the translation starts in.
        :param to:          The coordinate system to which to convert.
        
        :returns: The given translation in the desired coordinate system.
        """
    @staticmethod
    @typing.overload
    def convert(rotation: Rotation3d, from_: CoordinateSystem, to: CoordinateSystem) -> Rotation3d:
        """
        Converts the given rotation from one coordinate system to another.
        
        :param rotation: The rotation to convert.
        :param from_:    The coordinate system the rotation starts in.
        :param to:       The coordinate system to which to convert.
        
        :returns: The given rotation in the desired coordinate system.
        """
    @staticmethod
    @typing.overload
    def convert(pose: Pose3d, from_: CoordinateSystem, to: CoordinateSystem) -> Pose3d:
        """
        Converts the given pose from one coordinate system to another.
        
        :param pose:  The pose to convert.
        :param from_: The coordinate system the pose starts in.
        :param to:    The coordinate system to which to convert.
        
        :returns: The given pose in the desired coordinate system.
        """
    @staticmethod
    @typing.overload
    def convert(transform: Transform3d, from_: CoordinateSystem, to: CoordinateSystem) -> Transform3d:
        """
        Converts the given transform from one coordinate system to another.
        
        :param transform: The transform to convert.
        :param from_:     The coordinate system the transform starts in.
        :param to:        The coordinate system to which to convert.
        
        :returns: The given transform in the desired coordinate system.
        """
    def __init__(self, positiveX: CoordinateAxis, positiveY: CoordinateAxis, positiveZ: CoordinateAxis) -> None:
        """
        Constructs a coordinate system with the given cardinal directions for each
        axis.
        
        :param positiveX: The cardinal direction of the positive x-axis.
        :param positiveY: The cardinal direction of the positive y-axis.
        :param positiveZ: The cardinal direction of the positive z-axis.
                          @throws std::domain_error if the coordinate system isn't special orthogonal
        """
class Ellipse2d:
    """
    Represents a 2d ellipse space containing translational, rotational, and
    scaling components.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9a8720>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromFeet(center: Pose2d, xSemiAxis: wpimath.units.feet, ySemiAxis: wpimath.units.feet) -> Ellipse2d:
        ...
    def __eq__(self, arg0: Ellipse2d) -> bool:
        """
        Checks equality between this Ellipse2d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    @typing.overload
    def __init__(self, center: Pose2d, xSemiAxis: wpimath.units.meters, ySemiAxis: wpimath.units.meters) -> None:
        """
        Constructs an ellipse around a center point and two semi-axes, a horizontal
        and vertical one.
        
        :param center:    The center of the ellipse.
        :param xSemiAxis: The x semi-axis.
        :param ySemiAxis: The y semi-axis.
        """
    @typing.overload
    def __init__(self, center: Translation2d, radius: typing.SupportsFloat) -> None:
        """
        Constructs a perfectly circular ellipse with the specified radius.
        
        :param center: The center of the circle.
        :param radius: The radius of the circle.
        """
    def __repr__(self) -> str:
        ...
    def center(self) -> Pose2d:
        """
        Returns the center of the ellipse.
        
        :returns: The center of the ellipse.
        """
    def contains(self, point: Translation2d) -> bool:
        """
        Checks if a point is contained within this ellipse. This is inclusive, if
        the point lies on the circumference this will return ``true``.
        
        :param point: The point to check.
        
        :returns: True, if the point is within or on the ellipse.
        """
    def distance(self, point: Translation2d) -> wpimath.units.meters:
        """
        Returns the distance between the perimeter of the ellipse and the point.
        
        :param point: The point to check.
        
        :returns: The distance (0, if the point is contained by the ellipse)
        """
    def focalPoints(self) -> tuple[Translation2d, Translation2d]:
        """
        Returns the focal points of the ellipse. In a perfect circle, this will
        always return the center.
        
        :returns: The focal points.
        """
    def intersects(self, point: Translation2d) -> bool:
        """
        Checks if a point is intersected by this ellipse's circumference.
        
        :param point: The point to check.
        
        :returns: True, if this ellipse's circumference intersects the point.
        """
    def nearest(self, point: Translation2d) -> Translation2d:
        """
        Returns the nearest point that is contained within the ellipse.
        
        :param point: The point that this will find the nearest point to.
        
        :returns: A new point that is nearest to ``point`` and contained in the
                  ellipse.
        """
    def rotateBy(self, other: Rotation2d) -> Ellipse2d:
        """
        Rotates the center of the ellipse and returns the new ellipse.
        
        :param other: The rotation to transform by.
        
        :returns: The rotated ellipse.
        """
    def rotation(self) -> Rotation2d:
        """
        Returns the rotational component of the ellipse.
        
        :returns: The rotational component of the ellipse.
        """
    def transformBy(self, other: Transform2d) -> Ellipse2d:
        """
        Transforms the center of the ellipse and returns the new ellipse.
        
        :param other: The transform to transform by.
        
        :returns: The transformed ellipse.
        """
    @property
    def xsemiaxis(self) -> wpimath.units.meters:
        ...
    @property
    def xsemiaxis_feet(self) -> wpimath.units.feet:
        ...
    @property
    def ysemiaxis(self) -> wpimath.units.meters:
        ...
    @property
    def ysemiaxis_feet(self) -> wpimath.units.feet:
        ...
class Pose2d:
    """
    Represents a 2D pose containing translational and rotational elements.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9a9020>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    @typing.overload
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet, r: Rotation2d) -> Pose2d:
        ...
    @staticmethod
    @typing.overload
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet, angle: wpimath.units.radians) -> Pose2d:
        ...
    @staticmethod
    def fromMatrix(matrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]) -> Pose2d:
        """
        Constructs a pose with the specified affine transformation matrix.
        
        :param matrix: The affine transformation matrix.
                       @throws std::domain_error if the affine transformation matrix is invalid.
        """
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the pose's translation.
        
        :returns: The x component of the pose's translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the pose's translation.
        
        :returns: The y component of the pose's translation.
        """
    def __add__(self, arg0: Transform2d) -> Pose2d:
        """
        Transforms the pose by the given transformation and returns the new
        transformed pose.
        
        ::
        
          [x_new]    [cos, -sin, 0][transform.x]
          [y_new] += [sin,  cos, 0][transform.y]
          [t_new]    [  0,    0, 1][transform.t]
        
        :param other: The transform to transform the pose by.
        
        :returns: The transformed pose.
        """
    def __eq__(self, arg0: Pose2d) -> bool:
        """
        Checks equality between this Pose2d and another object.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a pose at the origin facing toward the positive X axis.
        """
    @typing.overload
    def __init__(self, translation: Translation2d, rotation: Rotation2d) -> None:
        """
        Constructs a pose with the specified translation and rotation.
        
        :param translation: The translational component of the pose.
        :param rotation:    The rotational component of the pose.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, rotation: Rotation2d) -> None:
        """
        Constructs a pose with x and y translations instead of a separate
        Translation2d.
        
        :param x:        The x component of the translational component of the pose.
        :param y:        The y component of the translational component of the pose.
        :param rotation: The rotational component of the pose.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, angle: wpimath.units.radians) -> None:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Pose2d:
        """
        Multiplies the current pose by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Pose2d.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Pose2d) -> Transform2d:
        """
        Returns the Transform2d that maps the one pose to another.
        
        :param other: The initial pose of the transformation.
        
        :returns: The transform that maps the other pose to the current pose.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Pose2d:
        """
        Divides the current pose by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Pose2d.
        """
    def exp(self, twist: Twist2d) -> Pose2d:
        """
        Obtain a new Pose2d from a (constant curvature) velocity.
        
        See https://file.tavsys.net/control/controls-engineering-in-frc.pdf section
        10.2 "Pose exponential" for a derivation.
        
        The twist is a change in pose in the robot's coordinate frame since the
        previous pose update. When the user runs exp() on the previous known
        field-relative pose with the argument being the twist, the user will
        receive the new field-relative pose.
        
        "Exp" represents the pose exponential, which is solving a differential
        equation moving the pose forward in time.
        
        :param twist: The change in pose in the robot's coordinate frame since the
                      previous pose update. For example, if a non-holonomic robot moves forward
                      0.01 meters and changes angle by 0.5 degrees since the previous pose
                      update, the twist would be Twist2d{0.01_m, 0_m, 0.5_deg}.
        
        :returns: The new pose of the robot.
        """
    def log(self, end: Pose2d) -> Twist2d:
        """
        Returns a Twist2d that maps this pose to the end pose. If c is the output
        of a.Log(b), then a.Exp(c) would yield b.
        
        :param end: The end pose for the transformation.
        
        :returns: The twist that maps this to end.
        """
    def nearest(self, poses: list[Pose2d]) -> Pose2d:
        """
        Returns the nearest Pose2d from a collection of poses.
        
        If two or more poses in the collection have the same distance from this
        pose, return the one with the closest rotation component.
        
        :param poses: The collection of poses.
        
        :returns: The nearest Pose2d from the collection.
        """
    def relativeTo(self, other: Pose2d) -> Pose2d:
        """
        Returns the current pose relative to the given pose.
        
        This function can often be used for trajectory tracking or pose
        stabilization algorithms to get the error between the reference and the
        current pose.
        
        :param other: The pose that is the origin of the new coordinate frame that
                      the current pose will be converted into.
        
        :returns: The current pose relative to the new origin pose.
        """
    def rotateAround(self, point: Translation2d, rot: Rotation2d) -> Pose2d:
        """
        Rotates the current pose around a point in 2D space.
        
        :param point: The point in 2D space to rotate around.
        :param rot:   The rotation to rotate the pose by.
        
        :returns: The new rotated pose.
        """
    def rotateBy(self, other: Rotation2d) -> Pose2d:
        """
        Rotates the pose around the origin and returns the new pose.
        
        :param other: The rotation to transform the pose by.
        
        :returns: The rotated pose.
        """
    def rotation(self) -> Rotation2d:
        """
        Returns the underlying rotation.
        
        :returns: Reference to the rotational component of the pose.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]:
        """
        Returns an affine transformation matrix representation of this pose.
        """
    def transformBy(self, other: Transform2d) -> Pose2d:
        """
        Transforms the pose by the given transformation and returns the new pose.
        See + operator for the matrix multiplication performed.
        
        :param other: The transform to transform the pose by.
        
        :returns: The transformed pose.
        """
    def translation(self) -> Translation2d:
        """
        Returns the underlying translation.
        
        :returns: Reference to the translational component of the pose.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
class Pose3d:
    """
    Represents a 3D pose containing translational and rotational elements.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9a9a70>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet, z: wpimath.units.feet, r: Rotation3d) -> Pose3d:
        ...
    @staticmethod
    def fromMatrix(matrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[4, 4]"]) -> Pose3d:
        """
        Constructs a pose with the specified affine transformation matrix.
        
        :param matrix: The affine transformation matrix.
                       @throws std::domain_error if the affine transformation matrix is invalid.
        """
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the pose's translation.
        
        :returns: The x component of the pose's translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the pose's translation.
        
        :returns: The y component of the pose's translation.
        """
    def Z(self) -> wpimath.units.meters:
        """
        Returns the Z component of the pose's translation.
        
        :returns: The z component of the pose's translation.
        """
    def __add__(self, arg0: Transform3d) -> Pose3d:
        """
        Transforms the pose by the given transformation and returns the new
        transformed pose. The transform is applied relative to the pose's frame.
        Note that this differs from Pose3d::RotateBy(const Rotation3d&), which is
        applied relative to the global frame and around the origin.
        
        :param other: The transform to transform the pose by.
        
        :returns: The transformed pose.
        """
    def __eq__(self, arg0: Pose3d) -> bool:
        """
        Checks equality between this Pose3d and another object.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a pose at the origin facing toward the positive X axis.
        """
    @typing.overload
    def __init__(self, translation: Translation3d, rotation: Rotation3d) -> None:
        """
        Constructs a pose with the specified translation and rotation.
        
        :param translation: The translational component of the pose.
        :param rotation:    The rotational component of the pose.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, z: wpimath.units.meters, rotation: Rotation3d) -> None:
        """
        Constructs a pose with x, y, and z translations instead of a separate
        Translation3d.
        
        :param x:        The x component of the translational component of the pose.
        :param y:        The y component of the translational component of the pose.
        :param z:        The z component of the translational component of the pose.
        :param rotation: The rotational component of the pose.
        """
    @typing.overload
    def __init__(self, pose: Pose2d) -> None:
        """
        Constructs a 3D pose from a 2D pose in the X-Y plane.
        
        :param pose: The 2D pose.
                     @see Rotation3d(Rotation2d)
                     @see Translation3d(Translation2d)
        """
    def __mul__(self, arg0: typing.SupportsFloat) -> Pose3d:
        """
        Multiplies the current pose by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Pose2d.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Pose3d) -> Transform3d:
        """
        Returns the Transform3d that maps the one pose to another.
        
        :param other: The initial pose of the transformation.
        
        :returns: The transform that maps the other pose to the current pose.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Pose3d:
        """
        Divides the current pose by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Pose2d.
        """
    def exp(self, twist: Twist3d) -> Pose3d:
        """
        Obtain a new Pose3d from a (constant curvature) velocity.
        
        The twist is a change in pose in the robot's coordinate frame since the
        previous pose update. When the user runs exp() on the previous known
        field-relative pose with the argument being the twist, the user will
        receive the new field-relative pose.
        
        "Exp" represents the pose exponential, which is solving a differential
        equation moving the pose forward in time.
        
        :param twist: The change in pose in the robot's coordinate frame since the
                      previous pose update. For example, if a non-holonomic robot moves forward
                      0.01 meters and changes angle by 0.5 degrees since the previous pose
                      update, the twist would be Twist3d{0.01_m, 0_m, 0_m, Rotation3d{0.0, 0.0,
                      0.5_deg}}.
        
        :returns: The new pose of the robot.
        """
    def log(self, end: Pose3d) -> Twist3d:
        """
        Returns a Twist3d that maps this pose to the end pose. If c is the output
        of a.Log(b), then a.Exp(c) would yield b.
        
        :param end: The end pose for the transformation.
        
        :returns: The twist that maps this to end.
        """
    def nearest(self, poses: list[Pose3d]) -> Pose3d:
        """
        Returns the nearest Pose3d from a collection of poses.
        
        If two or more poses in the collection have the same distance from this
        pose, return the one with the closest rotation component.
        
        :param poses: The collection of poses.
        
        :returns: The nearest Pose3d from the collection.
        """
    def relativeTo(self, other: Pose3d) -> Pose3d:
        """
        Returns the current pose relative to the given pose.
        
        This function can often be used for trajectory tracking or pose
        stabilization algorithms to get the error between the reference and the
        current pose.
        
        :param other: The pose that is the origin of the new coordinate frame that
                      the current pose will be converted into.
        
        :returns: The current pose relative to the new origin pose.
        """
    def rotateAround(self, point: Translation3d, rot: Rotation3d) -> Pose3d:
        """
        Rotates the current pose around a point in 3D space.
        
        :param point: The point in 3D space to rotate around.
        :param rot:   The rotation to rotate the pose by.
        
        :returns: The new rotated pose.
        """
    def rotateBy(self, other: Rotation3d) -> Pose3d:
        """
        Rotates the pose around the origin and returns the new pose.
        
        :param other: The rotation to transform the pose by, which is applied
                      extrinsically (from the global frame).
        
        :returns: The rotated pose.
        """
    def rotation(self) -> Rotation3d:
        """
        Returns the underlying rotation.
        
        :returns: Reference to the rotational component of the pose.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[4, 4]"]:
        """
        Returns an affine transformation matrix representation of this pose.
        """
    def toPose2d(self) -> Pose2d:
        """
        Returns a Pose2d representing this Pose3d projected into the X-Y plane.
        """
    def transformBy(self, other: Transform3d) -> Pose3d:
        """
        Transforms the pose by the given transformation and returns the new
        transformed pose. The transform is applied relative to the pose's frame.
        Note that this differs from Pose3d::RotateBy(const Rotation3d&), which is
        applied relative to the global frame and around the origin.
        
        :param other: The transform to transform the pose by.
        
        :returns: The transformed pose.
        """
    def translation(self) -> Translation3d:
        """
        Returns the underlying translation.
        
        :returns: Reference to the translational component of the pose.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
    @property
    def z(self) -> wpimath.units.meters:
        ...
    @property
    def z_feet(self) -> wpimath.units.feet:
        ...
class Quaternion:
    """
    Represents a quaternion.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9aa2b0>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromRotationVector(rvec: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> Quaternion:
        """
        Returns the quaternion representation of this rotation vector.
        
        This is also the exp operator of 𝖘𝖔(3).
        
        source: wpimath/algorithms.md
        """
    def W(self) -> float:
        """
        Returns W component of the quaternion.
        """
    def X(self) -> float:
        """
        Returns X component of the quaternion.
        """
    def Y(self) -> float:
        """
        Returns Y component of the quaternion.
        """
    def Z(self) -> float:
        """
        Returns Z component of the quaternion.
        """
    def __add__(self, arg0: Quaternion) -> Quaternion:
        """
        Adds with another quaternion.
        
        :param other: the other quaternion
        """
    def __eq__(self, arg0: Quaternion) -> bool:
        """
        Checks equality between this Quaternion and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a quaternion with a default angle of 0 degrees.
        """
    @typing.overload
    def __init__(self, w: typing.SupportsFloat, x: typing.SupportsFloat, y: typing.SupportsFloat, z: typing.SupportsFloat) -> None:
        """
        Constructs a quaternion with the given components.
        
        :param w: W component of the quaternion.
        :param x: X component of the quaternion.
        :param y: Y component of the quaternion.
        :param z: Z component of the quaternion.
        """
    @typing.overload
    def __mul__(self, arg0: typing.SupportsFloat) -> Quaternion:
        """
        Multiples with a scalar value.
        
        :param other: the scalar value
        """
    @typing.overload
    def __mul__(self, arg0: Quaternion) -> Quaternion:
        """
        Multiply with another quaternion.
        
        :param other: The other quaternion.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Quaternion) -> Quaternion:
        """
        Subtracts another quaternion.
        
        :param other: the other quaternion
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Quaternion:
        """
        Divides by a scalar value.
        
        :param other: the scalar value
        """
    def conjugate(self) -> Quaternion:
        """
        Returns the conjugate of the quaternion.
        """
    def dot(self, other: Quaternion) -> float:
        """
        Returns the elementwise product of two quaternions.
        """
    @typing.overload
    def exp(self, other: Quaternion) -> Quaternion:
        """
        Matrix exponential of a quaternion.
        
        :param other: the "Twist" that will be applied to this quaternion.
        """
    @typing.overload
    def exp(self) -> Quaternion:
        """
        Matrix exponential of a quaternion.
        
        source: wpimath/algorithms.md
        
        If this quaternion is in 𝖘𝖔(3) and you are looking for an element of
        SO(3), use FromRotationVector
        """
    def inverse(self) -> Quaternion:
        """
        Returns the inverse of the quaternion.
        """
    @typing.overload
    def log(self, other: Quaternion) -> Quaternion:
        """
        Log operator of a quaternion.
        
        :param other: The quaternion to map this quaternion onto
        """
    @typing.overload
    def log(self) -> Quaternion:
        """
        Log operator of a quaternion.
        
        source:  wpimath/algorithms.md
        
        If this quaternion is in SO(3) and you are looking for an element of 𝖘𝖔(3),
        use ToRotationVector
        """
    def norm(self) -> float:
        """
        Calculates the L2 norm of the quaternion.
        """
    def normalize(self) -> Quaternion:
        """
        Normalizes the quaternion.
        """
    def pow(self, t: typing.SupportsFloat) -> Quaternion:
        """
        Calculates this quaternion raised to a power.
        
        :param t: the power to raise this quaternion to.
        """
    def toRotationVector(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns the rotation vector representation of this quaternion.
        
        This is also the log operator of SO(3).
        """
class Rectangle2d:
    """
    Represents a 2d rectangular space containing translational, rotational, and
    scaling components.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9aa850>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromFeet(center: Pose2d, xWidth: wpimath.units.feet, yWidth: wpimath.units.feet) -> Rectangle2d:
        ...
    def __eq__(self, arg0: Rectangle2d) -> bool:
        """
        Checks equality between this Rectangle2d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    @typing.overload
    def __init__(self, center: Pose2d, xWidth: wpimath.units.meters, yWidth: wpimath.units.meters) -> None:
        """
        Constructs a rectangle at the specified position with the specified width
        and height.
        
        :param center: The position (translation and rotation) of the rectangle.
        :param xWidth: The x size component of the rectangle, in unrotated
                       coordinate frame.
        :param yWidth: The y size component of the rectangle, in unrotated
                       coordinate frame.
        """
    @typing.overload
    def __init__(self, cornerA: Translation2d, cornerB: Translation2d) -> None:
        """
        Creates an unrotated rectangle from the given corners. The corners should
        be diagonally opposite of each other.
        
        :param cornerA: The first corner of the rectangle.
        :param cornerB: The second corner of the rectangle.
        """
    def __repr__(self) -> str:
        ...
    def center(self) -> Pose2d:
        """
        Returns the center of the rectangle.
        
        :returns: The center of the rectangle.
        """
    def contains(self, point: Translation2d) -> bool:
        """
        Checks if a point is contained within the rectangle. This is inclusive, if
        the point lies on the perimeter it will return true.
        
        :param point: The point to check.
        
        :returns: True, if the rectangle contains the point or the perimeter
                  intersects the point.
        """
    def distance(self, point: Translation2d) -> wpimath.units.meters:
        """
        Returns the distance between the perimeter of the rectangle and the point.
        
        :param point: The point to check.
        
        :returns: The distance (0, if the point is contained by the rectangle)
        """
    def intersects(self, point: Translation2d) -> bool:
        """
        Checks if a point is intersected by the rectangle's perimeter.
        
        :param point: The point to check.
        
        :returns: True, if the rectangle's perimeter intersects the point.
        """
    def nearest(self, point: Translation2d) -> Translation2d:
        """
        Returns the nearest point that is contained within the rectangle.
        
        :param point: The point that this will find the nearest point to.
        
        :returns: A new point that is nearest to ``point`` and contained in the
                  rectangle.
        """
    def rotateBy(self, other: Rotation2d) -> Rectangle2d:
        """
        Rotates the center of the rectangle and returns the new rectangle.
        
        :param other: The rotation to transform by.
        
        :returns: The rotated rectangle.
        """
    def rotation(self) -> Rotation2d:
        """
        Returns the rotational component of the rectangle.
        
        :returns: The rotational component of the rectangle.
        """
    def transformBy(self, other: Transform2d) -> Rectangle2d:
        """
        Transforms the center of the rectangle and returns the new rectangle.
        
        :param other: The transform to transform by.
        
        :returns: The transformed rectangle
        """
    @property
    def xwidth(self) -> wpimath.units.meters:
        ...
    @property
    def xwidth_feet(self) -> wpimath.units.feet:
        ...
    @property
    def ywidth(self) -> wpimath.units.meters:
        ...
    @property
    def ywidth_feet(self) -> wpimath.units.feet:
        ...
class Rotation2d:
    """
    A rotation in a 2D coordinate frame represented by a point on the unit circle
    (cosine and sine).
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9aaf70>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromDegrees(value: wpimath.units.degrees) -> Rotation2d:
        ...
    @staticmethod
    def fromMatrix(rotationMatrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 2]"]) -> Rotation2d:
        """
        Constructs a Rotation2d from a rotation matrix.
        
        :param rotationMatrix: The rotation matrix.
                               @throws std::domain_error if the rotation matrix isn't special orthogonal.
        """
    @staticmethod
    def fromRotations(arg0: wpimath.units.turns) -> Rotation2d:
        ...
    def __add__(self, arg0: Rotation2d) -> Rotation2d:
        """
        Adds two rotations together, with the result being bounded between -π and
        π.
        
        For example, <code>Rotation2d{30_deg} + Rotation2d{60_deg}</code> equals
        <code>Rotation2d{units::radian_t{std::numbers::pi/2.0}}</code>
        
        :param other: The rotation to add.
        
        :returns: The sum of the two rotations.
        """
    def __eq__(self, arg0: Rotation2d) -> bool:
        """
        Checks equality between this Rotation2d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a Rotation2d with a default angle of 0 degrees.
        """
    @typing.overload
    def __init__(self, value: wpimath.units.radians) -> None:
        """
        Constructs a Rotation2d with the given radian value.
        :param value: The value of the angle in radians.
        """
    @typing.overload
    def __init__(self, x: typing.SupportsFloat, y: typing.SupportsFloat) -> None:
        """
        Constructs a Rotation2d with the given x and y (cosine and sine)
        components. The x and y don't have to be normalized.
        
        :param x: The x component or cosine of the rotation.
        :param y: The y component or sine of the rotation.
        """
    def __mul__(self, arg0: typing.SupportsFloat) -> Rotation2d:
        """
        Multiplies the current rotation by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Rotation2d.
        """
    def __neg__(self) -> Rotation2d:
        """
        Takes the inverse of the current rotation. This is simply the negative of
        the current angular value.
        
        :returns: The inverse of the current rotation.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Rotation2d) -> Rotation2d:
        """
        Subtracts the new rotation from the current rotation and returns the new
        rotation.
        
        For example, <code>Rotation2d{10_deg} - Rotation2d{100_deg}</code> equals
        <code>Rotation2d{units::radian_t{-std::numbers::pi/2.0}}</code>
        
        :param other: The rotation to subtract.
        
        :returns: The difference between the two rotations.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Rotation2d:
        """
        Divides the current rotation by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Rotation2d.
        """
    def cos(self) -> float:
        """
        Returns the cosine of the rotation.
        
        :returns: The cosine of the rotation.
        """
    def degrees(self) -> wpimath.units.degrees:
        """
        Returns the degree value of the rotation constrained within [-180, 180].
        
        :returns: The degree value of the rotation constrained within [-180, 180].
        """
    def radians(self) -> wpimath.units.radians:
        """
        Returns the radian value of the rotation constrained within [-π, π].
        
        :returns: The radian value of the rotation constrained within [-π, π].
        """
    def rotateBy(self, other: Rotation2d) -> Rotation2d:
        """
        Adds the new rotation to the current rotation using a rotation matrix.
        
        ::
        
          [cos_new]   [other.cos, -other.sin][cos]
          [sin_new] = [other.sin,  other.cos][sin]
          value_new = std::atan2(sin_new, cos_new)
        
        :param other: The rotation to rotate by.
        
        :returns: The new rotated Rotation2d.
        """
    def sin(self) -> float:
        """
        Returns the sine of the rotation.
        
        :returns: The sine of the rotation.
        """
    def tan(self) -> float:
        """
        Returns the tangent of the rotation.
        
        :returns: The tangent of the rotation.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 2]"]:
        """
        Returns matrix representation of this rotation.
        """
class Rotation3d:
    """
    A rotation in a 3D coordinate frame represented by a quaternion.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9ab810>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromDegrees(roll: wpimath.units.degrees, pitch: wpimath.units.degrees, yaw: wpimath.units.degrees) -> Rotation3d:
        ...
    def X(self) -> wpimath.units.radians:
        """
        Returns the counterclockwise rotation angle around the X axis (roll).
        """
    def Y(self) -> wpimath.units.radians:
        """
        Returns the counterclockwise rotation angle around the Y axis (pitch).
        """
    def Z(self) -> wpimath.units.radians:
        """
        Returns the counterclockwise rotation angle around the Z axis (yaw).
        """
    def __add__(self, arg0: Rotation3d) -> Rotation3d:
        """
        Adds two rotations together.
        
        :param other: The rotation to add.
        
        :returns: The sum of the two rotations.
        """
    def __eq__(self, arg0: Rotation3d) -> bool:
        """
        Checks equality between this Rotation3d and another object.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a Rotation3d representing no rotation.
        """
    @typing.overload
    def __init__(self, q: Quaternion) -> None:
        """
        Constructs a Rotation3d from a quaternion.
        
        :param q: The quaternion.
        """
    @typing.overload
    def __init__(self, roll: wpimath.units.radians, pitch: wpimath.units.radians, yaw: wpimath.units.radians) -> None:
        """
        Constructs a Rotation3d from extrinsic roll, pitch, and yaw.
        
        Extrinsic rotations occur in that order around the axes in the fixed global
        frame rather than the body frame.
        
        Angles are measured counterclockwise with the rotation axis pointing "out
        of the page". If you point your right thumb along the positive axis
        direction, your fingers curl in the direction of positive rotation.
        
        :param roll:  The counterclockwise rotation angle around the X axis (roll).
        :param pitch: The counterclockwise rotation angle around the Y axis (pitch).
        :param yaw:   The counterclockwise rotation angle around the Z axis (yaw).
        """
    @typing.overload
    def __init__(self, axis: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"], angle: wpimath.units.radians) -> None:
        """
        Constructs a Rotation3d with the given axis-angle representation. The axis
        doesn't have to be normalized.
        
        :param axis:  The rotation axis.
        :param angle: The rotation around the axis.
        """
    @typing.overload
    def __init__(self, rvec: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> None:
        """
        Constructs a Rotation3d with the given rotation vector representation. This
        representation is equivalent to axis-angle, where the normalized axis is
        multiplied by the rotation around the axis in radians.
        
        :param rvec: The rotation vector.
        """
    @typing.overload
    def __init__(self, rotationMatrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]) -> None:
        """
        Constructs a Rotation3d from a rotation matrix.
        
        :param rotationMatrix: The rotation matrix.
                               @throws std::domain_error if the rotation matrix isn't special orthogonal.
        """
    @typing.overload
    def __init__(self, initial: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"], final: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> None:
        """
        Constructs a Rotation3d that rotates the initial vector onto the final
        vector.
        
        This is useful for turning a 3D vector (final) into an orientation relative
        to a coordinate system vector (initial).
        
        :param initial: The initial vector.
        :param final:   The final vector.
        """
    @typing.overload
    def __init__(self, rotation: Rotation2d) -> None:
        """
        Constructs a 3D rotation from a 2D rotation in the X-Y plane.
        
        :param rotation: The 2D rotation.
                         @see Pose3d(Pose2d)
                         @see Transform3d(Transform2d)
        """
    def __mul__(self, arg0: typing.SupportsFloat) -> Rotation3d:
        """
        Multiplies the current rotation by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Rotation3d.
        """
    def __neg__(self) -> Rotation3d:
        """
        Takes the inverse of the current rotation.
        
        :returns: The inverse of the current rotation.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Rotation3d) -> Rotation3d:
        """
        Subtracts the new rotation from the current rotation and returns the new
        rotation.
        
        :param other: The rotation to subtract.
        
        :returns: The difference between the two rotations.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Rotation3d:
        """
        Divides the current rotation by a scalar.
        
        :param scalar: The scalar.
        
        :returns: The new scaled Rotation3d.
        """
    def axis(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns the axis in the axis-angle representation of this rotation.
        """
    def getQuaternion(self) -> Quaternion:
        """
        Returns the quaternion representation of the Rotation3d.
        """
    def rotateBy(self, other: Rotation3d) -> Rotation3d:
        """
        Adds the new rotation to the current rotation. The other rotation is
        applied extrinsically, which means that it rotates around the global axes.
        For example, Rotation3d{90_deg, 0, 0}.RotateBy(Rotation3d{0, 45_deg, 0})
        rotates by 90 degrees around the +X axis and then by 45 degrees around the
        global +Y axis. (This is equivalent to Rotation3d{90_deg, 45_deg, 0})
        
        :param other: The extrinsic rotation to rotate by.
        
        :returns: The new rotated Rotation3d.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]:
        """
        Returns rotation matrix representation of this rotation.
        """
    def toRotation2d(self) -> Rotation2d:
        """
        Returns a Rotation2d representing this Rotation3d projected into the X-Y
        plane.
        """
    def toVector(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns rotation vector representation of this rotation.
        
        :returns: Rotation vector representation of this rotation.
        """
    @property
    def angle(self) -> wpimath.units.radians:
        ...
    @property
    def angle_degrees(self) -> wpimath.units.degrees:
        ...
    @property
    def x(self) -> wpimath.units.radians:
        ...
    @property
    def x_degrees(self) -> wpimath.units.degrees:
        ...
    @property
    def y(self) -> wpimath.units.radians:
        ...
    @property
    def y_degrees(self) -> wpimath.units.degrees:
        ...
    @property
    def z(self) -> wpimath.units.radians:
        ...
    @property
    def z_degrees(self) -> wpimath.units.degrees:
        ...
class Transform2d:
    """
    Represents a transformation for a Pose2d in the pose's frame.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9abe70>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet, angle: wpimath.units.radians) -> Transform2d:
        ...
    @staticmethod
    def fromMatrix(matrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 3]"]) -> Transform2d:
        """
        Constructs a pose with the specified affine transformation matrix.
        
        :param matrix: The affine transformation matrix.
                       @throws std::domain_error if the affine transformation matrix is invalid.
        """
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the transformation's translation.
        
        :returns: The x component of the transformation's translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the transformation's translation.
        
        :returns: The y component of the transformation's translation.
        """
    def __add__(self, arg0: Transform2d) -> Transform2d:
        """
        Composes two transformations. The second transform is applied relative to
        the orientation of the first.
        
        :param other: The transform to compose with this one.
        
        :returns: The composition of the two transformations.
        """
    def __eq__(self, arg0: Transform2d) -> bool:
        """
        Checks equality between this Transform2d and another object.
        """
    @typing.overload
    def __init__(self, initial: Pose2d, final: Pose2d) -> None:
        """
        Constructs the transform that maps the initial pose to the final pose.
        
        :param initial: The initial pose for the transformation.
        :param final:   The final pose for the transformation.
        """
    @typing.overload
    def __init__(self, translation: Translation2d, rotation: Rotation2d) -> None:
        """
        Constructs a transform with the given translation and rotation components.
        
        :param translation: Translational component of the transform.
        :param rotation:    Rotational component of the transform.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, rotation: Rotation2d) -> None:
        """
        Constructs a transform with x and y translations instead of a separate
        Translation2d.
        
        :param x:        The x component of the translational component of the transform.
        :param y:        The y component of the translational component of the transform.
        :param rotation: The rotational component of the transform.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs the identity transform -- maps an initial pose to itself.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, angle: wpimath.units.radians) -> None:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Transform2d:
        """
        Multiplies the transform by the scalar.
        
        :param scalar: The scalar.
        
        :returns: The scaled Transform2d.
        """
    def __repr__(self) -> str:
        ...
    def __truediv__(self, arg0: typing.SupportsFloat) -> Transform2d:
        """
        Divides the transform by the scalar.
        
        :param scalar: The scalar.
        
        :returns: The scaled Transform2d.
        """
    def inverse(self) -> Transform2d:
        """
        Invert the transformation. This is useful for undoing a transformation.
        
        :returns: The inverted transformation.
        """
    def rotation(self) -> Rotation2d:
        """
        Returns the rotational component of the transformation.
        
        :returns: Reference to the rotational component of the transform.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]:
        """
        Returns an affine transformation matrix representation of this
        transformation.
        """
    def translation(self) -> Translation2d:
        """
        Returns the translation component of the transformation.
        
        :returns: Reference to the translational component of the transform.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
class Transform3d:
    """
    Represents a transformation for a Pose3d in the pose's frame.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9bc570>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromMatrix(matrix: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[4, 4]"]) -> Transform3d:
        """
        Constructs a transform with the specified affine transformation matrix.
        
        :param matrix: The affine transformation matrix.
                       @throws std::domain_error if the affine transformation matrix is invalid.
        """
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the transformation's translation.
        
        :returns: The x component of the transformation's translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the transformation's translation.
        
        :returns: The y component of the transformation's translation.
        """
    def Z(self) -> wpimath.units.meters:
        """
        Returns the Z component of the transformation's translation.
        
        :returns: The z component of the transformation's translation.
        """
    def __add__(self, arg0: Transform3d) -> Transform3d:
        """
        Composes two transformations. The second transform is applied relative to
        the orientation of the first.
        
        :param other: The transform to compose with this one.
        
        :returns: The composition of the two transformations.
        """
    def __eq__(self, arg0: Transform3d) -> bool:
        """
        Checks equality between this Transform3d and another object.
        """
    @typing.overload
    def __init__(self, initial: Pose3d, final: Pose3d) -> None:
        """
        Constructs the transform that maps the initial pose to the final pose.
        
        :param initial: The initial pose for the transformation.
        :param final:   The final pose for the transformation.
        """
    @typing.overload
    def __init__(self, translation: Translation3d, rotation: Rotation3d) -> None:
        """
        Constructs a transform with the given translation and rotation components.
        
        :param translation: Translational component of the transform.
        :param rotation:    Rotational component of the transform.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, z: wpimath.units.meters, rotation: Rotation3d) -> None:
        """
        Constructs a transform with x, y, and z translations instead of a separate
        Translation3d.
        
        :param x:        The x component of the translational component of the transform.
        :param y:        The y component of the translational component of the transform.
        :param z:        The z component of the translational component of the transform.
        :param rotation: The rotational component of the transform.
        """
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs the identity transform -- maps an initial pose to itself.
        """
    @typing.overload
    def __init__(self, transform: Transform2d) -> None:
        """
        Constructs a 3D transform from a 2D transform in the X-Y plane.
        **
        
        :param transform: The 2D transform.
                          @see Rotation3d(Rotation2d)
                          @see Translation3d(Translation2d)
        """
    def __mul__(self, arg0: typing.SupportsFloat) -> Transform3d:
        """
        Multiplies the transform by the scalar.
        
        :param scalar: The scalar.
        
        :returns: The scaled Transform3d.
        """
    def __repr__(self) -> str:
        ...
    def __truediv__(self, arg0: typing.SupportsFloat) -> Transform3d:
        """
        Divides the transform by the scalar.
        
        :param scalar: The scalar.
        
        :returns: The scaled Transform3d.
        """
    def inverse(self) -> Transform3d:
        """
        Invert the transformation. This is useful for undoing a transformation.
        
        :returns: The inverted transformation.
        """
    def rotation(self) -> Rotation3d:
        """
        Returns the rotational component of the transformation.
        
        :returns: Reference to the rotational component of the transform.
        """
    def toMatrix(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[4, 4]"]:
        """
        Returns an affine transformation matrix representation of this
        transformation.
        """
    def translation(self) -> Translation3d:
        """
        Returns the translation component of the transformation.
        
        :returns: Reference to the translational component of the transform.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
    @property
    def z(self) -> wpimath.units.meters:
        ...
    @property
    def z_feet(self) -> wpimath.units.feet:
        ...
class Translation2d:
    """
    Represents a translation in 2D space.
    This object can be used to represent a point or a vector.
    
    This assumes that you are using conventional mathematical axes.
    When the robot is at the origin facing in the positive X direction, forward
    is positive X and left is positive Y.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9bcf30>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    @typing.overload
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet) -> Translation2d:
        ...
    @staticmethod
    @typing.overload
    def fromFeet(distance: wpimath.units.feet, angle: Rotation2d) -> Translation2d:
        ...
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the translation.
        
        :returns: The X component of the translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the translation.
        
        :returns: The Y component of the translation.
        """
    def __abs__(self) -> wpimath.units.meters:
        ...
    def __add__(self, arg0: Translation2d) -> Translation2d:
        """
        Returns the sum of two translations in 2D space.
        
        For example, Translation3d{1.0, 2.5} + Translation3d{2.0, 5.5} =
        Translation3d{3.0, 8.0}.
        
        :param other: The translation to add.
        
        :returns: The sum of the translations.
        """
    def __eq__(self, arg0: Translation2d) -> bool:
        """
        Checks equality between this Translation2d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    def __getitem__(self, arg0: typing.SupportsInt) -> wpimath.units.meters:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a Translation2d with X and Y components equal to zero.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters) -> None:
        """
        Constructs a Translation2d with the X and Y components equal to the
        provided values.
        
        :param x: The x component of the translation.
        :param y: The y component of the translation.
        """
    @typing.overload
    def __init__(self, distance: wpimath.units.meters, angle: Rotation2d) -> None:
        """
        Constructs a Translation2d with the provided distance and angle. This is
        essentially converting from polar coordinates to Cartesian coordinates.
        
        :param distance: The distance from the origin to the end of the translation.
        :param angle:    The angle between the x-axis and the translation vector.
        """
    @typing.overload
    def __init__(self, vector: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[2, 1]"]) -> None:
        """
        Constructs a Translation2d from a 2D translation vector. The values are
        assumed to be in meters.
        
        :param vector: The translation vector.
        """
    def __len__(self) -> int:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Translation2d:
        """
        Returns the translation multiplied by a scalar.
        
        For example, Translation2d{2.0, 2.5} * 2 = Translation2d{4.0, 5.0}.
        
        :param scalar: The scalar to multiply by.
        
        :returns: The scaled translation.
        """
    def __neg__(self) -> Translation2d:
        """
        Returns the inverse of the current translation. This is equivalent to
        rotating by 180 degrees, flipping the point over both axes, or negating all
        components of the translation.
        
        :returns: The inverse of the current translation.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Translation2d) -> Translation2d:
        """
        Returns the difference between two translations.
        
        For example, Translation2d{5.0, 4.0} - Translation2d{1.0, 2.0} =
        Translation2d{4.0, 2.0}.
        
        :param other: The translation to subtract.
        
        :returns: The difference between the two translations.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Translation2d:
        """
        Returns the translation divided by a scalar.
        
        For example, Translation2d{2.0, 2.5} / 2 = Translation2d{1.0, 1.25}.
        
        :param scalar: The scalar to divide by.
        
        :returns: The scaled translation.
        """
    def angle(self) -> Rotation2d:
        """
        Returns the angle this translation forms with the positive X axis.
        
        :returns: The angle of the translation
        """
    def distance(self, other: Translation2d) -> wpimath.units.meters:
        """
        Calculates the distance between two translations in 2D space.
        
        The distance between translations is defined as √((x₂−x₁)²+(y₂−y₁)²).
        
        :param other: The translation to compute the distance to.
        
        :returns: The distance between the two translations.
        """
    def distanceFeet(self, arg0: Translation2d) -> wpimath.units.feet:
        ...
    def nearest(self, translations: list[Translation2d]) -> Translation2d:
        """
        Returns the nearest Translation2d from a collection of translations
        
        :param translations: The collection of translations.
        
        :returns: The nearest Translation2d from the collection.
        """
    def norm(self) -> wpimath.units.meters:
        """
        Returns the norm, or distance from the origin to the translation.
        
        :returns: The norm of the translation.
        """
    def normFeet(self) -> wpimath.units.feet:
        ...
    def rotateAround(self, other: Translation2d, rot: Rotation2d) -> Translation2d:
        """
        Rotates this translation around another translation in 2D space.
        
        ::
        
          [x_new]   [rot.cos, -rot.sin][x - other.x]   [other.x]
          [y_new] = [rot.sin,  rot.cos][y - other.y] + [other.y]
        
        :param other: The other translation to rotate around.
        :param rot:   The rotation to rotate the translation by.
        
        :returns: The new rotated translation.
        """
    def rotateBy(self, other: Rotation2d) -> Translation2d:
        """
        Applies a rotation to the translation in 2D space.
        
        This multiplies the translation vector by a counterclockwise rotation
        matrix of the given angle.
        
        ::
        
          [x_new]   [other.cos, -other.sin][x]
          [y_new] = [other.sin,  other.cos][y]
        
        For example, rotating a Translation2d of &lt;2, 0&gt; by 90 degrees will
        return a Translation2d of &lt;0, 2&gt;.
        
        :param other: The rotation to rotate the translation by.
        
        :returns: The new rotated translation.
        """
    def toVector(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[2, 1]"]:
        """
        Returns a 2D translation vector representation of this translation.
        
        :returns: A 2D translation vector representation of this translation.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
class Translation3d:
    """
    Represents a translation in 3D space.
    This object can be used to represent a point or a vector.
    
    This assumes that you are using conventional mathematical axes. When the
    robot is at the origin facing in the positive X direction, forward is
    positive X, left is positive Y, and up is positive Z.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9bd9b0>
    __hash__: typing.ClassVar[None] = None
    @staticmethod
    def fromFeet(x: wpimath.units.feet, y: wpimath.units.feet, z: wpimath.units.feet) -> Translation3d:
        ...
    def X(self) -> wpimath.units.meters:
        """
        Returns the X component of the translation.
        
        :returns: The Z component of the translation.
        """
    def Y(self) -> wpimath.units.meters:
        """
        Returns the Y component of the translation.
        
        :returns: The Y component of the translation.
        """
    def Z(self) -> wpimath.units.meters:
        """
        Returns the Z component of the translation.
        
        :returns: The Z component of the translation.
        """
    def __abs__(self) -> wpimath.units.meters:
        ...
    def __add__(self, arg0: Translation3d) -> Translation3d:
        """
        Returns the sum of two translations in 3D space.
        
        For example, Translation3d{1.0, 2.5, 3.5} + Translation3d{2.0, 5.5, 7.5} =
        Translation3d{3.0, 8.0, 11.0}.
        
        :param other: The translation to add.
        
        :returns: The sum of the translations.
        """
    def __eq__(self, arg0: Translation3d) -> bool:
        """
        Checks equality between this Translation3d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    def __getitem__(self, arg0: typing.SupportsInt) -> wpimath.units.meters:
        ...
    @typing.overload
    def __init__(self) -> None:
        """
        Constructs a Translation3d with X, Y, and Z components equal to zero.
        """
    @typing.overload
    def __init__(self, x: wpimath.units.meters, y: wpimath.units.meters, z: wpimath.units.meters) -> None:
        """
        Constructs a Translation3d with the X, Y, and Z components equal to the
        provided values.
        
        :param x: The x component of the translation.
        :param y: The y component of the translation.
        :param z: The z component of the translation.
        """
    @typing.overload
    def __init__(self, distance: wpimath.units.meters, angle: Rotation3d) -> None:
        """
        Constructs a Translation3d with the provided distance and angle. This is
        essentially converting from polar coordinates to Cartesian coordinates.
        
        :param distance: The distance from the origin to the end of the translation.
        :param angle:    The angle between the x-axis and the translation vector.
        """
    @typing.overload
    def __init__(self, vector: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> None:
        """
        Constructs a Translation3d from a 3D translation vector. The values are
        assumed to be in meters.
        
        :param vector: The translation vector.
        """
    @typing.overload
    def __init__(self, translation: Translation2d) -> None:
        """
        Constructs a 3D translation from a 2D translation in the X-Y plane.
        
        :param translation: The 2D translation.
                            @see Pose3d(Pose2d)
                            @see Transform3d(Transform2d)
        """
    def __len__(self) -> int:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Translation3d:
        """
        Returns the translation multiplied by a scalar.
        
        For example, Translation3d{2.0, 2.5, 4.5} * 2 = Translation3d{4.0, 5.0,
        9.0}.
        
        :param scalar: The scalar to multiply by.
        
        :returns: The scaled translation.
        """
    def __neg__(self) -> Translation3d:
        """
        Returns the inverse of the current translation. This is equivalent to
        negating all components of the translation.
        
        :returns: The inverse of the current translation.
        """
    def __repr__(self) -> str:
        ...
    def __sub__(self, arg0: Translation3d) -> Translation3d:
        """
        Returns the difference between two translations.
        
        For example, Translation3d{5.0, 4.0, 3.0} - Translation3d{1.0, 2.0, 3.0} =
        Translation3d{4.0, 2.0, 0.0}.
        
        :param other: The translation to subtract.
        
        :returns: The difference between the two translations.
        """
    def __truediv__(self, arg0: typing.SupportsFloat) -> Translation3d:
        """
        Returns the translation divided by a scalar.
        
        For example, Translation3d{2.0, 2.5, 4.5} / 2 = Translation3d{1.0, 1.25,
        2.25}.
        
        :param scalar: The scalar to divide by.
        
        :returns: The scaled translation.
        """
    def distance(self, other: Translation3d) -> wpimath.units.meters:
        """
        Calculates the distance between two translations in 3D space.
        
        The distance between translations is defined as
        √((x₂−x₁)²+(y₂−y₁)²+(z₂−z₁)²).
        
        :param other: The translation to compute the distance to.
        
        :returns: The distance between the two translations.
        """
    def distanceFeet(self, arg0: Translation3d) -> wpimath.units.feet:
        ...
    def nearest(self, translations: list[Translation3d]) -> Translation3d:
        """
        Returns the nearest Translation3d from a collection of translations
        
        :param translations: The collection of translations.
        
        :returns: The nearest Translation3d from the collection.
        """
    def norm(self) -> wpimath.units.meters:
        """
        Returns the norm, or distance from the origin to the translation.
        
        :returns: The norm of the translation.
        """
    def normFeet(self) -> wpimath.units.feet:
        ...
    def rotateAround(self, other: Translation3d, rot: Rotation3d) -> Translation3d:
        """
        Rotates this translation around another translation in 3D space.
        
        :param other: The other translation to rotate around.
        :param rot:   The rotation to rotate the translation by.
        
        :returns: The new rotated translation.
        """
    def rotateBy(self, other: Rotation3d) -> Translation3d:
        """
        Applies a rotation to the translation in 3D space.
        
        For example, rotating a Translation3d of &lt;2, 0, 0&gt; by 90 degrees
        around the Z axis will return a Translation3d of &lt;0, 2, 0&gt;.
        
        :param other: The rotation to rotate the translation by.
        
        :returns: The new rotated translation.
        """
    def toTranslation2d(self) -> Translation2d:
        """
        Returns a Translation2d representing this Translation3d projected into the
        X-Y plane.
        """
    def toVector(self) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 1]"]:
        """
        Returns a 3D translation vector representation of this translation.
        
        :returns: A 3D translation vector representation of this translation.
        """
    @property
    def x(self) -> wpimath.units.meters:
        ...
    @property
    def x_feet(self) -> wpimath.units.feet:
        ...
    @property
    def y(self) -> wpimath.units.meters:
        ...
    @property
    def y_feet(self) -> wpimath.units.feet:
        ...
    @property
    def z(self) -> wpimath.units.meters:
        ...
    @property
    def z_feet(self) -> wpimath.units.feet:
        ...
class Twist2d:
    """
    A change in distance along a 2D arc since the last pose update. We can use
    ideas from differential calculus to create new Pose2ds from a Twist2d and
    vice versa.
    
    A Twist can be used to represent a difference between two poses.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9bdf50>
    __hash__: typing.ClassVar[None] = None
    dtheta_degrees: wpimath.units.degrees
    dx_feet: wpimath.units.feet
    dy_feet: wpimath.units.feet
    @staticmethod
    def fromFeet(dx: wpimath.units.feet = 0, dy: wpimath.units.feet = 0, dtheta: wpimath.units.radians = 0) -> Twist2d:
        ...
    def __eq__(self, arg0: Twist2d) -> bool:
        """
        Checks equality between this Twist2d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    def __init__(self, dx: wpimath.units.meters = 0, dy: wpimath.units.meters = 0, dtheta: wpimath.units.radians = 0) -> None:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Twist2d:
        """
        Scale this by a given factor.
        
        :param factor: The factor by which to scale.
        
        :returns: The scaled Twist2d.
        """
    def __repr__(self) -> str:
        ...
    @property
    def dtheta(self) -> wpimath.units.radians:
        """
        Angular "dtheta" component (radians)
        """
    @dtheta.setter
    def dtheta(self, arg0: wpimath.units.radians) -> None:
        ...
    @property
    def dx(self) -> wpimath.units.meters:
        """
        Linear "dx" component
        """
    @dx.setter
    def dx(self, arg0: wpimath.units.meters) -> None:
        ...
    @property
    def dy(self) -> wpimath.units.meters:
        """
        Linear "dy" component
        """
    @dy.setter
    def dy(self, arg0: wpimath.units.meters) -> None:
        ...
class Twist3d:
    """
    A change in distance along a 3D arc since the last pose update. We can use
    ideas from differential calculus to create new Pose3ds from a Twist3d and
    vice versa.
    
    A Twist can be used to represent a difference between two poses.
    """
    WPIStruct: typing.ClassVar[typing.Any]  # value = <capsule object "WPyStruct" at 0xff8caa9be850>
    __hash__: typing.ClassVar[None] = None
    dx_feet: wpimath.units.feet
    dy_feet: wpimath.units.feet
    dz_feet: wpimath.units.feet
    rx_degrees: wpimath.units.degrees
    ry_degrees: wpimath.units.degrees
    rz_degrees: wpimath.units.degrees
    @staticmethod
    def fromFeet(dx: wpimath.units.feet = 0, dy: wpimath.units.feet = 0, dz: wpimath.units.feet = 0, rx: wpimath.units.radians = 0, ry: wpimath.units.radians = 0, rz: wpimath.units.radians = 0) -> Twist3d:
        ...
    def __eq__(self, arg0: Twist3d) -> bool:
        """
        Checks equality between this Twist3d and another object.
        
        :param other: The other object.
        
        :returns: Whether the two objects are equal.
        """
    def __init__(self, dx: wpimath.units.meters = 0, dy: wpimath.units.meters = 0, dz: wpimath.units.meters = 0, rx: wpimath.units.radians = 0, ry: wpimath.units.radians = 0, rz: wpimath.units.radians = 0) -> None:
        ...
    def __mul__(self, arg0: typing.SupportsFloat) -> Twist3d:
        """
        Scale this by a given factor.
        
        :param factor: The factor by which to scale.
        
        :returns: The scaled Twist3d.
        """
    def __repr__(self) -> str:
        ...
    @property
    def dx(self) -> wpimath.units.meters:
        """
        Linear "dx" component
        """
    @dx.setter
    def dx(self, arg0: wpimath.units.meters) -> None:
        ...
    @property
    def dy(self) -> wpimath.units.meters:
        """
        Linear "dy" component
        """
    @dy.setter
    def dy(self, arg0: wpimath.units.meters) -> None:
        ...
    @property
    def dz(self) -> wpimath.units.meters:
        """
        Linear "dz" component
        """
    @dz.setter
    def dz(self, arg0: wpimath.units.meters) -> None:
        ...
    @property
    def rx(self) -> wpimath.units.radians:
        """
        Rotation vector x component.
        """
    @rx.setter
    def rx(self, arg0: wpimath.units.radians) -> None:
        ...
    @property
    def ry(self) -> wpimath.units.radians:
        """
        Rotation vector y component.
        """
    @ry.setter
    def ry(self, arg0: wpimath.units.radians) -> None:
        ...
    @property
    def rz(self) -> wpimath.units.radians:
        """
        Rotation vector z component.
        """
    @rz.setter
    def rz(self, arg0: wpimath.units.radians) -> None:
        ...
def rotationVectorToMatrix(rotation: typing.Annotated[numpy.typing.ArrayLike, numpy.float64, "[3, 1]"]) -> typing.Annotated[numpy.typing.NDArray[numpy.float64], "[3, 3]"]:
    """
    Applies the hat operator to a rotation vector.
    
    It takes a rotation vector and returns the corresponding matrix
    representation of the Lie algebra element (a 3x3 rotation matrix).
    
    :param rotation: The rotation vector.
    
    :returns: The rotation vector as a 3x3 rotation matrix.
    """
