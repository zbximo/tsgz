# -*- encoding: utf-8 -*-
# @ModuleName: Cluster
# @Author: ximo
# @Time: 2024/5/10 10:53
import time

import numpy as np
from BCEmbedding import EmbeddingModel
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from paddlenlp import Taskflow
from utils.Tools import *
import config
import utils
from transformers import AutoTokenizer


class Cluster():
    def __init__(self, TEXT_EMB_MODEL_PATH=config.MODEL_CONFIG["bce-embedding-base_v1"],
                 POS_MODEL_PATH=config.MODEL_CONFIG["lac"]):
        self.pos_task = None
        self.model = None
        self.TEXT_EMB_MODEL_PATH = TEXT_EMB_MODEL_PATH
        self.POS_MODEL_PATH = POS_MODEL_PATH

    def load_text_emb(self, device='cuda:1'):
        self.model = EmbeddingModel(model_name_or_path=config.MODEL_CONFIG["bce-embedding-base_v1"],
                                    device=device)

    def load_pos_model(self, device_id=0):
        self.pos_task = Taskflow("pos_tagging", model="lac", mode="fast", task_path=self.POS_MODEL_PATH, device_id=0)

    def get_embedding(self, corpus):
        corpus_embeddings = self.model.encode(corpus)
        return corpus_embeddings

    def cluster_sentences(self, corpus, threshold):
        """
        embedding and clustering
        :param threshold: 欧式距离, 越小相似度越高
        :param corpus: List or Str
        :return: Dict{Cluster_id: List[Sentence_id]}
        """
        corpus_embeddings = self.get_embedding(corpus)

        clustering_model = AgglomerativeClustering(
            n_clusters=None, distance_threshold=threshold
        )
        clustering_model.fit(corpus_embeddings)
        cluster_assignment = clustering_model.labels_

        clustered_sentences = {}
        for sentence_id, cluster_id in enumerate(cluster_assignment):
            if cluster_id not in clustered_sentences:
                clustered_sentences[cluster_id] = []
            clustered_sentences[cluster_id].append(sentence_id)  # corpus index

            # clustered_sentences[cluster_id].append(corpus[sentence_id])
        return clustered_sentences

    def cluster_titles_agg(self, titles):
        """
        lac embedding and cluster
        :param titles:
        :return:
        """
        pos_result = self.get_pos(titles)
        corpus = ["".join(i) for i in pos_result]
        # print(corpus)
        result = self.cluster_sentences(corpus, 1)
        return result

    def cluster_titles_tfidf(self, titles):
        """
        lac tfidf pca
        :param titles:
        :return:
        """
        pos_result = self.get_pos(titles)
        corpus = [" ".join(i) for i in pos_result]
        stop_words = get_stopwords()
        countVectorizer = CountVectorizer(stop_words=stop_words, analyzer="word")
        count_v = countVectorizer.fit_transform(corpus)

        tfidfTransformer = TfidfTransformer()
        tfidf = tfidfTransformer.fit_transform(count_v)
        pca = PCA(n_components=2)
        pca_weights = pca.fit_transform(tfidf.toarray())

        # clf = DBSCAN(eps=0.4, min_samples=2)

        clf = AgglomerativeClustering(n_clusters=None, distance_threshold=1)
        y = clf.fit_predict(pca_weights)
        result = {}
        for text_idx, label_idx in enumerate(y):
            key = "cluster_{}".format(label_idx)
            if key not in result:
                result[key] = [text_idx]
            else:
                result[key].append(text_idx)
        return result
        # for clu_k, clu_v in result.items():
        #     print("\n", "~" * 170)
        #     print(clu_k)
        #     # print(clu_v)
        #     for i in clu_v:
        #         print(text_list[i], corpus[i], "\n===============================>")

    def get_pos(self, titles):
        """

        :param titles:
        :return: List[List[str]]
        [['普京'], ['普京', '访华', '中国', '欢迎']]
        """

        """
        标签	含义	标签	含义	标签	含义	标签	含义
        n	普通名词	f	方位名词	s	处所名词	t	时间
        nr	人名	ns	地名	nt	机构名	nw	作品名
        nz	其他专名	v	普通动词	vd	动副词	vn	名动词
        a	形容词	ad	副形词	an	名形词	d	副词
        m	数量词	q	量词	r	代词	p	介词
        c	连词	u	助词	xc	其他虚词	w	标点符号
        PER	人名	LOC	地名	ORG	机构名	TIME	时间
        """

        pos_result = self.pos_task(titles)
        save_result = []  # List[List[str]]     [['普京'], ['普京', '访华', '中国', '欢迎']]
        if isinstance(pos_result[0], tuple):
            pos_result = [pos_result]
        for sent in pos_result:
            save_result.append(self.format_result(sent))
        return save_result

    def format_result(self, result):
        save_result = []
        usage = ["n", "nr", "nz", "PER", "f", 'ns', 'v', 'LOC', 's',
                 'nt', 'vd', "ORG", 't', 'nw', 'vn', "TIME", 'w']

        for r in result:
            if r[1] in usage:
                save_result.append(r[0])
        return save_result

    @staticmethod
    def cosine_similarity(vectors1, vectors2):
        dot_product = np.dot(vectors1, vectors2.T)
        norm_vectors1 = np.linalg.norm(vectors1, axis=1, keepdims=True)
        norm_vectors2 = np.linalg.norm(vectors2, axis=1, keepdims=True)
        similarity = dot_product / (norm_vectors1 * norm_vectors2.T)
        return similarity

    def similarity(self, source, target, threshold=0.4, use_emd=True):
        """

        :param source:
        :param target: 事件标题
        :param threshold: 采用的是cosine, 相似度阈值越大相似度越高
        :param use_emd:
        :return:
        """
        if isinstance(source, str):
            source = [source]
        if isinstance(target, str):
            target = [target]
        if use_emd:
            source_emd = self.get_embedding(source)
            target_emd = self.get_embedding(target)
        else:
            source_emd = source
            target_emd = target
        similarity = self.cosine_similarity(source_emd, target_emd)
        max_indexs = np.argmax(np.array(similarity), axis=1)
        max_indexs_r = []
        max_score = []
        for i, index in enumerate(max_indexs):
            max_score.append(similarity[i][index])
            if similarity[i][index] > threshold:
                max_indexs_r.append(index)
            else:
                max_indexs_r.append(len(target))
        # print(max_indexs_r, max_score)
        return max_indexs_r, max_score


if __name__ == '__main__':
    cluster = Cluster()
    cluster.load_text_emb()
    # corpus = ["中俄联手推动军事技术合作","中俄联手推动军事合作","中俄推动军事技术合作", "中俄签署大规模经济合作协议", "普京访问强化中俄文化交流"]
    # x = cluster.cluster_sentences(corpus,threshold=0.3)
    # print(x)
    # x = cluster.similarity
    # source = ["日本政府采用高科技处理核废水", "赖清德就职三天后北京“无预警”环台军演 首次覆盖金马等外岛"]
    # for i in range(1000):
    #     source = ["日本政府采用高科技处理核废水"]
    #     target = ["日本政府在核污染问题上的政策变化", "各国如何应对日本核污染问题", "科技如何帮助处理日本核污染问题"]*60
    #     similar_matrix, score = cluster.similarity(source, target, 0)
    #     # print(similar_matrix, score )
    #     if i%50==0:
    #         print(time.time())
    # print(time.time())
    # source = ["日本政府采用高科技处理核废水"]*9000
    # target = ["日本政府在核污染问题上的政策变化", "各国如何应对日本核污染问题", "科技如何帮助处理日本核污染问题"]*100
    # # similar_matrix, score = cluster.similarity(source, target, 0)
    # cluster.cluster_sentences(source,0.4)
    # print(time.time())
