import requests
import hashlib
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.glbitm.org"

TARGET_PATHS = [
    "/about", "/about-us", "/leadership", "/management", "/director",
    "/department", "/departments", "/faculty", "/academics", "/hod",
    "/admission", "/admissions", "/fees", "/eligibility",
    "/placement", "/placements", "/training-and-placement", "/tpo",
]

KEYWORDS = [
    "ceo", "director", "chairman", "vice chairman", "dean",
    "training and placement", "tpo",
    "department", "hod", "faculty",
    "admission", "eligibility", "fee", "fees",
    "placement", "highest package", "average package",
    "ctc", "salary", "recruiter"
]

visited_urls = set()
seen_hashes = set()
collected_text = []


def is_relevant(text: str) -> bool:
    text = text.lower()
    return any(k in text for k in KEYWORDS)


def is_unique(text: str) -> bool:
    h = hashlib.md5(text.encode("utf-8")).hexdigest()
    if h in seen_hashes:
        return False
    seen_hashes.add(h)
    return True


def extract_main_content(soup):
    """
    Extract only meaningful content, not menus or footers
    """
    for tag in ["main", "article"]:
        content = soup.find(tag)
        if content:
            return content.get_text(" ", strip=True)

    # Fallback: important content divs
    for div in soup.find_all("div"):
        classes = " ".join(div.get("class", [])).lower()
        if any(k in classes for k in ["content", "about", "department", "placement"]):
            text = div.get_text(" ", strip=True)
            if len(text) > 300:
                return text

    return ""


def scrape(url):
    if url in visited_urls:
        return

    visited_urls.add(url)
    print("Scraping:", url)

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove useless elements
        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        page_text = extract_main_content(soup)

        if page_text and is_relevant(page_text) and is_unique(page_text):
            collected_text.append(page_text)

        # Follow only important links
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(path in href for path in TARGET_PATHS):
                next_url = urljoin(BASE_URL, href)
                scrape(next_url)

    except Exception as e:
        print("Error:", e)


if __name__ == "__main__":
    scrape(BASE_URL)

    with open("clean_text.txt", "w", encoding="utf-8") as f:
        for text in collected_text:
            f.write(text + "\n\n")

    print("✅ Clean & deduplicated scraping completed")
