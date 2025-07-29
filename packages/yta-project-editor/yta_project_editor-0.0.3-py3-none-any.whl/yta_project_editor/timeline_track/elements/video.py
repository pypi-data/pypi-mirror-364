from yta_project_editor.timeline_track.elements import TimelineTrackElement
from yta_video_editor.editor import VideoEditor


class VideoTimelineTrackElement(TimelineTrackElement):
    """
    A wrapper to be able to identify and handle
    a video element in a timeline track.
    """

    def __init__(
        self,
        video: VideoEditor
    ):
        self.element = video
        """
        The instance of the element that actually
        contains the information we need to process
        it as a video element.
        """
        #self.duration = video.duration