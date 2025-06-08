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
        self.kindleSimpHL = self.kindleHLtoSimpHL(book.highlightList)
        self.HTMLSimpHL = []
        try:
            print("Importing a local book...")
            self.importHTMLFile(self.pathName)
        except:
            print("Could not find a local book. Running first time creation instead...")
            self.createBookfile(self.pathName)
            self.HTMLSimpHL = self.HTMLHLtoSimpHL(self.pathName)
        #self.ender = self.getEnder()
        self.localList = []
        #self.compareLists(self.HTMLSimpHL, self.kindleSimpHL)
        self.updateLocalList()


    def getFileName(self, book):
        regxPattern = '[^A-Za-z0-9 ]+'
        
        #Removes characters that don't work in file names and shortens the title to 30 characters in total
        cleanTitle = re.sub(regxPattern, '', book.title[:30])
        
        #Same as above, but also removed the 'By: ' text the kindle notebook puts in front of author names
        cleanAuthor = re.sub(regxPattern, '', book.author[4:30])
        fileName = cleanTitle + " - " + cleanAuthor + ".html"

        print(fileName)
        
        return fileName
    
    
    def importHTMLFile(self, pathName):
        self.HTMLSimpHL = self.HTMLHLtoSimpHL(pathName)

    def createBookfile(self, pathName):
        
        #CODING QUESTION: Modularity wise when I create a book I should just create the file name directly from the book I think.
        #On the other hand I don't want to have to do that again when I have to reference the book again. Actually, I'm just going to
        #Have to recreate the filename from the book anyway to tie this reference to the local html file again after the program closes.
        #The solution then is to just have the filename get generated from the book each time and not necessarily store it as a class variable.
        self.export(pathName, self.kindleSimpHL)

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
    
    def updateBookfile(self, updatedBook):
        pass
    
    def kindleHLtoSimpHL(self, bookHighlights):
        kindleHighlights = []
        for highlight in bookHighlights:
            simpleHighlight = SimpleHighlight(highlight, 'kindle')
            kindleHighlights.append(simpleHighlight)
        
        return kindleHighlights    
    
    def HTMLHLtoSimpHL(self, filePath):
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
        htmlTextList = []
        kindleTextList = []
        mergedList = []

        for localHL in HTMLSimple:
            
            #Remove any complete local highlights from the kindle list
            if localHL.truncated == False:
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text in kindleHL.text:
                        kindleSimple.pop(i)
                mergedList.append(localHL)
           
            if localHL.truncated == True:
                #See if there is an untruncated version of the text among the kindle highlights
                for i, kindleHL in enumerate(kindleSimple):
                    if localHL.text in kindleHL.text:
                        #Match located! Now see if it is untruncated
                        if kindleHL.truncated == True:
                            kindleSimple.pop(i)
                        if kindleHL.truncated == False:
                            mergedList.append(localHL)
        
        #Add any new highlights to the merged list
        for kindleHL in kindleSimple:
            mergedList.append(kindleHL)

        for simp in mergedList:
            simp.print()

    def getRefText(self, text):
        pass

    def cleanTruncatedText(truncatedText):
        pass

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
        

