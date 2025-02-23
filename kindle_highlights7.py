from dotenv import dotenv_values
from splinter import Browser
from bs4 import BeautifulSoup
import sys
import json
import time

BROWSER_NAME = 'firefox'
AMZ_ACCOUNT = dotenv_values(".env")
KINDLE_NOTEBOOK = 'https://read.amazon.com/kp/notebook'
BROWSER = Browser(BROWSER_NAME)

def createInitialHighlightList():
    soup = BeautifulSoup(BROWSER.html, 'lxml')
    divs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
    print('Divs found on initial list creation:')
    print(len(divs))
    highlightList = []
    # skip the first div, as it's got weird stuff in it
    for div in divs[1:]:
        highlight = {}
        h = div.span.text.strip()
        #test_book['color'] = ''
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

def getPageHighlightCount():
    soup = BeautifulSoup(BROWSER.html, 'lxml')
    highlightDivs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
    highlightCount = len(highlightDivs) - 1 #subtract one because the first div is not a highlight
    print("getPageHighlightCount Result:")
    print(highlightCount)
    return highlightCount

def exportToFile(highlightBook):
    mergeHighlights = False
    f = open("test.html", mode='w', encoding='utf-8', errors='replace')

    for highlight in test_book['highlights']:

        f.write('<p>')

        #Toggle "part of a multi-part highlight" on and off
        if highlight['color'] == 'Yellow':
            mergeHighlights = not mergeHighlights

        if highlight['truncated']:
            f.write("<h4>HIGHLIGHT IS TRUNCATED</h4>")

        f.write(highlight['highlight'])

        f.write('</p>')

        if highlight['note']:
            f.write('<h5>')

            f.write(highlight['note'])

            f.write('</h5>')

        if mergeHighlights == False:
            f.write('<HR>')
        else:
            pass

    f.close()

#Gets the title, author, and button to press to open the book on the notebook page
def getLibrary():
    soup = BeautifulSoup(BROWSER.html, 'lxml')
    library = soup.find_all("div", {"class": "kp-notebook-library-each-book"})

    libraryList = []

    for book in library:
        button = BROWSER.find_by_id(book.get('id'))
        title = book.find('h2').text
        author = book.find('p').text
        libraryList.append({'title': title, 'author': author, 'button': button})

    return libraryList

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

pickBook()

startingPageHighlightCount = getPageHighlightCount()
#End the program if startingPageHighlightCount is 0 because that means there are no highlights to copy at all.
if startingPageHighlightCount == 0:
    print("No highlights found. Exiting...")
    exit()

test_book = {}
test_book['highlights'] = createInitialHighlightList()
exportToFile(test_book)
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
