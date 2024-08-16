# -*- encoding: utf-8 -*-
# @ModuleName: Cluster
# @Author: ximo
# @Time: 2024/5/10 10:53

import numpy as np
from BCEmbedding import EmbeddingModel
from sklearn.cluster import AgglomerativeClustering

import config


class Cluster():
    def __init__(self, TEXT_EMB_MODEL_PATH=config.MODEL_CONFIG["bce-embedding-base_v1"]):
        self.pos_task = None
        self.model = None
        self.TEXT_EMB_MODEL_PATH = TEXT_EMB_MODEL_PATH

    def load_text_emb(self, device='cuda:1'):
        self.model = EmbeddingModel(model_name_or_path=config.MODEL_CONFIG["bce-embedding-base_v1"],
                                    device=device)

    def get_embedding(self, corpus):
        corpus_embeddings = self.model.encode(corpus, enable_tqdm=False, batch_size=200)
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

    @staticmethod
    def cosine_similarity(vectors1, vectors2):
        if isinstance(vectors1, list):
            vectors1 = np.array(vectors1)
        if isinstance(vectors2, list):
            vectors2 = np.array(vectors2)
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
