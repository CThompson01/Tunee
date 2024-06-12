import pytest
from tunee import *

TEST_AUDIO_DIR = 'test_audio/'
TEST_AUDIO_LENGTHS = {
	"mbf.wav": 1,
	"context.wav": 12
}

@pytest.mark.parametrize("audio_file", os.listdir(TEST_AUDIO_DIR))
def test_get_length(audio_file):
	length = get_length(f'{TEST_AUDIO_DIR}/{audio_file}')
	expected_length = TEST_AUDIO_LENGTHS[audio_file]
	assert length >= expected_length and length <= expected_length+1