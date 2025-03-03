import config
from splinter import Browser
from bs4 import BeautifulSoup
from highlight import Highlight
import re

class Book:
    def __init__(self, title, author, button, browser):
        self.title = title
        self.author = author
        self.button = button
        self.browser = browser
        self.fileName = self.getFileName()
        self.soup = None
        self.selected = False
        self.highlightCount = 0
        self.highlightList = []
        self.BOOK_STORAGE_FOLDER = config.BOOK_STORAGE_FOLDER

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
            if div.find('div', {'class': 'kp-notebook-highlight'}):
            
                highlight = Highlight(div)

                highlightList.append(highlight)
        
        return highlightList

    def updateHighlightList(self):
        pass

    def load(self):
        self.getSoup()
        self.highlightCount = self.getHighlightCount(self.soup)
        self.highlightList = self.createHighlightList(self.soup)

    def getFileName(self): 
        regxPattern = '[^A-Za-z0-9 ]+'
        cleanTitle = re.sub(regxPattern, '', self.title)
        cleanAuthor = re.sub(regxPattern, '', self.author)
        fileName = cleanTitle + " - " + cleanAuthor + ".html"
        
        return fileName

    def export(self, fileName, highlightList, exportFolder):
        mergeHighlights = False
        f = open(exportFolder + fileName , mode='a', encoding='utf-8', errors='replace')

        for highlight in highlightList:

            #Toggle "part of a multi-part highlight" on and off
            if highlight.color == 'Yellow':
                mergeHighlights = not mergeHighlights

            if highlight.truncated:
                f.write('<p ' + config.TRUNCATED_HIGHLIGHT_STYLE + '>')
            else:
                f.write('<p>')

            f.write(highlight.text)

            f.write('</p>')

            if highlight.note:
                f.write('<h5>')

                f.write(highlight.note)

                f.write('</h5>')

            if mergeHighlights == False:
                f.write('<HR>')
            else:
                pass

        f.close()

    def getLocalHighlightTextList(self):
        htmlFile = (open(self.BOOK_STORAGE_FOLDER + self.fileName , mode='r' , encoding='utf-8'))

        highlightTextList = []

        soup = BeautifulSoup(htmlFile, 'lxml')

        htmlFile.close()
        
        for pTag in soup.find_all("p"):
            highlightTextList.append(pTag.get_text())

        return highlightTextList
    
    def getNewHighlights(self):

        newHighlights = []
        newHighlightCount = 0
        
        localHighlights = self.getLocalHighlightTextList()

        for onlineHighlight in self.highlightList:
            if onlineHighlight.text not in localHighlights:
                newHighlightCount += 1
                newHighlights.append(onlineHighlight)

        if newHighlightCount == 0:
            print("No new highlights found")
        else:
            print("Found " + str(newHighlightCount) + " new highlights!")
            return newHighlights
        
    def update(self, newHighlights):
        self.export(self.fileName, newHighlights, self.BOOK_STORAGE_FOLDER) 
        self.export(fileName= self.fileName, highlightList = newHighlights, exportFolder = config.NEW_HIGHLIGHT_FOLDER)

    def make(self):
        self.export(self.fileName, self.highlightList, self.BOOK_STORAGE_FOLDER)
        self.export(self.fileName, self.highlightList, config.NEW_HIGHLIGHT_FOLDER)




