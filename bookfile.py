import re
import sys
import config
from bs4 import BeautifulSoup

class Bookfile:
    def __init__(self, book):
        self.book = book
        self.pathName = config.BOOK_STORAGE_FOLDER + self.getFileName(book)
        self.header = self.getHeader()
        self.createBookfile(self.book)
        self.kindleLocalHL = self.kindleHLtoLocalHL(book.highlightList)
        self.HTMLLocalHL = self.HTMLHLtoLocalHL(self.pathName)
        #self.ender = self.getEnder()
        self.localList = []
        #self.updateLocalList(self.kindleLocalHL, self.HTMLLocalHL)
        #self.compareLists(self.HTMLLocalHL, self.kindleLocalHL)


    def getFileName(self, book):
        regxPattern = '[^A-Za-z0-9 ]+'
        
        #Removes characters that don't work in file names and shortens the title to 30 characters in total
        cleanTitle = re.sub(regxPattern, '', book.title[:30])
        
        #Same as above, but also removed the 'By: ' text the kindle notebook puts in front of author names
        cleanAuthor = re.sub(regxPattern, '', book.author[4:30])
        fileName = cleanTitle + " - " + cleanAuthor + ".html"

        print(fileName)
        
        return fileName

    def createBookfile(self, book):
        
        #CODING QUESTION: Modularity wise when I create a book I should just create the file name directly from the book I think.
        #On the other hand I don't want to have to do that again when I have to reference the book again. Actually, I'm just going to
        #Have to recreate the filename from the book anyway to tie this reference to the local html file again after the program closes.
        #The solution then is to just have the filename get generated from the book each time and not necessarily store it as a class variable.
        self.export(self.getFileName(book), book.highlightList, config.BOOK_STORAGE_FOLDER)

    def export(self, fileName, highlightList, exportFolder):
        mergeHighlights = False
        f = open(exportFolder + fileName , mode='a', encoding='utf-8', errors='replace')
        f.write(self.header)

        for highlight in highlightList:

            #Toggle "part of a multi-part highlight" on and off
            if highlight.color == 'Yellow':
                mergeHighlights = not mergeHighlights

            if highlight.truncated:
                f.write('<div class="text ' + highlight.color + ' true">')
            else:
                f.write('<div class="text ' + highlight.color + ' false">')

            f.write(highlight.text)

            f.write('<div class="note">')

            if highlight.note:    

                f.write(highlight.note)

            #Close note div
            f.write('</div>\n')

            #Close the individual highlight's div
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

    def kindleHLtoLocalHL(self, bookHighlights):
        kindleHighlights = []
        for highlight in bookHighlights:
            localHighlight = {
                'truncated': highlight.truncated,
                'color': highlight.color,
                'text': highlight.text,
                'note': highlight.note
            }
            #print(localHighlight['text'])
            #print('/n')
            
            kindleHighlights.append(localHighlight)
        
        return kindleHighlights
    
    def HTMLHLtoLocalHL(self, filePath):
        localHighlights = []
        htmlFile = open(filePath, mode='r', encoding='utf-8')
        soup = BeautifulSoup(htmlFile, 'lxml')
        htmlFile.close()

        for div in soup.findAll('div'):
            
            localHighlight = {}
            
            if div.attrs['class'][0] == 'text':
                localHighlight['truncated'] = div.attrs['class'][2]
                localHighlight['color'] = div.attrs['class'][1]
                localHighlight['text'] = div.text
            
            if div.attrs['class'][0] == 'note':
                localHighlight['note'] = div.text

            print(localHighlight)
            print()
            
            localHighlights.append(localHighlight)

        return localHighlights

    def updateLocalList(self, kindleList, HTMLList):

        for localHighlight in HTMLList:
            if localHighlight['text'][:25] in kindleList['text'][:20]:
                print('Found kindle highlight:')
                print('Searched using\n')
                print(localHighlight['text'][20])
                print()
                print("Found text:\n")
                print(kindleList['text'])
                print('\n')

    def getRefText(self, text):
        pass

    def cleanTruncatedText(truncatedText):
        pass

    def compareLists(self, HTMLList, kindleList):
        print("Local list length:")
        print(len(HTMLList))
        print("kindle list length:")
        print(len(kindleList))
        for dict in HTMLList:
            print(dict)
            print('')
        print(HTMLList == kindleList)
