from splinter import Browser
from bs4 import BeautifulSoup

class Book:
    def __init__(self, title, author, button, browser):
        self.title = title
        self.author = author
        self.button = button
        self.browser = browser
        self.soup = None
        self.selected = False
        self.highlightCount = 0
        self.highlightList = []

    def __str__(self):
        return self.title
    
    def select(self):
        self.button.click()
        self.selected = True

    def checkSoup(self):
        if self.soup == None:
            print("Book is missing its soup!")
            return False
        else:
            print("Book has its soup!")
            return True

    def getSoup(self):
        self.soup = BeautifulSoup(self.browser.html, 'lxml')

    def getHighlightCount(self, soup):
            highlightDivs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
            highlightCount = len(highlightDivs) - 1 #subtract one because the first div is not a highlight
            print("getSoupHighlightCount Result:")
            print(highlightCount)
            return highlightCount

    def createHighlightList(self, soup):
        divs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
        print('Divs found on initial list creation:')
        print(len(divs))
        highlightList = []
        # skip the first div, as it's got weird stuff in it
        for div in divs[1:]:
            highlight = {}
            h = div.span.text.strip()
            highlight['deleted'] = False
            #give it an index number (so I can sort by index number )
            if 'highlight' in h:
                highlight['color'] = h[:h.find('highlight')].strip()
            if div.find('div', {'class': 'a-alert-content'}):
                highlight['truncated'] = True
            else:
                highlight['truncated'] = False
            if div.find('div', {'class': 'kp-notebook-highlight'}):
                hTxtDiv = div.find('div', {'class': 'kp-notebook-highlight'})
                highlight['id'] = hTxtDiv.get('id')
                highlight['highlight'] = hTxtDiv.text.strip()

                #Selects the div that contains a note that each highlight div should have
                noteTxtDiv = div.find('div', {'class': 'kp-notebook-note'})
                #The id of note divs that don't actually have notes is always 'note-' so I'm not doing anything if that is found.
                if noteTxtDiv.get('id') == 'note-':
                    highlight['note'] = None
                else:
                    #Every note from the site inserts 'note:' without a space in front of each note. I'm taking that off and putting on my own
                    #better version.
                    highlight['note'] = 'NOTE: ' + noteTxtDiv.text.strip()[5:]

                highlightList.append(highlight)
                #then go through the process of deleting the highlight
        return highlightList

    def updateHighlightList(self):
        pass

    def load(self):
        self.getSoup()
        self.highlightCount = self.getHighlightCount(self.soup)
        self.highlightList = self.createHighlightList(self.soup)
