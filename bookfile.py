import re
import sys
import os
import config
import htmlparts
from bs4 import BeautifulSoup
from simpleHighlight import SimpleHighlight

class Bookfile:
    def __init__(self, book):
        self.book = book
        self.fileName = self.getFileName(book)
        self.pathName = config.BOOK_STORAGE_FOLDER + self.fileName
        self.header = htmlparts.HEADER_TEXT
        self.ender = self.getEnder()
        self.kindleSimpHL = self.importKindle(book.highlightList)
        self.setBookfile(self.pathName, self.kindleSimpHL)
        self.HTMLSimpHL = self.importHTMLFile(self.pathName)
        self.localList = []

    def getFileName(self, book):
        regxPattern = '[^A-Za-z0-9 ]+'
        
        #Removes characters that don't work in file names and shortens the title to 30 characters in total
        cleanTitle = re.sub(regxPattern, '', book.title[:30])
        
        #Same as above, but also removed the 'By: ' text the kindle notebook puts in front of author names
        cleanAuthor = re.sub(regxPattern, '', book.author[4:30])
        fileName = cleanTitle + " - " + cleanAuthor + ".html"

        print(fileName)
        
        return fileName
    
    def updateBookfile(self):
        self.localList = self.updateLocalList()
        self.export(self.pathName, self.localList)

    def export(self, pathName, highlightList):
        mergeHighlights = False
        f = open(pathName , mode='w', encoding='utf-8', errors='replace')
        f.write(htmlparts.HEADER_TEXT)

        for highlight in highlightList:

            #Toggle "part of a multi-part highlight" on and off
            if highlight.color == 'Yellow':
                mergeHighlights = not mergeHighlights

            if highlight.truncated:
                f.write('<div class="highlight ' + highlight.color + ' True">\n')
            else:
                f.write('<div class="highlight ' + highlight.color + ' False">\n')
            
            #Create the text div
            f.write('\t<div class="text">')
            f.write(highlight.text)
            f.write('</div>\n')

            #Create the note div
            f.write('\t<div class="note">')
            if highlight.note:    
                f.write(highlight.note)
            f.write('</div>\n')

            #Entire highlight div
            f.write('</div>\n')

            if mergeHighlights == False:
                f.write('<HR>\n')
            else:
                pass
        
        f.write(htmlparts.ENDER_TEXT)
        f.close()
    
    def importKindle(self, bookHighlights):
        print("Importing kindle highlights")
        kindleHighlights = []
        for highlight in bookHighlights:
            simpleHighlight = SimpleHighlight(highlight, 'kindle')
            kindleHighlights.append(simpleHighlight)
        
        return kindleHighlights
    
    #Imports all the highlights found in the local book file
    def importHTMLFile(self, filePath):
        localHighlights = []
        htmlFile = open(filePath, mode='r', encoding='utf-8')
        soup = BeautifulSoup(htmlFile, 'lxml')
        htmlFile.close()

        for highlightDiv in soup.findAll('div', {'class': 'highlight'}):
            simpleHighlight = SimpleHighlight(highlightDiv, 'html') 
            localHighlights.append(simpleHighlight)

        return localHighlights

    def updateLocalList(self):
        HTMLSimple = self.HTMLSimpHL
        kindleSimple = self.kindleSimpHL
        mergedList = []
        
        #Still not sure if I need this. For some reason the NOT Truncated local highlight compares work better with it.
        #Need to test around it more to figure out exactly what is going on.
        compareTxtCnt = 50
        
        #Since this is in truncated localHL text it needs to be removed before searching for untruncated KindleHL text
        tncateWarningTxt = "… Some highlights have been hidden or truncated due to export limits."

        for localHL in HTMLSimple:
            
            #If a local highlight is completed it doesn't need to be updated from the kindle list in any case. 
            if localHL.truncated == False:
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text[:compareTxtCnt] in kindleHL.text[:compareTxtCnt]:
                        #This shrinks the kindle list so I don't have to search through as many highlights to find matches later.
                        kindleSimple.pop(i)
                mergedList.append(localHL)
           
            if localHL.truncated == True:
                #See if there is an untruncated version of the text among the kindle highlights so you can update the truncated local text.
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text[:-len(tncateWarningTxt)] in kindleHL.text:
                        print()
                        print("TRUNCATED LOCAL FOUND MATCH WITH KINDLE HIGHLIGHT:")
                        print()
                        print("Local Highlight Text:")
                        print(localHL.text)
                        print()
                        print("Online highlight Text:")
                        print(kindleHL.text)
                        #Match located! Now see if it is untruncated
                        if kindleHL.truncated == False:
                            mergedList.append(kindleSimple[i])
                        if kindleHL.truncated == True:
                            kindleSimple.pop(i)
                            mergedList.append(localHL)

        
        #Add any new highlights to the merged list
        for kindleHL in kindleSimple:
            mergedList.append(kindleHL)

        return mergedList
    
    def setBookfile(self, pathName, kindleHighlights):

        if os.path.isfile(pathName):
            print("Local book file found.")
        else:
            print("Local book file does NOT exist. Creating one from found online highlights...")
            self.export(pathName, kindleHighlights)

    def updateKindleList(self, updatedOnlineBook):
        self.kindleSimpHL = self.importKindle(updatedOnlineBook.highlightList)



    #This is just for testing to make sure when I convert a local and kindle highlight they end up with the exact same data.
    def compareLists(self, HTMLList, kindleList):
        print("Local list length:")
        print(len(HTMLList))
        print("kindle list length:")
        print(len(kindleList))
        checkIndex = []
        for i in range(len(HTMLList)):
            print("**********COMPARING THESE HIGHLIGHTS**********")
            print("HTML Simp:")
            print(HTMLList[i].note)
            print("Kindle Simp:")
            print(kindleList[i].note)
            print("Same data?:")
            if HTMLList[i].note == kindleList[i].note:
                print("True")
            else:
                print("False")
                checkIndex.append(i)
        print()

        print("Mismatch found at these indexes: ")
        for i in checkIndex:
            print(i)
        print("End compareLists")
        

