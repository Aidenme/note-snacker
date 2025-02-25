from splinter import Browser
from bs4 import BeautifulSoup

class Book:
    def __init__(self, title, author, button, browser):
        self.title = title
        self.author = author
        self.button = button
        self.browser = browser
        self.soup = None
        self.selected = False
        self.highlightCount = 0

    def __str__(self):
        return self.title
    
    def select(self):
        self.button.click()
        self.selected = True

    def checkSoup(self):
        if self.soup == None:
            print("Book is missing its soup!")
            return False
        else:
            print("Book has its soup!")
            return True

    def getSoup(self):
        self.soup = BeautifulSoup(self.browser.html, 'lxml')

    def getHighlightCount(self, soup):
            highlightDivs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
            highlightCount = len(highlightDivs) - 1 #subtract one because the first div is not a highlight
            print("getSoupHighlightCount Result:")
            print(highlightCount)
            return highlightCount

    def createHighlightList(self, soup):
            divs = soup.find_all('div', {'class': 'kp-notebook-row-separator'})
            print('Divs found on initial list creation:')
            print(len(divs))
            #highlightList = []

    def updateHighlightList(self):
        pass

    def load(self):
        self.getSoup()
        self.highlightCount = self.getHighlightCount(self.soup)
        self.createHighlightList(self.soup)
