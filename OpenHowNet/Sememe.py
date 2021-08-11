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
        related_sememes_forward (dict): 
            the sememes related with the sememe in HowNet and the sememe is head sememe in triples.
        related_sememes_backward (dict): 
            the sememes related with the sememe in HowNet and the sememe is tail sememe in triples.

    Args:
        hownet_sememe (str):
            An sememe in HowNet in the form of (English annotation|Chinese annotation).
        freq (int):
            the sememe occurence frequency in HowNet.
    """

    def __init__(self, hownet_sememe, freq):
        """Initialize a sememe by sememe annotations.
        """
        self.en, self.zh = hownet_sememe.split('|')
        self.en_zh = hownet_sememe
        self.freq = freq
        self.related_sememes_forward = {}
        self.related_sememes_backward = {}
        self.senses = []

    def __repr__(self):
        """Define how to print the sememe.
        """
        return self.en_zh

    def add_related_sememes_forward(self, head, relation, tail):
        """Add a sememe triple to the sememe.

        Sememe triple contains (head sememe, relation, tail sememe).
        """
        if relation not in self.related_sememes_forward.keys():
            self.related_sememes_forward[relation] = []
        self.related_sememes_forward[relation].append(tail)

    def add_related_sememes_backward(self, head, relation, tail):
        """Add a sememe triple to the sememe.

        Sememe triple contains (head sememe, relation, tail sememe).
        """
        if relation not in self.related_sememes_backward.keys():
            self.related_sememes_backward[relation] = []
        self.related_sememes_backward[relation].append(head)

    def get_senses(self):
        """Get the senses annotated with the sememe.

        Returns:
            (`list[Sense]`) the list of the senses annotated with the sememe.
        """
        return self.senses

    def get_related_sememes(self, return_triples=False):
        """Get the sememes related with the sememe.

        Args:
            return_triples (`bool`):
                You can choose to return the list of triples or return the list of related sememes.

        Returns:
            (`list`) the list of triples or return the list of related sememes.
        """
        res = []
        if return_triples:
            for k, v in self.related_sememes_forward.items():
                res.extend([(self, k, i) for i in v])
            for k, v in self.related_sememes_backward.items():
                res.extend([(i, k, self) for i in v])
        else:
            for i in self.related_sememes_forward.values():
                res.extend(i)
        return res
    
    def get_sememe_via_relation(self, relation, return_triples=False):
        """Get the sememes that have relation with the sememe.

        Args:
            relation (`str`):
                The relation between the sememes to search and the sememe.
            return_triples (`bool`):
                You can choose to return the list of triples or return the list of related sememes.
        
        Returns:
            (`list`) the list of triples or the list of related sememes.
        """

        res = []
        if relation in self.related_sememes_forward.keys():
            if return_triples:
                res.extend([(self, relation, i) for i in self.related_sememes_forward[relation]])
            else:
                res.extend(self.related_sememes_forward[relation])
        return res

