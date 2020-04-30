# 基于知网的词语语义相似度计算

# 语义相似度计算

本程序实现了基于知网的词语语义相似度计算，利用知网中的义原 (sememe) 信息计算给定两个词 (word) 的相似度，或计算给定词 (word) 各词义 (sense) 在知网中最相近的10个词义 (sense) 。

本程序采用的算法部分参考了 [Liu et al., 2013] 中的方法，但略去了其中对于义原 (sememe) 的定义相似度 (DEF similarity) 的考虑。



## 数据

词语语义相似度计算依赖于《知网》知识系统2008版 (HowNet 2008: http://www.keenage.com/html/c_content_2008.htm)

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

其中，从下标3378的词义 (sense) 开始，有对应的中文符号，在计算语义相似度时，我们只考虑这部分词义。

## 依赖

- Python (>=3.5)
- AnyTree (=2.43)




# 使用

- 首次使用需对HowNet数据进行加载，并预先计算两两义原 (sememe) 之间的相似度。可采用如下两种方法之一：

  - 将main.py中的first_time设置为True，执行程序（耗时较长，约2.5小时）。

  或

  - 下载`hownet.pkl`、`sememe_root.pkl`、`sememe_sim_table.pkl`，放入`pickle`文件夹下。

  此后使用时注意将main.py中的first_time设置为False。

- 语义相似度的计算共有两种模式：

  1. 输入一个词 (word)，对于该词的各个词义，分别输出最相近的10个词义。例如

     ```
     Select a mode (1 or 2): 1
     Please input a word ("q" to quit): 笔记本
     19455, 笔记本		18641, 本, 1.00; 18879, 本子, 1.00; 18880, 本子, 1.00; 19462, 笔记簿, 1.00; 21286, 表册, 1.00; 21287, 表册, 1.00; 26159, 簿册, 1.00; 26160, 簿籍, 1.00; 26162, 簿子, 1.00; 28058, 册, 1.00; 
     19456, 笔记本		18641, 本, 1.00; 18879, 本子, 1.00; 18880, 本子, 1.00; 19462, 笔记簿, 1.00; 21286, 表册, 1.00; 21287, 表册, 1.00; 26159, 簿册, 1.00; 26160, 簿籍, 1.00; 26162, 簿子, 1.00; 28058, 册, 1.00; 
     19457, 笔记本		4203, iPad, 1.00; 19458, 笔记本电脑, 1.00; 19459, 笔记本电脑, 1.00; 19460, 笔记本电脑, 1.00; 19461, 笔记本电脑, 1.00; 19463, 笔记簿电脑, 1.00; 19464, 笔记簿电脑, 1.00; 20567, 便携式电脑, 1.00; 20568, 便携式计算机, 1.00; 20569, 便携式计算机, 1.00; 
     ```

  2. 先后输入两个词 (word) ，输出这两个词的语义相似度（两个词各词义之间相似度的最小值）。例如

     ```
     Select a mode (1 or 2): 2
     Please input the first word ("q" to quit): 男人
     Please input the second word ("q" to quit): 父亲
     Word similarity:  0.8394999999999999
     ```



## 参考文献

[Liu et al., 2013]  Jiangming Liu, Jinan Xu, Yujie Zhang. An Approach of Hybrid Hierarchical Structure for Word Similarity Computing by HowNet. In Proceedings of IJCNLP.