from yta_project_editor.timeline_track.elements import TimelineTrackElement


class AudioTimelineTrackElement(TimelineTrackElement):
    """
    A wrapper to be able to identify and handle
    an audio element in a timeline track.
    """
    
    def __init__(
        self,
        audio: any
    ):
        # TODO: This element has to point to the one
        # that we have in the 'yta_audio_editor' library
        # that is able to handle an audio instance and
        # to allow us editing it.
        self.element = audio
        """
        The instance of the element that actually
        contains the information we need to process
        it as an audio element.
        """
        #self.duration = audio.duration