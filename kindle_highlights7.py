import config
from dotenv import dotenv_values
from splinter import Browser
from bs4 import BeautifulSoup
from book import Book
import sys
import json
import time
import os

BROWSER_NAME = config.BROWSER_NAME
AMZ_ACCOUNT = dotenv_values(".env")
KINDLE_NOTEBOOK = config.KINDLE_NOTEBOOK
BROWSER = Browser(BROWSER_NAME)
BOOK_STORAGE_FOLDER = config.BOOK_STORAGE_FOLDER

def getHighlightFromId(highlightId):
    newHighlight = {}
    soup = BeautifulSoup(BROWSER.html, "lxml")
    highlightDiv = soup.find("div", {"id": highlightId})

    if highlightDiv.find("div", {"class": "a-alert-content"}):
        newHighlight["truncated"] = True
    else:
        newHighlight["truncated"] = False

    newHighlight["highlight"] = highlightDiv.text.strip()
    return newHighlight


def printHighlight(highlightFull):
    print(highlightFull["highlight"][:20])


def fillAllHighlights(highlightBook):
    newHighlightParts = {}
    for highlight in highlightBook["highlights"]:
        printHighlight(highlight)
        if highlight["deleted"] == False:
            if highlight["truncated"]:
                newHighlightParts = getHighlightFromId(highlight["id"])
                if newHighlightParts["truncated"]:
                    pass
                else:
                    highlight["highlight"] = newHighlightParts["highlight"]

                    # Now that it is discovered that highlight is no longer truncated, let the program know that.
                    highlight["truncated"] = False
                    print("Deleting Highlight")
                    deleteHighlight(highlight)
                    highlight["deleted"] = True
            else:
                deleteHighlight(highlight)
                highlight["deleted"] = True
                print("Deleting Highlight")
        else:
            pass

    return highlightBook


def setSoup(book):
    book.soup = BeautifulSoup(BROWSER.html, "lxml")


# Gets the title, author, and button to press to open the book on the notebook page
def getLibrary():
    # Need soup on init to get stuff on the side bar to create the book.
    soup = BeautifulSoup(BROWSER.html, "lxml")
    kindleLibrary = soup.find_all("div", {"class": "kp-notebook-library-each-book"})

    library = []

    for book in kindleLibrary:
        button = BROWSER.find_by_id(book.get("id"))
        title = book.find("h2").text
        author = book.find("p").text

        library.append(Book(title, author, button, BROWSER))

    return library


# Lets you pick a book out of all books
def pickBook():

    library = getLibrary()

    for index, book in enumerate(library):
        print(str(index + 1) + "\n" + book["title"] + "\n")

    bookLibraryIndex = (
        int(input("Enter index number of the book to extract notes from:")) - 1
    )

    print(library[bookLibraryIndex]["title"])
    print("Loading Book...")
    library[bookLibraryIndex]["button"].click()
    # Wait for the page to load. It can take a while on pages with tons of highlights and not
    # Starting off with the right count can cause lots of issues.
    time.sleep(5)
    print("Book loaded")


# Handles signing into the kindle notebook website
def signIn():
    BROWSER.visit(KINDLE_NOTEBOOK)
    BROWSER.fill("email", AMZ_ACCOUNT["EMAIL"])
    time.sleep(2)
    button = BROWSER.find_by_id("continue")
    button.click()
    time.sleep(2)
    BROWSER.fill("password", AMZ_ACCOUNT["PASSWORD"])
    button = BROWSER.find_by_id("signInSubmit")
    button.click()
    time.sleep(2)


print()
print("Welcome to Note Snacker 7!")
print("Now loading your selected browser, " + BROWSER_NAME + "...")

signIn()

library = getLibrary()

aBook = library[4]

aBook.select()

time.sleep(5)

aBook.load()

if aBook.highlightCount == 0:
    print("No online highlights found, exiting...")
    exit()

aBook.checkColors()

while aBook.checkForTruncatedHighlights == True:

    #Deletes highlights that are not truncated
    aBook.deleteCompleteHighlights()

    #Reloading should unlock highlights that were previously truncated
    BROWSER.reload()

    #Finds the highlights that got untruncated
    aBook.updateHighlightList()

else:
    print("No more truncated highlights detected.")

if aBook.fileName in os.listdir(BOOK_STORAGE_FOLDER):
    
    #newHighlights are just-downloaded highlights that aren't in the html file.
    newHighlights = aBook.getNewHighlights()
    
    if newHighlights == None:
        
        print("No new highlights found for stored book.")
    
    else:
        
        aBook.update(newHighlights)
else:
    
    aBook.make()

#print(aBook.getFileName())

#aBook.export()

#aBook.getNewHighlights()

sys.exit("Initial highlights copied, exiting...")

# Does a handful of checks to make sure the highlight colors are correct in the book to avoid disasters.
checkColors(test_book["highlights"])

while True:
    print("Main Loop Runs")

    # Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed. If something goes wrong all the work
    # done so far is immediately exported so it's not just lost in RAM as the program crashes.
    # Also I'm putting all of these try/except statements in this loop because it seems too complicated to get the book to print as is from within all these various functions.
    try:
        test_book = fillAllHighlights(test_book)
    except:
        print("An error occured")
        exportToFile(test_book)

    # Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed.
    try:
        # fillAllHighlights() causes some highlights to be deleted so the page needs to be reloaded to unlock more highlights to copy.
        BROWSER.reload()
        print("Refreshing...")
        time.sleep(5)
        print("Refresh complete!")
    except:
        print("An error occured")
        exportToFile(test_book)

    # Putting tries on everything that attempts to read data from the browser in case the internet goes down or the window gets closed.
    try:
        # Getting the highlight count again since fillAllHighlights() has run and deleted some. Used later to check if highlights are still getting deleted/unlocked and if the program can continue.
        newPageHighlightCount = getPageHighlightCount()
    except:
        print("An error occured")
        exportToFile(test_book)

    # Exit the loop if there are no highlights left to get. This will cause the export to run since it is directly outside the loop
    if newPageHighlightCount == 0:
        print("All Highlights copied!")
        break

    # Exits the loop if highlights are no longer able to be untruncated and deleted.
    # This is how you tell if the deleting process is getting stuck on something or nothing more can get untruncated.
    if newPageHighlightCount < startingPageHighlightCount:
        startingPageHighlightCount = newPageHighlightCount
    else:
        print("Highlights did not decrease")
        break

exportToFile(test_book)

print("done")

# BROWSER.quit()
