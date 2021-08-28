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
        >>> result_list = hownet_dict.get_sense("苹果")

        >>> # Visualize the sememe tree of the sense
        >>> hownet_dict.get_sememes_by_word('苹果', display='visual')

    """

    def __init__(self, init_sim=False):
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
                self.sense_dic[k].sememes = self.gen_sememe_list(
                    self.sense_dic[k])
                for s in self.sense_dic[k].sememes.values():
                    s.senses.append(self.sense_dic[k])

            # Initialize the sense dic to retrieve by word.
            self.en_map = dict()
            self.zh_map = dict()
            for k in self.sense_dic.keys():
                en_word = self.sense_dic[k].en_word.strip()
                zh_word = self.sense_dic[k].zh_word.strip()
                if en_word not in self.en_map:
                    self.en_map[en_word] = list()
                self.en_map[en_word].append(self.sense_dic[k])
                if zh_word not in self.zh_map:
                    self.zh_map[zh_word] = list()
                self.zh_map[zh_word].append(self.sense_dic[k])
            print('Initializing OpenHowNet succeeded!')

            # Initialize the similarity calculation
            if init_sim:
                self.initialize_similarity_calculation()
        except FileNotFoundError as e:
            print(e)

    def __getitem__(self, item):
        """Shortcut for get_sense(self,item,None)

        Args:
            item (`str`):
                target word. if item == '*', return the list of all senses.

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = set()
        if item == "*":
            for v in self.sense_dic.values():
                res.add(v)
            return list(res)
        if item in self.en_map:
            res |= set(self.en_map[item])
        if item in self.zh_map:
            res |= set(self.zh_map[item])
        if item in self.sense_dic and self.sense_dic[item] not in res:
            res.add(self.sense_dic[item])
        return list(res)

    def __len__(self):
        """Get the num of the concepts in HowNet.

        Returns:
            (`Int`): the num of the concepts in HowNet.
        """
        return len(self.sense_dic)

    def __str__(self):
        return str(type(self))

    def get_sense(self, word, language=None, pos=None, strict=True):
        """Common sense search API, you can specify the language of the target word to boost the search performance.
        Besides if you are not sure about the word, you can set `strict` to False to fuzzy match the sense.

        Args:
            word (`str`): 
                target word.
            language (`str`): 
                target language, default: None. (The func will search both in English and Chinese, which will consume a lot of time.)
                you can set to `en` or `zh`, which means search in English or Chinese.
            pos (`str`):
                the part of speech of the result.
            strict (`bool`): 
                whether to search the sense strictly.

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = set()
        if strict:
            if language == "en":
                if (word in self.en_map):
                    res |= set(self.en_map[word])
            elif language == "zh":
                if (word in self.zh_map):
                    res |= set(self.zh_map[word])
            else:
                res = self[word]
        else:
            if language == "en":
                for k in self.en_map.keys():
                    if k.find(word) != -1:
                        res |= set(self.en_map[k])
            elif language == "zh":
                for k in self.zh_map.keys():
                    if k.find(word) != -1:
                        res |= set(self.zh_map[k])
            else:
                for k in self.en_map.keys():
                    if k.find(word) != -1:
                        res |= set(self.en_map[k])
                for k in self.zh_map.keys():
                    if k.find(word) != -1:
                        res |= set(self.zh_map[k])
                for k in self.sense_dic.keys():
                    if k.find(word) != -1:
                        res.add(self.sense_dic[k])
        if pos:
            temp = res.copy()
            for i in temp:
                grammar = i.en_grammar if language == 'en' else i.zh_grammar
                if grammar != pos:
                    res.remove(i)
        return list(res)

    def get_sememe(self, word, language=None, strict=True):
        """The commen sememe search API. you can specify the language of the target word to boost the search performance.
        Besides if you are not sure about the word, you can set `strict` to False to fuzzy match the sememe.

        Args:
            word (`str`): 
                target word.
            language (`str`): 
                target language, default: None. (The func will search both in English and Chinese, which will consume a lot of time.)
                you can set to `en` or `zh`, which means search in English or Chinese
            strict (`bool`): 
                whether to search the sense strictly.

        Returns:
            (`list[Sememe]`) candidates HowNet sememes, if the target word does not exist, return an empty list.
        """
        res = []
        if strict:
            if language == 'en':
                for v in self.sememe_dic.values():
                    if v.en == word and v not in res:
                        res.append(v)
            elif language == 'zh':
                for v in self.sememe_dic.values():
                    if v.zh == word and v not in res:
                        res.append(v)
            else:
                for v in self.sememe_dic.values():
                    if (v.en == word or v.zh == word or v.en_zh == word) and v not in res:
                        res.append(v)
        else:
            if language == 'en':
                for v in self.sememe_dic.values():
                    if v.en.find(word) != -1 and v not in res:
                        res.append(v)
            elif language == 'zh':
                for v in self.sememe_dic.values():
                    if v.zh.find(word) != -1 and v not in res:
                        res.append(v)
            else:
                for v in self.sememe_dic.values():
                    if v.en_zh.find(word) != -1 and v not in res:
                        res.append(v)
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

    def gen_sememe_list(self, sense):
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
                    result.append({'sense': item, 'sememes': item.get_sememe_tree(
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
            return
        else:
            print("Wrong display mode: ", display)
        return result

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
    def get_sememe_relation(self, x, y, return_triples=False, strict=True):
        """Show relationship between two sememes.

        Args:
            x (`str`): 
                the word #0 to search the sememe.
            y (`str`): 
                the word #1 to search the sememe.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the relations.
            strict (`bool`):
                you can choose to search the sememe relation strictly by the word.
                set to False if you are not sure about the x and y.


        Returns:
            (`list`) a list contains sememe triples. x is the head sememe and y is the tail sememe.
        """
        res = []
        sememe_x = self.get_sememe(x, strict=strict)
        sememe_y = self.get_sememe(y, strict=strict)
        for s_x in sememe_x:
            for s_y in sememe_y:
                if (s_x.en_zh, s_y.en_zh) in self.sememe_relation_dic.keys():
                    if return_triples:
                        res.append(
                            (s_x, self.sememe_relation_dic[(s_x.en_zh, s_y.en_zh)], s_y))
                    else:
                        res.append(self.sememe_relation_dic[(
                            s_x.en_zh, s_y.en_zh)])
        return res

    def get_sememe_via_relation(self, x, relation, return_triples=False, strict=True):
        """Show all sememes that x has relation with.

        Args:
            x (`str`): 
                the word to search the sememe.
            relation (`str`):
                the relaiton to search the sememe.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the sememes.
            strict (`bool`):
                you can choose to search the sememe relation strictly by the word.
                set to False if you are not sure about the x.

        Returns:
            (`list[Sememe]`) a list contains all related sememes.
        """
        res = set()
        sememe_x = self.get_sememe(x, strict=strict)
        for s_x in sememe_x:
            res |= set(s_x.get_sememe_via_relation(
                relation, return_triples=return_triples))
        return list(res)

    def get_related_sememes(self, x, return_triples=False, strict=True):
        """Show all sememes that x has any relation with.

        Args:
            x (`str`): 
                the word to search the sememe.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the sememes.
            strict (`bool`):
                you can choose to search the sememe relation strictly by the word.
                set to False if you are not sure about the x.

        Returns:
            (`list`) a list contains sememe triples.
        """
        res = set()
        sememe_x = self.get_sememe(x, strict=strict)
        for s_x in sememe_x:
            res |= set(s_x.get_related_sememes(return_triples=return_triples))
        return list(res)

    def get_senses_by_sememe(self, x, strict=True):
        """Get the senses labeled by sememe x.

        Args:
            x (`str`):
                Target sememe
        Returns:
            (`list[Sense]`) The list of senses which contains No, ch_word and en_word.
        """
        res = set()
        sememe_x = self.get_sense(x, strict=strict)
        for s_x in sememe_x:
            res |= set(self.sememe_dic[s_x].senses)
        return list(res)

    # Similarity calculation
    def initialize_similarity_calculation(self):
        """Initialize the similarity calculation via sememes.
        Implementation is contributed by Jun Yan, which is based on the paper :
        "Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP"
        """
        sememe_sim_table_pickle_path = 'resources/sememe_sim_table'
        sense_tree_path = 'resources/sense_tree'
        sense_syn_path = 'resources/synonym'

        package_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            self.sememe_sim_table = pickle.load(
                get_resource(os.path.join(package_directory, sememe_sim_table_pickle_path), "rb"))
            self.sense_tree_dic = pickle.load(
                get_resource(os.path.join(package_directory, sense_tree_path), 'rb'))
            self.sense_syn_dic = pickle.load(
                get_resource(os.path.join(package_directory, sense_syn_path), 'rb'))
        except FileNotFoundError as e:
            print(
                "Enabling Word Similarity Calculation requires specific data files, please check the completeness of your download package.")
            print(e)
            return
        print("Initializing similarity calculation succeeded!")
        return

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

    def calculate_word_similarity(self, word0, word1, strict=True):
        """Calculate the word similarity between two words via sememes
        Args:
            word0 (`str`): 
                target word #0
            word1 (`str`): 
                target word #1
            strict (`bool`):
                you can choose to search the sense strictly or not.
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

        senses1 = self.get_sense(word0, strict=strict)
        senses2 = self.get_sense(word1, strict=strict)
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
        if not hasattr(self, "sense_tree_dic") or not hasattr(self, "sememe_sim_table"):
            print("Please initialize the similarity calculation firstly!")
            return
        if self.sense_tree_dic is None or self.sememe_sim_table is None:
            print("Please initialize the similarity calculation firstly!")
            return
        ss = sense.get_sememe_list()
        ll = list(ss)
        ll = [i.en_zh for i in ll]
        ll.sort()
        k = '_'.join(ll)
        return [self.sense_dic[i] for i in self.sense_syn_dic[k]]

    def _get_words_list_by_rule(self, senses, language='zh', score=False, grammar=None, K=10):
        """Get sense list by language/grammar/K.
        """
        res = []
        for s in senses:
            word = s[0].en_word if language == 'en' else s[0].zh_word
            if word == '':
                continue
            if grammar == None:
                if word not in res:
                    if score:
                        flag = 0
                        for i in res:
                            if i[0] == word:
                                flag = 1
                        if flag == 0:
                            res.append((word, s[1]))
                    else:
                        res.append(word)
                    if len(res) == K:
                        return res
                    continue
            else:
                s_grammar = s[0].en_grammar if language == 'en' else s[0].zh_grammar
                if s_grammar == grammar:
                    if word not in res:
                        if score:
                            flag = 0
                            for i in res:
                                if i[0] == word:
                                    flag = 1
                            if flag == 0:
                                res.append((word, s[1]))
                        else:
                            res.append(word)
                        if len(res) == K:
                            return res
                        continue
        return res

    def get_nearest_words(self, word, language=None, score=False, pos=None, merge=False, K=10, strict=True):
        """
        Get the topK nearest words of the given word, the word similarity is calculated based on HowNet annotation.
        If the given word does not exist in HowNet annotations, this function will return an empty list.

        Args: 
            word (`str`): 
                target word
            language (`str`):
                specify the language of the word and the search result, you can choose from en/zh.
            score (`bool`):
                you can choose to get the similarity score between the words.
            pos (`str`):
                you can set the part of speech of the word.
            merge (`bool`):
                you can choose to merge the words of all the result senses into one list.
            K (`int`): 
                specify the number of the nearest words you want to retrieve.
            strict (`bool`):
                you can choose to search the word strictly or not.
        Returns: 
            (`list`) a list of the nearest K words.
            if merge==False, returns a list of senses retrieved by the word and their synonym seperately.
            If the given word does not exist in HowNet annotations, this function will return an empty list.
        """
        if not hasattr(self, "sense_tree_dic") or not hasattr(self, "sememe_sim_table"):
            print("Please initialize the similarity calculation firstly!")
            return
        if self.sense_tree_dic is None or self.sememe_sim_table is None:
            print("Please initialize the similarity calculation firstly!")
            return
        if language == None:
            print('Please set the language of the similar words.')
            print('Language can be set to en or zh.')
            return
        # Retireve the senses annotated with word.
        senses = self.get_sense(word, pos=pos, strict=strict)
        res_temp = list()
        for i in senses:
            tree1 = self.sense_tree_dic[i.No]
            scores = {}
            for j in self.sense_dic.keys():
                if j != i.No and int(j) >= 3378:
                    tree2 = self.sense_tree_dic[j]
                    sim = self.sense_similarity(
                        tree1, tree2, self.sememe_sim_table)
                    scores[self.sense_dic[j]] = sim
            result = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            res_item = dict()
            res_item['sense'] = i
            res_item['synonym'] = result
            res_temp.append(res_item)
        if merge:
            res = list()
            for i in res_temp:
                res.extend(i['synonym'])
            res = sorted(res, key=lambda x: x[1], reverse=True)
            res = self._get_words_list_by_rule(
                res, language=language, score=score, grammar=pos, K=K)
            return res
        else:
            res = dict()
            for i in res_temp:
                res[i['sense']] = self._get_words_list_by_rule(
                    i['synonym'], language=language, score=score, grammar=pos, K=K)
            return res
