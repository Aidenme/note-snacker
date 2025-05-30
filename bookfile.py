import re

class Bookfile:
    def __init__(self, book):
        self.book = book
        self.fileName = self.getFileName(self.book)
        self.makeBookfile()

    def getFileName(self, book):
        regxPattern = '[^A-Za-z0-9 ]+'
        
        #Removes characters that don't work in file names and shortens the title to 30 characters in total
        cleanTitle = re.sub(regxPattern, '', book.title[:30])
        
        #Same as above, but also removed the 'By: ' text the kindle notebook puts in front of author names
        cleanAuthor = re.sub(regxPattern, '', book.author[4:30])
        fileName = cleanTitle + " - " + cleanAuthor + ".html"

        print(fileName)
        
        return fileName

    def makeBookfile(self):
        pass
        
