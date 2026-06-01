import unittest

from subtitle_lab import parse_subtitles, render_srt, render_vtt, shift_cues, validate_cues


class SubtitleLabTests(unittest.TestCase):
    def test_parse_and_clean_srt(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:02,000
  Hello,   world!
"""
        )

        self.assertEqual(len(cues), 1)
        self.assertEqual(cues[0].lines, ["Hello, world!"])

    def test_shift_clamps_at_zero(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:02,000
Hello
"""
        )

        shifted = shift_cues(cues, -1500)

        self.assertEqual(shifted[0].start_ms, 0)
        self.assertEqual(shifted[0].end_ms, 500)

    def test_render_vtt(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:02,250
Hello
"""
        )

        self.assertIn("WEBVTT", render_vtt(cues))
        self.assertIn("00:00:01.000 --> 00:00:02.250", render_vtt(cues))

    def test_round_trip_srt(self):
        cues = parse_subtitles(
            """
2
00:00:03,000 --> 00:00:04,000
Second cue
"""
        )

        self.assertEqual(
            render_srt(cues),
            "1\n00:00:03,000 --> 00:00:04,000\nSecond cue\n",
        )

    def test_validate_detects_overlap(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:03,000
First

2
00:00:02,500 --> 00:00:04,000
Second
"""
        )

        self.assertEqual(validate_cues(cues), ["Cue 2: overlaps with the previous cue."])

    def test_validate_accepts_good_file(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:02,000
First

2
00:00:02,500 --> 00:00:04,000
Second
"""
        )

        self.assertEqual(validate_cues(cues), [])


if __name__ == "__main__":
    unittest.main()
