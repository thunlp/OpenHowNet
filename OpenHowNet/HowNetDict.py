"""
HowNetDict Class
=================
"""

import os
import pickle
import sys
from typing import Dict, Any

from anytree import Node, RenderTree
from anytree.exporter import DictExporter, JsonExporter

from .Sense import Sense
from .Sememe import Sememe
from .SememeTreeParser import GenSememeTree
from .Download import get_resource


class HowNetDict(object):
    """Class for running the OpenHowNet API.
    Provides a convenient way to search information in HowNet,
    display sememe trees, calculate word similarity via sememes, etc.

    Example::

        >>> # Initialize the OpenHowNet
        >>> import OpenHowNet
        >>> hownet_dict = OpenHowNet.HowNetDict()

        >>> # Search a word in HowNet and get a list of senses contain the word
        >>> result_list = hownet_dict.get("苹果")

        >>> # Visualize the sememe tree of the sense
        >>> hownet_dict.get_sememes_by_word('苹果', display='visual')

    """

    def __init__(self):
        '''Initialize HowNetDict
        '''
        try:
            package_directory = os.path.dirname(os.path.abspath(__file__))
            sememe_dir, sememe_triples_dir, data_dir = [os.path.join(package_directory, file_name) for file_name in [
                'resources/sememe_all', 'resources/sememe_triples_taxonomy.txt', 'resources/HowNet_dict_complete']]

            # Initialize sememe list from sememe_all.
            self.sememe_dic = dict()
            self.sememe_relation_dic = dict()
            with get_resource(sememe_dir, 'rb') as sememe_dict:
                sememe_all = pickle.load(sememe_dict)
            sememe_dict.close()
            for k, v in sememe_all.items():
                self.sememe_dic[k] = Sememe(k, v)
            sememe_triples = get_resource(sememe_triples_dir, "r")
            for line in sememe_triples.readlines():
                line = line.strip().split(" ")
                self.sememe_dic[line[0]].add_related_sememes_forward(
                    self.sememe_dic[line[0]], line[1], self.sememe_dic[line[2]])
                self.sememe_dic[line[2]].add_related_sememes_backward(
                    self.sememe_dic[line[0]], line[1], self.sememe_dic[line[2]])
                self.sememe_relation_dic[(
                    line[0], line[2])] = line[1]
            sememe_triples.close()

            # Initialize sense list from HowNet_dict_complete
            self.sense_dic = dict()
            with get_resource(data_dir, 'rb') as origin_dict:
                hownet_dict = pickle.load(origin_dict)
            origin_dict.close()
            for k, v in hownet_dict.items():
                self.sense_dic[k] = Sense(v)
                self.sense_dic[k].sememes = self._gen_sememe_list(
                    self.sense_dic[k])
                for s in self.sense_dic[k].sememes.values():
                    s.senses.append(self.sense_dic[k])

            # Initialize the sense dic to retrieve by word.
            self.en_map = dict()
            self.zh_map = dict()
            for k in self.sense_dic.keys():
                en_word = self.sense_dic[k].en_word.strip()
                zh_word = self.sense_dic[k].ch_word.strip()
                if en_word not in self.en_map:
                    self.en_map[en_word] = list()
                self.en_map[en_word].append(self.sense_dic[k])
                if zh_word not in self.zh_map:
                    self.zh_map[zh_word] = list()
                self.zh_map[zh_word].append(self.sense_dic[k])

        except FileNotFoundError as e:
            print(e)

    def __getitem__(self, item):
        """Shortcut for Get(self,item,None)

        Args:
            item (`str`):
                target word. if item == '*', return the list of all senses.

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = list()
        if item == "*":
            for item in self.sense_dic.values():
                res.append(item)
            return res
        if item in self.en_map:
            res.extend(self.en_map[item])
        elif item in self.zh_map:
            res.extend(self.zh_map[item])
        elif item in self.sense_dic:
            res.append(self.sense_dic[item])
        return res

    def __len__(self):
        """Get the num of the concepts in HowNet.

        Returns:
            (`Int`): the num of the concepts in HowNet.
        """
        return len(self.sense_dic)

    def get(self, word, language=None):
        """Common word search API, you can specify the language of the target word to boost the search performance

        Args:
            word (`str`): target word.
            language (`str`): target language, default: None. (The func will search both in English and Chinese, which will consume a lot of time.)

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = list()
        if language == "en":
            if (word in self.en_map):
                res = self.en_map[word]
        elif language == "zh":
            if (word in self.zh_map):
                res = self.zh_map[word]
        else:
            res = self[word]
        return res

    def get_zh_words(self):
        """Get all Chinese words annotated in HowNet

        Returns:
            (`list`) All annotated Chinese words in HowNet.
        """
        return list(self.zh_map.keys())

    def get_en_words(self):
        """Get all English words annotated in HowNet

        Returns:
            (`list`) All annotated English words in HowNet.
        """
        return list(self.en_map.keys())

    def sememe_fuzzy_match(self, s):
        """To fuzzy match the sememe by english/language word.

        Args:
            s (`str`):
                the string to match the sememe.

        Returns:
            (`list[Sememe]`) the sememe list which is annotated with s.
        """
        res = []
        for k in self.sememe_dic.keys():
            if k.find(s) != -1:
                res.append(k)
        return res

    def _gen_sememe_list(self, sense):
        """Get sememe list for the sense by the Def.

        Args:
            sense(`Sense`):
                the sense to generate sememe tree.

        Returns:
            (`list[Sememe]`) the sememe list of the sense.
        """
        kdml = sense.Def
        res = dict()
        for i in range(len(kdml)):
            if kdml[i] == '|':
                start_idx = i
                end_idx = i
                while kdml[start_idx] not in ['{', '"']:
                    start_idx = start_idx - 1
                while kdml[end_idx] not in ['}', ':', '"']:
                    end_idx = end_idx + 1
                res[kdml[start_idx + 1:end_idx].replace(' ', '_')
                    ] = self.sememe_dic[kdml[start_idx + 1:end_idx].replace(' ', '_')]
        return res

    def get_senses_by_word(self, word):
        """Commen sense search API.

        Args:
            word (`str`):
                Specific word(en/zh/id) you want to search in HowNet.

        Returns:
            (`list[Sense]`) the list of Sense.
        """
        return self[word]

    def get_sememes_by_word(self, word, display='dict', merge=False, expanded_layer=-1, K=None):
        """Commen sememe search API.
        Given specific word, you can get corresponding HowNet annotations.

        Args:
            word (`str`):
                Specific word(en/zh/id) you want to search in HowNet. You can use "*" to specify that you need annotations of all words.
            display (`str`):
                How to display the sememes you retrieved, you can choose from tree/dict/list/visual.
            merge (`bool`):
                Only works when display == 'list'. Decide whether to merge multi-sense word query results into one
            expanded_layer (`int`):
                Only works when display == 'list'. Continously expand k layer. By default, it will be set to -1 (expand full layers)
            K (`int`):
                Only works when display == 'visual'.The maximum number of visualized words, ordered by id (ascending).
                Illegal number will be automatically ignored and the function will display all retrieved results.

        Examples:

            >>> # Returns the sememe tree of the retrieved senses in the form of dict
            >>> hownet_dict.get_sememes_by_word('苹果')

            >>> # Returns the root node of sememe tree of the retrieved senses in the form of anytree
            >>> hownet_dict.get_sememes_by_word('苹果', display='tree')

            >>> # Returns the sememe list of the retrieved senses separately
            >>> hownet_dict.get_sememes_by_word('苹果', display='list')

            >>> # Returns the sememe list of the retrieved senses merged into one
            >>> hownet_dict.get_sememes_by_word('苹果', display='list', merge=True)

            >>> # Visualize the sememe tree
            >>> hownet_dict.get_sememes_by_word('苹果', display='visual')

        """
        queryResult = self[word]
        queryResult.sort(key=lambda x: x.No)
        result = set() if merge else list()
        if display == 'dict' or display == 'tree':
            for item in queryResult:
                try:
                    result.append({'sense': item, 'sememes': item.gen_sememe_tree(
                        return_node=display == 'tree')})
                except Exception as e:
                    print("Generate Sememe Tree Failed for", item.No)
                    print("Exception:", e)
                    continue
        elif display == 'list':
            for item in queryResult:
                try:
                    if not merge:
                        result.append(
                            {"sense": item,
                             "sememes": item.get_sememe_list(expanded_layer)})
                    else:
                        result |= set(item.get_sememe_list(expanded_layer))
                except Exception as e:
                    print(word)
                    print("Wrong Item:", item)
                    print("Exception:", e)
                    raise e
        elif display == 'visual':
            print("Find {0} result(s)".format(len(queryResult)))
            if K is not None and K >= 1 and type(K) == int:
                queryResult = queryResult[:K]
            for index, item in enumerate(queryResult):
                print("Display #{0} sememe tree".format(index))
                item.visualize_sememe_tree()
        else:
            print("Wrong display mode: ", display)
        return result

    def __str__(self):
        return str(type(self))

    def has(self, item, language=None):
        """Check that whether certain word(English Word/Chinese Word/ID) exist in HowNet
        Only perform exact match because HowNet is case-sensitive
        By default, it will search the target word in both the English vocabulary and the Chinese vocabulary

        Args:
            item (`str`):
                target word to be searched in HowNet
            language (`str`):
                specify the language of the target search word
        Returns:
            (`bool`) whether the word exists in HowNet annotation
        """
        if language == "en":
            return item in self.en_map
        elif language == "zh":
            return item in self.zh_map

        return item in self.en_map or item in self.zh_map or item in self.sense_dic

    def get_all_sememes(self):
        """Get the complete sememe dict in HowNet

        Returns:
            (`dict`) a dict of all sememes
        """
        return self.sememe_dic

    # Sememe relation
    def get_sememe_relation(self, x, y, return_triples=False):
        """Show relationship between two sememes.

        Returns:
            (`list`) a list contains sememe triples. x is the head sememe and y is the tail sememe.
        """
        res = []
        sememe_x = self.sememe_fuzzy_match(x)
        sememe_y = self.sememe_fuzzy_match(y)
        for s_x in sememe_x:
            for s_y in sememe_y:
                if (s_x, s_y) in self.sememe_relation_dic.keys():
                    if return_triples:
                        res.append((self.sememe_dic[s_x], self.sememe_relation_dic[(
                            s_x, s_y)], self.sememe_dic[s_y]))
                    else:
                        res.append(self.sememe_relation_dic[(
                            s_x, s_y)])
        return res

    def get_sememe_via_relation(self, x, relation, return_triples=False):
        """Show all sememes that x has relation with.

        Returns:
            (`list[Sememe]`) a string represents all related sememes.
        """
        res = []
        sememe_x = self.sememe_fuzzy_match(x)
        for s_x in sememe_x:
            res.extend(self.sememe_dic[s_x].get_sememe_via_relation(
                relation, return_triples=return_triples))
        return res

    def get_related_sememes(self, x, return_triples=False):
        """Show all sememes that x has any relation with.

        Returns:
            (`list`) a list contains sememe triples.
        """
        res = []
        sememe_x = self.sememe_fuzzy_match(x)
        for s_x in sememe_x:
            res.extend(s_x.get_related_sememes(return_triples=return_triples))
        return res

    def get_senses_by_sememe(self, x):
        """Get the senses labeled by sememe x.

        Args:
            x (`str`):
                Target sememe
        Returns:
            (`list[Sense]`) The list of senses which contains No, ch_word and en_word.
        """
        res = []
        sememe_x = self.sememe_fuzzy_match(x)
        for s_x in sememe_x:
            res.extend(self.sememe_dic[s_x].senses)
        return res

    # Sememe similarity calculation
    def initialize_sememe_similarity_calculation(self):
        """Initialize the word similarity calculation via sememes.
        Implementation is contributed by Jun Yan, which is based on the paper :
        "Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP"

        Returns: 
            (`bool`) whether the initialization succeed.
        """
        sememe_sim_table_pickle_path = 'resources/sememe_sim_table.pkl'
        sense_tree_path = 'resources/sense_tree'
        sense_syn_path = 'resources/synonym'

        package_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            self.sememe_sim_table = pickle.load(
                get_resource(os.path.join(package_directory, sememe_sim_table_pickle_path), "rb"))
            self.sense_tree_dic = pickle.load(
                get_resource(os.path.join(package_directory, sense_tree_path), 'rb'))
            self.sense_syn_dic = pickle.load(
                get_resource(os.path.join(package_directory, sense_synonym_path), 'rb'))
        except FileNotFoundError as e:
            print(
                "Enabling Word Similarity Calculation requires specific data files, please check the completeness of your download package.")
            print(e)
            return False
        return True

    def sense_similarity(self, node1, node2, sememe_sim_table):
        """Calculate the similarity between two senses.
        """
        delta = 0.1
        beta_relation = 0.3
        beta_sememe = 0.7

        relation_sim = 0
        if node1.is_leaf and node2.is_leaf:
            beta_relation = 0
            beta_sememe = 1
        else:
            role_match = 0
            N = len(node1.children) + len(node2.children)
            flag1 = [1] * len(node1.children)
            flag2 = [1] * len(node2.children)
            for i in range(len(node1.children)):
                for j in range(len(node2.children)):
                    if node1.children[i].role == node2.children[j].role and flag1[i] == 1 and flag2[j] == 1:
                        flag1[i] = 0
                        flag2[j] = 0
                        role_match = role_match + 1
                        relation_sim = relation_sim + \
                            self.sense_similarity(
                                node1.children[i], node2.children[j], sememe_sim_table)
            relation_sim = relation_sim + (sum(flag1) + sum(flag2)) * delta
            relation_sim = relation_sim / (N - role_match)

        if (node1.name, node2.name) in sememe_sim_table:
            sememe_sim = sememe_sim_table[(node1.name, node2.name)]
        else:
            sememe_sim = sememe_sim_table[(node2.name, node1.name)]
        return beta_relation * relation_sim + beta_sememe * sememe_sim

    def get_nearest_words_via_sememes(self, word, K=10):
        """
        Get the topK nearest words of the given word, the word similarity is calculated based on HowNet annotation.
        If the given word does not exist in HowNet annotations, this function will return an empty list.
        Args: 
            word (`str`): 
                target word
            K (`int`): 
                specify the number of the nearest words you want to retrieve.
        Returns: 
            (`list`) a list of the nearest K words.
            If the given word does not exist in HowNet annotations, this function will return an empty list.
            If the initialization method of word similarity calculation has not been called yet, it will also return an empty list and print corresponding error message.
        """
        res = list()
        if not hasattr(self, "sense_tree_dic") or not hasattr(self, "sememe_sim_table"):
            print("Please initialize the similarity calculation firstly!")
            return res
        if self.sense_tree_dic is None or self.sememe_sim_table is None:
            print("Please initialize the similarity calculation firstly!")
            return res
        if not self.has(word):
            print(word + ' is not annotated in HowNet.')
            return res
        sense_list = self[word]
        banned_id = [i.No for i in sense_list]
        for i in sense_list:
            tree1 = self.sense_tree_dic[i.No]
            score = {}
            for j in self.sense_dic.keys():
                if j not in banned_id and int(j) >= 3378:
                    tree2 = self.sense_tree_dic[j]
                    sim = self.sense_similarity(
                        tree1, tree2, self.sememe_sim_table)
                    score[self.sense_dic[j]] = sim
            result = sorted(score.items(), key=lambda x: x[1], reverse=True)
            topK = result[0:K]
            queryRes = dict()
            queryRes["sense"] = i
            queryRes["synset"] = topK
            res.append(queryRes)
        return res

    def calculate_word_similarity(self, word0, word1):
        """Calculate the word similarity between two words via sememes
        Args:
            word0 (`str`): 
                target word #0
            word1 (`str`): 
                target word #1
        Returns: 
            (`float`) the word similarity calculated via sememes.
            If word0 or word1 does not exist in HowNet annotation, it will return 0.0
            If the initialization method of word similarity calculation has not been called yet, it will also return 0.0 and print corresponding error message.
        """
        res = 0.0
        if not hasattr(self, "sense_tree_dic") or not hasattr(self, "sememe_sim_table"):
            print("Please initialize the similarity calculation firstly!")
            return res
        if self.sense_tree_dic is None or self.sememe_sim_table is None:
            print("Please initialize the similarity calculation firstly!")
            return res
        if not self.has(word0):
            print(word0 + ' is not annotated in HowNet.')
            return res
        if not self.has(word1):
            print(word1 + ' is not annotated in HowNet.')
            return res
        senses1 = self[word0]
        senses2 = self[word1]
        max_sim = -1
        for id1 in senses1:
            for id2 in senses2:
                sim = self.sense_similarity(
                    self.sense_tree_dic[id1.No], self.sense_tree_dic[id2.No],  self.sememe_sim_table)
                if sim > max_sim:
                    max_sim = sim
        return max_sim

    def get_sense_synonyms(self, sense):
        """Get the senses that have the same sememe annotation with the sense

        Returns:
            (`list[Sense]`) the list of senses that have the same sememe annotation with the sense.
        """
        ss = sense.get_sememe_list()
        ll = list(ss)
        ll = [i.en_ch for i in ll]
        ll.sort()
        k = '_'.join(ll)
        return [self.sense_dic[i] for i in self.sense_syn_dic[k]]
