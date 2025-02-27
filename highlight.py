from splinter import Browser
from bs4 import BeautifulSoup

class Highlight:
    def __init__(self, div):
        self.div = div
        self.text = self.getText(div)
        self.note = self.getNote(div)
        self.color = self.getColor(div)
        self.id = self.getId(div)
        self.truncated = self.getTruncated(div)
        self.deleted = False
    
    def getColor(self, div):
        h = div.span.text.strip()
        if 'highlight' in h:
                highlightColor = h[:h.find('highlight')].strip()
        return highlightColor

    def getTruncated(self, div):
        if div.find('div', {'class': 'a-alert-content'}):
            isTruncated = True
        else:
            isTruncated = False
        return isTruncated

    def getId(self, div):
        hTxtDiv = div.find('div', {'class': 'kp-notebook-highlight'})
        highlightId = hTxtDiv.get('id')
        return highlightId

    def getText(self, div):
        hTxtDiv = div.find('div', {'class': 'kp-notebook-highlight'})
        highlightText = hTxtDiv.text.strip()
        return highlightText

    def getNote(self, div):
        #Selects the div that contains a note that each highlight div should have
        if div.find('div', {'class': 'kp-notebook-note'}):
            noteTxtDiv = div.find('div', {'class': 'kp-notebook-note'})
            #The id of note divs that don't actually have notes is always 'note-' so I'm not doing anything if that is found.
            if noteTxtDiv.get('id') == 'note-':
                highlightNote = None
            else:
                #Every note from the site inserts 'note:' without a space in front of each note. I'm taking that off and putting on my own
                #better version.
                highlightNote = 'NOTE: ' + noteTxtDiv.text.strip()[5:]
        else:
            highlightNote = None
        
        return highlightNote
