from splinter import Browser
from bs4 import BeautifulSoup
import time

class Highlight:
    def __init__(self, div, browser):
        self.div = div
        self.browser = browser
        self.text = self.getText(div)
        self.note = self.getNote(div)
        self.color = self.getColor(div)
        self.id = self.getId(div)
        self.truncated = self.getTruncated(div)
        self.optionsButton = self.getOptionsButton(browser)
        self.deleted = False
    
    def __str__(self):
        return self.text
    
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
    
    def getOptionsButton(self, browser):
        print("getOptionsButton Ran")
        cleanId = self.id[len("highlight-") :]
        newId = "popover-" + cleanId
        optionsButton = browser.find_by_id(newId)
        return optionsButton
    
    def clickOptionsButton(self):
        self.optionsButton.click()

    def delete(self):
        
        self.optionsButton.click()
        
        time.sleep(2)
        
        #Click the delete option that appears when you open the options list
        deleteButton = self.browser.find_by_id("deletehighlight")
        deleteButton.click()

        time.sleep(2)
        
        #You'll be asked to confirm deleting the highlight
        deleteConfirmButton = self.browser.find_by_xpath(
        "//html/body/div[@class='a-modal-scroller a-declarative']/div/div/div[2]/span[2]/span/span/input"
        )

        #Clcking the confirm button deletes the highlight for good
        deleteConfirmButton.click()

        self.deleted = True



