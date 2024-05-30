# -*- encoding: utf-8 -*-
# @ModuleName: Cluster
# @Author: ximo
# @Time: 2024/5/10 10:53
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer, TfidfTransformer
from paddlenlp import Taskflow
from utils.Tools import *
import config
import utils


class Cluster():
    def __init__(self, TEXT_EMB_MODEL_PATH=config.MODEL_CONFIG["text_emb"],
                 POS_MODEL_PATH=config.MODEL_CONFIG["lac"]):
        self.pos_task = None
        self.model = None
        self.TEXT_EMB_MODEL_PATH = TEXT_EMB_MODEL_PATH
        self.POS_MODEL_PATH = POS_MODEL_PATH

    def load_text_emb(self):
        self.model = SentenceTransformer(self.TEXT_EMB_MODEL_PATH)

    def load_pos_model(self):
        self.pos_task = Taskflow("pos_tagging", model="lac", mode="fast", task_path=self.POS_MODEL_PATH,device_id=0)

    def get_embedding(self, corpus):
        corpus_embeddings = self.model.encode(corpus)
        return corpus_embeddings

    def cluster_sentences(self, corpus, threshold):
        """
        embedding and clustering
        :param threshold:
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
