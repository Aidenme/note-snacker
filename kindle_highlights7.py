import config
from dotenv import dotenv_values
from splinter import Browser
from bs4 import BeautifulSoup
from book import Book
import sys
import json
import time

BROWSER_NAME = config.BROWSER_NAME
AMZ_ACCOUNT = dotenv_values(".env")
KINDLE_NOTEBOOK = config.KINDLE_NOTEBOOK
BROWSER = Browser(BROWSER_NAME)
BOOK_STORAGE_FOLDER = config.BOOK_STORAGE_FOLDER

def checkColors(highlightBook):

    errorCount = 0
    #To determine if there is an even number of yellow highlights to ensure every opening yellow highlight has a closing highlight.
    yellowCount = 0
    #Indicates if the following highlights should (or should not) be considered part of a multi-highlight
    openYellow = False

    for highlight in highlightBook:

        if highlight['color'] == 'Yellow':
            #When a yellow highlight is found it needs to be added to the total yellow highlight count for the even highlight test later
            yellowCount += 1
            #When yellow highlights are hit this will either start a multi-highlight or close it
            openYellow = not openYellow
            #I don't care about the yellow highlight itself, I just need those two above values to change when a yellow highlight is hit.
            #This causes the for loop to move on to the next highlight without progressing to those if statements below.
            continue

        #If a not pink highlight is found between two yellow highlights that means something is the wrong color and what should be a multi-highlight is not
        if (openYellow == True and highlight['color'] != 'Pink'):
            print("Multi-highlight breaker found:")
            printHighlight(highlight)
            errorCount += 1

        #If a pink highlight is found and it's not part of a multi-highlight something is amiss.
        if (openYellow == False and highlight['color'] == 'Pink'):
            print("Unclosed pink highlight found:")
            printHighlight(highlight)
            errorCount += 1

    #An uneven number of yellow highlights means a yellow highlight was opened and not closed
    if yellowCount % 2 != 0:
        print("Unclosed yellow highlight detected")
        errorCount += 1

    if errorCount != 0:
        print(str(errorCount) + " error(s) detected")
        print("Please fix errors and try again")
        exit()
    else:
        print("No errors detected, color checks PASSED!")


def deleteHighlight(testHighlight):
    time.sleep(2)
    cleanId = testHighlight['id'][len('highlight-'):]
    newId = 'popover-' + cleanId
    optionsButton = BROWSER.find_by_id(newId)
    optionsButton.click()
    time.sleep(2)
    deleteButton = BROWSER.find_by_id('deletehighlight')
    deleteButton.click()
    time.sleep(2)
    deleteConfirm = BROWSER.find_by_xpath('//html/body/div[4]/div/div/div[2]/span[2]/span/span/input')
    deleteConfirm.click()

def getHighlightFromId(highlightId):
    newHighlight = {}
    soup = BeautifulSoup(BROWSER.html, 'lxml')
    highlightDiv = soup.find('div', {'id': highlightId})

    if highlightDiv.find('div', {'class': 'a-alert-content'}):
        newHighlight['truncated'] = True
    else:
        newHighlight['truncated'] = False

    newHighlight['highlight'] = highlightDiv.text.strip()
    return newHighlight

def printHighlight(highlightFull):
    print(highlightFull['highlight'][:20])

def fillAllHighlights(highlightBook):
    newHighlightParts = {}
    for highlight in highlightBook['highlights']:
        printHighlight(highlight)
        if highlight['deleted'] == False:
            if highlight['truncated']:
                newHighlightParts = getHighlightFromId(highlight['id'])
                if newHighlightParts['truncated']:
                    pass
                else:
                    highlight['highlight'] = newHighlightParts['highlight']

                    #Now that it is discovered that highlight is no longer truncated, let the program know that.
                    highlight['truncated'] = False
                    print("Deleting Highlight")
                    deleteHighlight(highlight)
                    highlight['deleted'] = True
            else:
                    deleteHighlight(highlight)
                    highlight['deleted'] = True
                    print("Deleting Highlight")
        else:
            pass

    return highlightBook

def setSoup(book):
    book.soup = BeautifulSoup(BROWSER.html, 'lxml')

#Gets the title, author, and button to press to open the book on the notebook page
def getLibrary():
    #Need soup on init to get stuff on the side bar to create the book.
    soup = BeautifulSoup(BROWSER.html, 'lxml')
    kindleLibrary = soup.find_all("div", {"class": "kp-notebook-library-each-book"})

    library = []

    for book in kindleLibrary:
        button = BROWSER.find_by_id(book.get('id'))
        title = book.find('h2').text
        author = book.find('p').text

        library.append(Book(title, author, button, BROWSER))

    return library

#Lets you pick a book out of all books
def pickBook():

    library = getLibrary()

    for index, book in enumerate(library):
        print(str(index +1) + "\n" + book['title'] + "\n")

    bookLibraryIndex = int(input("Enter index number of the book to extract notes from:")) - 1

    print(library[bookLibraryIndex]['title'])
    print("Loading Book...")
    library[bookLibraryIndex]['button'].click()
    #Wait for the page to load. It can take a while on pages with tons of highlights and not
    #Starting off with the right count can cause lots of issues.
    time.sleep(5)
    print("Book loaded")

#Handles signing into the kindle notebook website
def signIn():
    BROWSER.visit(KINDLE_NOTEBOOK)
    BROWSER.fill('email', AMZ_ACCOUNT["EMAIL"])
    time.sleep(2)
    button = BROWSER.find_by_id('continue')
    button.click()
    time.sleep(2)
    BROWSER.fill('password', AMZ_ACCOUNT["PASSWORD"])
    button = BROWSER.find_by_id('signInSubmit')
    button.click()
    time.sleep(2)


print()
print("Welcome to Note Snacker 7!")
print("Now loading your selected browser, " + BROWSER_NAME + "...")

signIn()

library = getLibrary()

aBook = library[2]

aBook.select()

time.sleep(2)

aBook.load()

startingPageHighlightCount = aBook.highlightCount
#End the program if startingPageHighlightCount is 0 because that means there are no highlights to copy at all.
if startingPageHighlightCount == 0:
    print("No highlights found. Exiting...")
    exit()

print(aBook.getFileName())

aBook.export(BOOK_STORAGE_FOLDER)
#exportToFile(aBook)
sys.exit("Initial highlights copied, exiting...")

#Does a handful of checks to make sure the highlight colors are correct in the book to avoid disasters.
checkColors(test_book['highlights'])

while True:
    print("Main Loop Runs")

    #Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed. If something goes wrong all the work
    #done so far is immediately exported so it's not just lost in RAM as the program crashes.
    #Also I'm putting all of these try/except statements in this loop because it seems too complicated to get the book to print as is from within all these various functions.
    try:
        test_book = fillAllHighlights(test_book)
    except:
        print("An error occured")
        exportToFile(test_book)

    #Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed.
    try:
        #fillAllHighlights() causes some highlights to be deleted so the page needs to be reloaded to unlock more highlights to copy.
        BROWSER.reload()
        print("Refreshing...")
        time.sleep(5)
        print("Refresh complete!")
    except:
        print("An error occured")
        exportToFile(test_book)

    #Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed.
    try:
        #Getting the highlight count again since fillAllHighlights() has run and deleted some. Used later to check if highlights are still getting deleted/unlocked and if the program can continue.
        newPageHighlightCount = getPageHighlightCount()
    except:
        print("An error occured")
        exportToFile(test_book)

    #Exit the loop if there are no highlights left to get. This will cause the export to run since it is directly outside the loop
    if newPageHighlightCount == 0:
        print("All Highlights copied!")
        break

    #Exits the loop if highlights are no longer able to be untruncated and deleted.
    #This is how you tell if the deleting process is getting stuck on something or nothing more can get untruncated.
    if newPageHighlightCount < startingPageHighlightCount:
        startingPageHighlightCount = newPageHighlightCount
    else:
        print("Highlights did not decrease")
        break

exportToFile(test_book)

print('done')

#BROWSER.quit()
