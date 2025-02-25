from bs4 import BeautifulSoup

class Highlight:
    def __init__(self, div):
        self.div = div
        self.note = None
        self.color = None
        self.truncated = False
        self.deleted = False
        self.makeHighlightFromDiv(div)

    def makeHighlightFromDiv(div):
        pass
