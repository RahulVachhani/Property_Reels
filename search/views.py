
import re
import pandas as pd
from django.http import JsonResponse
from .models import PropertyReel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors



def recommend_properties(request):
   

    user_query = request.GET.get('query', '')

    # Fetch all property reels from database
    reels = PropertyReel.objects.all()
    if not reels:
        return JsonResponse({'message': 'No property reels available'}, status=404)

    # Convert to DataFrame
    df = pd.DataFrame(list(reels.values('id', 'video', 'description')))

    # Apply AI-based text similarity
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['description'])
    query_vector = vectorizer.transform([user_query])

    # Compute similarity
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Sort results
    df['score'] = similarity_scores
    df = df.sort_values(by='score', ascending=False)

    results = df.head(2).to_dict(orient='records')
    return JsonResponse({'recommended_reels': results})





def extract_location(query):
    """Extract location from user query using regex."""
    location_keywords = ["Mumbai", "Delhi", "New York", "London", "Paris", "Dubai", "LA", "Berlin", "Bangalore", "Sydney"] 
    for keyword in location_keywords:
        if re.search(rf'\b{keyword}\b', query, re.IGNORECASE):
            return keyword
    return None

def recommend_properties1(request):
    user_query = request.GET.get('query', '').strip()

    if not user_query:
        return JsonResponse({'message': 'Query parameter is required'}, status=400)

    # Extract location from user query
    location = extract_location(user_query)

    # Fetch all property reels from database
    reels = PropertyReel.objects.all()
    if location:
        reels = reels.filter(description__icontains=location)

    if not reels.exists():
        return JsonResponse({'message': 'No properties found for the given location'}, status=404)

    # Convert to DataFrame
    df = pd.DataFrame(list(reels.values('id', 'video', 'description')))

    # Apply TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['description'])

    # Initialize KNN Model (using cosine similarity)
    knn = NearestNeighbors(n_neighbors=1, metric='cosine')
    knn.fit(tfidf_matrix)

    # Transform user query into vector and find nearest neighbors
    query_vector = vectorizer.transform([user_query])
    distances, indices = knn.kneighbors(query_vector)

    # Fetch top k recommendations
    recommended_reels = df.iloc[indices[0]].copy()
    recommended_reels['score'] = 1 - distances[0]  # Convert cosine distance to similarity score

    # Convert results to JSON format
    results = recommended_reels.to_dict(orient='records')

    return JsonResponse({'recommended_reels': results})



import spacy

# Load NLP model for location extraction
nlp = spacy.load("en_core_web_sm")  # Ensure you have this installed (`pip install spacy && python -m spacy download en_core_web_sm`)

def extract_location2(query):
    """Extracts location from a full address using NLP"""
    doc = nlp(query)
    print(doc)
    location_parts = [ent.text for ent in doc.ents if ent.label_ in ["GPE", "LOC"]]  # GPE = Geo-Political Entity, LOC = Location
    print(" ".join(location_parts) if location_parts else None)
    return " ".join(location_parts) if location_parts else None

def recommend_properties2(request):
    user_query = request.GET.get('query', '').strip()

    if not user_query:
        return JsonResponse({'message': 'Query parameter is required'}, status=400)

    # Extract location from user query
    location = extract_location2(user_query)

    
    reels = PropertyReel.objects.all()
    if location:
        reels = reels.filter(description__icontains=location)
    print(len(reels))
    if not reels.exists():
        return JsonResponse({'message': 'No properties found for the given location'}, status=404)

    # Convert to DataFrame
    df = pd.DataFrame(list(reels.values('id', 'video', 'description')))
    print(df)
    # Apply TF-IDF Vectorization
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['description'])

    # Initialize KNN Model (using cosine similarity)
    # knn = NearestNeighbors(n_neighbors=len(reels), metric='cosine')
    # knn.fit(tfidf_matrix)

    # # Transform user query into vector and find nearest neighbors
    # query_vector = vectorizer.transform([user_query])
    # distances, indices = knn.kneighbors(query_vector)

    # # Fetch top k recommendations
    # recommended_reels = df.iloc[indices[0]].copy()
    # recommended_reels['score'] = 1 - distances[0]  # Convert cosine distance to similarity score
    # recommended_reels = recommended_reels[recommended_reels['score'] > 0]
    # # Convert results to JSON format
    # results = recommended_reels.to_dict(orient='records')
    query_vector = vectorizer.transform([user_query])

    # Compute similarity
    similarity_scores = cosine_similarity(query_vector, tfidf_matrix).flatten()

    # Sort results
    df['score'] = similarity_scores
    df = df.sort_values(by='score', ascending=False)

    results = df.head(len(reels)).to_dict(orient='records')

    return JsonResponse({'recommended_reels': results})