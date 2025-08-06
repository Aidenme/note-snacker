import config
from dotenv import dotenv_values
from splinter import Browser
from bs4 import BeautifulSoup
from book import Book
from bookfile import Bookfile
import sys
import time
import os

BROWSER_NAME = config.BROWSER_NAME
AMZ_ACCOUNT = dotenv_values(".env")
KINDLE_NOTEBOOK = config.KINDLE_NOTEBOOK
BROWSER = Browser(BROWSER_NAME)
BOOK_STORAGE_FOLDER = config.BOOK_STORAGE_FOLDER
DELETE_HIGHLIGHTS = config.DELETE_HIGHLIGHTS
#MAX_PASSES = config.MAX_PASSES
COUNT_PASSES = config.COUNT_PASSES
BOOK_LIBRARY_INDEX = 0

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
def pickBook(library):

    for index, book in enumerate(library):
        print(str(index + 1) + "\n" + book.title + "\n")

    bookLibraryIndex = (
        int(input("Enter index number of the book to extract notes from:")) - 1
    )

    print(library[bookLibraryIndex].title)

    return bookLibraryIndex


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

def export(book):
    if book.fileName in os.listdir(BOOK_STORAGE_FOLDER):
    
        #newHighlights are just-downloaded highlights that aren't in the html file.
        newHighlights = book.getNewHighlights()
    
        if newHighlights == None:
        
            print("No new highlights found for stored book.")
    
        else:
        
            book.update(newHighlights)
    else:
    
        book.make()
    
print()
print("Welcome to Note Snacker 7!")
print("Now loading your selected browser, " + BROWSER_NAME + "...")

signIn()

library = getLibrary()
BOOK_LIBRARY_INDEX = pickBook(library)

aBook = library[BOOK_LIBRARY_INDEX]

aBook.select()

localBook = Bookfile(aBook)

if DELETE_HIGHLIGHTS == False:
    localBook.updateBookfile()
    sys.exit("Done!")

if COUNT_PASSES == True:
    MAX_PASSES = config.MAX_PASSES
else:
    MAX_PASSES = 1

passCount = 0
while aBook.getTruncatedHighlightCount() > 0 and passCount < MAX_PASSES:

    #Deletes highlights that are not truncated
    try:
        aBook.deleteCompleteHighlights()
    except Exception as e:
        print("An Error occured: Unable to delete complete highlights")
        print(e)
        localBook.updateBookfile()
        sys.exit()

    #Reloading should unlock highlights that were previously truncated
    try:
        #Select the book to reload it since a page refresh would load up the book at index 0.
        BROWSER.reload()
        time.sleep(5)
        library = getLibrary()
        aBook = library[BOOK_LIBRARY_INDEX]
        aBook.select()
        localBook = Bookfile(aBook)
    except Exception as e:
        print("An error occured: Unable to reload the book")
        print(e)
        localBook.updateBookfile()
        sys.exit()

    #Finds the highlights that got untruncated. Updates their text and truncated status to untruncated.  
    try:
        aBook.updateHighlightList()
    except Exception as e:
        print("An error occured: Unable to update highlight list")
        print(e)
        localBook.updateBookfile()
        sys.exit()

    if COUNT_PASSES == True:
        passCount += 1
        print("Total passes: " + str(passCount)) 

else:
    localBook.updateBookfile()

    #Clean up remaining highlights
    print("Cleaning up remaining highlights...")
    aBook.deleteCompleteHighlights()

#BROWSER.quit()

sys.exit("Done!")