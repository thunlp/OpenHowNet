import os
import pickle
import sys
from typing import Dict, Any

from anytree import RenderTree

from OpenHowNet.SememeTreeParser import GenSememeTree
from OpenHowNet.pack.submit_user import util
from OpenHowNet.pack.submit_user.main import sense_similarity, word_similarity

from OpenHowNet.Download import get_resource

class Sememe(object):
    """Sememe class.

    The smallest semantic unit. Described in English and Chinese.

    Attributes:
        en: English word to describe the sememe.
        ch: Chinese word to describe the sememe.
        freq: the sememe occurence frequency in HowNet
    """
    def __init__(self, hownet_sememe):
        """Initialize a sememe by sememe annotations.

        :param hownet_sememe: sememe annotiation in HowNet.
        """
        self.en, self.ch = hownet_sememe.split('|')

class Sense(object):
    """Contains variables of a sense.

    Initialized by an item in HowNet.
    Contains numbering, word, POS of word, sememe tree, etc.

    Attributes:
        No: the id of the sense in HowNet.
        en_word: the word describing the sense in HowNet in English.
        en_grammar: the POS of the word in English.
        ch_word: the word describing the sense in HowNet in Chinese.
        ch_grammar: the POS of the word in Chinese.
        Def: the sememe tree of the sense.
    """
    def __init__(self, hownet_sense):
        """Initialize a sense object by a hownet item.

        Initialize the attributes of the sense.

        :param hownet_sense: (Dict)The Annotation of the sense in HowNet.
        """
        self.No = hownet_sense['No']
        self.en_word = hownet_sense['en_word']
        self.en_grammar = hownet_sense['en_grammar']
        self.ch_word = hownet_sense['ch_word']
        self.ch_grammar = hownet_sense['ch_grammar']
        self.Def = hownet_sense['Def']
    
    
    def get_sememes(self, display = "list"):
        """Get the sememe annotiation of the sense.

        You can retrieve sememes of the sense in different display mode.

        :param display: (str)The display mode of sememes.
            You can choose from list/json/visual.
        :return: sememe list or sememe tree or sememe dict
        """
        pass


class HowNetDict(object):

    def __init__(self, use_sim=False):
        '''
        Initialize HowNetDict
        :param use_sim: "lazy" option for loading similarity computation file.
        '''
        try:
            package_directory = os.path.dirname(os.path.abspath(__file__))
            data_dir = os.path.join(package_directory, "HowNet_dict_complete")
            self.en_map = dict()
            self.zh_map = dict()
            self.ids = dict()

            # load dict complete
            with get_resource(data_dir, 'rb') as origin_dict:
                word_dict = pickle.load(origin_dict)
                # self.max_count = len(word_dict) + 10
            for key in word_dict:
                now_dict = word_dict[key]
                en_word = now_dict["en_word"].strip()
                zh_word = now_dict["ch_word"].strip()
                if en_word not in self.en_map:
                    self.en_map[en_word] = list()
                self.en_map[en_word].append(now_dict)
                if zh_word not in self.zh_map:
                    self.zh_map[zh_word] = list()
                self.zh_map[zh_word].append(now_dict)
                if now_dict["No"] not in self.ids:
                    self.ids[now_dict["No"]] = list()
                self.ids[now_dict['No']].append(now_dict)
            if use_sim:
                if not self.initialize_sememe_similarity_calculation():
                    self.hownet = None
                    self.sememe_root = None
                    self.sememe_sim_table = None
        except FileNotFoundError as e:
            print(e)
            # raise FileNotFoundError("Important data file lost, please download the HowNet package again")
    
    def __getitem__(self, item):
        """
        Shortcut for Get(self,item,None)
        :param item: target word.
        :return:(List) candidates HowNet annotation, if the target word does not exist, return an empty list.
        """
        res = list()
        if item == "I WANT ALL!":
            for item in self.ids.values():
                res.extend(item)
            return res
        if item in self.en_map:
            res.extend(self.en_map[item])
        if item in self.zh_map:
            res.extend(self.zh_map[item])
        if item in self.ids:
            res.extend(self.ids[item])
        return res

    def __len__(self):
        """
        Get the num of the concepts in HowNet.
        :return:(Int) the num of the concepts in HowNet.
        """
        return len(self.ids)

    def get(self, word, language=None):
        """
        Common word search API, you can specify the language of the target word to boost the search performance
        :param word: target word
        :param language: target language, default: None
                (The func will search both in English and Chinese, which will consume a lot of time.)
        :return:(List) candidates HowNet annotation, if the target word does not exist, return an empty list.
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
        """
        Get all Chinese words annotated in HowNet
        :return: (list) All annotated Chinese words in HowNet.
        """
        return list(self.zh_map.keys())

    def get_en_words(self):
        """
        Get all English words annotated in HowNet
        :return: (list) All annotated English words in HowNet.
        """
        return list(self.en_map.keys())

    def _expand_tree(self, tree, layer, isRoot=True):
        """
        Expand the sememe tree by iteration.
        :param tree: the sememe tree to expand.
        :param propertyName: the language of the name of every sememe node.
        :param layer: the layer num to expand the tree.
        :return:(Set) the sememe set of the sememe tree.
        """
        res = set()
        if layer == 0:
            return res
        target = tree
        
        # special process with the root node
        if isinstance(tree, dict):
            target = list()
            target.append(tree)
        for item in target:
            try:
                if not isRoot:
                    res.add(item["name"])
                if "children" in item:
                    res |= self._expand_tree(item["children"], layer - 1, isRoot=False)
            except Exception as e:
                if isinstance(e, IndexError):
                    continue
                raise e
        return res
    '''
    def visualize_sememe_trees(self, word, K=None):
        """

        :param word: (str)The target word to be visualized in command line. Notice that single word may correspond to multiple HowNet annotations.
        :param K: (int)The maximum number of visualized words, ordered by id (ascending). Illegal number will be automatically ignored and the function will display all retrieved results.
        :return:
        """
        queryResult = list(self[word])
        queryResult.sort(key=lambda x: x["No"])
        print("Find {0} result(s)".format(len(queryResult)))
        if K is not None and K >= 1 and type(K) == int:
            queryResult = queryResult[:K]

        for index, item in enumerate(queryResult):
            # tree = GenSememeTree(item["Def"], returnNode=True)
            tree = GenSememeTree(item["Def"], word, returnNode=True)
            tree = RenderTree(tree)
            print("Display #{0} sememe tree".format(index))
            for pre, fill, node in tree:
                print("%s[%s]%s" % (pre, node.role, node.name))
    '''
    def get_sememes_by_word(self, word, display='json', merge=False, expanded_layer=-1, K=None):
        """
        Given specific word, you can get corresponding HowNet annotation.
        :param word: (str)specific word(en/zh/id) you want to search in HowNet.
                      You can use "I WANT ALL" or "*" to specify that you need annotations of all words.
        :param display: (str)how to display the sememes you retrieved, you can choose from 'json'/'list'/'visual'.
        :param merge: (boolean)only works when display == 'list'. Decide whether to merge multi-sense word query results into one
        :param expanded_layer: (int)only works when display == 'list'. Continously expand k layer
                                By default, it will be set to -1 (expand full layers)
        :param K: (int)only works when display == 'visual'.The maximum number of visualized words, ordered by id (ascending). 
                                Illegal number will be automatically ignored and the function will display all retrieved results.
        :return: list of converted sememe trees in accordance with requirements specified by the params
        """
        queryResult = self[word]
        result = set() if merge else list()
        if display == 'json':
            for item in queryResult:
                try:
                    result.append({"word": item, "tree": GenSememeTree(item["Def"], word)})
                except Exception as e:
                    print("Generate Sememe Tree Failed for", item["No"])
                    print("Exception:", e)
                    continue
        elif display == 'list':       
            for item in queryResult:
                try:
                    if not merge:
                        result.append(
                            {"ch_word": item['ch_word'],
                             "en_word": item['en_word'],
                             "sememes": self._expand_tree(GenSememeTree(item["Def"], word), expanded_layer)})
                    else:
                        result |= set(self._expand_tree(GenSememeTree(item["Def"], word), expanded_layer))
                except Exception as e:
                    print(word)
                    print("Wrong Item:", item)
                    print("Exception:", e)
                    raise e
        elif display == 'visual':
            queryResult.sort(key=lambda x: x["No"])
            print("Find {0} result(s)".format(len(queryResult)))
            if K is not None and K >= 1 and type(K) == int:
                queryResult = queryResult[:K]
            for index, item in enumerate(queryResult):
                tree = GenSememeTree(item["Def"], word, returnNode=True)
                tree = RenderTree(tree)
                print("Display #{0} sememe tree".format(index))
                for pre, fill, node in tree:
                    print("%s[%s]%s" % (pre, node.role, node.name))
        else:
            print("Wrong display mode: ", display)
        return result

    def __str__(self):
        return str(type(self))

    def has(self, item, language=None):
        """
        Check that whether certain word(English Word/Chinese Word/ID) exist in HowNet
        Only perform exact match because HowNet is case-sensitive
        By default, it will search the target word in both the English vocabulary and the Chinese vocabulary
        :param item: target word to be searched in HowNet
        :param language: specify the language of the target search word
        :return:(Boolean) whether the word exists in HowNet annotation
        """
        if language == "en":
            return item in self.en_map
        elif language == "zh":
            return item in self.zh_map

        return item in self.en_map or item in self.zh_map or item in self.ids

    def get_all_sememes(self, freq=False):
        """
        Get the complete sememe list in HowNet
        Also can get the frequency of occurrence of sememe in HowNet
        :param freq: (Bool) whether to get the frequency
        :return: (List) a list of sememes or (Dict) a dict of sememe and its frequency
        """
        if hasattr(self, "sememe_all"):
            return self.sememe_all if freq else list(self.sememe_all.keys())
        else:
            package_directory = os.path.dirname(os.path.abspath(__file__))
            f = get_resource("sememe_all", 'rb')
            sememe_all = pickle.load(f)
            self.sememe_all = sememe_all
            return self.sememe_all if freq else list(self.sememe_all.keys())
    
    def initialize_sememe_similarity_calculation(self):
        """
        Initialize the word similarity calculation via sememes.
        Implementation is contributed by Jun Yan, which is based on the paper :
        "Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP"
        :return: (Boolean) whether the initialization succeed.
        """
        pickle_prefix = os.sep.join(['pack', 'submit_user', 'pickle'])
        sememe_root_pickle_path = 'sememe_root.pkl'
        hownet_pickle_path = 'hownet.pkl'
        sememe_sim_table_pickle_path = 'sememe_sim_table.pkl'

        package_directory = os.path.dirname(os.path.abspath(__file__))
        try:
            sys.modules["util"] = util
            self.sememe_root = pickle.load(
                open(os.path.join(package_directory, pickle_prefix, sememe_root_pickle_path), "rb"))
            self.hownet = pickle.load(open(os.path.join(package_directory, pickle_prefix, hownet_pickle_path), "rb"))
            self.sememe_sim_table = pickle.load(
                open(os.path.join(package_directory, pickle_prefix, sememe_sim_table_pickle_path), "rb"))
            del sys.modules["util"]
        except FileNotFoundError as e:
            print(
                "Enabling Word Similarity Calculation requires specific data files, please check the completeness of your download package.")
            print(e)
            return False
        return True

    def get_nearest_words_via_sememes(self, word, K=10):
        """
        Get the topK nearest words of the given word, the word similarity is calculated based on HowNet annotation.
        If the given word does not exist in HowNet annotations, this function will return an empty list.
        :param word: target word
        :param K: specify the number of the nearest words you want to retrieve.
        :return: (List) a list of the nearest K words.
                If the given word does not exist in HowNet annotations, this function will return an empty list.
                If the initialization method of word similarity calculation has not been called yet, it will also return an empty list and print corresponding error message.
        """
        res = list()
        if not hasattr(self, "hownet") or not hasattr(self, "sememe_sim_table") or not hasattr(self, "sememe_root"):
            print("Please initialize the similarity calculation firstly!")
            return res
        if self.hownet is None or self.sememe_sim_table is None or self.sememe_root is None:
            print("Please initialize the similarity calculation firstly!")
            return res
        if word not in self.hownet.word2idx:
            print(word + ' is not annotated in HowNet.')
            return res
        for i in self.hownet.word[self.hownet.word2idx[word]].sense_id:
            tree1 = self.hownet.sense[i].tree
            score = {}
            banned_id = self.hownet.word[self.hownet.sense[i].word_id].sense_id
            for j in range(3378, len(self.hownet.sense)):
                if j not in banned_id:
                    tree2 = self.hownet.sense[j].tree
                    sim = sense_similarity(tree1, tree2, self.hownet, self.sememe_sim_table)
                    score[j] = sim
            result = sorted(score.items(), key=lambda x: x[1], reverse=True)
            topK = result[0:K]
            # line = str(i) + ', ' + self.hownet.sense[i].str + '\t\t'
            queryRes = dict()
            queryRes["id"] = i
            queryRes["word"] = self.hownet.sense[i].str
            queryRes["synset"] = list()
            for m in topK:
                #   line = line + str(m[0]) + ', ' + self.hownet.sense[m[0]].str + ', ' + str("%.2f" % m[1]) + '; '
                single_syn: Dict[str, Any] = {"id": m[0], "word": self.hownet.sense[m[0]].str, "score": m[1]}
                queryRes["synset"].append(single_syn)
            # line = line
            # print(line)
            res.append(queryRes)
        return res

    def calculate_word_similarity(self, word0, word1):
        """
        calculate the word similarity between two words via sememes
        :param word0: target word #0
        :param word1: target word #1
        :return: (Float) the word similarity calculated via sememes.
                 If word0 or word1 does not exist in HowNet annotation, it will return 0.0
                If the initialization method of word similarity calculation has not been called yet, it will also return 0.0 and print corresponding error message.
        """
        res = 0.0
        if not hasattr(self, "hownet") or not hasattr(self, "sememe_sim_table") or not hasattr(self, "sememe_root"):
            print("Please initialize the similarity calculation firstly!")
            return res
        if self.hownet is None or self.sememe_sim_table is None or self.sememe_root is None:
            print("Please initialize the similarity calculation firstly!")
            return res
        if word0 not in self.hownet.word2idx:
            print(word0 + ' is not annotated in HowNet.')
            return res
        if word1 not in self.hownet.word2idx:
            print(word1 + ' is not annotated in HowNet.')
            return res
        return word_similarity(word0, word1, self.hownet, self.sememe_sim_table)
    
    def _load_taxonomy(self):
        """
        Load taxonomy from file to follow dicts:
            sememe_taxonomy: (head sememe, tail sememe) as key and relation as value
            sememe_dict: (head sememe, relation) as key and tail sememe as value
            sememe_related: sememe as key and ((head_sememe, relation, tail sememe)) as value
        """
        f = get_resource("sememe_triples_taxonomy.txt", "r")
        self.sememe_taxonomy = {}
        self.sememe_dict = {}
        self.sememe_related = {}
        for line in f.readlines():
            line = line.strip().split(" ")

            self.sememe_taxonomy[(line[0], line[2])] = line[1]
            
            if not (line[0], line[1]) in self.sememe_dict:
                self.sememe_dict[(line[0], line[1])] = []
            self.sememe_dict[(line[0], line[1])].append(line[2])
            
            if not line[0] in self.sememe_related:
                self.sememe_related[line[0]] = set()
            self.sememe_related[line[0]].add((line[0], line[1], line[2]))
            if not line[2] in self.sememe_related:
                self.sememe_related[line[2]] = set()
            self.sememe_related[line[2]].add((line[0], line[1], line[2]))

            for u in line[0].split("|"):
                for v in line[2].split("|"):
                    self.sememe_taxonomy[(u, v)] = self.sememe_taxonomy[(line[0], v)] = self.sememe_taxonomy[(u, line[2])] = line[1]
                if not (u, line[1]) in self.sememe_dict:
                    self.sememe_dict[(u, line[1])] = []
                self.sememe_dict[(u, line[1])].append(line[2])
                if not u in self.sememe_related:
                    self.sememe_related[u] = set()
                self.sememe_related[u].add((line[0], line[1], line[2]))
                if not v in self.sememe_related:
                    self.sememe_related[v] = set()
                self.sememe_related[v].add((line[0], line[1], line[2]))

    def get_sememe_relation(self, x, y):
        """
        Show relationship between two sememes.
        :return: (String) a string represents the relation.
        """
        if not hasattr(self, "sememe_taxonomy"):
            self._load_taxonomy()

        return self.sememe_taxonomy.get((x, y), "none")
    
    def get_sememe_via_relation(self, x, relation):
        """
        Show all sememes that x has relation with.
        :return: (List) a string represents all related sememes.
        """
        if not hasattr(self, "sememe_dict"):
            self._load_taxonomy()
        
        return [x for x in self.sememe_dict.get((x, relation), [])]
    
    def get_related_sememes(self, x):
        """
        Show all sememes that x has any relation with.
        :param x: target sememe, you can use any language(en/zh).
        :return: (List) a list contains sememe triples.
        """
        if not hasattr(self, "sememe_dict"):
            self._load_taxonomy()
        
        return list(self.sememe_related.get(x, "none"))

    def _load_sememe_sense_dic(self):
        """
        Load sememe to sense dict from file
        """
        f = get_resource("sememe_sense_dic", "rb")
        
        self.sememe_sense_dic = pickle.load(f)
    
    def get_senses_by_sememe(self, x):
        """
        Get the senses labeled by sememe x.
        :param x: (str)Target sememe
        :return: the list of senses which contains No, ch_word and en_word.
        """
        if not hasattr(self, "sememe_sense_dic"):
            self._load_sememe_sense_dic()
        
        return self.sememe_sense_dic.get(x, [])