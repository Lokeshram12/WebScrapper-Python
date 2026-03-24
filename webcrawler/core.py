import requests
import asyncio
from urllib.parse import urlparse
import aiohttp
from crawl import normalize_url, extract_page_data

# ----------------------------
# Shared synchronous get_html
# ----------------------------
def get_html(url, session=None):
    """
    Fetch HTML. If session is None, use requests (sync). Otherwise, use aiohttp session (async).
    """
    if session is None:
        # Sync requests
        try:
            response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
            if response.status_code >= 400:
                raise Exception(f"HTTP error: {response.status_code}")

            content_type = response.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                raise Exception(f"Invalid content type: {content_type}")

            return response.text
        except requests.RequestException as e:
            raise Exception(f"Request failed: {e}")

    else:
        # Async aiohttp call
        async def fetch():
            try:
                async with session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
                    if response.status >= 400:
                        raise Exception(f"HTTP error: {response.status}")

                    content_type = response.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        raise Exception(f"Invalid content type: {content_type}")

                    return await response.text()
            except aiohttp.ClientError as e:
                raise Exception(f"Request failed: {e}")

        return fetch()


# ----------------------------
# Synchronous crawler
# ----------------------------
def crawl_page(base_url, current_url=None, page_data=None):
    if page_data is None:
        page_data = {}

    if current_url is None:
        current_url = base_url

    # Domain check
    base_domain = urlparse(base_url).netloc
    current_domain = urlparse(current_url).netloc
    if base_domain != current_domain:
        return page_data

    normalized = normalize_url(current_url)
    if normalized in page_data:
        return page_data

    try:
        print(f"Crawling: {current_url}")
        html = get_html(current_url)
        data = extract_page_data(html, current_url)
        page_data[normalized] = data

        for url in data["outgoing_links"]:
            crawl_page(base_url, url, page_data)

    except Exception as e:
        print(f"Error crawling {current_url}: {e}")

    return page_data


class AsyncCrawler:
    def __init__(self, base_url, max_concurrency=3, max_pages=50):
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.session = None

        # New fields for max_pages and stopping
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        """Return True if first time visiting, else False. Also handle max_pages limit."""
        async with self.lock:
            if self.should_stop:
                return False

            if normalized_url in self.page_data:
                return False

            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                # Cancel all running tasks
                for task in list(self.all_tasks):
                    task.cancel()
                return False

            return True

    async def get_html(self, url):
        """Async get_html using aiohttp"""
        return await get_html(url, session=self.session)

    async def crawl_page(self, current_url=None):
        if current_url is None:
            current_url = self.base_url

        if self.should_stop:
            return

        # Domain check
        if urlparse(current_url).netloc != self.base_domain:
            return

        normalized = normalize_url(current_url)
        first_time = await self.add_page_visit(normalized)
        if not first_time:
            return

        try:
            async with self.semaphore:
                print(f"Crawling: {current_url}")
                html = await self.get_html(current_url)

            data = extract_page_data(html, current_url)

            async with self.lock:
                self.page_data[normalized] = data

            # Schedule tasks for outgoing links
            tasks = []
            for url in data["outgoing_links"]:
                if self.should_stop:
                    break
                task = asyncio.create_task(self.crawl_page(url))
                self.all_tasks.add(task)
                # Remove task from all_tasks when done
                task.add_done_callback(lambda t: self.all_tasks.discard(t))
                tasks.append(task)

            if tasks:
                await asyncio.gather(*tasks)

        except asyncio.CancelledError:
            # Task was cancelled because max_pages was reached
            pass
        except Exception as e:
            print(f"Error crawling {current_url}: {e}")

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data