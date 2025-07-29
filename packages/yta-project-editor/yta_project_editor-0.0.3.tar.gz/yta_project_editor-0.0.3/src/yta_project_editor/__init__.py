"""
Welcome to Youtube Autonomous Project Editor
Module.

Module to work as a whole project video editor
with all the capabilities we have been 
programming all this time.
"""
from yta_project_editor.timeline_track import TimelineTrack
from yta_project_editor.validator import ProjectEditorValidator
from yta_project_editor.settings import DEFAULT_DIMENSIONS
from yta_video_base.duration import set_video_duration
from yta_constants.video import ExtendVideoMode
from yta_constants.project import TimelineTrackType
from yta_validation.parameter import ParameterValidator
from yta_validation import PythonValidator
from moviepy import CompositeVideoClip
from typing import Union


class ProjectEditor:
    """
    Class representing a whole but single video project
    in which we have a timeline with different tracks
    and clips on them.

    A project must have, at least, these attributes:
    - `name` (optional)
    - `width` (or combined as resolution)
    - `height` (or combined as resolution)
    - `frame_rate` (or fps)
    - `duration` (calculated, end of last clip)
    - `tracks`
    """

    @property
    def start_time(
        self
    ) -> float:
        """
        The moment in which the first timeline track
        starts.
        """
        return (
            min(
                self.timeline_tracks,
                key = lambda timeline_track: timeline_track.start_time
            ).start_time
            if self.has_timeline_tracks else
            0.0
        )
    
    @property
    def end_time(
        self
    ) -> float:
        """
        The moment in which the last timeline track
        finished.
        """
        return (
            max(
                self.timeline_tracks,
                key = lambda timeline_track: timeline_track.end_time
            ).end_time
            if self.has_timeline_tracks else
            0.0
        )

    @property
    def duration(
        self
    ) -> float:
        """
        The duration of the project based on all the
        timeline tracks that are set.
        """
        return self.end_time - self.start_time
         
    @property
    def has_timeline_tracks(
        self
    ) -> bool:
        """
        Boolean to indicate if it has timeline tracks
        or not.
        """
        return len(self.timeline_tracks) > 0

    def __init__(
        self,
        name: Union[str, None] = None,
        width: int = DEFAULT_DIMENSIONS[0],
        height: int = DEFAULT_DIMENSIONS[1],
        fps: int = 60
    ):
        ParameterValidator.validate_string('name', name, do_accept_empty = True)
        ProjectEditorValidator.validate_width(width)
        ProjectEditorValidator.validate_height(height)
        ProjectEditorValidator.validate_fps(fps)

        self.timeline_tracks: list[TimelineTrack] = [
            TimelineTrack(0, TimelineTrackType.VIDEO),
            # TODO: I Simplify everything by now and I only
            # handle one video track
            #TimelineTrack(0, TimelineTrackType.AUDIO)
        ]
        """
        The different timeline tracks that hold the
        video, audio and other elements of the 
        project.
        """
        self.name: str = (
            name
            if (
                name is not None and
                name is not ''
            ) else
            # TODO: Generate random project name
            'projecto_random'
        )
        """
        The name of the project to be identified.
        """
        self.width: int = width
        """
        The width of the project to be exported with.
        """
        self.height: int = height
        """
        The height of the projectt to be exported
        with.
        """
        self.fps: float = fps
        """
        The frames per second of the project to be
        exported with.
        """

    def get_tracks(
        self,
        type: TimelineTrackType
    ) -> list[TimelineTrack]:
        """
        Get the timeline tracks of the provided 'type' sorted by
        index in ascending order.
        """
        type = TimelineTrackType.to_enum(type)

        return sorted(
            [
                track
                for track in self.timeline_tracks
                if track.type == type
            ], 
            key = lambda track: track.index
        )
    
    def get_last_track(
        self,
        type: TimelineTrackType
    ) -> Union[TimelineTrack, None]:
        """
        Get the last track of the type provided,
        which means the one that ends the last.
        """
        filtered = self.get_tracks(type)

        return (
            max(filtered, key = lambda l: l.end_time)
            if filtered else
            None
        )
    
    # TODO: I think this is useless
    def get_last_track_index(
        self,
        type: TimelineTrackType
    ) -> Union[int, None]:
        """
        Get the last index used for the tracks of the given
        'type', that will be None if no tracks of that type.
        """
        type = TimelineTrackType.to_enum(type)

        tracks = self.get_tracks(type)

        # TODO: Be careful, this is the index within the
        # list of that type, not within the general list
        return (
            tracks[-1:].index
            if not PythonValidator.is_empty_list(tracks) else
            None
        )

    def add_track(
        self,
        type: TimelineTrackType = TimelineTrackType.VIDEO
    ) -> int:
        """
        Add a new track of the provided 'type' and returns
        the index in which it has been placed.
        """
        type = (
            TimelineTrackType.to_enum(type)
            if type is not None else
            TimelineTrackType.VIDEO
        )

        tracks = self.get_tracks(type)
        index = (
            len(tracks) + 1
            if tracks else
            0
        )

        self.timeline_tracks.append(TimelineTrack(index, type))

        return index
    
    def remove_track(
        self,
        track: TimelineTrack
    ):
        ParameterValidator.validate_mandatory_instance_of('track', track, TimelineTrack)
        
        if track not in self.timeline_tracks:
            raise Exception('The provided "track" does not exist in this project.')

        self.timeline_tracks.remove(track)

    def build(
        self
    ):
        # TODO: Remove this code below when this is done 
        # individually by each track. By now I'm forcing
        # all tracks clips to have the same duration as
        # the longest track clip has, but must be done
        # using a general and common 'max_duration'
        # property that is not calculated here.
        tracks_clips = [
            track.build()
            for track in self.timeline_tracks
        ]
        max_duration = max(
            track_clip.duration
            for track_clip in tracks_clips
        )
        tracks_clips = [
            set_video_duration(track_clip, max_duration, extend_mode = ExtendVideoMode.BLACK_TRANSPARENT_BACKGROUND)
            for track_clip in tracks_clips
        ]

        return CompositeVideoClip(tracks_clips)