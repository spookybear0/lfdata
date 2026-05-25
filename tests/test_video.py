from datetime import datetime
from lfdata.model import LFGame
from lfdata.video import VideoGenerator


def test_video_generator_generate(tmp_path) -> None:
    game = LFGame(
        game_id='video_test_game',
        timestamp=datetime.now(),
        game_type='Test Game',
    )

    generator = VideoGenerator(game)
    output_file = tmp_path / 'output.mp4'

    generated_path = generator.generate(output_file)
    assert generated_path.exists()
    assert generated_path == output_file
