import hdbscan

def cluster_embeddings(embeddings):
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    return clusterer.fit_predict(embeddings)
