"""Offline checks: a click is not platform acceptance; never contact a browser."""
import argparse
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from contextlib import redirect_stdout
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
# CDP transport is irrelevant here and must not connect to a real browser.
transport = types.ModuleType("xhs.cdp")
transport.Page = Mock
with patch.dict(sys.modules, {"xhs.cdp": transport}):
    from xhs import publish, publish_video
spec = importlib.util.spec_from_file_location("xhs_cli_test", SCRIPTS / "cli.py")
cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli)


class SubmissionEvidenceTests(unittest.TestCase):
    def test_single_click_is_reported_as_unknown(self):
        browser, page = Mock(), Mock()
        page.evaluate.return_value = True
        output = io.StringIO()
        with patch.object(cli, "_connect_existing", return_value=(browser, page)), \
             patch.object(publish.time, "sleep"), redirect_stdout(output), \
             self.assertRaises(SystemExit) as result:
            cli.cmd_click_publish(argparse.Namespace())
        self.assertEqual(result.exception.code, 0)
        self.assertEqual(json.loads(output.getvalue())["submission_state"],
                         "submission_unknown")
        page.evaluate.assert_called_once()
        browser.close.assert_called_once()

    def test_click_exception_does_not_retry_or_emit_success(self):
        browser, page = Mock(), Mock()
        page.evaluate.side_effect = TimeoutError("unknown click result")
        output = io.StringIO()
        with patch.object(cli, "_connect_existing", return_value=(browser, page)), \
             redirect_stdout(output), self.assertRaises(TimeoutError):
            cli.cmd_click_publish(argparse.Namespace())
        page.evaluate.assert_called_once()
        self.assertEqual(output.getvalue(), "")
        browser.close.assert_called_once()

    def test_missing_button_is_failure(self):
        page = Mock()
        page.evaluate.return_value = False
        with self.assertRaises(publish.PublishError):
            publish.click_publish_button(page)
        page.evaluate.assert_called_once()

    def test_video_click_timeout_is_not_retried(self):
        page = Mock()
        page.click_element.side_effect = TimeoutError("unknown click result")
        with patch.object(publish_video, "_wait_for_publish_button_clickable"), \
             self.assertRaises(TimeoutError):
            publish_video.click_publish_video_button(page)
        page.click_element.assert_called_once()

    def test_documented_fill_video_arguments_exist(self):
        args = cli.build_parser().parse_args([
            "fill-publish-video", "--title-file", "title.txt",
            "--content-file", "content.txt", "--video", "video.mp4",
            "--tags", "话题一", "话题二"])
        self.assertEqual(args.command, "fill-publish-video")
        self.assertEqual(args.tags, ["话题一", "话题二"])


if __name__ == "__main__":
    unittest.main()
