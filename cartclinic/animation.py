# Source Generated with Decompyle++
# File: animation.pyc (Python 3.10)

import logging
import sys
import time
from libpyretro.cartclinic.comms import Session
from libpyretro.cartclinic.protocol.common import ChromaticBitmap
from cartclinic.consts import BITMAP_REFRESH_INTERVAL_S
from flashing_tool.chromatic_subprocess import PauseableSubprocess
from flashing_tool.util import resolve_path
flashing_tool_logger = logging.getLogger('mrupdater')

class Animation:
    '''This class stores a list of ChromaticBitmap images and tracks the
    current frame, looping back to the start when it reaches the end.
    '''
    
    def __init__(self = None, frames = None, refresh_interval_s = None):
        if len(frames) == 0:
            raise ValueError('Animations must have at least one frame')
        self.frames = frames
        self.refresh_interval_s = refresh_interval_s
        self.last_refresh_time = time.monotonic() - refresh_interval_s
        self.cur_index = 0

    
    def get_next_frame(self = None):
        '''Return the current frame and increment to the next'''
        frame = self.frames[self.cur_index]
        self.cur_index = self.cur_index + 1
        if self.cur_index >= len(self.frames):
            self.cur_index = 0
        self.last_refresh_time = time.monotonic()
        return frame

    
    def draw_bitmap(self = None, session = None, bitmap = None):
        session.set_frame_buffer(bitmap)

    
    def is_stale(self = None):
        delta = time.monotonic() - self.last_refresh_time
        return delta > self.refresh_interval_s

    
    def update_animation_if_stale(self = None, session = None):
        if not self.is_stale():
            return False
        None.draw_bitmap(session, self.get_next_frame())
        return True



class AnimateChromaticSubprocess(PauseableSubprocess):
    '''Animates the Chromatic screen given an Animation object. This should
    not be running asynchronously with any other cartridge operations.
    '''
    
    def __init__(self = None, chromatic_session = None):
        super().__init__()
        self.chromatic_session = chromatic_session
        self.play_only_once = False
        self.played_once = False
        if sys.platform == 'linux':
            self.animation = get_linux_animation()
            self.play_only_once = True
            return None
        self.animation = None()

    
    def run_once(self):
        if self.play_only_once and self.played_once:
            return None
        updated = None.animation.update_animation_if_stale(self.chromatic_session)
        if not updated or self.play_only_once or self.played_once:
            self.played_once = True
            time.sleep(1)
            return None
        return None
        return None

    __classcell__ = None


def get_cart_clinic_loading_animation():
    frame1_path = resolve_path('resources/img/cartclinic/loading1.bmp')
    frame2_path = resolve_path('resources/img/cartclinic/loading2.bmp')
    return Animation([
        ChromaticBitmap.from_bmp(frame1_path),
        ChromaticBitmap.from_bmp(frame2_path)], BITMAP_REFRESH_INTERVAL_S, **('refresh_interval_s',))


def get_linux_animation():
    frame_path = resolve_path('resources/img/cartclinic/please_wait.bmp')
    return Animation([
        ChromaticBitmap.from_bmp(frame_path)], BITMAP_REFRESH_INTERVAL_S, **('refresh_interval_s',))

