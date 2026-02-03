import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.glbitm.org"

# Pages that usually contain useful info
TARGET_PATHS = [
    "/about",
    "/about-us",
    "/leadership",
    "/management",
    "/director",
    "/administration",

    # Academics
    "/department",
    "/departments",
    "/faculty",
    "/academics",
    "/hod",

    # Admissions
    "/admission",
    "/admissions",
    "/apply",
    "/fees",
    "/eligibility",

    # Placements
    "/placement",
    "/placements",
    "/training-and-placement",
    "/tpo",
]


# Keywords to KEEP
KEYWORDS = [
    # Leadership
    "ceo",
    "director",
    "chairman",
    "vice chairman",

    "dean",
    "training and placement",
    "t&p",
    "tpo",

    # Academics
    "department",
    "hod",
    "head of department",
    "faculty",

    # Admissions
    "admission",
    "eligibility",
    "fee",
    "fees",
    "apply",
    "entrance",
    "counselling",

    # Placements
    "placement",
    "placements",
    "highest package",
    "average package",
    "ctc",
    "salary",
    "recruiter",
    "company",
    "student",
]


visited = set()
collected_text = []

def is_relevant(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in KEYWORDS)

def scrape(url):
    if url in visited:
        return
    visited.add(url)

    print("Scraping:", url)

    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # Remove scripts, styles, nav, footer
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        page_text = soup.get_text(separator=" ", strip=True)

        if is_relevant(page_text):
            collected_text.append(page_text)

        # Follow only relevant internal links
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()

            if any(path in href for path in TARGET_PATHS):
                next_url = urljoin(BASE_URL, href)
                scrape(next_url)

    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    scrape(BASE_URL)

    with open("raw_text.txt", "w", encoding="utf-8") as f:
        for text in collected_text:
            f.write(text + "\n\n")

    print("✅ Relevant scraping completed.")

