test:
	python -m unittest tests/test.py

test_image_no_caption:
	python -m unittest tests.test.TestConversion.test_image_no_caption

test_image_caption:
	python -m unittest tests.test.TestConversion.test_image_caption

test_video_no_caption:
	python -m unittest tests.test.TestConversion.test_video_no_caption

test_video_caption:
	python -m unittest tests.test.TestConversion.test_video_caption
