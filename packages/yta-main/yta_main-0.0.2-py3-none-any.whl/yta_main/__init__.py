"""
Youtube Autonomous Main Module.

The module in which you can test everything
you want about the YTA project. Good luck! :)
"""
from yta_video_editor.editor import VideoEditor
from yta_video_base.video import VideoExtended


def main(
):
    """
    To test the different YTA libraries.
    """
    print('Hello YTA! :)')
    TEST_FOLDER = 'test_files/'
    test_video_file_input = f'{TEST_FOLDER}test_1.mp4'
    test_video_file_output = f'{TEST_FOLDER}output.mp4'
    
    # video_editor = VideoEditor(test_video_file_input)
    # video_editor.contrast(100).zoom(200).save(test_video_file_output)

    video = VideoExtended(test_video_file_input)
    video.set_rotation(145)
    video.save(test_video_file_output)

if __name__ == '__main__':
    main()