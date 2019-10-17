# OpenHowNet

<img src="openhownet-logo.png" width = "300"  alt="OpenHowNet Logo" align=center />

### [English Version](https://github.com/thunlp/OpenHowNet/blob/master/README.md)

本项目存放HowNet核心数据和清华大学自然语言处理实验室（THUNLP）开发的OpenHowNet API，提供方便的义原信息查询、义原树展示、基于义原的词相似度计算等功能。您还可以访问我们的[网站](https://openhownet.thunlp.org)体验义原在线查询和展示功能。

如果您在研究中使用了OpenHowNet提供的数据或API，请引用以下两篇文章：

	@article{qi2019openhownet,
	  title={OpenHowNet: An Open Sememe-based Lexical Knowledge Base},
	  author={Qi, Fanchao and Yang, Chenghao and Liu, Zhiyuan and Dong, Qiang and Sun, Maosong and Dong, Zhendong},
	  journal={arXiv preprint arXiv:1901.09957},
	  year={2019},
	}
	@inproceedings{dong2003hownet,
	  title={HowNet-a hybrid language and knowledge resource},
	  author={Dong, Zhendong and Dong, Qiang},
	  booktitle={Proceedings of NLP-KE},
	  year={2003},
	}

## HowNet核心数据
HowNet核心数据文件（`HowNet.txt`）由223,767个中英文词和词组所代表的概念构成。HowNet为每个概念标注了基于义原的定义以及词性、情感倾向、例句等信息。下面是HowNet中一个概念的示例：

```
NO.=042012 #概念编号
W_C=贷 #中文词
G_C=verb [9MustObj] [dai4] #中文词词性
S_C=PlusFeeling|正面情感 #情感倾向
E_C=定斩不~，严惩不~  #中文词例句
W_E=forgive #英文词 
G_E=verb [7 forgiveverb-0vt,sobj,ofnpa22    ]  #英文词词性
S_E=PlusFeeling|正面情感 #情感倾向
E_E=    #英文词例句
DEF={forgive|原谅} # 基于义原的定义
RMK=
```

## OpenHowNet API
### 运行要求

* Python==3.6
* anytree==2.4.3
* tqdm==4.31.1
* requests==2.22.0

### 安装

* 通过 pip 安装（推荐）

```bash
pip install OpenHowNet
```
* 通过 Github 安装

```bash
git clone https://github.com/thunlp/OpenHowNet-API/
cd OpenHowNet-API/OpenHowNet
chmod +x run.sh
./run.sh
```

### 接口说明 / Interfaces

|接口|功能说明|参数说明|
|---|-------|-------|
|get(self, word, language=None)|检索HowNet中词语对应的概念标注的完整信息|`word`表示待查词，`language`为`en`(英文)或`zh`(中文)，默认双语同时查找|
|get\_sememes\_by\_word(self, word, structured=False, lang='zh', merge=False, expanded_layer=-1)|检索输入词的义原，可以选择是否合并多个义项，也可以选择是否以结构化的方式返回，还可以指定展开层数。|`word`表示待查词，`language`为`en`(英文)或`zh`(中文), `structured`表示是否以结构化的方式返回，`merge`控制是否合并多义项，`expanded_layer`控制展开层数，默认全展开|
|initialize\_sememe\_similarity\_calculation(self)|初始化基于义原的词语相似度计算（需要读取相关文件并有短暂延迟）|
|calculate\_word\_similarity(self, word0, word1)|计算基于义原的词语相似度，调用前必须先调用上一个函数进行初始化|`word0`和`word1`表示待计算相似度的词对|
|get\_nearest\_words\_via\_sememes(self, word, K=10)|在使用基于义原的词语相似度度量下，检索和待查词最接近的K个词|`word`表示待查词，`K`表示K近邻算法取的Top-K|
|get\_sememe\_relation(self, sememe0, sememe1)|获取两个义原之间的关系|`sememem0`和`sememem1`代表待查义原|
|get\_sememe\_via\_relation(self, sememe, relation, lang='zh')|检索和某个义原存在某种关系所有义原|`sememe`代表待查义原，`relation`代表关系，`language`为`en`(英文)或`zh`(中文)|

### 使用示例

#### 初始化

```python
import OpenHowNet
hownet_dict = OpenHowNet.HowNetDict()
```
这里如果没有下载义原数据会报错，需要执行`OpenHowNet.download()`。

#### 获取HowNet中的词语对应概念的标注

默认情况下，api将搜索HowNet中输入词的中文和英文标注，带来不必要的开销。注意，如果目标词在HowNet中无标注，将返回空list。

```python
>>> result_list = hownet_dict.get("苹果")
>>> print("检索数量：",len(result_list))
>>> print("检索结果范例:",result_list[0])
检索数量： 6
检索结果范例: {'Def': '{computer|电脑:modifier={PatternValue|样式值:CoEvent={able|能:scope={bring|携带:patient={$}}}}{SpeBrand|特定牌子}}', 'en_grammar': 'noun', 'ch_grammar': 'noun', 'No': '127151', 'syn': [{'id': '004024', 'text': 'IBM'}, {'id': '041684', 'text': '戴尔'}, {'id': '049006', 'text': '东芝'}, {'id': '106795', 'text': '联想'}, {'id': '156029', 'text': '索尼'}, {'id': '004203', 'text': 'iPad'}, {'id': '019457', 'text': '笔记本'}, {'id': '019458', 'text': '笔记本电脑'}, {'id': '019459', 'text': '笔记本电脑'}, {'id': '019460', 'text': '笔记本电脑'}, {'id': '019461', 'text': '笔记本电脑'}, {'id': '019463', 'text': '笔记簿电脑'}, {'id': '019464', 'text': '笔记簿电脑'}, {'id': '020567', 'text': '便携式电脑'}, {'id': '020568', 'text': '便携式计算机'}, {'id': '020569', 'text': '便携式计算机'}, {'id': '127224', 'text': '平板电脑'}, {'id': '127225', 'text': '平板电脑'}, {'id': '172264', 'text': '膝上型电脑'}, {'id': '172265', 'text': '膝上型电脑'}], 'ch_word': '苹果', 'en_word': 'apple'}

>>> hownet_dict.get("test_for_non_exist_word")
[]
```

你可以通过如下方式可视化义原标注信息（义原树），K=2表示只显示输入词对应的两个概念的义原树

```python
>>> hownet_dict.visualize_sememe_trees("苹果", K=2)
Find 6 result(s)
Display #0 sememe tree
[sense]苹果
└── [None]computer|电脑
    ├── [modifier]PatternValue|样式值
    │   └── [CoEvent]able|能
    │       └── [scope]bring|携带
    │           └── [patient]$
    └── [patient]SpeBrand|特定牌	子
Display #1 sememe tree
[sense]苹果
└── [None]fruit|水果
```

为了增加搜索效率，你可以指定目标词的语言。

```python
>>> result_list = hownet_dict.get("苹果", language="zh")
>>> print("单语检索数量：",len(result_list))
单语检索数量： 6
>>> print("单语检索结果范例:",result_list[0])
单语检索结果范例: {'Def': '{computer|电脑:modifier={PatternValue|样式值:CoEvent={able|能:scope={bring|携带:patient={$}}}}{SpeBrand|特定牌子}}', 'en_grammar': 'noun', 'ch_grammar': 'noun', 'No': '127151', 'syn': [{'id': '004024', 'text': 'IBM'}, {'id': '041684', 'text': '戴尔'}, {'id': '049006', 'text': '东芝'}, {'id': '106795', 'text': '联想'}, {'id': '156029', 'text': '索尼'}, {'id': '004203', 'text': 'iPad'}, {'id': '019457', 'text': '笔记本'}, {'id': '019458', 'text': '笔记本电脑'}, {'id': '019459', 'text': '笔记本电脑'}, {'id': '019460', 'text': '笔记本电脑'}, {'id': '019461', 'text': '笔记本电脑'}, {'id': '019463', 'text': '笔记簿电脑'}, {'id': '019464', 'text': '笔记簿电脑'}, {'id': '020567', 'text': '便携式电脑'}, {'id': '020568', 'text': '便携式计算机'}, {'id': '020569', 'text': '便携式计算机'}, {'id': '127224', 'text': '平板电脑'}, {'id': '127225', 'text': '平板电脑'}, {'id': '172264', 'text': '膝上型电脑'}, {'id': '172265', 'text': '膝上型电脑'}], 'ch_word': '苹果', 'en_word': 'apple'}

>>> print("混合检索结果数量:",len(hownet_dict.get("X")))
混合检索结果数量: 5
>>> print("中文检索结果数量:",len(hownet_dict.get("X",language="zh")))
中文检索结果数量: 3
>>> print("英语检索结果数量:",len(hownet_dict.get("X",language="en")))
英语检索结果数量: 2

>>> hownet_dict.get("苹果", language="en")
[]
```

#### 获取所有HowNet中的词语

```python
>>> ch_word_list = hownet_dict.get_ch_words()
>>> print(ch_word_list[:30])
['', '"', '#', '#号标签', '$', '%', "'", '(', ')', '*', '+', '-', '--', '...', '...出什么问题', '...底', '...底下', '...发生故障', '...发生了什么', '...何如', '...家里有几口人', '...检测呈阳性', '...检测呈阴性', '...来', '...内', '...为止', '...也同样使然', '...以来', '...以内', '...以上']

>>> en_word_list = hownet_dict.get_en_words()
>>> print(en_word_list[:30])
['A', 'An', 'Frenchmen', 'Frenchwomen', 'Ottomans', 'a', 'aardwolves', 'abaci', 'abandoned', 'abbreviated', 'abode', 'aboideaux', 'aboiteaux', 'abscissae', 'absorbed', 'acanthi', 'acari', 'accepted', 'acciaccature', 'acclaimed', 'accommodating', 'accompanied', 'accounting', 'accused', 'acetabula', 'acetified', 'aching', 'acicula', 'acini', 'acquired']
```

#### 获取输入词去结构的义原集合

注意：`lang`、`merge`、`expanded_layer`等参数只在`structured = False`时有效。这是因为当处理结构化的数据时，有多种方式解释这些参数，使用者可以自行选择。在下一章节，你将看到如何使用结构化的数据。参数的详细解释在文档中给出。

获取合并过后的多义词的义原

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=False,lang="zh",merge=True)
{'电脑', '交流', '用具', '水果', '特定牌子', '样式值', '能', '树', '生殖', '携带'}

>>> hownet_dict.get_sememes_by_word("apple",structured=False,lang="en",merge=True)
{'communicate', 'able', 'reproduce', 'SpeBrand', 'computer', 'bring', 'tool', 'PatternValue', 'tree', '$', 'fruit'}
```

即使指定的语言和目标词本身语言不匹配，api仍然可以正常工作，并且返回的结果中的语言将是你指定的语言。

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=False,lang="en",merge=True)
{'apple': {'communicate', 'able', 'reproduce', 'SpeBrand', 'computer', 'bring', 'tool', 'PatternValue', 'tree', '$', 'fruit'}, 'malus pumila': {'reproduce', 'fruit', 'tree'}, 'orchard apple tree': {'reproduce', 'fruit', 'tree'}}
```

你可以按照如下方式指定展开的层数：

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=False,merge=True,expanded_layer=2)
{'电脑', '树', '用具', '水果'}
```

你可以在获取所有词的义原树时指定展开层数：

```python
>>> hownet_dict.get_sememes_by_word("*",structured=False,merge=True)
# 结果太长请自己尝试
```

如果你想查看HowNet中特定词的不同意思，只需要将参数`merged`设为`False`。

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=False,lang="zh",merge=False)
[{'word': '苹果', 'sememes': {'特定牌子', '样式值', '电脑', '能', '携带'}},
{'word': '苹果', 'sememes': {'水果'}},
{'word': '苹果', 'sememes': {'特定牌子', '样式值', '能', '交流', '用具', '携带'}},
{'word': '苹果', 'sememes': {'树', '生殖', '水果'}},
{'word': '苹果', 'sememes': {'树', '生殖', '水果'}},
{'word': '苹果', 'sememes': {'树', '生殖', '水果'}}]

>>> hownet_dict.get_sememes_by_word("apple",structured=False,lang="en",merge=False)
[{'word': 'apple', 'sememes': {'able', 'computer', 'bring', 'SpeBrand', 'PatternValue', '$'}},
{'word': 'apple', 'sememes': {'fruit'}},
{'word': 'apple', 'sememes': {'communicate', 'able', 'bring', 'tool', 'SpeBrand', 'PatternValue', '$'}},
{'word': 'apple', 'sememes': {'reproduce', 'fruit', 'tree'}},
{'word': 'apple', 'sememes': {'communicate', 'able', 'bring', 'tool', 'SpeBrand', 'PatternValue', '$'}},
{'word': 'apple', 'sememes': {'reproduce', 'fruit', 'tree'}},
{'word': 'apple', 'sememes': {'fruit'}},
{'word': 'apple', 'sememes': {'fruit'}}]
```

#### 获取输入词结构化的义原树

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=True)[0]["tree"]
{'role': 'sense', 'name': '苹果','children': [
    {'role': 'None', 'name': 'computer|电脑', 'children': [
        {'role': 'modifier', 'name': 'PatternValue|样式值', 'children': [
            {'role': 'CoEvent', 'name': 'able|能', 'children': [
                {'role': 'scope', 'name': 'bring|携带', 'children': [
                    {'role': 'patient', 'name': '$'}
                ]}
            ]}
        ]},
        {'role': 'patient', 'name': 'SpeBrand|特定牌子'}
    ]}
]}
```

可以用两种方式查看对应的标注数据

```python
>>> hownet_dict.get_sememes_by_word("苹果",structured=True)[0]["tree"] # or
>>> hownet_dict.get_sememes_by_word("苹果",structured=True)[0]["word"]
>>> # two results are the same, only displaying one
{'Def': '{computer|电脑:modifier={PatternValue|样式值:CoEvent={able|能:scope={bring|携带:patient={$}}}}{SpeBrand|特定牌子}}',
'en_grammar': 'noun',
'ch_grammar': 'noun',
'No': '127151',
'syn': [
    {'id': '004024', 'text': 'IBM'},
    {'id': '041684', 'text': '戴尔'},
    {'id': '049006', 'text': '东芝'},
    {'id': '106795', 'text': '联想'},
    {'id': '156029', 'text': '索尼'},
    {'id': '004203', 'text': 'iPad'},
    {'id': '019457', 'text': '笔记本'},
    {'id': '019458', 'text': '笔记本电脑'},
    {'id': '019459', 'text': '笔记本电脑'},
    {'id': '019460', 'text': '笔记本电脑'},
    {'id': '019461', 'text': '笔记本电脑'},
    {'id': '019463', 'text': '笔记簿电脑'},
    {'id': '019464', 'text': '笔记簿电脑'},
    {'id': '020567', 'text': '便携式电脑'},
    {'id': '020568', 'text': '便携式计算机'},
    {'id': '020569', 'text': '便携式计算机'},
    {'id': '127224', 'text': '平板电脑'},
    {'id': '127225', 'text': '平板电脑'},
    {'id': '172264', 'text': '膝上型电脑'},
    {'id': '172265', 'text': '膝上型电脑'}
],
'ch_word': '苹果',
'en_word': 'apple'}
```

#### 获取指定词的同义词

相似度计算是基于义原的。

```python
>>> hownet_dict["苹果"][0]["syn"]
[{'id': '004024', 'text': 'IBM'},
 {'id': '041684', 'text': '戴尔'},
 {'id': '049006', 'text': '东芝'},
 {'id': '106795', 'text': '联想'},
 {'id': '156029', 'text': '索尼'},
 {'id': '004203', 'text': 'iPad'},
 {'id': '019457', 'text': '笔记本'},
 {'id': '019458', 'text': '笔记本电脑'},
 {'id': '019459', 'text': '笔记本电脑'},
 {'id': '019460', 'text': '笔记本电脑'},
 {'id': '019461', 'text': '笔记本电脑'},
 {'id': '019463', 'text': '笔记簿电脑'},
 {'id': '019464', 'text': '笔记簿电脑'},
 {'id': '020567', 'text': '便携式电脑'},
 {'id': '020568', 'text': '便携式计算机'},
 {'id': '020569', 'text': '便携式计算机'},
 {'id': '127224', 'text': '平板电脑'},
 {'id': '127225', 'text': '平板电脑'},
 {'id': '172264', 'text': '膝上型电脑'},
 {'id': '172265', 'text': '膝上型电脑'}]
```

#### 通过ID访问词

```python
>>> hownet_dict["004024"]
['Def', 'en_grammar', 'ch_grammar', 'No', 'syn', 'ch_word', 'en_word']
```

#### 获取所有义原

```python
>>> len(hownet_dict.get_all_sememes())
2187
```

#### 查询义原之间的关系

你输入的义原可以使用任意语言：

```python
>>> hownet_dict.get_sememe_relation("音量值", "尖声")
'hyponym'

>>> hownet_dict.get_sememe_relation("尖声", "SoundVolumeValue")
'hyponym'

>>> hownet_dict.get_sememe_relation("shrill", "SoundVolumeValue")
'hypernym'

>>> hownet_dict.get_sememe_relation("音量值", "shrill")
'hypernym'
```

输出共有 hypernym, hyponym, antonym, converse 四种。

#### 检索与输入义原存在某种关系的所有义原

你输入的义原可以使用任意语言，但是关系必须为英文小写；同时你可以指定输出的义原的语言，默认为中文。

```python
>>> hownet_dict.get_sememe_via_relation("音量值", "hyponym")
['高声', '低声', '尖声', '沙哑', '无声', '有声']

>>> hownet_dict.get_sememe_via_relation("音量值", "hyponym", lang="en")
['loud', 'LowVoice', 'shrill', 'hoarse', 'silent', 'talking']

>>> hownet_dict.get_sememe_via_relation("SoundVolumeValue", "hyponym", lang="en")
['loud', 'LowVoice', 'shrill', 'hoarse', 'silent', 'talking']
```

### 高级功能：通过义原计算词语相似度

实现方法基于以下论文：

> Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP

#### 额外初始化

由于计算相似度需要额外的文件，初始化的开销将比之前的大。你可以按照如下方式初始化：

```python
>>> hownet_dict_advanced = OpenHowNet.HowNetDict(use_sim=True)
```

你也可以在需要使用时再进行额外的初始化，这时，初始化的返回值将代表额外的初始化是否成功。

```python
>>> hownet_dict.initialize_sememe_similarity_calculation()
True
```

#### 获取K个最接近输入词的词

如果输入词不在HowNet中，函数将返回一个空list。

```python
>>> query_result = hownet_dict_advanced.get_nearest_words_via_sememes("苹果",20)
>>> example = query_result[0]
>>> print("word_name:",example["word"])
word_name: 苹果
>>> print("id:",example["id"])
id: 127151
>>> print("synset and corresonding word&id&score:")
synset and corresonding word&id&score:
>>> print(example["synset"])
[{'id': 4024, 'word': 'IBM', 'score': 1.0},
 {'id': 41684, 'word': '戴尔', 'score': 1.0},
 {'id': 49006, 'word': '东芝', 'score': 1.0},
 {'id': 106795, 'word': '联想', 'score': 1.0},
 {'id': 156029, 'word': '索尼', 'score': 1.0},
 {'id': 4203, 'word': 'iPad', 'score': 0.865},
 {'id': 19457, 'word': '笔记本', 'score': 0.865},
 {'id': 19458, 'word': '笔记本电脑', 'score': 0.865},
 {'id': 19459, 'word': '笔记本电脑', 'score': 0.865},
 {'id': 19460, 'word': '笔记本电脑', 'score': 0.865},
 {'id': 19461, 'word': '笔记本电脑', 'score': 0.865},
 {'id': 19463, 'word': '笔记簿电脑', 'score': 0.865},
 {'id': 19464, 'word': '笔记簿电脑', 'score': 0.865},
 {'id': 20567, 'word': '便携式电脑', 'score': 0.865},
 {'id': 20568, 'word': '便携式计算机', 'score': 0.865},
 {'id': 20569, 'word': '便携式计算机', 'score': 0.865},
 {'id': 127224, 'word': '平板电脑', 'score': 0.865},
 {'id': 127225, 'word': '平板电脑', 'score': 0.865},
 {'id': 172264, 'word': '膝上型电脑', 'score': 0.865},
 {'id': 172265, 'word': '膝上型电脑', 'score': 0.865}]
```

#### 计算两个指定词的相似度

如果其中的任何一个词不在HowNet中，函数将返回0。

```python
>>> hownet_dict_advanced.calculate_word_similarity("苹果", "梨")
1.0
```
