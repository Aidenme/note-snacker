import re
import sys
import config
from bs4 import BeautifulSoup
from simpleHighlight import SimpleHighlight

class Bookfile:
    def __init__(self, book):
        self.book = book
        self.fileName = self.getFileName(book)
        self.pathName = config.BOOK_STORAGE_FOLDER + self.fileName
        self.header = self.getHeader()
        self.kindleSimpHL = []
        self.HTMLSimpHL = []
        self.importKindle(book.highlightList)
        try:
            print("Importing a local book...")
            self.importHTMLFile(self.pathName)
        except:
            print("Could not find a local book. Running first time creation instead...")
            #This requires kindleSimpHL to exist (Can I just make that one of the arguments sent then?)
            self.createBookfile(self.pathName)
        #self.ender = self.getEnder()
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

    def createBookfile(self, pathName):
        print("Creating local book...")
        self.export(pathName, self.kindleSimpHL)
        print("Local book created")
        print("Importing local book...")
        self.importHTMLFile(pathName)

    def export(self, pathName, highlightList):
        mergeHighlights = False
        f = open(pathName , mode='w', encoding='utf-8', errors='replace')
        f.write(self.header)

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

        f.close()

    def getHeader(self):
        headerText = '''
<html>
<head>
    <link rel="stylesheet" href="../visualize_color.css">
</head>
<body>
'''
        return headerText
    
    def importKindle(self, bookHighlights):
        print("Importing kindle highlights")
        kindleHighlights = []
        for highlight in bookHighlights:
            simpleHighlight = SimpleHighlight(highlight, 'kindle')
            kindleHighlights.append(simpleHighlight)
        
        self.kindleSimpHL = kindleHighlights
    
    #Imports all the highlights found in the local book file
    def importHTMLFile(self, filePath):
        localHighlights = []
        htmlFile = open(filePath, mode='r', encoding='utf-8')
        soup = BeautifulSoup(htmlFile, 'lxml')
        htmlFile.close()

        for highlightDiv in soup.findAll('div', {'class': 'highlight'}):
            simpleHighlight = SimpleHighlight(highlightDiv, 'html') 
            localHighlights.append(simpleHighlight)

        self.HTMLSimpHL = localHighlights

    def updateLocalList(self):
        HTMLSimple = self.HTMLSimpHL
        kindleSimple = self.kindleSimpHL
        mergedList = []

        for localHL in HTMLSimple:
            
            #If a local highlight is completed it doesn't need to be updated from the kindle list in any case. 
            if localHL.truncated == False:
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text in kindleHL.text:
                        #This shrinks the kindle list so I don't have to search through as many highlights to find matches later.
                        kindleSimple.pop(i)
                mergedList.append(localHL)
           
            if localHL.truncated == True:
                #See if there is an untruncated version of the text among the kindle highlights so you can update the truncated local text.
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text in kindleHL.text:
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
        

