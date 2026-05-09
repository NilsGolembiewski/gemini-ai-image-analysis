import unittest

from ai_image_cli.prompts import build_analyze_prompt, build_mobile_prompt, build_webpage_prompt


class PromptTests(unittest.TestCase):
    def test_analyze_prompt_defaults(self):
        prompt = build_analyze_prompt(None)
        self.assertIn("Analyze this image", prompt)

    def test_webpage_prompt_includes_focus_and_accessibility(self):
        prompt = build_webpage_prompt(focus="accessibility", include_accessibility=True, user_prompt="Check form clarity")
        self.assertIn("accessibility", prompt)
        self.assertIn("Check form clarity", prompt)

    def test_mobile_prompt_includes_platform(self):
        prompt = build_mobile_prompt(platform="ios", focus="navigation", include_ux_heuristics=True, user_prompt=None)
        self.assertIn("ios", prompt)
        self.assertIn("navigation", prompt)
