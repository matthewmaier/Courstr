2024-02-19
At the moment the vtt files are adjusted and combined incorrectly
The ending and beginning microseconds can overlap
The "WEBVTT" tag isn't removed from files 2, 3, etc
example:
00:14:29.760 --> 00:14:33.919
the last words in the previous file.WEBVTT

00:14:33.768 --> 00:14:36.408
the first words in the next file,