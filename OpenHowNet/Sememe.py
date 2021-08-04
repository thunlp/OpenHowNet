"""
Sememe Class
=============
"""

class Sememe(object):
    """Sememe class.

    The smallest semantic unit. Described in English and Chinese.

    Attributes:
        en: English word to describe the sememe.
        ch: Chinese word to describe the sememe.
        freq: the sememe occurence frequency in HowNet.
        related_sememes_forward: the sememes related with the sememe in HowNet and the sememe is head sememe in triples.
        related_sememes_backward: the sememes related with the sememe in HowNet and the sememe is tail sememe in triples.
    """

    def __init__(self, hownet_sememe, freq):
        """Initialize a sememe by sememe annotations.

        :param hownet_sememe: sememe annotiation in HowNet.
        :param freq: sememe occurence freqency.
        """
        self.en, self.ch = hownet_sememe.split('|')
        self.en_ch = hownet_sememe
        self.freq = freq
        self.related_sememes_forward = {}
        self.related_sememes_backward = {}
        self.senses = []

    def __repr__(self):
        """
        Define how to print the sememe.
        """
        return self.en_ch

    def add_related_sememes_forward(self, head, relation, tail):
        """Add a sememe triple to the sememe.

        Sememe triple contains (head sememe, relation, tail sememe).
        """
        self.related_sememes_forward[relation] = tail

    def add_related_sememes_backward(self, head, relation, tail):
        """Add a sememe triple to the sememe.

        Sememe triple contains (head sememe, relation, tail sememe).
        """
        self.related_sememes_backward[relation] = head