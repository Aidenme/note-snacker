import config
from splinter import Browser
from bs4 import BeautifulSoup
from highlight import Highlight
import re
import time

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
        self.BOOK_STORAGE_FOLDER = config.BOOK_STORAGE_FOLDER

    def __str__(self):
        return self.title
    
    def select(self):
        self.button.click()
        self.selected = True
        time.sleep(5)
        self.soup = BeautifulSoup(self.browser.html, 'lxml')

    def checkSoup(self):
        if self.soup == None:
            print("Book is missing its soup!")
            return False
        else:
            print("Book has its soup!")
            return True

    def getHighlightCount(self):
            highlightDivs = self.soup.find_all('div', {'class': 'kp-notebook-row-separator'})
            highlightCount = len(highlightDivs) - 1 #subtract one because the first div is not a highlight
            print("getSoupHighlightCount Result:")
            print(highlightCount)
            return highlightCount

    def createHighlightList(self):
        divs = self.soup.find_all('div', {'class': 'kp-notebook-row-separator'})
        print('Divs found on initial list creation:')
        print(len(divs))
        highlightList = []
        # skip the first div, as it's got weird stuff in it
        for div in divs[1:]:
            if div.find('div', {'class': 'kp-notebook-highlight'}):
            
                highlight = Highlight(div, self.browser)

                highlightList.append(highlight)
        
        self.highlightList = highlightList

    def getLocalHighlightTextList(self):
        htmlFile = (open(self.BOOK_STORAGE_FOLDER + self.fileName , mode='r' , encoding='utf-8'))

        highlightTextList = []

        soup = BeautifulSoup(htmlFile, 'lxml')

        htmlFile.close()
        
        #Note that this will include the truncated highlight alert text which will make it differ from the online highlight.
        #This should not be a problem since truncated text was only getting stored for testing purposes, but it will
        #be stored if you have to do an emergency export.
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
        #Since the appending will just create a new file if there is nothing to append to, this just exports twice. It appends
        #to any books already in BOOK_STORAGE_FOLDER, but creates a new highlight in the NEW_HIGHLIGHT_FOLDER.
        self.export(self.fileName, self.highlightList, self.BOOK_STORAGE_FOLDER)
        self.export(self.fileName, self.highlightList, config.NEW_HIGHLIGHT_FOLDER)

    def checkColors(self):
        print("Checking highlight colors...\n")

        # To determine if there is an even number of yellow highlights to ensure every opening yellow highlight has a closing highlight.
        yellowCount = 0
        # Indicates if the following highlights should (or should not) be considered part of a multi-highlight
        openYellow = False

        for highlight in self.highlightList:

            if highlight.color == "Yellow":
                # When a yellow highlight is found it needs to be added to the total yellow highlight count for the even highlight test later
                yellowCount += 1
                # When yellow highlights are hit this will either start a multi-highlight or close it
                openYellow = not openYellow
                # I don't care about the yellow highlight itself, I just need those two above values to change when a yellow highlight is hit.
                # This causes the for loop to move on to the next highlight without progressing to those if statements below.
                continue

            # If a not pink highlight is found between two yellow highlights that means something is the wrong color and what should be a multi-highlight is not
            if openYellow == True and highlight.color != "Pink":
                print("ERROR: HIGHLIGHT IS THE WRONG COLOR AFTER AN OPEN YELLOW HIGHLIGHT\n")
                print("BROKEN HIGHLIGHT:")
                print(highlight)
                exit()

            # If a pink highlight is found and it's not part of a multi-highlight something is amiss.
            if openYellow == False and highlight.color == "Pink":
                print("ERROR: PINK HIGHLIGHT NOT BETWEEN YELLOW HIGHLIGHTS\n")
                print("BROKEN HIGHLIGHT")
                print(highlight)
                exit()

        # An uneven number of yellow highlights means a yellow highlight was opened and not closed
        if yellowCount % 2 != 0:
            print("ERROR: UNEVEN NUMBER OF YELLOW HIGHLIGHTS. SOMETHING WAS OPENED AND NOT CLOSED")
            exit()

        print("No highlight errors detected!")

    def highlightButtonClick(self):
        self.highlightList[0].clickOptionsButton()

    def deleteHighlight(self, highlightIndex):
        self.highlightList[highlightIndex].delete()

    #Runs in the book class because highlights need the full soup to reference themselves
    def updateHighlightText(self, highlight):
        
        #Can't reference highlight.div itself because they are all the same
        highlightDiv = self.soup.find("div", {"id": highlight.id})

        newText = highlightDiv.text.strip()
        
        highlight.text = newText

    #Runs in the book class because highlights need the full soup to reference themselves
    def updateHighlightTruncated(self, highlight):

        highlightDiv = self.soup.find("div", {"id": highlight.id})

        if highlightDiv.find("div", {"class": "a-alert-content"}):
            highlight.truncated = True
        else:
            highlight.truncated = False


    def deleteCompleteHighlights(self):
        
        for highlight in self.highlightList:
            if highlight.deleted == False:
                if highlight.truncated == False:
                    print("Deleting highlight:")
                    print(highlight.text + "\n")
                    highlight.delete()
                    time.sleep(2)

    def updateHighlightList(self):
        
        for highlight in self.highlightList:

            #Makes this skip highlights that have already been deleted
            if highlight.deleted == True:
                continue
            
            #When the page refreshes the options buttons need to be relinked
            updatedOptionsButton = highlight.getOptionsButton(self.browser)
            highlight.optionsButton = updatedOptionsButton
            
            if highlight.truncated == True:
                self.updateHighlightText(highlight)
                self.updateHighlightTruncated(highlight)

    def getTruncatedHighlightCount(self):
        truncatedHighlightCount = 0
        notTruncatedHighlightCount = 0
        for highlight in self.highlightList: 
            if highlight.truncated == True:
                truncatedHighlightCount += 1
            else:
                notTruncatedHighlightCount += 1
        
        print("Truncated highlight count: " + str(truncatedHighlightCount))
        print("Untruncated highlight count: " + str(notTruncatedHighlightCount))
        
        return truncatedHighlightCount






