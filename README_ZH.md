<p align="center">
  <a href="https://openhownet.thunlp.org/">
    <img src="openhownet-logo.png" width = "300"  alt="OpenHowNet Logo" align=center />
  </a>
</p>

### [English Version](README.md)

本项目存放HowNet核心数据和清华大学自然语言处理实验室（THUNLP）开发的OpenHowNet API，提供方便的义原信息查询、义原树展示、基于义原的词相似度计算等功能。您还可以访问我们的[网站](https://openhownet.thunlp.org)体验义原在线查询和展示功能。

如果您在研究中使用了OpenHowNet提供的数据或API，请引用以下论文：

@article{
    qi2019openhownet,
​    title={OpenHowNet: An Open Sememe-based Lexical Knowledge Base},
​    author={Qi, Fanchao and Yang, Chenghao and Liu, Zhiyuan and Dong, Qiang and Sun, Maosong and Dong, Zhendong},
​    journal={arXiv preprint arXiv:1901.09957},
​    year={2019},
​}

## HowNet核心数据

HowNet核心数据文件（`HowNet.txt`）由237,973个中英文词和词组所代表的概念构成。HowNet为每个概念标注了基于义原的定义以及词性、情感倾向、例句等信息。下面是HowNet中一个概念的示例：

```
NO.=000000026417 # 概念编号
W_C=不惜    # 中文词
G_C=verb [2 5000  ] [bu4 xi1]   # 中文词词性
S_C=PlusFeeling|正面情感    # 中文词情感倾向
E_C=~牺牲业余时间，~付出全部精力，~出卖自己的灵魂   # 中文词例句
W_E=do not hesitate to  # 英文词
G_E=verb [51do verb -0 vt,sobj       ]  # 英文词词性
S_E=PlusFeeling|正面情感    # 英文词情感倾向
E_E=    # 英文词例句
DEF={willing|愿意}  # 基于义原的定义
RMK=
```

## OpenHowNet API

### 运行要求

* Python>=3.6
* anytree>=2.4.3
* tqdm>=4.31.1
* requests>=2.22.0

### 安装

你可以选择使用 `pip` 或者克隆本仓库来安装OpenHowNet工具包

1. **通过 pip 安装（推荐）**

```bash
pip install OpenHowNet
```

2. **通过 Github 安装**

```bash
git clone https://github.com/thunlp/OpenHowNet/
cd OpenHowNet
python setup.py install
```

### 核心数据类型

* **HowNetDict**：HowNet词典类，封装对于HowNet核心数据的检索、展示、相似度计算等核心功能。
* **Sense**：封装HowNet中的概念的信息，包含基于义原的中英文词语、词性、义原描述的定义等信息。
* **Sememe**：封装HowNet中的义原的信息，包含描述义原的中英文词语、义原出现频率以及义原间关系信息。

### 使用示例


#### 初始化


```python
import OpenHowNet
hownet_dict = OpenHowNet.HowNetDict()
```

这里如果没有下载义原数据会报错，需要执行 `OpenHowNet.download()` 。


#### 基本功能：获取HowNet中的词语对应的概念


默认情况下，api将搜索HowNet中输入词的中文和英文标注，并返回标注有目标词语的Sense实例列表。为了提高效率，可以设置输入词的语言。注意，如果目标词在HowNet中无标注，将返回空list。


```python
>>> # Get the senses list annotated with "苹果".
>>> result_list = hownet_dict.get_sense("苹果")
>>> print("The number of retrievals: ", len(result_list))
The number of retrievals:  8
>>> print("An example of retrievals: ", result_list)
An example of retrievals:  [No.244401|apple|苹果, No.244402|malus pumila|苹果, No.244403|orchard apple tree|苹果, No.244396|apple|苹果, No.244397|apple|苹果, No.244398|IPHONE|苹果, No.244399|apple|苹果, No.244400|iphone|苹果]
```

通过每个Sense实例，可以得到每个概念的详细信息。

```python
>>> sense_example = result_list[0]
>>> print("Sense example:", sense_example)
Sense example: No.244401|apple|苹果
>>> print("Sense id: ",sense_example.No)
Sense id:  000000244401
>>> print("English word in the sense: ", sense_example.en_word)
English word in the sense:  apple
>>> print("Chinese word in the sense: ", sense_example.zh_word)
Chinese word in the sense:  苹果
>>> print("HowNet Def of the sense: ", sense_example.Def)
HowNet Def of the sense:  {tree|树:{reproduce|生殖:PatientProduct={fruit|水果},agent={~}}}
>>> print("Sememe list of the sense: ", sense_example.get_sememe_list())
Sememe list of the sense:  {fruit|水果, tree|树, reproduce|生殖}
```

你可以通过如下方式可视化每个义原的标注信息（义原树）。


```python
>>> sense_example.visualize_sememe_tree()
[sense]No.244401|apple|苹果
└── [None]tree|树
    └── [agent]reproduce|生殖
        └── [PatientProduct]fruit|水果
```

#### 获取HowNet中的所有词语和义原

工具包提供了方便的获取HowNet中的所有的词语、义原等信息的api。


```python
>>> all_senses = hownet_dict.get_sense('*')
>>> print("The number of all senses: {}".format(len(all_senses)))
The number of all senses: 237974
>>> zh_word_list = hownet_dict.get_zh_words()
>>> en_word_list = hownet_dict.get_en_words()
>>> print("Chinese words in HowNet: ",zh_word_list[:30])
Chinese words in HowNet:  ['', '"', '#', '#号标签', '$', '$.J.', '$A.', '$NZ.', '%', "'", '(', ')', '*', '+', ',', '-', '--', '.', '...', '...为止', '...也同样使然', '...以上', '...以内', '...以来', '...何如', '...内', '...出什么问题', '...发生了什么', '...发生故障', '...家里有几口人']
>>> print("English words in HowNet: ",en_word_list[:30])
English words in HowNet:  ['A', 'An', 'Frenchmen', 'Frenchwomen', 'Ottomans', 'a', 'aardwolves', 'abaci', 'abandoned', 'abbreviated', 'abode', 'aboideaux', 'aboiteaux', 'abscissae', 'absorbed', 'acanthi', 'acari', 'accepted', 'acciaccature', 'acclaimed', 'accommodating', 'accompanied', 'accounting', 'accused', 'acetabula', 'acetified', 'aching', 'acicula', 'acini', 'acquired']
```


#### 获取输入词获取义原标注


工具包提供了根据输入的目标词语检索相关义原标注信息的功能。默认情况下，工具包将查找该词语标注的Sense列表，并返回每个Sense对应的Sememe列表。


```python
>>> hownet_dict.get_sememes_by_word(word = '苹果', display='list', merge=False, expanded_layer=-1, K=None)
[{'sense': No.244396|apple|苹果,
  'sememes': {PatternValue|样式值, SpeBrand|特定牌子, able|能, bring|携带, computer|电脑}},
 {'sense': No.244397|apple|苹果, 
  'sememes': {fruit|水果}},
 {'sense': No.244398|IPHONE|苹果,
  'sememes': {PatternValue|样式值, SpeBrand|特定牌子, able|能, bring|携带, communicate|交流, tool|用具}},
 {'sense': No.244399|apple|苹果,
  'sememes': {PatternValue|样式值, SpeBrand|特定牌子, able|能, bring|携带, communicate|交流, tool|用具}},
 {'sense': No.244400|iphone|苹果,
  'sememes': {PatternValue|样式值, SpeBrand|特定牌子, able|能, bring|携带, communicate|交流, tool|用具}},
 {'sense': No.244401|apple|苹果, 
  'sememes': {fruit|水果, reproduce|生殖, tree|树}},
 {'sense': No.244402|malus pumila|苹果,
  'sememes': {fruit|水果, reproduce|生殖, tree|树}},
 {'sense': No.244403|orchard apple tree|苹果,
  'sememes': {fruit|水果, reproduce|生殖, tree|树}}]
```

通过设置 `display` ，可以将义原以列表形式、词典形式、树节点形式、可视化形式等不同形式进行展示。

当 `display=='list'` 时，可以选择将所有Sense的义原列表合并到同一个列表，以及设置义原树展开的层数等。

```python
>>> hownet_dict.get_sememes_by_word(word = '苹果', display='list', merge=True, expanded_layer=-1, K=None)
{PatternValue|样式值, SpeBrand|特定牌子, able|能, bring|携带, communicate|交流, computer|电脑, fruit|水果,
 reproduce|生殖, tool|用具, tree|树}
```


#### 查询义原之间的关系


你可以输入任何语言来查找义原并查找义原之间的关系。同时可以选择将整个三元组输出。


```python
>>> relations = hownet_dict.get_sememe_relation('FormValue','圆', return_triples=False)
>>> print(relations)
'hyponym'
>>> triples = hownet_dict.get_sememe_relation('FormValue','圆', return_triples=True)
>>> print(triples)
[(FormValue|形状值, 'hyponym', round|圆)]
```


#### 检索与输入义原存在某种关系的所有义原


你输入的义原可以使用任意语言，但是关系必须为英文小写。同样的，可以选择将整个三元组输出。


```python
>>> triples = hownet_dict.get_sememe_via_relation('FormValue', 'hyponym',return_triples=True)
>>> print(triples)
[(FormValue|形状值, 'hyponym', round|圆), (FormValue|形状值, 'hyponym', unformed|不成形), (AppearanceValue|外观值, 'hyponym', FormValue|形状值), (FormValue|形状值, 'hyponym', angular|角), (FormValue|形状值, 'hyponym', square|方), (FormValue|形状值, 'hyponym', netlike|网), (FormValue|形状值, 'hyponym', formed|成形)]
```


### 高级功能：通过义原计算词语相似度


实现方法基于以下论文：


> Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP


#### 额外初始化


由于计算相似度需要额外的文件，初始化的开销将比之前的大。你可以按照如下方式初始化：


```python
>>> hownet_dict_anvanced = OpenHowNet.HowNetDict(init_sim=True)
Initializing OpenHowNet succeeded!
Initializing similarity calculation succeeded!
```


你也可以在需要使用时再进行额外的初始化。


```python
>>> hownet_dict.initialize_similarity_calculation()
Initializing similarity calculation succeeded!
```


#### 获取K个最接近输入词的词


工具包将查找输入词标注的Sense，并分别查找K个最接近的Sense，并输出对应的词语。注意：应设置输入词的语言。同时可以选择设置所需词语的词性、输出词语相似度以及无视Sense将所有词语合并到同一个列表等，具体请查询文档说明。如果输入词不在HowNet中，函数将返回一个空list。


```python
>>> hownet_dict_anvanced.get_nearest_words('苹果', language='zh',K=5)
{No.244396|apple|苹果: ['IBM', '东芝', '华为', '戴尔', '索尼'],
 No.244397|apple|苹果: ['丑橘', '乌梅', '五敛子', '凤梨', '刺梨'],
 No.244398|IPHONE|苹果: ['OPPO', '华为', '苹果', '智能手机', '彩笔'],
 No.244399|apple|苹果: ['OPPO', '华为', '苹果', '智能手机', '彩笔'],
 No.244400|iphone|苹果: ['OPPO', '华为', '苹果', '智能手机', '彩笔'],
 No.244401|apple|苹果: ['山梨', '山楂', '山楂树', '山里红', '开心果树'],
 No.244402|malus pumila|苹果: ['山梨', '山楂', '山楂树', '山里红', '开心果树'],
 No.244403|orchard apple tree|苹果: ['山梨', '山楂', '山楂树', '山里红', '开心果树']}
>>> hownet_dict_anvanced.get_nearest_words('苹果', language='zh',K=5, merge=True)
['IBM', '东芝', '华为', '戴尔', '索尼']
```


#### 计算两个指定词的相似度


如果其中的任何一个词不在HowNet中，函数将返回-1。

```python
>>> print('The similarity of 苹果 and 梨 is {}.'.format(hownet_dict_anvanced.calculate_word_similarity('苹果','梨')))
The similarity of 苹果 and 梨 is 1.0.
```

