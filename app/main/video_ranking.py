# app\main\video_ranking.py

from sklearn.feature_extraction.text import TfidfVectorizer # type: ignore
from sklearn.metrics.pairwise import cosine_similarity # type: ignore

def rank_videos_by_relevance(subtopic, videos):
    # Ensure videos is a list of dictionaries with 'description' key
    if not videos or not all('description' in video for video in videos):
        print("Invalid video list. Each video must contain a 'description' key.")
        return []

    video_descriptions = [video['description'] for video in videos]
    
    # Vectorize the subtopic and video descriptions
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([subtopic] + video_descriptions)
    
    # Calculate cosine similarity
    similarities = cosine_similarity(vectors[0:1], vectors[1:]).flatten()
    
    # Zip similarities with videos and sort by similarity score
    ranked_videos = [video for _, video in sorted(zip(similarities, videos), key=lambda x: x[0], reverse=True)]
    
    return ranked_videos
