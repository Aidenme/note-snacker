import re
import sys
import config

class Bookfile:
    def __init__(self, book):
        self.book = book
        self.header = self.getHeader()
        #self.ender = self.getEnder()
        self.createBookfile(self.book)


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
                f.write('<p class="' + highlight.color + ' truncated">')
            else:
                f.write('<p class="' + highlight.color + '">')

            f.write(highlight.text)

            if highlight.note:
                f.write('<h5>')

                f.write(highlight.note)

                f.write('</h5>\n')

            f.write('</p>\n')

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