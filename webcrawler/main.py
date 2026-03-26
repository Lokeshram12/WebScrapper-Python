import sys
import asyncio
from core import AsyncCrawler
from json_report import write_json_report

async def main():
    if len(sys.argv) < 2:
        print("No website provided")
        sys.exit(1)

    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    max_pages = int(sys.argv[3]) if len(sys.argv) > 3 else 50

    print(f"Starting crawl of: {base_url}")
    print(f"Max concurrency: {max_concurrency}, Max pages: {max_pages}")

    async with AsyncCrawler(base_url, max_concurrency=max_concurrency, max_pages=max_pages) as crawler:
        page_data = await crawler.crawl()
        
        write_json_report(page_data)
        print("JSON report written to report.json")
    # print(f"\nTotal pages crawled: {len(page_data)}\n")
    # for page in page_data.values():
    #     print(f"URL: {page['url']}, Heading: {page['heading']}, Paragraph: {page['first_paragraph']}")
    #     print(f"Outgoing links: {page['outgoing_links']}")
    #     print(f"Images: {page['image_urls']}\n")


if __name__ == "__main__":
    asyncio.run(main())