"""Tests for `pyav_reader` package."""
# ruff: noqa: E501

import os

import pytest

from ffmphisdp.pyav_reader import ControlledVideoReader
from ffmphisdp.utils import create_video, decode_all_frames, decode_legacy, expected_frame_color, is_almost_same_color


def fps_conversion_test_case(
    test_obj, filename, fps, expected_frames, red_shift, green_shift, decoder=decode_all_frames
):
    """Test a video decoded in ffmphisdp at a given framerate returns the expected frames"""
    # Change cache to be smaller than the number of frames in the test videos
    all_frames = decoder(filename, framerate=fps, use_gpu=False)
    frame_infos = list(all_frames.keys())
    frame_selection = list(all_frames.values())
    video_handle = ControlledVideoReader(
        filename,
        frame_infos=frame_infos,
        frame_selection=frame_selection,
    )
    frame_idx = 0
    while True:
        ret, frame = video_handle.read()
        if ret is False:  # indicate we reached the last frame or there was a reading error
            assert frame_idx == len(expected_frames), 'stopped at wrong frame'
            break
        # The videos are built with single colored frame, all pixels have the same color
        frame_color = frame[0, 0]  # BGR format
        expected_red, expected_green, _ = expected_frame_color(expected_frames[frame_idx], red_shift, green_shift)
        # Need to account for the fact that encoding will slightly degrade colors
        # we assume less than 1.5% gap (4/255)
        print(
            f'idx: {frame_idx}, expected {expected_frames[frame_idx]} got',
            frame_color,
            f'expected: [.., {expected_green}, {expected_red}]',
        )
        assert is_almost_same_color(frame_color[2], expected_red), (
            f'{frame_color[2]} != {expected_red} (fps: {fps}, Frame_idx {frame_idx}, Frame {frame_color}, color: red)'
        )
        assert is_almost_same_color(frame_color[1], expected_green), (
            f'{frame_color[1]} != {expected_green} (fps: {fps}, Frame_idx {frame_idx}, Frame {frame_color}, color: green)'
        )
        frame_idx += 1


@pytest.mark.parametrize('encoder', ['libx264', 'libx265'])
class TestPyAvReader:
    """Tests for `pyab_reader` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    @pytest.mark.parametrize(
        'layout, fps, expected_frames',
        [
            ('ffmphisdp', 25, [i for i in range(50)]),
            (
                'ffmphisdp',
                13.3,
                [0, 2, 4, 6, 8, 10, 12, 14, 15, 17, 19, 21, 23, 25, 27, 29, 31, 32, 34, 36, 38, 40, 42, 44, 46, 47, 49],
            ),
            ('ffmphisdp', 10, [1, 3, 6, 8, 11, 13, 16, 18, 21, 23, 26, 28, 31, 33, 36, 38, 41, 43, 46, 48]),
            ('ffmphisdp', 5, [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]),
            ('legacy', 25, [i for i in range(50)]),
            ('legacy', 10, [0, 1, 2, 4, 7, 9, 12, 14, 17, 19, 22, 24, 27, 29, 32, 34, 37, 39, 42, 44, 47, 49]),
        ],
    )
    def test_video_reader_CFR(self, encoder, layout, fps, expected_frames):
        """Test the video reader with a CFR video"""
        # Create the video file
        red_shift = 11
        green_shift = 17
        filename = 'test_CFR.mp4'
        create_video([(filename, 25, 50)], filename, red_shift=red_shift, green_shift=green_shift, encoder=encoder)

        fps_conversion_test_case(
            self,
            filename,
            fps,
            expected_frames,
            red_shift,
            green_shift,
            decoder=decode_all_frames if layout == 'ffmphisdp' else decode_legacy,
        )

        # Cleanup
        os.remove(filename)

    @pytest.mark.parametrize(
        'fps, expected_frames',
        [
            (25, [i for i in range(25)] + [25 + i * 2 for i in range(25)]),
            (10, [1, 3, 6, 8, 11, 13, 16, 18, 21, 23, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72]),
            (5, [2, 7, 12, 17, 22, 29, 39, 49, 59, 69]),
        ],
    )
    def test_video_reader_VFR(self, encoder, fps, expected_frames):
        """Test the video reader with a VFR video"""
        # Create the video file
        red_shift = 11
        green_shift = 17
        filename = 'test_VFR.mp4'
        create_video(
            [('test_VFR.1.mp4', 25, 25), ('test_VFR.2.mp4', 50, 50)],
            filename,
            red_shift=red_shift,
            green_shift=green_shift,
            encoder=encoder,
        )

        fps_conversion_test_case(self, filename, fps, expected_frames, red_shift, green_shift)

        # Cleanup
        os.remove('test_VFR.1.mp4')
        os.remove('test_VFR.2.mp4')
        os.remove(filename)

    def test_video_reader_start_frame(self, encoder):
        """Test setting the frame index for the video reader with a CFR video"""
        # Create the video file
        red_shift = 11
        green_shift = 17
        filename = 'test_set_frame_idx.mp4'
        create_video([(filename, 25, 50)], filename, red_shift=red_shift, green_shift=green_shift, encoder=encoder)

        # Test ControlledFPSVideoCapture at various fps
        fps_test_cases = {
            10: [
                (0, [1, 3, 6, 8, 11, 13, 16, 18, 21]),
                (1, [1, 3, 6, 8, 11, 13, 16, 18, 21]),
                (2, [3, 6, 8, 11, 13, 16, 18, 21, 23]),
                (3, [3, 6, 8, 11, 13, 16, 18, 21, 23]),
                (4, [6, 8, 11, 13, 16, 18, 21, 23, 26]),
                (7, [8, 11, 13, 16, 18, 21, 23, 26, 28]),
                (11, [11, 13, 16, 18, 21, 23, 26, 28, 31]),
                (12, [13, 16, 18, 21, 23, 26, 28, 31, 33]),
                (16, [16, 18, 21, 23, 26, 28, 31, 33, 36]),
                (17, [18, 21, 23, 26, 28, 31, 33, 36, 38]),
            ],
            25: [
                (0, [0, 1, 2, 3, 4, 5]),
                (1, [1, 2, 3, 4, 5, 6]),
                (2, [2, 3, 4, 5, 6, 7]),
                (3, [3, 4, 5, 6, 7, 8]),
            ],
            5: [
                (0, [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]),
                (1, [2, 7, 12, 17, 22, 27, 32, 37, 42, 47]),
                (3, [7, 12, 17, 22, 27, 32, 37, 42, 47]),
                (17, [17, 22, 27, 32, 37, 42, 47]),
                (19, [22, 27, 32, 37, 42, 47]),
                (25, [27, 32, 37, 42, 47]),
            ],
        }
        for fps, test_cases in fps_test_cases.items():
            all_frames = decode_all_frames(filename, framerate=fps, use_gpu=False)
            frame_infos = list(all_frames.keys())
            frame_selection = list(all_frames.values())
            video_reader = ControlledVideoReader(
                filename,
                frame_infos=frame_infos,
                frame_selection=frame_selection,
            )
            for frame_idx, expected_frames in test_cases:
                video_reader.set_frame_idx(frame_idx)
                for expected_frame in expected_frames:
                    ret, frame = video_reader.read()
                    assert ret, 'reading error'
                    frame_color = frame[0, 0]
                    expected_red, expected_green, _ = expected_frame_color(expected_frame, red_shift, green_shift)
                    print(
                        f'start idx: {frame_idx}, expected: {expected_frame} got',
                        frame_color,
                        f'expected: [.., {expected_green}, {expected_red}]',
                    )
                    assert is_almost_same_color(frame_color[2], expected_red), (
                        f'{frame_color[2]} != {expected_red} (fps= {fps}, Frame_idx {frame_idx}, Expected_frame: {expected_frame}, Frame {frame_color}, color: red)'
                    )
                    assert is_almost_same_color(frame_color[1], expected_green), (
                        f'{frame_color[1]} != {expected_green} (fps= {fps}, Frame_idx {frame_idx}, Expected_frame: {expected_frame}, Frame {frame_color}, color: green)'
                    )

        # Cleanup
        os.remove(filename)
