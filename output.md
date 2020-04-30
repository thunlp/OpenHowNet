# A simple demo for the HowNet Python Package

To begin with, make sure you have installed **Python 3.X**.  The **anytree**
dependency is required to be installed.

It is our only required dependency
because other python packages we need in building the **HowNet** Python Package
will be **defaultly** installed with the Python 3.X. 

Then you should download
the **HowNet** Package.  Please checkout the installation by import the
**Standards** module like the following code:

```python
from HowNet import Standards
```

After that we can build a **HowNet dict**:

```python
hownet_dict = Standards.HowNetDict()
```

Finally, the preparation work is all done! Then let's explore some important
features of HowNetDict!

# Basic Usage of OpenHowNet Python Package

## Get word annotations in HowNet
<b> By default, the api will search the target
word in both English and Chinese annotations in HowNet, which will cause
significant search overhead. Note that if the target word does not exist in
HowNet annotation, this api will simply return an empty list. </b>

```python
result_list = hownet_dict.get("苹果")
print("检索数量：",len(result_list))
print("检索结果范例:",result_list[0])
```

```python
hownet_dict.get("test_for_non_exist_word")
```

<b> You can visualize the retrieved HowNet structured annotations ("sememe
tree") of the target word as follow : <br>
    (K=2 means only display 2 sememe
trees) </b>

```python
hownet_dict.visualize_sememe_trees("苹果", K=2)
```

<b> To boost the efficiency of the search process, you can specify the language
of the target word as the following. </b>

```python
result_list = hownet_dict.get("苹果", language="zh")
print("单语检索数量：",len(result_list))
print("单语检索结果范例:",result_list[0])
print("-------双语混合检索测试---------")
print("混合检索结果数量:",len(hownet_dict.get("X")))
print("中文检索结果数量:",len(hownet_dict.get("X",language="zh")))
print("英语检索结果数量:",len(hownet_dict.get("X",language="en")))
```

```python
hownet_dict.get("苹果", language="en")
```

## Get All Words annotated in HowNet

```python
zh_word_list = hownet_dict.get_zh_words()
en_word_list = hownet_dict.get_en_words()
```

```python
print(zh_word_list[:30])
```

```python
print(en_word_list[:30])
```

## Get Flattened Sememe Trees for certain word or all words in HowNet

<b>
Cautions: the parameters "lang", "merge" and "expanded_layer" only works when
"structured = False". The main consideration is that there are multiple ways to
interpret these params when deal with structured data. We leave the freedom to
our end user. In next section, you will be able to see how to utilize the
structured data.

   Detailed explanation of params will be displayed in our
documentation.</b>

### Get the full merged sememe list from multi-sense words

```python
hownet_dict.get_sememes_by_word("苹果",structured=False,lang="zh",merge=True)
```

```python
hownet_dict.get_sememes_by_word("apple",structured=False,lang="en",merge=True)
```

**Even if the language is not corresponding to the target word, the api still
works. It will keep all the returned word entries to be in the same language you
specified**

```python
hownet_dict.get_sememes_by_word("苹果",structured=False,lang="en",merge=True)
```

**Note that, in the latest version, if the number of the word entries equals to
one, for convenience, the api will simply return the set of sememes. See Out[11]
for example.**

<b> You could specify the number of the expanded layers like the following:</b>

```python
hownet_dict.get_sememes_by_word("苹果",structured=False,merge=True,expanded_layer=1)
```

<b>You could get all flattened sememe trees for all words as well as specify the
number of the expanded layers:</b>

```python
hownet_dict.get_sememes_by_word("*",structured=False,merge=True)
```

<b> If you would like to see the sememe lists for different senses of particular
word in HowNet,  just need to set the param "merged" to False.</b>

```python
hownet_dict.get_sememes_by_word("苹果",structured=False,lang="zh",merge=False)
```

```python
hownet_dict.get_sememes_by_word("apple",structured=False,lang="en",merge=False)
```

## Get Structured Sememe Trees for certain words in HowNet

```python
hownet_dict.get_sememes_by_word("苹果",structured=True)[0]["tree"]
```

<b> Two ways to see the corresponding annotation data </b>

```python
hownet_dict.get_sememes_by_word("苹果",structured=True)[0]["word"]
```

```python
hownet_dict["苹果"][0]
```

## Get the static synonyms of the certain word
<b>The similarity metrics are
based on HowNet.</b>

```python
hownet_dict["苹果"][0]["syn"]
```

## Get access of the word by ID

```python
hownet_dict["004024"]
```

## Get all sememes

```python
hownet_dict.get_all_sememes()
```

# Advanced Feature #1: Word Similarity Calculation via Sememes
<b>The following
parts are mainly implemented by Jun Yan and integrated by Chenghao Yang. Our
implementation is based on the paper: </b>

  >Jiangming Liu, Jinan Xu, Yujie
Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity
Computing by HowNet. In Proceedings of IJCNLP

## Extra Initialization

<b> Because there are some files required to be loaded for similarity
calculation. The initialization overhead will be larger than before. To begin
with, you can initialize the hownet_dict object as the following code:</b>

```python
hownet_dict_advanced = Standards.HowNetDict(use_sim=True)
```

<b>You can also postpone the initialization work of similarity calculation until
use. The following code serves as an example and the return value will indicate
whether the extra initialization process succeed.</b>

```python
hownet_dict.initialize_sememe_similarity_calculation()
```

## Get Top-K Nearest Words for the Given Word
<b>If the given word does not
exist in HowNet annotations, this function will return an empty list.</b>

```python
query_result = hownet_dict_advanced.get_nearest_words_via_sememes("苹果",20)
example = query_result[0]
print("word_name:",example["word"])
print("id:",example["id"])
print("synset and corresonding word&id&score:")
print(example["synset"])
```

```python
hownet_dict_advanced.get_nearest_words_via_sememes("苹果",20)
```

## Calculate the Similarity for the Given Two Words
<b>If any of the given words
does not exist in HowNet annotations, this function will return 0.</b>

```python
hownet_dict_advanced.calculate_word_similarity("苹果","梨")
```
