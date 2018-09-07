import os
from collections import defaultdict

from lxml import html

MESSAGES = "messages"
CORPUS = "corpus"


def pquit():
    print("Exiting..")
    quit()


files = []
for _, _, filename in os.walk(MESSAGES):
    files.extend(filename)


if len(files) > 1:
    print(f"Error: More than 1 file in '{MESSAGES}' folder!")
    pquit()
elif len(files) < 1:
    print(f"Error: Put your DM file in the '{MESSAGES}' folder!")
    pquit()

with open(os.path.join(MESSAGES, files[0])) as first_file:
    contents = first_file.read()

tree = html.fromstring(contents)
chatlogs = tree.xpath("//div[@class='chatlog__messages']")

# Isolate Message Authors
authors = []
for chatlog in chatlogs:
    author = chatlog.xpath(".//span[@class='chatlog__author-name']/text()")[0]
    if author not in authors:
        authors.append(author)

# Quit if no authors detected
if len(authors) > 2:
    print("|--- Group Chat/Server Detected ---|")
    wanted_authors = list(input("Enter Username (part before '#'): "))
elif len(authors) <= 2:
    print("|--- Direct Message Detected ---|")
    print("Choose option:")
    print(f"[1] {authors[0]}")
    print(f"[2] {authors[1]}")
    print(f"[3] Extract Both")
    wanted_authors = input("Enter Option # (any other key to quit): ")
    if wanted_authors == "1":
        wanted_authors = [authors[0]]
    elif wanted_authors == "2":
        wanted_authors = [authors[1]]
    elif wanted_authors == "3":
        wanted_authors = authors
    else:
        pquit()
else:
    print("Error: No authors detected.")
    pquit()

# Initialize Aggregate Messages
aggregate_messages = defaultdict(list)
for wanted_author in wanted_authors:
    aggregate_messages[wanted_author] = []

# Collect Messages
for wanted_author in wanted_authors:
    for chatlog in chatlogs:
        match_author = \
            chatlog.xpath(".//span[@class='chatlog__author-name']/text()")[0]
        if match_author == wanted_author:
            messages = \
                chatlog.xpath(".//div[@class='chatlog__content']/text()")
            aggregate_messages[wanted_author].extend(messages)

# Save Messages
if len(os.listdir(CORPUS)) > 0:
    print(f"Error: Corpus folder '{CORPUS}' is not empty!")
    pquit()

for author, messages in aggregate_messages.items():
    with open(os.path.join(CORPUS, f"{author}.txt"), "w") as corpus:
        for message in messages:
            corpus.write(f"{message.strip()}\n")
