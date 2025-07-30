import numpy as np
from sentence_transformers import SentenceTransformer

# Load the sentence transformer model locally
model = SentenceTransformer('all-MiniLM-L6-v2')

def cosine_similarity(vec1, vec2):
    """
    Compute the cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


def most_similar(query, candidates):
    """
    Given a query string and a list of candidate strings, returns the candidate most similar to the query (using embeddings and cosine similarity).
    Returns a tuple: (best_candidate, similarity_score)
    """
    query_vec = vectorize_text(query)
    candidate_vecs = vectorize_batch(candidates)
    scores = [cosine_similarity(query_vec, cand_vec) for cand_vec in candidate_vecs]
    best_idx = int(np.argmax(scores))
    return candidates[best_idx], scores[best_idx]

def most_similar_with_scores(query, candidates):
    """
    Like most_similar, but returns all candidates and their similarity scores, sorted descending.
    Returns a list of tuples: (candidate, score)
    """
    query_vec = vectorize_text(query)
    candidate_vecs = vectorize_batch(candidates)
    scores = [cosine_similarity(query_vec, cand_vec) for cand_vec in candidate_vecs]
    return sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)

def vectorize_text(text):
    """
    Vectorize a single string using the local sentence transformer model.
    Returns the embedding vector as a numpy array.
    """
    return model.encode(text, convert_to_numpy=True)

def vectorize_batch(list_of_strings):
    """
    Vectorize a list of strings in a batch using the local sentence transformer model.
    Returns a list of embedding vectors (numpy arrays).
    """
    return model.encode(list_of_strings, convert_to_numpy=True)