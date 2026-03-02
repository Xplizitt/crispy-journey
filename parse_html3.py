from bs4 import BeautifulSoup
import re

with open("stitch_admin.html", "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

main_content = soup.find("main")
if main_content:
    divs = main_content.find_all("div", class_=re.compile("p-8.*"))
    for div in divs:
        print("CONTENT AREA")
        print(str(div)[:500])
