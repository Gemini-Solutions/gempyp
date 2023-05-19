from lxml import etree

class CustomXMLParser(etree.XMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._comment_handler = lambda x: None