from anytree import Node, RenderTree
from anytree.exporter import DictExporter


def GenSememeTree(kdml, returnNode=False):
    "输入义原描述字符串，返回义原结构树：dict形式"
    entity_idx = []  # 义原起止位置集合
    node = []  # 树的节点集合
    pointer = []  # idx of '~' cases

    # 识别义原
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
            # Dictionary.sememes.add(kdml[start_idx + 1: end_idx])
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
                # Dictionary.roles.add(node[i].role)
    for i in pointer:
        node[i].parent.role = node[i].role
        node[i].parent = None

    # 转化成dict形式
    exporter = DictExporter()
    # exporter = JsonExporter(indent=2, sort_keys=True)
    if not returnNode:
        return exporter.export(node[0])
    else:
        return node[0]
