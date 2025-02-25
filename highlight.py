from bs4 import BeautifulSoup

class Highlight:
    def __init__(self, div):
        self.div = div
        self.text = None
        self.note = None
        self.color = None
        self.id = None
        self.truncated = False
        self.deleted = False
        self.makeHighlightFromDiv(div)

    def makeHighlightFromDiv(self, div):
        pass
