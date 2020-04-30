# 基于知网的词语语义相似度计算

# 语义相似度计算

本程序实现了基于知网的词语语义相似度计算，利用知网中的义原 (sememe) 信息计算给定两个词义 (sense) 的相似度，并输出每个词义 (sense) 以及知网中与其相似度最高的20个词义 (sense) 。

本程序采用的算法部分参考了 [Liu et al., 2013] 中的方法，但略去了其中对于义原 (sememe) 相似度的考虑。



## 数据

词语语义相似度计算依赖于《知网》知识系统2008版 (Hownet 2008: http://www.keenage.com/html/c_content_2008.htm)

请在data目录下放置如下文件：

- HowNet Taxonomy Attribute.txt
- HowNet Taxonomy AttributeValue.txt
- HowNet Taxonomy Entity.txt
- HowNet Taxonomy Event.txt
- HowNet Taxonomy ProperNoun.txt
- HowNet Taxonomy SecondaryFeature.txt
- HowNet Taxonomy Sign.txt
- HowNet_original_new.txt

本版本Hownet中包含：

- 127251 词 (word)
- 229751 词义 (sense)
- 2198 义原 (sememe)

其中，从下标3378的词义 (sense) 开始，有对应的中文符号，在语义的相似度时，我们只考虑这部分词义。



## 依赖

- Python (>=3.5)
- AnyTree (=2.43)



# 使用

- 首次使用，请将main.py中的first_time设置为False，否则设置为True。
- 执行相似度计算的命令为：

```
python main.py <start_sense_idx> <end_sense_idx>
```

程序将计算下标在 [start_sense_idx, end_sense_idx] 内的词义 (sense) 其它所有词义的相似度，当end_sense_idx为-1时，end_sense_idx取所有词义 (sense) 下标的上限。

例如，可通过如下命令分批计算得到所有词义之间的相似度：

```
python main.py 210001 -1
python main.py 180001 210000
python main.py 150001 180000
python main.py 120001 150000
python main.py 90001 120000
python main.py 60001 90000
python main.py 30001 60000
python main.py 3378 30000
```

- 输出文件为\<start_sense_idx>-\<end_sense_idx>.txt，每行格式为：

```
词义编号, 词义	相似度Top20{词义编号, 词义, 相似度;}
```

例如：

```
127151, 苹果		4024, IBM, 1.00; 41684, 戴尔, 1.00; 49006, 东芝, 1.00; 106795, 联想, 1.00; 156029, 索尼, 1.00; 4203, iPad, 0.86; 19457, 笔记本, 0.86; 19458, 笔记本电脑, 0.86; 19459, 笔记本电脑, 0.86; 19460, 笔记本电脑, 0.86; 19461, 笔记本电脑, 0.86; 19463, 笔记簿电脑, 0.86; 19464, 笔记簿电脑, 0.86; 20567, 便携式电脑, 0.86; 20568, 便携式计算机, 0.86; 20569, 便携式计算机, 0.86; 127224, 平板电脑, 0.86; 127225, 平板电脑, 0.86; 172264, 膝上型电脑, 0.86; 172265, 膝上型电脑, 0.86; 
```



## 参考文献

[Liu et al., 2013]  Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP.