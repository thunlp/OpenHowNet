"""
HowNetDict Class
=================
"""
import pickle
import os

from .Sense import Sense
from .Sememe import Sememe
from .BabelNetSynset import BabelNetSynset
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

    def __init__(self, init_sim=False, init_babel=False):
        '''Initialize HowNetDict

        Args:
            init_sim (`bool`) : whether to initialize the similarity calculation module.
            init_babel (`bool`) : whether to initialize the BabelNet synest search module.
        '''
        try:
            sememe_dir, sememe_triples_dir, data_dir = [os.path.join("resources", i) for i in [
                'sememe_all', 'sememe_triples_taxonomy.txt', 'HowNet_dict_complete']]

            # Initialize sememe list from sememe_all.
            self.sememe_dic = dict()
            with get_resource(sememe_dir, 'rb') as sememe_dict:
                sememe_all = pickle.load(sememe_dict)
            sememe_dict.close()
            for k, v in sememe_all.items():
                self.sememe_dic[k] = Sememe(k, v)

            # Initialize the relations between sememes
            sememe_triples = get_resource(sememe_triples_dir, "r")
            for line in sememe_triples.readlines():
                line = line.strip().split(" ")
                if line[1] not in self.sememe_dic[line[0]].related_sememes.keys():
                    self.sememe_dic[line[0]].related_sememes[line[1]] = []
                self.sememe_dic[line[0]].related_sememes[line[1]].append(
                    self.sememe_dic[line[2]])
            sememe_triples.close()

            # Initialize sense list from HowNet_dict
            self.sense_dic = dict()
            with get_resource(data_dir, 'rb') as origin_dict:
                hownet_dict = pickle.load(origin_dict)
            origin_dict.close()
            for k, v in hownet_dict.items():
                self.sense_dic[k] = Sense(v)
                self.sense_dic[k].sememes = self.__gen_sememe_list(
                    self.sense_dic[k])
                for s in self.sense_dic[k].sememes:
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

            # Initialize the BabelNet Synset dict
            if init_babel:
                self.initialize_babelnet_dict()

        except FileNotFoundError as e:
            print(e)

    def __getitem__(self, item):
        """Shortcut for get_sense().

        Args:
            item (`str`) : target word by which to search for the senses.

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = set()
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
            (`int`): the num of the concepts in HowNet.
        """
        return len(self.sense_dic)

    def __str__(self):
        return str(type(self))

    def get_sense(self, word, language=None, pos=None, strict=True):
        """Common sense search API, you can specify the language of the target word to boost the search performance.
        Besides if you are not sure about the word, you can set `strict` to False to fuzzy match the sense.

        Args:
            word (`str`) : target word.
            language (`str`) : 
                target language, default: None. (The func will search both in English and Chinese, which will consume a lot of time.)
                you can set to `en` or `zh`, which means search in English or Chinese.
            pos (`str`) : limit the part of speech of the result.
            strict (`bool`) :  whether to search the sense strictly.

        Returns:
            (`list[Sense]`) candidates HowNet senses, if the target word does not exist, return an empty list.
        """
        res = set()
        if language:
            if language != 'en' and language != 'zh':
                print("Language error, please set the correct language.")
                return
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
            if pos not in self.get_all_sense_pos():
                print("POS error, please set the correct POS.")
                return
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
        if language:
            if language != 'en' and language != 'zh':
                print("Language error, please set the correct language.")
                return
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
            (`list[str]`) All annotated Chinese words in HowNet.
        """
        return list(set(self.zh_map.keys()))

    def get_en_words(self):
        """Get all English words annotated in HowNet

        Returns:
            (`list[str]`) All annotated English words in HowNet.
        """
        return list(set(self.en_map.keys()))

    def __gen_sememe_list(self, sense):
        """Get sememe list for the sense by the Def.

        Args:
            sense(`Sense`):
                the sense to generate sememe tree.

        Returns:
            (`list[Sememe]`) the sememe list of the sense.
        """
        kdml = sense.Def
        res = list()
        for i in range(len(kdml)):
            if kdml[i] == '|':
                start_idx = i
                end_idx = i
                while kdml[start_idx] not in ['{', '"']:
                    start_idx = start_idx - 1
                while kdml[end_idx] not in ['}', ':', '"']:
                    end_idx = end_idx + 1
                res.append(
                    self.sememe_dic[kdml[start_idx + 1:end_idx].replace(' ', '_')])
        return res

    def get_sememes_by_word(self, word, display='list', merge=False, expanded_layer=-1, K=None):
        """Commen sememe search API.
        Given specific word, you can get corresponding HowNet annotations.
        The result can be display in various forms.

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
        if display not in ['tree', 'dict', 'list', 'visual']:
            print("Display error, please set the correct display.")
            return
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
        return list(result)

    def has(self, item, language=None):
        """Check that whether certain word(English Word/Chinese Word/ID) exist in HowNet
        Only perform exact match because HowNet is case-sensitive
        By default, it will search the target word in both the English vocabulary and the Chinese vocabulary

        Args:
            item (`str`):target word to be searched in HowNet
            language (`str`):specify the language of the target search word

        Returns:
            (`bool`) whether the word exists in HowNet annotation
        """
        if language:
            if language != 'en' and language != 'zh':
                print("Language error, please set the correct language.")
                return
        if language == "en":
            return item in self.en_map
        elif language == "zh":
            return item in self.zh_map

        return item in self.en_map or item in self.zh_map or item in self.sense_dic

    def get_all_sememes(self):
        """Get the complete sememes in HowNet.

        Returns:
            (`list[Sememe]`) a list of all sememes
        """
        return list(self.sememe_dic.values())

    def get_all_senses(self):
        """Get the complete senses in HowNet

        Returns:
            (`list[Sense]`) a list of all senses
        """
        return list(self.sense_dic.values())

    def get_all_sense_pos(self):
        """Get all the pos of words in senses in HowNet.

        Returns:
            (`list[str]`) the pos of the words in HowNet.
        """
        return ['det', 'root', 'prep', 'aux', 'wh', 'adv', 'conj', 'infs', 'prefix', 'num', 'suffix', 'pun', 'noun', 'verb', 'stru', 'expr', 'adj', 'classifier', 'pp', 'letter', 'pron', 'echo', 'char', 'coor']

    # Sememe relation
    def get_all_sememe_relations(self):
        """Get all the relations between sememes in HowNet.

        Returns:
            (`list[str]`) all the relations between sememes in HowNet.
        """
        return ['hypernym', 'hyponym', 'antonym', 'converse']

    def get_sememe_relation(self, x, y, return_triples=False, strict=True):
        """Show relationship between two sememes.
        The function will search for the sememes by the words and 
        retrieve the relation of two sememe.

        Args:
            x (`str`): the word #0 to search the sememe.
            y (`str`): the word #1 to search the sememe.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the relations.
            strict (`bool`):
                you can choose to search the sememe relation strictly by the word.
                set to False if you are not sure about the x and y.

        Returns:
            (`list`) a list contains sememe triples or a list contains relations. 
            Note that x is the head sememe and y is the tail sememe in the triples.
        """
        res = []
        sememe_x = self.get_sememe(x, strict=strict)
        sememe_y = self.get_sememe(y, strict=strict)
        for s_x in sememe_x:
            for k in s_x.related_sememes.keys():
                for s_y in sememe_y:
                    if s_y in s_x.related_sememes[k]:
                        if return_triples:
                            res.append(
                                (s_x, k, s_y))
                        else:
                            res.append(k)
        return res

    def get_related_sememes(self, x, relation=None, return_triples=False, strict=True):
        """Show all sememes that x has any relation with.
        By setting the relation you can get the sememes that have the exact relation
        with the target sememe.

        Args:
            x (`str`): the word to search the sememe.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the sememes.
            strict (`bool`):
                you can choose to search the sememe relation strictly by the word.
                set to False if you are not sure about the x.

        Returns:
            (`list`) a list contains sememe triples or contains sememes.
        """
        if relation:
            if relation not in self.get_all_sememe_relations():
                print("Relation not exist.")
                return
        res = set()
        sememe_x = self.get_sememe(x, strict=strict)
        if relation:
            for s_x in sememe_x:
                res |= set(s_x.get_related_sememes(
                    relation=relation, return_triples=return_triples))
        else:
            for s_x in sememe_x:
                res |= set(s_x.get_related_sememes(
                    return_triples=return_triples))
        return list(res)

    def get_senses_by_sememe(self, x, strict=True):
        """Get the senses labeled by sememe x.

        Args:
            x (`str`) : the word to search the sememe.
        Returns:
            (`list[Sense]`) The list of senses which contains the sememe x.
        """
        res = set()
        sememe_x = self.get_sememe(x, strict=strict)
        for s_x in sememe_x:
            res |= s_x.get_senses()
        return list(res)

    # Similarity calculation
    def initialize_similarity_calculation(self):
        """Initialize the similarity calculation via sememes.
        Implementation is contributed by Jun Yan, which is based on the paper :
        "Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP"
        """
        sememe_sim_table_pickle_path, sense_tree_path, sense_syn_path = [os.path.join("resources", i) for i in [
            'sememe_sim_table', 'sense_tree', 'synonym']]

        try:
            self.sememe_sim_table = pickle.load(
                get_resource(sememe_sim_table_pickle_path, "rb"))
            self.sense_tree_dic = pickle.load(
                get_resource(sense_tree_path, 'rb'))
            self.sense_syn_dic = pickle.load(
                get_resource(sense_syn_path, 'rb'))
        except FileNotFoundError as e:
            print(
                "Enabling Word Similarity Calculation requires specific data files, please check the completeness of your download package.")
            print(e)
            return
        print("Initializing similarity calculation succeeded!")
        return

    def __sense_similarity(self, node1, node2, sememe_sim_table):
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
                            self.__sense_similarity(
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
            word0 (`str`): target word #0
            word1 (`str`): target word #1
            strict (`bool`):
                you can choose to search the sense strictly or not.
        Returns: 
            (`float`) the word similarity calculated via sememes.
            If word0 or word1 does not exist in HowNet annotation, it will return -1
            If the initialization method of word similarity calculation has not been called yet, it will also return 0.0 and print corresponding error message.
        """
        res = -1
        if not hasattr(self, "sense_tree_dic") or not hasattr(self, "sememe_sim_table"):
            print("Please initialize the similarity calculation firstly!")
            return res
        if self.sense_tree_dic is None or self.sememe_sim_table is None:
            print("Please initialize the similarity calculation firstly!")
            return res

        senses1 = self.get_sense(word0, strict=strict)
        senses2 = self.get_sense(word1, strict=strict)
        for id1 in senses1:
            for id2 in senses2:
                sim = self.__sense_similarity(
                    self.sense_tree_dic[id1.No], self.sense_tree_dic[id2.No],  self.sememe_sim_table)
                if sim > res:
                    res = sim
        return res

    def get_sense_synonyms(self, sense):
        """Get the senses that have the same sememe annotation with the sense

        Args:
            sense(`Sense`) : the targe sense to search the synonyms.

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

    def __get_words_list_by_rule(self, senses, language='zh', score=False, grammar=None, K=10):
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
            word (`str`): target word.
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
        if language:
            if language != 'en' and language != 'zh':
                print("Language error, please set the correct language.")
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
                    sim = self.__sense_similarity(
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
            res = self.__get_words_list_by_rule(
                res, language=language, score=score, grammar=pos, K=K)
            return res
        else:
            res = dict()
            for i in res_temp:
                res[i['sense']] = self.__get_words_list_by_rule(
                    i['synonym'], language=language, score=score, grammar=pos, K=K)
            return res

    # BabelNet synset dict
    def initialize_babelnet_dict(self):
        """Initialize the BabelNet Synset dict.
        """
        babel_data_path = os.path.join('resources', 'babel_data')
        try:
            babel_synset_list = pickle.load(
                get_resource(babel_data_path, "rb"))

            self.synset_dic = {}
            self.en_synset_dic = {}
            self.zh_synset_dic = {}
            for synset in babel_synset_list:
                self.synset_dic[synset['bn']] = BabelNetSynset(synset)
                self.synset_dic[synset['bn']].sememes = [
                    self.sememe_dic[i] for i in synset['sememes']]
            for synset in babel_synset_list:
                for k in synset['rel'].keys():
                    self.synset_dic[synset['bn']].related_synsets[k] = [
                        self.synset_dic[i] for i in synset['rel'][k]]
            for synset in babel_synset_list:
                for i in synset['en_synonyms']:
                    if i not in self.en_synset_dic.keys():
                        self.en_synset_dic[i] = list()
                    self.en_synset_dic[i].append(self.synset_dic[synset['bn']])
                for i in synset['zh_synonyms']:
                    if i not in self.zh_synset_dic.keys():
                        self.zh_synset_dic[i] = list()
                    self.zh_synset_dic[i].append(self.synset_dic[synset['bn']])

        except FileNotFoundError as e:
            print(
                "Enabling BabelNet Synset Dict requires specific data files, please check the completeness of your download package.")
            print(e)
            return
        print("Initializing BabelNet Synset Dict succeeded!")
        return

    def get_synset(self, word, language=None, pos=None, strict=True):
        """Get the synset by the word.
        You can choose to set the limit of the language of the word.

        Args:
            word(`str`): target word to search for the synset.
            language(`str`): the language of the retrieved word.
            strict(`bool`): whether to search for the synset by word strictly.
            pos(`str`): limitation on the result. Can be set to a/v/n/r.

        Returns:
            (`list[BabelNetSynset]`) the list of retrieved synsets.
        """
        if not hasattr(self, "synset_dic"):
            print("Please initialize BabelNet synest dict firstly!")
            return
        if language:
            if language != 'en' and language != 'zh':
                print("Language error, please set the correct language.")
                return
        if pos:
            if pos not in self.get_all_synset_pos():
                print("POS error, please set the correct POS.")
                return
        res = set()
        if strict:
            if language == 'en':
                if (word in self.en_synset_dic.keys()):
                    res |= set(self.en_synset_dic[word])
            elif language == 'zh':
                if (word in self.zh_synset_dic.keys()):
                    res |= set(self.zh_synset_dic[word])
            else:
                if (word in self.synset_dic.keys()):
                    res |= set([self.synset_dic[word]])
                if (word in self.en_synset_dic.keys()):
                    res |= set(self.en_synset_dic[word])
                if (word in self.zh_synset_dic.keys()):
                    res |= set(self.zh_synset_dic[word])
        else:
            if language == 'en':
                for k in self.en_synset_dic.keys():
                    if k.find(word) != -1:
                        res |= set(self.en_synset_dic[k])
            elif language == 'zh':
                for k in self.zh_synset_dic.keys():
                    if k.find(word) != -1:
                        res |= set(self.zh_synset_dic[k])
            else:
                for k in self.synset_dic.keys():
                    if k.find(word) != -1:
                        res |= set([self.synset_dic[k]])
                for k in self.en_synset_dic.keys():
                    if k.find(word) != -1:
                        res |= set(self.en_synset_dic[k])
                for k in self.zh_synset_dic.keys():
                    if k.find(word) != -1:
                        res |= set(self.zh_synset_dic[k])
        if pos:
            temp = res.copy()
            for i in temp:
                if i.pos != pos:
                    res.remove(i)
        return list(res)

    def get_all_babel_synsets(self):
        """Get the complete BabelNet synsets.

        Returns:
            (`list[BabelNetSynset]`) a list of all BabelNet synsets.
        """
        if not hasattr(self, "synset_dic"):
            print('Please initialize the BabelNet synset dict.')
            return
        return self.synset_dic.values()

    def get_all_synset_pos(self):
        return ['a', 'v', 'n', 'r']

    def get_all_synset_relations(self):
        """Return all the relations between synsets in BabelNet.
        """
        return ['similar', 'derivation', 'similar_to', 'derivationally_related_form', 'gloss_related_form_(monosemous)',
                'gloss_related_form_(disambiguated)', 'also_see', 'pertainym', 'pertainym_(pertains_to_nouns)', 'category_domain',
                'domain_of_synset_-_topic', 'antonym', 'attribute', 'region_domain', 'usage_domain', 'domain_of_synset_-_usage',
                'domain_of_synset_-_region', 'verb_group', 'hypernym', 'hyponym', 'entailment', 'cause', 'this_taxon_is_source_of',
                'natural_product_of_taxon', 'color', 'subclass_of', 'instance_of', 'semantically_related_form', 'part_meronym',
                'uses', 'practiced_by', 'member_meronym', 'member_holonym', 'taxon_rank', 'recommended_unit_of_measurement',
                'health_specialty', 'different_from', 'country_of_origin', 'iucn_conservation_status', 'instances_hyponym',
                'instance_hyponym', 'political_ideology', 'located_in_the_administrative_territorial_entity', 'part_holonym',
                'antiparticle', 'interaction', 'part_of', 'opposite_of', 'facet_of', 'use', 'has_part', 'programming_language',
                'said_to_be_the_same_as', 'named_after', 'followed_by', 'substance_meronym', 'streak_color', 'instance_hypernym',
                'twinned_administrative_body', 'continent', 'country', 'location_of_creation', 'material_used', 'month_of_the_year',
                'applies_to_jurisdiction', 'work_location', 'member_of_political_party', 'country_of_citizenship', 'occupation',
                'parent_taxon', 'taxonomic_type', 'member_of_category_domain', 'member_of_this_domain_-_topic', 'cause_of_death',
                'field_of_work', 'place_of_death', 'place_of_birth', 'prime_factor', 'model_item', 'studied_by', 'has_parts_of_the_class',
                'has_quality', 'used_by', 'has_cause', 'religion', 'killed_by', 'child', 'substance_holonym', 'basin_country',
                'connects_with', 'from_narrative_universe', 'located_on_terrain_feature', 'location_of_discovery',
                'diplomatic_relation', 'official_language', 'language_used', 'capital', 'member_of',
                'contains_administrative_territorial_entity', 'shares_border_with', 'has_effect', 'medical_condition', 'ethnic_group',
                'sport', 'indigenous_to', 'writing_system', 'noble_title', 'partially_coincident_with', 'immediate_cause_of',
                'has_immediate_cause', 'lowest_point', 'follows', 'subject_has_role', 'grammatical_option_indicates', 'parent_astronomical_body',
                'separated_from', 'place_of_burial', 'genre', 'participant', 'highest_point', 'located_in_or_next_to_body_of_water', 'location',
                'found_in_taxon', 'conflict', 'child_astronomical_body', 'interested_in', 'writing_language', 'instrument', 'languages_spoken_written_or_signed',
                'employer', 'educated_at', 'capital_of', 'possible_treatment', 'afflicts', 'symptoms', 'father', 'this_zoological_name_is_coordinate_with', 'taxon_synonym',
                'measured_physical_quantity', 'has_grammatical_case', 'official_symbol', 'head_of_state', 'replaces', 'has_fruit_type', 'has_facet_polytope',
                'studies', 'worshipped_by', 'based_on', 'depicts', 'residence', 'mouth_of_the_watercourse', 'author', 'main_subject',
                'owner_of', 'discoverer_or_inventor', 'basic_form_of_government', 'anatomical_location', 'drug_used_for_treatment', 'hair_color',
                'spouse', 'sibling', 'medical_condition_treated', 'manifestation_of', 'position_held', 'product_or_material_produced',
                'territory_claimed_by', 'field_of_this_occupation', 'language_of_work_or_name', 'currency', 'office_held_by_head_of_government',
                'permanent_duplicated_item', 'fabrication_method', 'risk_factor', 'headquarters_location', 'public_holiday', 'unmarried_partner',
                'significant_event', 'manner_of_death', 'native_language', 'military_rank', 'award_received', 'source_of_energy', 'physically_interacts_with',
                'inflows', 'lake_outflow', 'iconographic_symbol', 'military_branch', 'official_color', 'founded_by', 'calculated_from', 'has_natural_reservoir',
                'replaced_by', 'movement', 'has_contributing_factor', 'spore_print_color', 'sex_or_gender', 'member_of_region_domain', 'member_of_this_domain_-_region',
                'endemic_to', 'arterial_supply', 'day_in_year_for_periodic_occurrence', 'produced_by', 'owned_by', 'godparent', 'allegiance', 'main_food_source',
                'develops_from', 'family', 'patron_saint', 'does_not_have_part', 'copyright_representative', 'location_of_formation', 'typically_sells',
                'notable_work', 'tributary', 'characters', 'canonization_status', 'student_of', 'academic_degree', 'time_period', 'mountain_range',
                'influenced_by', 'sexual_orientation', 'sexually_homologous_with', 'habitat', 'item_operated', 'medical_examinations',
                'office_held_by_head_of_the_organization', 'original_combination', 'office_held_by_head_of_state', 'culture', 'feast_day', 'route_of_administration', 'type_locality_(geology)',
                'located_in_time_zone', 'given_name', 'operator', 'produced_sound', 'designed_to_carry', 'side_effect', 'next_lower_rank', 'currency_symbol_description',
                'central_bank/issuer', 'enclave_within', 'less_than', 'industry', 'exclave_of', 'significant_drug_interaction', 'foods_traditionally_associated',
                'day_of_week', 'is_a_list_of', 'appointed_by', 'objective_of_project_or_action', 'conjugate_acid', 'conferred_by', 'cell_component', 'domain_of_saint_or_deity',
                'place_of_detention', 'direction_relative_to_location', 'official_religion', 'legislative_body', 'shape', 'performer', 'target', 'organizer',
                'occupant', 'has_grammatical_mood', 'has_tense', 'described_by_source', 'penalty', 'invasive_to', 'subsidiary', 'creator', 'discography', 'voice_type',
                'uses_capitalization_for', 'linguistic_typology', 'official_residence', 'territory_overlaps', 'contributing_factor_of', 'encodes', 'professorship',
                'encoded_by', 'biological_process', 'narrative_location', 'archives_at', 'measures', 'doctoral_student', 'dual_to', 'flower_color', 'convicted_of',
                'first_aid_measures', 'place_of_origin_(switzerland)', 'destination_point', 'constellation', 'history_of_topic', 'parent_organization', 'lifestyle',
                'legal_form', 'ancestral_home', 'terminus', 'original_language_of_film_or_tv_show', 'historic_county', 'member_of_usage_domain', 'member_of_this_domain_-_usage',
                'honorific_prefix', 'next_higher_rank', 'lakes_on_river', 'origin_of_the_watercourse', 'participant_in', 'located_in_present-day_administrative_territorial_entity',
                'pathogen_transmission_process', 'geography_of_topic', 'depicted_by', 'student', 'conjugate_base', 'host', 'solid_solution_series_with', 'contains',
                'organization_directed_by_the_office_or_person', 'distribution_format', 'relative', 'mother', 'represents', 'sports_discipline_competed_in', 'victory', 'part_of_the_series',
                'is_pollinated_by', 'authority', 'molecular_function', 'commemorates', 'basionym', 'temporal_range_start', 'powered_by', 'anthem', 'prerequisite', 'central_bank',
                'of', 'developer', 'sponsor', 'has_works_in_the_collection', 'social_classification', 'contributor_to_the_creative_work_or_subject', 'voice_actor', 'chairperson',
                'commissioned_by', 'manufacturer', 'anatomical_branch_of', 'foundational_text', 'appears_in_the_form_of',
                'contains_settlement', 'dialect_of', 'base', 'has_vertex_figure', 'season_starts', 'members_have_occupation',
                'has_anatomical_branch', 'does_not_have_quality', 'commander_of_(deprecated)', "topic's_main_category",
                'measurement_scale', 'present_in_work', 'significant_person', 'gui_toolkit_or_framework', 'operating_area',
                'wears', 'designated_as_terrorist_by', 'platform', 'has_boundary', 'derivative_work', 'greater_than',
                'place_of_publication', 'offers_view_on', 'architectural_style', 'parent_of_this_hybrid_breed_or_cultivar',
                'doctoral_advisor', 'by-product', 'signatory', 'production_statistics', 'codomain', 'domain', 'honorific_suffix',
                'had_as_last_meal', 'birthday', 'historical_region', 'cause_of_destruction', 'people_or_cargo_transported',
                'place_served_by_transport_hub', 'family_name', 'programming_paradigm', 'enemy_of', 'has_list', 'language_regulatory_body',
                'incarnation_of', 'muscle_insertion', 'open_days', 'payment_types_accepted', 'member_of_military_unit', 'crosses',
                'determination_method', 'publisher', 'by-product_of', 'statement_describes']

    def get_synset_relation(self, x, y, return_triples=False, strict=True):
        """Get the relation between two synsets.
        The function will search for the candidate synsets by x and y.

        Args:
            x(`str`): the word #0 to search the synset.
            y(`str`): the word #1 to search the synset.
            return_triples(`bool`): whether to return the triples.
            strict(`bool`): whether to search for the synsets strictly.

        Returns:
            (`list`) list contains the relations or triples.

        """
        if not hasattr(self, "synset_dic"):
            print("Please initialize BabelNet synest dict firstly!")
            return
        res = list()
        synsets1 = self.get_synset(x, strict=strict)
        synsets2 = self.get_synset(y, strict=strict)

        for s1 in synsets1:
            for r in s1.related_synsets.keys():
                for s2 in synsets2:
                    if s2 in s1.related_synsets[r]:
                        if return_triples:
                            res.append((s1, r, s2))
                        else:
                            res.append(r)
        return res

    def get_related_synsets(self, x, relation=None, return_triples=False, strict=True):
        """Show all BabelNet synset that x has any relation with.
        By setting the relation you can get the synsets that have the exact relation
        with the target synset.

        Args:
            x (`str`): the word to search the synset.
            return_triples (`bool`):
                you can choose to get the list of triples or just the list of the synsets.
            strict (`bool`):
                you can choose to search the synset relation strictly by the word.
                set to False if you are not sure about the x.

        Returns:
            (`list`) a list contains synset triples or contains synsets.
        """
        if not hasattr(self, "synset_dic"):
            print("Please initialize BabelNet synest dict firstly!")
            return
        if relation:
            if relation not in self.get_all_synset_relations():
                print("Relation not exist.")
                return
        res = list()
        synsets = self.get_synset(x, strict=strict)
        if relation:
            for s in synsets:
                res.extend(s.get_synset_via_relation(
                    relation, return_triples=return_triples))
        else:
            for s in synsets:
                res.extend(s.get_related_synsets(
                    return_triples=return_triples))
        return res

    def get_sememes_by_word_in_BabelNet(self, x, merge=False):
        """The sememe search API based on BabelNet synsets.
        Given specific word, you can get corresponding sememe annotations.

        Args:
            x(`str`): the target word to search for the sememes.
            merge(`bool`): whether to merge the results into one.

        """
        if not hasattr(self, "synset_dic"):
            print("Please initialize BabelNet synest dict firstly!")
            return
        res = set()
        synsets = self.get_synset(x)
        if merge:
            for s in synsets:
                res |= set(s.get_sememe_list())
            return list(res)
        else:
            res = list()
            for s in synsets:
                res.append({'synset': s, 'sememes': s.get_sememe_list()})
            return res
