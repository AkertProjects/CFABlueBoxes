#! Python
# Goes to bookshelf and downloads blue box questions from the CFA textbooks

import requests, json, re, os
from bs4 import BeautifulSoup

username = input('Please type in your E-mail: ')
password = input('Please type in your password: ')

# Provide username and password
payload = {
    'user[email]': username,
    'user[password]': password
}

# Specifying year and level of books
Year = input('What year of books do you want?: ')
Level = input('What Level? (I,II,III): ')

# Creating a folder for the documents
startingLocation = os.path.abspath(os.curdir)
location = startingLocation + '\CFABlueBoxes'
if not os.path.exists(location):
    os.makedirs(location)
os.chdir(location)

# Logging in and keeping a session open
with requests.Session() as s:
    p = s.post('https://jigsaw.vitalsource.com/login', params=payload)
    Library = p.text
    parsed_Library = json.loads(Library)['books']
    my_regex = re.compile(str(Year) + r'\sCFA\sLevel\s' + Level + r'\s')
    isbnList = []
    # grabbing all the books to read
    for book in parsed_Library:
        title = book['title']
        isbn = book['isbn']
        if my_regex.search(title):
            isbnList.append({'title':title, 'isbn':int(isbn)})
    # Going to each book's table of contents first
    for book in isbnList:
        bookUrl = 'https://jigsaw.vitalsource.com/books/' + str(book['isbn']) + '/cfi/6/8!'
        tableOfContents = s.get(bookUrl).text
        soup = BeautifulSoup(tableOfContents, "html.parser")
        tags = soup.findAll('li')
        newLocation = startingLocation + '\CFABlueBoxes' + r'\ ' + book['title']
        if not os.path.exists(newLocation):
            os.makedirs(newLocation)
        os.chdir(newLocation)
        # Grabbing the links to all of the readings
        for tag in tags:
            links = tag.findAll('a')
            for link in links:
                readingRegex = re.compile(r'Reading\s{1,10}\d{1,3}')
                text = link.text
                if readingRegex.search(text):
                    newLink = link['href']
                    newURL = 'https://jigsaw.vitalsource.com/books/' + str(book['isbn']) + '/epub/OEBPS/' + str(newLink)
                    reading = s.get(newURL).text
                    soupReading = BeautifulSoup(reading, "html.parser")
                    for span_tag in soupReading.findAll('span'):
                        span_tag.replace_with('')
                    title = soupReading.find('title').text
                    title = " ".join(re.findall("[a-zA-Z]+", title))
                    # Grabbing all of the blue boxes which are denoted by "figure" in the HTML
                    # Trying to also save them off as HTML documents, with text, tables, and images
                    figures = soupReading.findAll("figure", {"class": "example"})
                    if len(figures) >= 1:
                        readingFile = open('%s.html' % title, 'wb')
                        for figure in figures:
                            for image_tag in figure.findAll('img'):
                                image_tag['src'] = 'https://jigsaw.vitalsource.com/books/' + str(book['isbn']) + '/epub/OEBPS/' + image_tag['src']
                            readingFile.write(figure.encode('UTF-8'))
                        readingFile.close()
                    else:
                        continue


