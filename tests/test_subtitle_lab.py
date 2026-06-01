import tempfile
import unittest
from pathlib import Path

from subtitle_lab import (
    batch_convert,
    parse_subtitles,
    repair_cues,
    render_srt,
    render_vtt,
    shift_cues,
    summarize_cues,
    validate_cues,
)


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

    def test_repair_fixes_overlap_and_invalid_duration(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:03,000
First

2
00:00:02,500 --> 00:00:02,500
Second
"""
        )

        repaired = repair_cues(cues, min_gap_ms=100, min_duration_ms=750)

        self.assertEqual(repaired[1].start_ms, 3100)
        self.assertEqual(repaired[1].end_ms, 3850)
        self.assertEqual(validate_cues(repaired), [])

    def test_batch_convert_preserves_nested_directories(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            input_dir = root / "input"
            output_dir = root / "output"
            nested = input_dir / "season-1"
            nested.mkdir(parents=True)
            (nested / "episode-1.srt").write_text(
                "1\n00:00:01,000 --> 00:00:02,000\nHello\n",
                encoding="utf-8",
            )
            (nested / "notes.txt").write_text("not a subtitle", encoding="utf-8")

            converted = batch_convert(input_dir, output_dir, "vtt", recursive=True)

            self.assertEqual(converted, 1)
            output = output_dir / "season-1" / "episode-1.vtt"
            self.assertTrue(output.exists())
            self.assertIn("WEBVTT", output.read_text(encoding="utf-8"))

    def test_summarize_cues(self):
        cues = parse_subtitles(
            """
1
00:00:01,000 --> 00:00:02,000
First

2
00:00:03,000 --> 00:00:05,500
Second
"""
        )

        self.assertEqual(
            summarize_cues(cues, "srt"),
            {
                "format": "srt",
                "cue_count": 2,
                "start": "00:00:01.000",
                "end": "00:00:05.500",
                "duration_ms": 4500,
            },
        )


if __name__ == "__main__":
    unittest.main()
