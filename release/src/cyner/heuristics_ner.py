r"""
Retrieved from:
https://github.com/aiforsec/CyNER/blob/main/cyner/heuristics_ner.py
this class has been modified to improve the regex rules, 
which makes regex match keyword more reasonable.
"""
from re import finditer

from .entity_extraction import EntityExtraction
from .entity import Entity


class HeuristicsNER(EntityExtraction):
    """
    Cybersecurity entity extraction using Heuristics
    Most are based on the paper "Cybersecurity Named Entity Recognition Using Multi-Modal Ensemble Learning"
    https://ieeexplore.ieee.org/document/9051704
    URL - https://stackoverflow.com/a/17773849/5131287
    IPv4 - https://stackoverflow.com/a/36760050/5131287
    IPv6 - https://stackoverflow.com/a/17871737/5131287

    """
    def __init__(self, config):
        super().__init__(config)
        self.patterns = {
            'URL': [r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', r"https?:[a-zA-Z0-9_.+-/#~]+ "],
            'Filepath': [r'[a-zA-Z]:\\([0-9a-zA-Z]+)', r'(\/[^\s\n]+)+'],
            'Email': [r'[a-z][_a-z0-9-.]+@[a-z0-9-.]+[a-z]+'],
            'IPv6': [r'(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))'],
            'IPv4': [r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$'],
            'CVE': [r'CVE—[0-9]{4}—[0-9]{4,6}'],
            'UUID':[r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'],
            'HEX':[r'[a-f0-9]{4,}',r'[A-F0-9]{4,}'],
            'Protocol': ['HTTP', 'SMS', 'HTTPS', 'AES'],
            'IPAddress': ['r"^\d{1,3}\[.]\d{1,3}\.\d{1,3}\.\d{1,3}$"'],
            'Domain': ['"^(((([A-Za-z0-9]+){1,63}\.)|(([A-Za-z0-9]+(\-)+[A-Za-z0-9]+){1,63}\.))+){1,255}$"',
                       '(//|\s+|^)(\w\.|\w[A-Za-z0-9-]{0,61}\w\.){1,3}[A-Za-z]{2,6}'],
            'Filename': [r'[A-Za-z0-9-_\.]+\.[a-z]{2,4}',
                        '^[a-zA-Z0-9](?:[a-zA-Z0-9 ._-]*[a-zA-Z0-9])?\.[a-zA-Z0-9_-]+$',
                         "^([A-Za-z]{1}[A-Za-z\\d_]*\\.)+[A-Za-z][A-Za-z\\d_]*$"],
        }

    def train(self):
        pass

    def get_entities(self, text):
        entities = []
        for label, pattern in self.patterns.items():
            for p in pattern:
                for match in finditer(p, text):
                    entities.append(Entity(match.span()[0], match.span()[1], match.group(), label))
        return entities
