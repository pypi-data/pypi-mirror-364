from __future__ import annotations
if annotations:
    from .BaseMarker import BaseMarker

class HTMLMarker(BaseMarker):
    """A HTML Marker is presented as text"""
    def __init__(self, key: str, label: str, position: dict, html:str, anchor: dict=None, classes:list=None):
        super().__init__(key, label, position)
        self.html = html
        self.anchor = anchor
        self.classes = classes

    @staticmethod
    def _from_response(response: tuple) -> "HTMLMarker":
        """Create a HTMLMarker object from markers.json.
                Response obtained from markers.json -> MarkerSet -> Markers -> HTMLMarker"""
        key = response[0]
        response = response[1]
        label = response['label']
        position = response['position']
        HTML = response['html']
        anchor = response['anchor']
        classes = response['classes']
        return HTMLMarker(key, label, position, HTML, anchor=anchor, classes=classes)


