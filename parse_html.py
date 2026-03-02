from bs4 import BeautifulSoup

with open("stitch_admin.html", "r") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

main_content = soup.find("main")
if main_content:
    print(main_content.prettify()[:1000])
