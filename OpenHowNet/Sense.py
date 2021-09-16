"""
Sense Class
=============
"""

from anytree import Node, RenderTree
from anytree.exporter import DictExporter, JsonExporter


class Sense(object):
    """Contains variables of a sense. Initialized by an item in HowNet.
    Contains numbering, word, POS of word, sememe tree, etc.

    Args:
        hownet_sense (dic):
            Dict contains the annotation of the sense in HowNet.
    """

    def __init__(self, hownet_sense):
        """Initialize a sense object by a hownet item.
        Initialize the attributes of the sense.
        """
        self.No = hownet_sense['No']
        self.en_word = hownet_sense['en_word']
        self.en_grammar = hownet_sense['en_grammar']
        self.zh_word = hownet_sense['ch_word']
        self.zh_grammar = hownet_sense['ch_grammar']
        self.Def = hownet_sense['Def']
        self.sememes = []

    def __repr__(self):
        """Define how to print the sense.
        """
        nzno = str(int(self.No))
        return 'No.' + nzno + "|%s|%s" % (self.en_word, self.zh_word)

    def __expand_tree(self, tree, layer, isRoot=True):
        """Expand the sememe tree by iteration.

        Args:
            tree(`dict`): 
                the sememe tree to expand.
            layer(`int`): 
                the layer num to expand the tree.
        """
        res = set()
        if layer == 0:
            return res
        target = tree

        if isinstance(tree, dict):
            target = list()
            target.append(tree)
        for item in target:
            try:
                if not isRoot:
                    if item['name'] != '$' and item['name'] != '?':
                        res.add(item["name"])
                if "children" in item:
                    res |= self.__expand_tree(
                        item["children"], layer - 1, isRoot=False)
            except Exception as e:
                if isinstance(e, IndexError):
                    continue
                raise e
        return res

    def get_sememe_list(self, layer=-1):
        """Expand the sememe tree by iteration.
        Return the sememe set of the tree.

        Args:
            layer(`int`): 
                the layer num to expand the tree.

        Returns:
            (`list[Sememe]`) the sememe set of the sememe tree.
        """
        tree = self.get_sememe_tree()
        return list(self.__expand_tree(tree, layer))

    def get_sememe_tree(self, return_node=False):
        """Generate sememe tree for the sense by the Def.

        Args:
            return_node(`bool`):
                whether to return as anytree node.

        Returns:
            (`dict`or`anytree.Node`) the sememe tree of the sense in the form of dict 
            or the root node of the sememe tree.
        """
        kdml = self.Def
        rmk_pos = kdml.find('RMK=')
        if rmk_pos >= 0:
            kdml = kdml[:rmk_pos]
        kdml_list = kdml.split(";")
        root = Node(self, role='sense')
        for kdml in kdml_list:
            entity_idx = []  # 义原起止位置集合
            node = []  # 树的节点集合
            pointer = []  # idx of '~' cases
            for i in range(len(kdml)):
                if kdml[i] in ['~', '?', '$']:
                    if kdml[i] == '~':
                        pointer.append(len(node))
                    entity_idx.append([i, i + 1])
                    node.append(Node(kdml[i], role='None'))
                elif kdml[i] == '|':
                    start_idx = i
                    end_idx = i
                    while kdml[start_idx] not in ['{', '"']:
                        start_idx = start_idx - 1
                    while kdml[end_idx] not in ['}', ':', '"']:
                        end_idx = end_idx + 1
                    entity_idx.append([start_idx + 1, end_idx])
                    for j in self.sememes:
                        if j.en_zh == kdml[start_idx + 1: end_idx].replace(' ', '_'):
                            node.append(Node(j, role='None'))

            for i in range(len(entity_idx)):
                cursor = entity_idx[i][0]
                left_brace = 0
                right_brace = 0
                quotation = 0
                while not (kdml[cursor] == ':' and ((quotation % 2 == 0 and left_brace == right_brace + 1) or
                                                    (quotation % 2 == 1 and left_brace == right_brace))):
                    if cursor == 0:
                        break
                    if kdml[cursor] == '{':
                        left_brace = left_brace + 1
                    elif kdml[cursor] == '}':
                        right_brace = right_brace + 1
                    elif kdml[cursor] == '"':
                        quotation = quotation + 1
                    cursor = cursor - 1
                parent_idx = -1
                for j in range(i - 1, -1, -1):  # 从当前位置往前找可以对应上的义原
                    if entity_idx[j][1] == cursor:
                        node[i].parent = node[j]
                        parent_idx = j
                        break
                if i != 0:
                    if parent_idx != -1:
                        right_range = entity_idx[parent_idx][1] - 1
                    else:
                        right_range = entity_idx[i - 1][1] - 1
                    role_begin_idx = -1
                    role_end_idx = -1
                    # 修改：在当前义原和父义原之间找
                    for j in range(entity_idx[i][0] - 1, right_range, -1):
                        if kdml[j] == '=':
                            role_end_idx = j
                        elif kdml[j] in [',', ':']:
                            role_begin_idx = j
                            break
                    if role_end_idx != -1:
                        node[i].role = kdml[role_begin_idx + 1: role_end_idx]
            for i in pointer:
                node[i].parent.role = node[i].role
                node[i].parent = None
            node[0].parent = root
            if not return_node:
                # 转化成dict形式
                # exporter = DictExporter()
                return DictExporter().export(root)
            else:
                return root

    def visualize_sememe_tree(self):
        """Visualize the sememe tree by sense Def.
        Print and return the sememe tree str.

        Returns:
            (`str`) the visualized sememe tree.
        """
        tree = self.get_sememe_tree(return_node=True)
        tree = RenderTree(tree)
        tree_str = ''
        for pre, fill, node in tree:
            tree_str += "%s[%s]%s\n" % (pre, node.role, node.name)
        print(tree_str)
