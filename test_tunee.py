"""
pytest file that tests the helper functions for Tunee
"""

import os
import pytest
import tunee

TEST_AUDIO_DIR = 'test_audio/'
TEST_AUDIO_LENGTHS = {
	'mbf.wav': 1,
	'context.wav': 12
}

TEST_URLS = [{'string': "https://www.youtube.com/watch?v=n5YHJMdN9FE", 'expected': True},
	{'string': "teddy bear squeeze sound", 'expected': False},
	{'string': "beans beans beans", 'expected': False},
	{'string': "https://www.youtube.com/watch?v=XBtALgPwTfo", 'expected': True}
]

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

@pytest.mark.parametrize('yt_video', TEST_URLS)
def test_dl_video(yt_video):
	"""
	Test the dl_video function by running through a list of YouTube videos
	and check that the function is properly returning the file name and that
	the file exists.
	"""
	video_data = tunee.dl_video(yt_video['string'])
	video_filepath = video_data['file_location']
	assert os.path.isfile(video_filepath)
	os.remove(video_filepath) # Clean up downloaded file after test passes

@pytest.mark.parametrize('check_string', TEST_URLS)
def test_is_url(check_string):
	"""
	Checks that the is_url function is properly returning whether the provided
	string is a URL or a search text.
	"""
	assert tunee.is_url(check_string['string']) is check_string['expected']
