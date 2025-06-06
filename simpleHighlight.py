from bs4 import BeautifulSoup

class SimpleHighlight:
    def __init__(self, advHighlight, type):
        if type == 'kindle':
            self.createFromKindleHL(advHighlight)
        if type == 'html':
            self.createFromHTML(advHighlight)
        self.truncated
        self.color
        self.text
        self.note
    
    def createFromKindleHL(self, kindleHighlight):
        self.color = kindleHighlight.color
        self.truncated = kindleHighlight.truncated
        self.text = kindleHighlight.text
        self.note = kindleHighlight.note

    def createFromHTML(self, div):
        self.truncated = eval(div.attrs['class'][2])
        self.color = div.attrs['class'][1]
        self.text = div.text
        self.note = div.find('div', {'class': 'note'}).text