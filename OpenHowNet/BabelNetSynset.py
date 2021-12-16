"""
BabelNetSynset Class
=======================
"""


class BabelNetSynset(object):
    """BabelNet synset class.
    Contains the abundant information in the BabelNet.

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

    def __init__(self, babelnet_synset):
        """Initialize an BabelNetSynset instance.
        """
        self.id = babelnet_synset['bn']
        self.pos = babelnet_synset['pos']
        self.en_synonyms = babelnet_synset['en_synonyms']
        self.zh_synonyms = babelnet_synset['zh_synonyms']
        self.en_glosses = babelnet_synset['en_glosses']
        self.zh_glosses = babelnet_synset['zh_glosses']
        self.sememes = []
        self.image_urls = babelnet_synset['image_urls']
        self.related_synsets = {}

    def __repr__(self):
        """Define how to print the BabelNet synset.
        """
        res = self.id + '|' + \
            self.en_synonyms[0] if len(self.en_synonyms) > 0 else id + '|'
        res += '|' + self.zh_synonyms[0] if len(self.zh_synonyms) > 0 else ''
        return res

    def get_sememe_list(self):
        """Get the sememe list labeled to the synset.
        """
        return self.sememes

    def get_image_url_list(self):
        """Get the image url list of the synset.
        """
        return self.image_urls

    def get_related_synsets(self, relation=None, return_triples=False):
        """Get the synsets related with the synset.
        You can set the relation to get the synsets that have the exact relation with the synset.

        Args:
            relation(`str`) : set the relation between target synset and retrieved synsets.
            return_triples(`bool`) : whether to return the triples or the synsets.
        """
        res = set()
        if relation:
            res = list()
            if relation not in self.related_synsets.keys():
                return res
            if return_triples:
                res.extend([(self, relation, s)
                           for s in self.related_synsets[relation]])
            else:
                res = self.related_synsets[relation]
        else:
            if return_triples:
                for k in self.related_synsets.keys():
                    res |= set([(self, k, v) for v in self.related_synsets[k]])
            else:
                for k in self.related_synsets.keys():
                    res |= set(self.related_synsets[k])
        return list(res)
