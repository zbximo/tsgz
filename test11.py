# -*- encoding: utf-8 -*-
# @ModuleName: test11
# @Author: ximo
# @Time: 2024/5/27 11:39

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.decomposition import PCA
from paddlenlp import Taskflow
from models.Cluster import Cluster
import config
import utils.Tools

# 1.加载数据
text_list = [
    '很棒的一款男士香水，淡淡的香味很清爽，使用后感觉整个人心情都变好了！感谢老板送的香水小样，以后还会光顾的，很满意的一次购物！物流速度也很快，值得购买！ ',
    '回购很多次了，依旧品质如一，和风雨值得信赖，真的好用，包装也精美，很适合送礼，性价比很高！喜欢香水的朋友值得购买！支持店家！',
    '节日礼物：很喜欢，还送了四瓶小的，之前买的固体香膏，都是木质的，香味不冲，作为给自己的礼物很理想\n留香时间：蛮持久的，合适',
    '节日礼物：520送老公的礼物\n味道浓淡：了一段时间， 这款香味比较淡，淡淡的清香，不刺鼻，很好闻\n留香时间：持久留香，一天基本上都会有淡淡的清香，喜欢的朋友的朋友抓紧入手了 ',
    '香水收到了 真的太棒了 包装也很高档  主要是味道太喜欢了 而且留香时间特别长 还有赠品  太给力了 ',
    '香水很好，香味很喜欢，包装很好，有手提袋，送朋友也是不错的选择。买的气质灰，很不错的一次购物。 ',
    '非常满意的一次购物，香水味道闻起来非常舒服，不刺鼻，和风雨正品，相信京东自营产品，用完之后还会来的，店家服务态度很好，么么哒 ',
    '大品牌值得信赖！和风雨男士香水礼盒套装！100ml 大瓶装更划算！海洋靛淡香清新自然好闻！适合大众男士！留香时间比较久！味道淡淡的！适合各种场合！京东平台值得放心！满意的一次购物！值得推荐购买！物美价廉！点赞！！',
    '眼就看这款式了 ，拿着好看 ?，刚开始是冲着这款香水颜值来的，本来还会担心味道刺鼻不好闻，没想到味道是我喜欢的淡淡的，?香味很好闻不刺鼻，闻着让人很放松，适合我们男士用，留香时间也很好，时间长了也可以闻到的，挺好。',
    '已经收到了，满满一大瓶子，估计可以用很久了。惊喜是没想到外包装盒子的质感那么好！！！绝对好评，瓶子也非常好看，拿起来特别有质感。稍微喷了一下，问起来有水果的味道，不会刺鼻，而是很清新的味道，像是在果园里一样，很喜欢的味道，暂时不知道留香时间，等明天白天试用一下，再来评价吧。'
]
text_list = [
    "普京即将访华",
    "普京访华，美国人很愤怒",
    "普京访华,英国人很生气",
    "普京即将访华, 中国表示非常欢迎",
    "普京到达中国，中国热烈欢迎",
    "普京即将访华, 日本人虎视眈眈",
]
stop_words = utils.Tools.get_stopwords()
c = Cluster()
c.load_pos_model()
pos_result = c.get_pos(text_list)

corpus = []
for i in pos_result:
    # print(i)
    corpus.append(" ".join(i))
# 4.特征提取
# 4.1 文本转换成词袋模型(词频作为统计指标)   加载停用词,添加词语进词袋时会过滤停用词
countVectorizer = CountVectorizer(stop_words=stop_words, analyzer="word")
count_v = countVectorizer.fit_transform(corpus)
# 词袋中的词语
# print(countVectorizer.get_feature_names_out())
# 词频向量
# print(count_v.toarray())
# 4.2 词频统计指标转换 tf-idf统计指标  (不是必须的,用哪种指标根据具体业务来看)
tfidfTransformer = TfidfTransformer()
tfidf = tfidfTransformer.fit_transform(count_v)
# print(tfidf.toarray())
pca = PCA(n_components=2)
pca_weights = pca.fit_transform(tfidf.toarray())

# print(pca_weights)
# 5.聚类计算 (这里用dbscan算法)
# clf = DBSCAN(eps=0.4, min_samples=2)

# clf = AgglomerativeClustering(n_clusters=None, distance_threshold=1)
# y = clf.fit_predict(pca_weights)
# # 每个文本对应的簇的编号 (-1 在dbscan中属于噪音簇,里面都是噪音点)
# print(y)
# result = {}
# for text_idx, label_idx in enumerate(y):
#     key = "cluster_{}".format(label_idx)
#     if key not in result:
#         result[key] = [text_idx]
#     else:
#         result[key].append(text_idx)
# for clu_k, clu_v in result.items():
#     print("\n", "~" * 170)
#     print(clu_k)
#     # print(clu_v)
#     for i in clu_v:
#         print(text_list[i], corpus[i], "\n===============================>")

from services.TaskService import TaskService

TS = TaskService()
TS.analyze_task(1, 48)
