from wikiraces.embed import vectorize_text, cosine_similarity
import wikipedia


def rerank_by_summary_similarity(destination: str, links: list[str], summary_sentences: int = 2):
    """
    Given a destination title and a list of link titles, fetch summaries for each,
    compute similarity between the destination summary and each link summary, and return the best link and its score.
    Returns (best_link, best_score).
    """
    try:
        dest_summary = wikipedia.summary(destination, sentences=summary_sentences, auto_suggest=False)
    except Exception as e:
        return
        
    dest_vec = vectorize_text(dest_summary)

    best_link = None
    best_score = -1.0
    for link in links:
        # If link is a tuple (title, score), extract the title
        if isinstance(link, (tuple, list)):
            link_title = link[0]
        else:
            link_title = link
        try:
            link_summary = wikipedia.summary(link_title, sentences=summary_sentences, auto_suggest=False)
        except Exception as e:
            continue
        link_vec = vectorize_text(link_summary)
        score = cosine_similarity(dest_vec, link_vec)
        if score > best_score:
            best_link = link_title
            best_score = score
    return best_link, best_score
