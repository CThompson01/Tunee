"""
pytest file that tests the helper functions for Tunee
"""

import os
import pytest
import tunee

TEST_AUDIO_DIR = 'test_audio/'
TEST_AUDIO_LENGTHS = {
	"mbf.wav": 1,
	"context.wav": 12
}

@pytest.mark.parametrize("audio_file", os.listdir(TEST_AUDIO_DIR))
def test_get_length(audio_file):
	"""
	Test the get_length function with all audio stored in TEST_AUDIO_DIR
	When adding new test audios, make sure to update TEST_AUDIO_LENGTHS
	as that is the dictionary used for the expected values
	"""
	length = tunee.get_length(f'{TEST_AUDIO_DIR}/{audio_file}')
	expected_length = TEST_AUDIO_LENGTHS[audio_file]
	assert expected_length <= length <= expected_length+1
