"""Offline tests: no network, no credentials. Run: python -m unittest tools/growth/test_growth_report.py"""
import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import growth_report as gr  # noqa: E402


def window(clicks, impressions, position, views, landing, events, rec_types=None):
    return {
        "gsc": [{"page": "/blog/weak/", "clicks": clicks, "impressions": impressions, "position": position},
                {"page": "/blog/other/", "clicks": 5, "impressions": 500, "position": 20.0}],
        "views": [{"pagePath": "/blog/weak/", "screenPageViews": views},
                  {"pagePath": "/blog/tunisian-daily-3/", "screenPageViews": 100.0}],
        "landing": [{"landingPage": "/blog/weak/", "sessions": landing[0], "engagedSessions": landing[1],
                     "screenPageViews": landing[2]}],
        "events": [{"eventName": k, "eventCount": v} for k, v in events.items()],
        "rec_types": rec_types,
        "notes": [],
    }


class Windows(unittest.TestCase):
    def test_four_weeks(self):
        pre, post = gr.windows(dt.date(2026, 10, 31))
        self.assertEqual(post, (dt.date(2026, 10, 1), dt.date(2026, 10, 28)))
        self.assertEqual(pre, (dt.date(2026, 9, 3), dt.date(2026, 9, 30)))

    def test_capped(self):
        pre, post = gr.windows(dt.date(2027, 3, 1), max_days=56)
        self.assertEqual((post[1] - post[0]).days + 1, 56)
        self.assertEqual(pre[1], dt.date(2026, 9, 30))

    def test_too_early(self):
        with self.assertRaises(SystemExit):
            gr.windows(dt.date(2026, 10, 2))


class Dialects(unittest.TestCase):
    def test_real_content(self):
        d = gr.page_dialects()
        self.assertEqual(d["/blog/weak/"], "shami")            # shami + tunisian counts as shami
        self.assertEqual(d["/blog/tunisian-daily-3/"], "tunisian")
        self.assertEqual(d["/blog/morning-after-yom-kippur/"], "shami")  # slug: override
        self.assertNotIn("/blog/post-yom-kippur/", d)


class Report(unittest.TestCase):
    def test_render(self):
        dialects = gr.page_dialects()
        pre = gr.summarize(window(1, 101, 9.1, 300.0, (50, 20, 60),
                                  {"followit_subscribe": 3, "audio_play": 40}), dialects)
        post = gr.summarize(window(6, 120, 8.8, 400.0, (80, 44, 120),
                                   {"followit_subscribe": 8, "recommendation_click": 25, "audio_play": 50},
                                   [{"customEvent:rec_type": "context", "eventCount": 15},
                                    {"customEvent:rec_type": "related", "eventCount": 10}]), dialects)
        md = gr.render(pre, post, *gr.windows(dt.date(2026, 10, 31)), dt.date(2026, 10, 31))
        self.assertIn("28 days after", md)
        self.assertIn("| `/blog/weak/` | 101 → 120 | 1 → 6 | 1.0% → 5.0% | 9.1 → 8.8 | CTR +4.0 pts |", md)
        self.assertIn("⚠ <100 impr.", md)                       # enough/bisaraha have no data here
        self.assertIn("| Engagement rate | 40.0% | 55.0% | +15.0 pts |", md)
        self.assertIn("| Pages per session | 1.20 | 1.50 | +25% |", md)
        self.assertIn("**25** clicks", md)
        self.assertIn("context 15, related 10", md)
        self.assertIn("| Tunisian archive | 25.0% | 20.0% |", md)

    def test_position_confound_flagged(self):
        d = gr.page_dialects()
        pre = gr.summarize(window(1, 200, 12.0, 1.0, (1, 1, 1), {}), d)
        post = gr.summarize(window(9, 200, 6.0, 1.0, (1, 1, 1), {}), d)
        md = gr.render(pre, post, *gr.windows(dt.date(2026, 10, 31)), dt.date(2026, 10, 31))
        self.assertIn("ranking moved", md)


if __name__ == "__main__":
    unittest.main()
