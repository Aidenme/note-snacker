from splinter import Browser
from bs4 import BeautifulSoup

class Highlight:
    def __init__(self, div):
        self.div = div
        self.text = None
        self.note = None
        self.color = None
        self.id = None
        self.truncated = False
        self.deleted = False
        self.makeHighlightFromDiv(div)

    def makeHighlightFromDiv(self, div):
        pass

    def getColor(self, div):
        h = div.span.text.strip()
        if 'highlight' in h:
                self.color = h[:h.find('highlight')].strip()

    def getTruncated(self, div):
        if div.find('div', {'class': 'a-alert-content'}):
            self.truncated = True
        else:
            self.truncated = False

    def getId(self, div):
        if div.find('div', {'class': 'kp-notebook-highlight'}):
            hTxtDiv = div.find('div', {'class': 'kp-notebook-highlight'})
            self.id = hTxtDiv.get('id')

    def getText(self, div):
        if div.find('div', {'class': 'kp-notebook-highlight'}):
            hTxtDiv = div.find('div', {'class': 'kp-notebook-highlight'})
            self.text = hTxtDiv.text.strip()
            print(self.text)

    def getNote(self, div):
        #Selects the div that contains a note that each highlight div should have
        if div.find('div', {'class': 'kp-notebook-note'}):
            noteTxtDiv = div.find('div', {'class': 'kp-notebook-note'})
            #The id of note divs that don't actually have notes is always 'note-' so I'm not doing anything if that is found.
            if noteTxtDiv.get('id') == 'note-':
                self.note = None
            else:
                #Every note from the site inserts 'note:' without a space in front of each note. I'm taking that off and putting on my own
                #better version.
                self.note = 'NOTE: ' + noteTxtDiv.text.strip()[5:]
        else:
            self.note = None
