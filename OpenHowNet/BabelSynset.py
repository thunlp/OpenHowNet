"""
BabelSynset Class
==================
"""

from .Download import get_resource


class BabelSynset(object):
    """BabelSynset class.

    Attributes:
        id (str): The unique identity of the BabelSynset in BabelNet.
        cat (str): The category of the BabelSynset
        en_synonyms (list): The English synonyms in the BabelSynset.
        zh_synonyms (list): The Chinese synonyms in the BabelSynset.
        en_glosses (list): The English glosses in the BabelSynset.
        zh_glosses (list): The Chinese glosses in the BabelSynset.
        related_synsets (dict):
            The related BabelSynsets and the corresponding relations.
        sememes (list):
            The sememes labeled to the BabelSynset.
    """

    def __init__(self, babel_synset):
        """Initialize an BabelSynset instance.
        """
        self.id = babel_synset['bn']
        self.pos = babel_synset['pos']
        self.en_synonyms = babel_synset['en_synonyms']
        self.zh_synonyms = babel_synset['zh_synonyms']
        self.en_glosses = babel_synset['en_glosses']
        self.zh_glosses = babel_synset['zh_glosses']
        self.sememes = []
        self.image_urls = babel_synset['image_urls']

    def __repr__(self):
        """Define how to print the babel synset.
        """
        res = self.id + '|' + \
            self.en_synonyms[0] if len(self.en_synonyms) > 0 else id + '|'
        res += '|' + self.zh_synonyms[0] if len(self.zh_synonyms) > 0 else ''
        return res

    def get_sememe_list(self):
        return self.sememes
    
    def get_image_url_list(self):
        return self.image_urls
