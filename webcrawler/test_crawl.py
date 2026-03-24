import unittest
from crawl import normalize_url,get_heading_from_html,get_first_paragraph_from_html,get_images_from_html,get_urls_from_html,extract_page_data
class TestCrawl(unittest.TestCase):
    def test_normalize_url(self):
        input_url = "https://www.boot.dev/blog/path"
        actual = normalize_url(input_url)
        expected = "www.boot.dev/blog/path"
        self.assertEqual(actual, expected)

    def test_get_heading_from_html_basic(self):
        input_body = '<html><body><h1>Test Title</h1></body></html>'
        actual = get_heading_from_html(input_body)
        expected = "Test Title"
        self.assertEqual(actual, expected)

    def test_get_first_paragraph_from_html_main_priority(self):
        input_body = '''<html><body>
            <p>Outside paragraph.</p>
            <main>
                <p>Main paragraph.</p>
            </main>
        </body></html>'''
        actual = get_first_paragraph_from_html(input_body)
        expected = "Main paragraph."
        self.assertEqual(actual, expected)

    def test_get_urls_from_html_absolute(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><a href="https://crawler-test.com"><span>Boot.dev</span></a></body></html>'
        actual = get_urls_from_html(input_body, input_url)
        expected = ["https://crawler-test.com"]
        self.assertEqual(actual, expected)

    def test_get_images_from_html_relative(self):
        input_url = "https://crawler-test.com"
        input_body = '<html><body><img src="/logo.png" alt="Logo"></body></html>'
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://crawler-test.com/logo.png"]
        self.assertEqual(actual, expected)

    def test_get_images_missing_src(self):
        input_url = "https://example.com"
        input_body = '<html><body><img alt="no source"></body></html>'
        
        actual = get_images_from_html(input_body, input_url)
        expected = []
        
        self.assertEqual(actual, expected)
    
    def test_get_images_relative_no_slash(self):
        input_url = "https://example.com/blog/"
        input_body = '<html><body><img src="images/pic.png"></body></html>'
        
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://example.com/blog/images/pic.png"]
        
        self.assertEqual(actual, expected)

    def test_get_images_protocol_relative(self):
        input_url = "https://example.com"
        input_body = '<html><body><img src="//cdn.example.com/img.png"></body></html>'
        
        actual = get_images_from_html(input_body, input_url)
        expected = ["https://cdn.example.com/img.png"]
        
        self.assertEqual(actual, expected)

    def test_get_images_mixed_urls(self):
        input_url = "https://example.com"
        input_body = '''
        <html><body>
            <img src="/logo.png">
            <img src="https://cdn.example.com/banner.jpg">
        </body></html>
        '''
        
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://example.com/logo.png",
            "https://cdn.example.com/banner.jpg"
        ]
        
        self.assertEqual(actual, expected)

    def test_get_images_multiple(self):
        input_url = "https://example.com"
        input_body = '<html><body><img src="/a.png"><img src="/b.png"></body></html>'
        
        actual = get_images_from_html(input_body, input_url)
        expected = [
            "https://example.com/a.png",
            "https://example.com/b.png"
        ]
        
        self.assertEqual(actual, expected)
    
    def test_extract_page_data_basic(self):
        input_url = "https://crawler-test.com"
        input_body = '''<html><body>
            <h1>Test Title</h1>
            <p>This is the first paragraph.</p>
            <a href="/link1">Link 1</a>
            <img src="/image1.jpg" alt="Image 1">
        </body></html>'''
        actual = extract_page_data(input_body, input_url)
        expected = {
            "url": "https://crawler-test.com",
            "heading": "Test Title",
            "first_paragraph": "This is the first paragraph.",
            "outgoing_links": ["https://crawler-test.com/link1"],
            "image_urls": ["https://crawler-test.com/image1.jpg"]
        }
        self.assertEqual(actual, expected)

    def test_extract_page_data_no_heading(self):
        html = '''
        <html>
            <body>
                <p>Only paragraph here.</p>
            </body>
        </html>
        '''
        url = "https://example.com"

        result = extract_page_data(html, url)

        expected = {
            "url": url,
            "heading": None,
            "first_paragraph": "Only paragraph here.",
            "outgoing_links": [],
            "image_urls": []
        }

        self.assertEqual(result, expected)

    def test_extract_page_data_h2_fallback(self):
        html = '''
        <html>
            <body>
                <h2>Sub Heading</h2>
                <p>Paragraph text.</p>
            </body>
        </html>
        '''
        url = "https://example.com"

        result = extract_page_data(html, url)

        expected = {
            "url": url,
            "heading": "Sub Heading",
            "first_paragraph": "Paragraph text.",
            "outgoing_links": [],
            "image_urls": []
        }

        self.assertEqual(result, expected)

    def test_extract_page_data_main_paragraph(self):
        html = '''
        <html>
            <body>
                <h1>Title</h1>
                <main>
                    <p>Main paragraph.</p>
                </main>
                <p>Secondary paragraph.</p>
            </body>
        </html>
        '''
        url = "https://example.com"

        result = extract_page_data(html, url)

        expected = {
            "url": url,
            "heading": "Title",
            "first_paragraph": "Main paragraph.",
            "outgoing_links": [],
            "image_urls": []
        }

        self.assertEqual(result, expected)

    def test_extract_page_data_links_and_images(self):
        html = '''
        <html>
            <body>
                <h1>Page</h1>
                <p>Content here.</p>
                <a href="/about">About</a>
                <a href="https://external.com">External</a>
                <img src="/img1.png"/>
                <img src="https://cdn.com/img2.png"/>
            </body>
        </html>
        '''
        url = "https://example.com"

        result = extract_page_data(html, url)

        expected = {
            "url": url,
            "heading": "Page",
            "first_paragraph": "Content here.",
            "outgoing_links": [
                "https://example.com/about",
                "https://external.com"
            ],
            "image_urls": [
                "https://example.com/img1.png",
                "https://cdn.com/img2.png"
            ]
        }

        self.assertEqual(result, expected)


    def test_extract_page_data_no_paragraph(self):
        html = '''
        <html>
            <body>
                <h1>Title Only</h1>
                <a href="/link">Link</a>
            </body>
        </html>
        '''
        url = "https://example.com"

        result = extract_page_data(html, url)

        expected = {
            "url": url,
            "heading": "Title Only",
            "first_paragraph": "",
            "outgoing_links": ["https://example.com/link"],
            "image_urls": []
        }

        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()