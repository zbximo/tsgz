# -*- encoding: utf-8 -*-
# @ModuleName: Cluster
# @Author: ximo
# @Time: 2024/5/10 10:53
from sentence_transformers import SentenceTransformer
from sklearn.cluster import AgglomerativeClustering
import config


class Cluster():
    def __init__(self, MODEL_PATH=config.MODEL_CONFIG["text_emb"]):
        self.MODEL_PATH = MODEL_PATH

        self.model = SentenceTransformer(MODEL_PATH)

    def get_embedding(self, corpus):
        corpus_embeddings = self.model.encode(corpus)
        return corpus_embeddings

    def cluster_sentences(self, corpus, threshold):
        """

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
