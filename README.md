# OpenHowNet API

本项目存放HowNet核心数据和THUNLP开发的OpenHowNet API，提供方便的HowNet信息查询、义原树展示、基于义原的词相似度计算等功能。关于OpenHowNet的更多信息可以访问我们的[网站](https://openhownet.thunlp.org)。

如果您在研究中使用了OpenHowNet的数据或API，请引用以下两篇文章：

	@inproceedings{dong2003hownet,
	  title={HowNet-a hybrid language and knowledge resource},
	  author={Dong, Zhendong and Dong, Qiang},
	  booktitle={Proceedings of NLP-KE},
	  year={2003},
	}
	@article{qi2019openhownet,
	  title={OpenHowNet: An Open Sememe-based Lexical Knowledge Base},
	  author={Qi, Fanchao and Yang, Chenghao and Liu, Zhiyuan and Dong, Qiang and Sun, Maosong and Dong, Zhendong},
	  journal={arXiv preprint},
	  year={2019},
	}
	  
## HowNet核心数据
数据文件（`HowNet.txt`）由223,767个以中英文词和词组所代表的概念构成，HowNet为每个概念标注了基于义原的定义以及词性、情感倾向、例句等信息。下图提供了HowNet中一个概念的例子：

![HowNet Example](hownet-example.png)

## OpenHowNet API

### 接口说明

|接口|功能说明|参数说明|
|---|-------|-------|
get(self, word, language=None)|检索HowNet中词语标注的完整信息|word表示待查词，language为en(英文)/ch(中文)，默认双语同时查找
get\_sememes\_by\_word(self, word, structured=False, lang='ch', merge=False, expanded_layer=-1)|检索输入词的义原，可以选择是否合并多义，也可以选择是否以结构化的方式返回，还可以指定展开层数。|word表示待查词，language为en(英文)/ch(中文), structured表示是否以结构化的方式返回，merge控制是否合并多义项，expanded_layer控制展开层数，默认全展开。
initialize\_sememe\_similarity\_calculation(self)|初始化基于义原的词语相似度计算（需要读取相关文件并有短暂延迟）|
calculate\_word\_similarity(self, word0, word1)|计算基于义原的词语相似度，调用前必须先调用上一个函数进行初始化|word0和word1表示待查的词语相似度对
get\_nearest\_words\_via\_sememes(self, word, K=10)|在使用基于义原的词语相似度度量下，计算和检索词最接近的K个词|Word表示检索词，K表示K近邻算法取的Top-K

请阅读文档`./HowNet/Standards.html`或查看Demo`DemoForHowNetPackage.ipynb`了解更多。

### 运行要求
* Python==3.6
* anytree==2.4.3

### 使用方式
1. 首先运行`HowNet/run.sh`来处理数据文件。
2. 然后可以打开Jupyter Demo 文件`DemoForHowNetPackage.ipynb`来运行API示例程序。
