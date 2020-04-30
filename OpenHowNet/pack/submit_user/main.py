from anytree import Node, RenderTree, search, walker
from OpenHowNet.pack.submit_user.util import Dictionary
import pickle
import time
import sys



def read_taxonomy(filepath):  # 读入sememe的上下位关系
   with open(filepath, encoding='GBK') as f:
        left_idx2depth = {-1: -1}
        lines = f.readlines()
        headline = lines[0]
        root = Node(headline[headline.find('{') + 1: headline.find('}')])
        previous_node = root
        previous_left_idx = -1
        previous_depth = 0
        for line in lines[1:]:
            left_idx = 0
            while line[left_idx] != '{':
                left_idx = left_idx + 1
            if left_idx == previous_left_idx:
                depth = previous_depth
            elif left_idx > previous_left_idx:
                depth = previous_depth + 1
            else:
                depth = left_idx2depth[left_idx]
            previous_left_idx = left_idx
            previous_depth = depth
            left_idx2depth[left_idx] = depth
            right_idx = left_idx
            while line[right_idx] != '}':
                right_idx = right_idx + 1
            while previous_node.depth + 1 != depth:
                previous_node = previous_node.parent
            previous_node = Node(line[left_idx + 1: right_idx], parent=previous_node)
        # for pre, fill, node in RenderTree(root):
        #     print("%s%s" % (pre, node.name))
        return root


def read_hownet(hownet_path):  # 读入hownet：各word的sememe集合
    hownet = Dictionary()
    with open(hownet_path, encoding='UTF8') as f:
        id = -1
        str = ''
        kdml = ''
        for line in f.readlines():
            if line.startswith('NO'):
                stage = 1
            elif line.startswith('W_C'):
                stage = 2
            elif line.startswith('DEF'):
                stage = 3
            else:
                stage = 0

            if stage == 1:
                id = int(line[4:-1])
            elif stage == 2:
                str = line[4:-1]
            elif stage == 3:
                kdml = line[4:-1]
                hownet.add_sense(id, str, kdml)
    return hownet


def prepare_sememe_sim(hownet, sememe_root, alpha, eps):  # 任意两个sememe之间的相似度表格
    sememe_sim_table = {}
    sememe = list(hownet.sememe)
    total_calc = int((1 + len(sememe)) * len(sememe) / 2)
    for i in range(len(sememe)):
        sememe_node1 = search.find(sememe_root, lambda node: node.name == sememe[i])
        flag = False
        for ancestor in sememe_node1.ancestors:
            if ancestor.name in ['Attribute|属性', 'Secondary Feature']:
                flag = True
                break
        for j in range(i, len(sememe)):
            sememe_node2 = search.find(sememe_root, lambda node: node.name == sememe[j])
            if sememe_node1 is None:
                print(sememe[i])
            if sememe_node2 is None:
                print(sememe[j])
            walk_result = walker.Walker().walk(sememe_node1, sememe_node2)
            sememe_sim = alpha * (sememe_node1.depth + sememe_node2.depth) / \
                         (alpha * (sememe_node1.depth + sememe_node2.depth) + \
                          abs(sememe_node1.depth - sememe_node2.depth) + len(walk_result[0]) + len(walk_result[2]))
            if flag:
                sememe_sim = sememe_sim * eps
            sememe_sim_table[(sememe[i], sememe[j])] = sememe_sim

            if len(sememe_sim_table) % 1000 == 0:
                print(len(sememe_sim_table), '/', total_calc)
    return sememe_sim_table


def word_similarity(str1, str2, hownet, sememe_sim_table):  # 计算两个word的相似度
    word_idx1 = hownet.word2idx[str1]
    senses1 = hownet.word[word_idx1].sense_id
    word_idx2 = hownet.word2idx[str2]
    senses2 = hownet.word[word_idx2].sense_id
    max_sim = -1
    for id1 in senses1:
        for id2 in senses2:
            sim = sense_similarity(hownet.sense[id1].tree, hownet.sense[id2].tree, hownet, sememe_sim_table)
            if sim > max_sim:
                max_sim = sim
    return max_sim


def sense_similarity(node1, node2, hownet, sememe_sim_table):  # 计算两个sense的相似度
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
                    relation_sim = relation_sim + sense_similarity(node1.children[i], node2.children[j], hownet, sememe_sim_table)
        relation_sim = relation_sim + (sum(flag1) + sum(flag2)) * delta
        relation_sim = relation_sim / (N - role_match)

    if (node1.name, node2.name) in sememe_sim_table:
        sememe_sim = sememe_sim_table[(node1.name, node2.name)]
    else:
        sememe_sim = sememe_sim_table[(node2.name, node1.name)]
    return beta_relation * relation_sim + beta_sememe * sememe_sim


if __name__ == "__main__":
    first_time = False
    pickle_prefix = 'pickle/'
    sememe_root_pickle_path = 'sememe_root.pkl'
    hownet_pickle_path = 'hownet.pkl'
    sememe_sim_table_pickle_path = 'sememe_sim_table.pkl'
    if first_time:
        print('Loading HowNet...', end='')
        sememe_root = Node('sememe_root')
        prefix = 'data/HowNet Taxonomy '
        for filename in ['AttributeValue', 'Attribute', 'Entity', 'Event', 'ProperNoun', 'SecondaryFeature', 'Sign']:
            node = read_taxonomy(prefix + filename + '.txt')
            node.parent = sememe_root

        hownet_path = 'data/HowNet_original_new.txt'
        hownet = read_hownet(hownet_path)
        with open(pickle_prefix + hownet_pickle_path, 'wb') as f:
            pickle.dump(hownet, f)
        print('Done!')
        print('word count: ', len(hownet.word))  # 127251
        print('sense count:', len(hownet.sense))  # 229751
        print('sememe count:', len(hownet.sememe))  # 2198

        with open(pickle_prefix + sememe_root_pickle_path, 'wb') as f:
            pickle.dump(sememe_root, f)

        print('Pre-calculating sememe similarity...')
        sememe_sim_table = prepare_sememe_sim(hownet, sememe_root, alpha=0.5, eps=0.1)
        print('Done!')
        with open(pickle_prefix + sememe_sim_table_pickle_path, 'wb') as f:
            pickle.dump(sememe_sim_table, f)
    else:
        with open(pickle_prefix + sememe_root_pickle_path, 'rb') as f:
            sememe_root = pickle.load(f)
        with open(pickle_prefix + hownet_pickle_path, 'rb') as f:
            hownet = pickle.load(f)
        with open(pickle_prefix + sememe_sim_table_pickle_path, 'rb') as f:
            sememe_sim_table = pickle.load(f)
        print('word count: ', len(hownet.word))  # 127251
        print('sense count:', len(hownet.sense))  # 229751
        print('sememe count:', len(hownet.sememe))  # 2198

    print("Mode 1: input a word and get 10 words with highest similarity.")
    print("Mode 2: input two words and get their similarity.")
    print("Select a mode (1 or 2): ", end='')
    mode = input()
    while mode not in ['1', '2']:
        print('Your input should be either 1 or 2.')
        print("Select a mode (1 or 2): ", end='')
        mode = input()
    mode = int(mode)
    if mode == 1:
        while True:
            print('Please input a word ("q" to quit): ', end="")
            str1 = input()
            if str1 == 'q':
                break
            if str1 not in hownet.word2idx:
                print(str1 + ' is not annotated in HowNet.')
                continue
            for i in hownet.word[hownet.word2idx[str1]].sense_id:
                tree1 = hownet.sense[i].tree
                score = {}
                banned_id = hownet.word[hownet.sense[i].word_id].sense_id
                for j in range(3378, len(hownet.sense)):
                    if j not in banned_id:
                        tree2 = hownet.sense[j].tree
                        sim = sense_similarity(tree1, tree2, hownet, sememe_sim_table)
                        score[j] = sim
                result = sorted(score.items(), key=lambda x: x[1], reverse=True)
                top10 = result[0:10]
                line = str(i) + ', ' + hownet.sense[i].str + '\t\t'
                for m in top10:
                    line = line + str(m[0]) + ', ' + hownet.sense[m[0]].str + ', ' + str("%.2f" % m[1]) + '; '
                line = line
                print(line)
    elif mode == 2:
        while True:
            print('Please input the first word ("q" to quit): ', end="")
            str1 = input()
            if str1 == 'q':
                break
            if str1 not in hownet.word2idx:
                print(str1 + ' is not annotated in HowNet.')
                continue
            print('Please input the second word ("q" to quit): ', end="")
            str2 = input()
            if str2 == 'q':
                break
            if str2 not in hownet.word2idx:
                print(str2 + ' is not annotated in HowNet.')
                continue
            print('Word similarity: ', word_similarity(str1, str2, hownet, sememe_sim_table))


