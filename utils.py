from io import BytesIO
import os
from xml.etree.ElementTree import Element, ElementTree


DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE')


class XML:
    """Convenience wrapper around ElementTree for JSX-like syntax"""

    def __init__(self, tag, *children, **attributes):
        self.element = Element(tag, **attributes)

        for child in children:
            if isinstance(child, XML):
                self.element.append(child.element)
            else:
                self.element.text = (self.element.text or '') + str(child)

    def __bytes__(self):
        document = BytesIO()
        tree = ElementTree(self.element)
        tree.write(document, encoding='utf-8', xml_declaration=True)
        return document.getvalue()
