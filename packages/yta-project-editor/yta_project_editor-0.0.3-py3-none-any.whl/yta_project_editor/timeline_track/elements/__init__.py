"""
The elements of a project timeline track have
these 2 different classes. One is identifying
a element that can be added to a timeline
track, and the other one is just a small 
wrapper of any element added on the timeline
track to be able to know its position.
"""
from yta_validation.parameter import ParameterValidator
from abc import ABC


class TimelineTrackElement(ABC):
    """
    Class to identify an element that can be
    placed in a project timeline track.

    All the classes that we handle and allow
    to be added on a timeline track has to
    inherit from this one.
    
    Do not confuse this with the other class
    `ElementOnTimelineTrack` which is to 
    identify the element once its been placed
    in the project timeline track.
    """

    def __init__(
        self,
        duration: float
    ):
        ParameterValidator.validate_mandatory_positive_number('duration', duration, do_include_zero = False)

        self.duration: float = duration
        """
        The duration of the element, that will be
        used to calculate the start and end time
        within the track.
        """

class ElementOnTimelineTrack:
    """
    Class to identify an element that has been
    placed in a timeline track within a project.

    This includes a reference to the element we
    are adding and some additional information
    needed to identify and process it when on a
    timeline track.
    """

    @property
    def end_time(
        self
    ) -> float:
        """
        The time moment in which the element should
        stop being reproduced/applied within the
        timeline track.
        """
        return self.start_time + self.element.duration
    
    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the element.
        """
        return self.element.duration

    def __init__(
        self,
        element: TimelineTrackElement,
        start_time: float
    ):
        # TODO: It is actually a subclass so...
        ParameterValidator.validate_mandatory_instance_of('element', element, TimelineTrackElement)
        ParameterValidator.validate_mandatory_positive_float('start_time', start_time, do_include_zero = True)

        self.element: TimelineTrackElement = element
        """
        The element that is being added.
        """
        self.start_time: float = start_time
        """
        The time moment in which the element should 
        start being reproduced/applied within the
        timeline track.
        """

    # TODO: Maybe imitate some options like in
    # editors: muted, invisible, etc.