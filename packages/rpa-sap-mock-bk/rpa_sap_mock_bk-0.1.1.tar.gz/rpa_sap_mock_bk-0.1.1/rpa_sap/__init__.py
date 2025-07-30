from .sap_keywords import SAPKeywords
from robotlibcore import DynamicCore

class SAP(DynamicCore):
    def __init__(self):
        libraries = [SAPKeywords()]
        super().__init__(libraries)
