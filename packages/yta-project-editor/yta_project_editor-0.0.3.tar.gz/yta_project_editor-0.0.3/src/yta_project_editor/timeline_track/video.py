from yta_project_editor.timeline_track import TimelineTrack
from yta_project_editor.timeline_track.elements import ElementOnTimelineTrack
from yta_project_editor.timeline_track.elements.video import VideoTimelineTrackElement
from yta_project_editor.settings import MAX_TIMELINE_TRACK_DURATION
from yta_validation.parameter import ParameterValidator
from yta_video_base.concatenation import concatenate_videos
from yta_video_moviepy.generator import MoviepyNormalClipGenerator


class VideoTimelineTrack(TimelineTrack):
    """
    Class to identify a timeline track that
    contains video elements.
    """

    # TODO: Review this method
    @property
    def elements_for_building(self):
        """
        The list of all the elements needed to fulfill the
        timeline track completely. This involves the actual
        elements but also the needed black background clips
        to fulfill the gaps between the clips.
        """
        all_clips = []
        current_time_moment = 0
        # TODO: This 'timeline_duration' must be calculated
        # according to all timeline tracks, so the longest
        # one is the one we need to assign here. Maybe pass
        # it as a parameter on the 'build' method (?)
        timeline_duration = self.elements[-1].end_time

        for clip in self.elements:
            # We fulfill the gap if existing
            if clip.start_time > current_time_moment:
                all_clips.append(
                    MoviepyNormalClipGenerator.get_static_default_color_background(
                        size = clip.size,
                        duration = clip.start_time - current_time_moment,
                        fps = clip.fps
                    )
                )
            
            # We add the existing clip processed
            all_clips.append(clip.video_processed)
            
            current_time_moment = clip.end_time
        
        # Check if gap at the end due to other longer tracks
        if current_time_moment < timeline_duration:
            # TODO: Maybe we need to do something with the fps
            all_clips.append(
                MoviepyNormalClipGenerator.get_static_default_color_background(
                    size = clip.size,
                    duration = timeline_duration - current_time_moment,
                    fps = self.elements[0].fps
                )
            )
        
        return all_clips

    # TODO: This method could change its name
    # due to some refactor with the SubClip
    # class
    def add_element(
        self,
        element: 'Clip',
        start_time: float
    ):
        """
        Append the provided 'clip' at the end of the list.

        TODO: Being in the end of the list doesn't mean being
        the last one displayed. By now I'm storing them just
        one after another and ordering them when trying to get
        them as a property. This will change in a near future
        to be more eficient.
        """
        ParameterValidator.validate_mandatory_instance_of('element', element, 'SubClip')
        ParameterValidator.validate_mandatory_number_between('start_time', start_time, 0, MAX_TIMELINE_TRACK_DURATION)

        # TODO: Check that the 'start_time' or the 'duration'
        # doesn't collide with another existing subclip. If
        # yes, choose what strategy to follow
        if any(
            element.start_time <= start_time <= element.end_time
            for element in self.elements
        ):
            raise Exception(f'There is one existing element at the {str(start_time)} time position.')
        
        # Transform into a real timeline track element
        element = VideoTimelineTrackElement(element)

        self.elements.append(ElementOnTimelineTrack(element, start_time))

    def remove_element(
        self,
        index: int
    ):
        """
        Delete the subclip in the provided 'index' position of
        the list (if existing), or raises an Exception if it
        doesn't exist or the list is empty.
        """
        # TODO: Maybe remove by passing the instance 
        # instead of the index (?)
        if not self.has_elements:
            # TODO: Maybe I should not raise an Exception here...
            raise Exception('No elements to remove.')
        
        ParameterValidator.validate_mandatory_number_between('index', index, 0, len(self.elements))

        # TODO: Be very careful, I have a 'subclips' property which
        # returns the subclips ordered, but the raw '_subclips'
        # property is not ordered, so here the 'index' is potentially
        # wrong. Think how to handle this in a near future, please.
        del self.elements[index]

    def build(
        self
    ):
        """
        Concatenate all the timeline track clips (fulfilling the
        gaps with black transparent background clips) and return the
        concatenated clip.
        """
        # TODO: What if I have one non-transparent and transparent
        # clips in this timeline track? They will be treated in a
        # similar way so it is not the expected behaviour...
        # TODO: This method has to be customized to accept
        # dimensions
        return concatenate_videos(self.elements_for_building)