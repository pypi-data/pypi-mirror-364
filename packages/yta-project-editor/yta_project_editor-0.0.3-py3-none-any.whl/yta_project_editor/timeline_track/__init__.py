from yta_project_editor.timeline_track.elements import TimelineTrackElement, ElementOnTimelineTrack
from yta_project_editor.validator import ProjectEditorValidator
from yta_constants.project import TimelineTrackType
from yta_validation.parameter import ParameterValidator
from typing import Union
from abc import ABC, abstractmethod


class TimelineTrack(ABC):
    """
    Class to identify a track within the
    project timeline.
    """

    @property
    def elements(
        self
    ) -> list[ElementOnTimelineTrack]:
        """
        Get the elements in the timeline but ordered
        by position, from left (begining of the
        timeline) to right (ending of the timeline).
        """
        return sorted(
            self._elements,
            key = lambda element: element.start_time
        )
    
    @property
    def start_time(
        self
    ) -> float:
        """
        The time moment in which the first element
        should start being reproduced/applied within the
        timeline track.
        """
        return (
            min(
                self.elements,
                key = lambda element: element.start_time
            ).start_time
            if self.has_elements else
            0.0
        )
    
    @property
    def end_time(
        self
    ) -> float:
        """
        The time moment in which the last element
        should stop being reproduced/applied within the
        timeline track.
        """
        return (
            max(
                self.elements,
                key = lambda element: element.end_time
            ).end_time
            if self.has_elements else
            0.0
        )
    
    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the whole timeline track,
        defined by the duration of its elements.
        """
        return self.end_time - self.start_time

    @property
    def is_video(
        self
    ) -> bool:
        """
        Boolean indicating if it is a video track or
        not.
        """
        return self.type == TimelineTrackType.VIDEO
    
    @property
    def is_audio(
        self
    ) -> bool:
        """
        Boolean indicating if it is an audio track
        or not.
        """
        return self.type == TimelineTrackType.AUDIO
    
    # TODO: Add more types when available
    
    @property
    def has_elements(
        self
    ) -> bool:
        """
        Boolean indicating if there is any clip on
        this timeline track.
        """
        return len(self._elements) > 0
    
    def __init__(
        self,
        index: int = 0,
        type: TimelineTrackType = TimelineTrackType.VIDEO
    ):
        ProjectEditorValidator.validate_track_index(index)

        type = (
            TimelineTrackType.to_enum(type)
            if type is not None else
            TimelineTrackType.VIDEO
        )

        self.index: int = index
        """
        The position of the track within the
        project, which means the priority from
        top (0) to bottom (9).
        """
        self.type: TimelineTrackType = type
        """
        The type of the track, that will identify
        the type of elements it holds.
        """
        self._elements: list[ElementOnTimelineTrack] = []
        """
        The elements placed on the timeline track.
        """

    # TODO: I don't know if we will handle this
    # 'get_element' with the index or not... (?)
    def get_element(
        self,
        index: int
    ) -> Union[ElementOnTimelineTrack, None]:
        """
        Get the element on the timeline track with
        the given index.
        """
        ParameterValidator.validate_mandatory_positive_int('index', index, do_include_zero = True)

        return (
            self._elements[index]
            if index < len(self._elements) else
            None
        )

    @abstractmethod
    def add_element(
        self,
        element: TimelineTrackElement,
        start_time: float
    ):
        """
        Add an element to the timeline track in the
        'start_time' moment provided.
        """
        pass

    # TODO: Remove with the instance or index (?)
    @abstractmethod
    def remove_element(
        self,
        element: TimelineTrackElement
    ):
        """
        Remove the element from the timeline track.
        """
        pass

    @abstractmethod
    def build(
        self
    ):
        """
        Build the result from the timeline track. This
        result will be used to composite the final 
        video.
        """
        pass
    