from anytree import Node, RenderTree


def compile(kdml):
    entity_idx = []
    node = []
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
            node.append(Node(kdml[start_idx + 1: end_idx], role='None'))
    for i in range(len(entity_idx)):
        cursor = entity_idx[i][0]
        left_brace = 0
        right_brace = 0
        quotation = 0
        while not (kdml[cursor] == ':' and ((quotation % 2 == 0 and left_brace == right_brace + 1) or \
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
        for j in range(i - 1, -1, -1):
            if entity_idx[j][1] == cursor:
                node[i].parent = node[j]
        if i != 0:
            role_begin_idx = -1
            role_end_idx = -1
            for j in range(entity_idx[i][0] - 1, entity_idx[i - 1][1] - 1, -1):
                if kdml[j] == '=':
                    role_end_idx = j
                elif kdml[j] in [',', ':']:
                    role_begin_idx = j
                    break
            if role_end_idx != -1:
                node[i].role = kdml[role_begin_idx + 1: role_end_idx]
                # Dictionary.roles.add(node[i].role)
    for i in pointer:
        node[i].name = node[i].parent.parent.name
    sememes = set()
    for i in node:
        sememes.add(i.name)
    return node[0], sememes


class Dictionary:

    def __init__(self):
        self.word = []
        self.sense = []
        self.word2idx = {}
        self.sememe = set()

    def add_sense(self, id, str, kdml):
        tree, sememes = compile(kdml)
        self.sememe = self.sememe | sememes
        if len(self.word) == 0 or str != self.word[-1].str:
            self.word2idx[str] = len(self.word2idx)
            self.word.append(Word(str))
        self.word[-1].sense_id.append(id)
        self.sense.append(Sense(id, tree, len(self.word) - 1, str))


class Word:
    def __init__(self, str):
        self.str = str
        self.sense_id = []


class Sense:
    def __init__(self, id, tree, word_id, str):
        self.id = id
        self.tree = tree
        self.word_id = word_id
        self.str = str

