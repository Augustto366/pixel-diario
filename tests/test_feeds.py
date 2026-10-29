import unittest
from datetime import timezone

from pixel_diario.feeds import data, ler_feed, limpar


class FeedTests(unittest.TestCase):
    def test_reads_rss_item_and_normalizes_content(self):
        feed = b"""<?xml version="1.0"?>
        <rss><channel><item>
          <title>New &amp; notable</title>
          <link>https://example.com/story</link>
          <pubDate>Wed, 28 Oct 2026 12:00:00 GMT</pubDate>
          <description><![CDATA[<p>A &amp; B update</p>]]></description>
        </item></channel></rss>"""

        items = ler_feed(feed, "Example", 1.1)

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["titulo"], "New & notable")
        self.assertEqual(items[0]["resumo"], "A & B update")
        self.assertEqual(items[0]["fonte"], "Example")
        self.assertEqual(items[0]["data"].tzinfo, timezone.utc)

    def test_reads_atom_link_and_iso_date(self):
        feed = b"""<feed xmlns="http://www.w3.org/2005/Atom">
          <entry><title>Atom story</title>
            <link href="https://example.com/atom"/>
            <updated>2026-10-28T12:00:00Z</updated>
          </entry>
        </feed>"""

        items = ler_feed(feed, "Atom", 1)

        self.assertEqual(items[0]["link"], "https://example.com/atom")
        self.assertEqual(items[0]["titulo"], "Atom story")

    def test_invalid_date_is_ignored(self):
        self.assertIsNone(data("not a date"))

    def test_cleaning_truncates_at_word_boundary(self):
        self.assertEqual(limpar("<p>alpha beta gamma</p>", 12), "alpha beta…")


if __name__ == "__main__":
    unittest.main()
