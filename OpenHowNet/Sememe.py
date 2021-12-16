"""
Sememe Class
=============
"""


class Sememe(object):
    """Sememe class.
    The smallest semantic unit. Described in English and Chinese.

    Attributes:
        en (str): English word to describe the sememe.
        zh (str): Chinese word to describe the sememe.
        freq (int): 
            the sememe occurence frequency in HowNet.
        related_sememes (dict): 
            the sememes related with the sememe in HowNet.
    """

    def __init__(self, hownet_sememe, freq):
        """Initialize a sememe by sememe annotations.

        Args:
            hownet_sememe (str): 
                An sememe in HowNet in the form of (English annotation|Chinese annotation).
            freq (int): 
                the sememe occurence frequency in HowNet.
        """
        self.en, self.zh = hownet_sememe.split('|')
        self.en_zh = hownet_sememe
        self.freq = freq
        self.related_sememes = {}
        self.senses = []

    def __repr__(self):
        """Define how to print the sememe.
        """
        return self.en_zh

    def get_senses(self):
        """Get the senses annotated with the sememe.
        Initialized by HowNetDict.__init__()

        Returns:
            (`list[Sense]`) the list of the senses annotated with the sememe.
        """
        return self.senses

    def get_related_sememes(self, relation=None, return_triples=False):
        """Get the sememes related with the sememe.

        Args:
            relation (`str`) : set the limitation on the relation between target sememe and the retrieved sememes.
            return_triples (`bool`):
                you can choose to return the list of triples or return the list of related sememes.

        Returns:
            (`list`) the list of triples or return the list of related sememes.
        """
        res = set()
        if relation:
            if relation in self.related_sememes.keys():
                if return_triples:
                    res |= set([(self, relation, i)
                                for i in self.related_sememes[relation]])
                else:
                    res |= set(self.related_sememes[relation])
        else:
            if return_triples:
                for k, v in self.related_sememes.items():
                    res |= set([(self, k, i) for i in v])
            else:
                for i in self.related_sememes.values():
                    res |= set(i)
        return list(res)
