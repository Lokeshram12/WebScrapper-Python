import json


def write_json_report(page_data, filename="report.json"):
    # Convert dictionary values to a sorted list by URL
    pages = sorted(page_data.values(), key=lambda p: p["url"])

    # Write to JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)