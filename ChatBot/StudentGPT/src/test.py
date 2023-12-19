from ChatBot.StudentGPT.src.PDFProcessor import PDFProcessor
import json

pdf = PDFProcessor("test2.pdf")

content = pdf.process_pdf()

with open("test.json", "w") as f:
    json.dump(content, f)



# tests
import fitz

pdf = fitz.open("test2.pdf")

page = pdf[12]
print(page.get_text(sort=True))


blocks = page.get_text("blocks")
header = (0, 0, page.rect.width, page.rect.height * 0.05)
footer = (
    0,
    page.rect.height - page.rect.height * 0.05,
    page.rect.width,
    page.rect.height,
)


for page in pdf.pages():
    print(page)
    page.set_cropbox(
        fitz.Rect(
            0,
            page.rect.height * 0.05,
            page.rect.width,
            page.rect.height - page.rect.height * 0.05,
        )
    )


body_text = list()

for block in sorted(blocks):
    if block[:4][1] > footer[1] or block[:4][1] < header[1]:
        print("text in header or footer")
    else:
        body_text.append(block[4])

body_text = "".join(body_text)
print(body)


links = page.get_links()


links = [link["uri"] for link in links]
text = page.get_text(sort=True)

text.replace(links[0]["uri"], "")

splitted = text.split("\n")

for element in splitted:
    print(element)
    print()
    if element in links[0]["uri"]:
        print("Found link")
        break

print(text)

splitted_text = text.split("\n")

items_to_remove = list()

for link in links:
    print("link: ", link)
    for i in range(len(splitted_text) - 1):
        part = splitted_text[i]
        print(part)
        print()
        if part in link or part == link:
            print("Found link")
            items_to_remove.append(i)
            break

for i in sorted(items_to_remove, reverse=True):
    del splitted_text[i]

text = "\n".join(splitted_text)
