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

aBook = library[4]

aBook.select()

time.sleep(5)

aBook.getSoup()

if aBook.getHighlightCount() == 0:
    print("No online highlights found, exiting...")
    exit()
else:
    aBook.createHighlightList()

aBook.checkColors()

while aBook.checkForTruncatedHighlights == True:

    #Deletes highlights that are not truncated
    try:
        aBook.deleteCompleteHighlights()
    except:
        print("An Error occured: Unable to delete all highlights!")
        export(aBook)

    #Reloading should unlock highlights that were previously truncated
    try:
        BROWSER.reload()
        aBook.getSoup()
    except:
        print("An error occured: Unable to update soup!")
        export(aBook)

    #Finds the highlights that got untruncated. Updates their text and truncated status to untruncated.  
    try:
        aBook.updateHighlightList()
    except:
        print("An error occured: Unable to update Highlight List!")
        export(aBook)

else:
    print("No more truncated highlights detected. Everything should be copied now!")
    export(aBook)

    #Clean up remaining highlights
    aBook.deleteCompleteHighlights()

#BROWSER.quit()

sys.exit("Done!")