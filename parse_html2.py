from bs4 import BeautifulSoup
import re

with open("stitch_admin.html", "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

main_content = soup.find("main")
if main_content:
    content_html = str(main_content)
    # Extract just the cards section and recent activity area
    sections = soup.find_all("section")
    for section in sections:
        print("SECTION")
        print(str(section)[:300])
