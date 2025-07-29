# TODO: Move these resolution constants below
# to a general constants or something
SD_480 = (720, 480)
HD_720 = (1280, 720)
FULLHD_1080 = (1920, 1080)
DCI_2K = (2018, 1080)
UHD_4K = (3840, 2160)
DCI_4K = (4096, 2160)
UHD_5K = (5120, 2880)
UHD_6K = (6144, 3160)
UHD_8K = (7680, 4320)
DCI_8K = (8192, 4320)


MAX_TIMELINE_TRACK_DURATION = 1200
"""
The maximum duration, in seconds, that a
timeline track can have according to all
the subclips on it. This value can change
to allow longer timeline tracks.
"""
TRACKS_INDEXES_LIMIT = (0, 9)
"""
The limit of the tracks indexes we have, starting
from 0, so only the upper limit + 1 tracks are
available in the edition system.
"""
MINIMUM_FPS = 5
"""
The lower frames per second the project can have.
"""
MAXIMUM_FPS = 120
"""
The greater frames per second the project can have.
"""
MINIMUM_DIMENSIONS = SD_480
"""
The lower dimension the project can have.
"""
MAXIMUM_DIMENSIONS = FULLHD_1080
"""
The greater dimension the project can have.
"""
DEFAULT_DIMENSIONS = FULLHD_1080
"""
The dimension that a project should have by default.
"""




