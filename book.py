from splinter import Browser
from bs4 import BeautifulSoup

class Book:
    def __init__(self, title, author, button, browser):
        self.title = title
        self.author = author
        self.button = button
        self.browser = browser
        self.soup = None

    def __str__(self):
        return self.title
    
    def select(self):
        self.button.click()

    def checkSoup(self):
        if self.soup == None:
            print("Book is missing its soup!")
            return False
        else:
            print("Book has its soup!")
            return True
        
    def setSoup(self, soup):
        self.soup = soup

    def getSoup(self, browser):
        self.soup = BeautifulSoup(browser.html, 'lxml')
