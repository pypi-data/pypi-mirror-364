# ffmphisDP

This package takes care of reading a video stream one frame at a time from a local file or a url while converting it to a given framerate.

Features:
- Streaming all frames from a video url or a video file
- Jumping to another point of the stream at a given frame index or timestamp
- For a given video and a given framerate always returns the same frames

## How to use it

    from ffmphisdp.video_reader import ControlledFPSVideoCapture

    stream = ControlledFPSVideoCapture("myvideo.mp4", fps=10)

    while True:
        ret, frame = stream.read()
        if not ret:
            break # End of the stream
        <do something with the frame>

## Important Note

Previously reading video was handled by the skcvideo package, it's important to understand that ffmphisdp introduces a breaking change from skcvideo.

The frames returned by ffmphisdp and those returned by skcvideo are not the exact same, care should be taken when using legacy data to read videos using the correct reader.

Here is an example, for a given video at 25fps converted to 10fps:
- skcvideo would return the original video frame indexes: `0,1,2,4,7,9,12,14,17`
- ffmphisdp return the original video frame indexes: `1,3,6,8,11,13,16`
