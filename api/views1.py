import numpy as np
import faiss
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from sentence_transformers import SentenceTransformer
import logging

from .models import Location, Area, Reels
from .serializers import ReelSerializers


class FindReel(APIView):
    """
    A production-grade API view that retrieves reels by location, area, and property type.
    If an exact match is not found, it falls back to recommending similar reels using a FAISS-based
    approximate nearest neighbor search on deep textual embeddings.
    """
    # Load and cache the SentenceTransformer model (e.g., at startup)
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

    def get(self, request):
        location = request.GET.get('location')
        area = request.GET.get('area')
        p_type = request.GET.get('p_type')

        if not location:
            return Response({'location': ['location is required']}, status=status.HTTP_400_BAD_REQUEST)

        locations = Location.objects.filter(location_name__icontains=location)
        if not locations.exists():
            return Response({'location': ['location does not exist']}, status=status.HTTP_400_BAD_REQUEST)
        
        reels = Reels.objects.filter(location=locations.first())

        if area:
            area_objs = Area.objects.filter(area_name__icontains=area)
            if not area_objs.exists():
                # Fall back to recommendations when area not found
                return self.recommend_reels(reels)
            reels = reels.filter(area=area_objs.first())

        if p_type:
            ptp = reels.filter(property_type=p_type)
            if not ptp.exists():
                # Fall back to recommendations if property type filtering yields nothing
                return self.recommend_reels(reels)
            reels = ptp

        if reels.exists():
            serializer = ReelSerializers(reels, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # No exact match – recommend similar reels
            return self.recommend_reels(reels)
    
    def recommend_reels(self, base_reels):
        """
        Recommend similar reels based on deep text embeddings and FAISS ANN search.
        Uses caching to store the FAISS index, embeddings, and mapping from FAISS indices to reel IDs.
        """
        try:
            # Try loading FAISS index and related data from cache
            index = cache.get('faiss_index')
            index_reel_ids = cache.get('index_reel_ids')
            embeddings = cache.get('reel_embeddings')
            
            if index is None or index_reel_ids is None or embeddings is None:
                # Build index if not found in cache
                all_reels = list(Reels.objects.all())
                if not all_reels:
                    return Response({'error': 'No reels available for recommendation.'}, status=status.HTTP_404_NOT_FOUND)
                
                # Create detailed description for each reel
                descriptions = [
                    f"{reel.location.location_name} {reel.area.area_name} {reel.property_type} {reel.description}"
                    for reel in all_reels
                ]
                
                # Compute embeddings in batch; convert to float32 numpy array
                embeddings = self.embedding_model.encode(descriptions, convert_to_tensor=False)
                embeddings = np.array(embeddings).astype('float32')
                
                # Normalize embeddings to use inner product as cosine similarity
                faiss.normalize_L2(embeddings)
                dimension = embeddings.shape[1]
                # Using a simple flat index; for larger datasets, consider using an IVF index or HNSW
                index = faiss.IndexFlatIP(dimension)
                index.add(embeddings)
                
                # Map FAISS index positions to reel IDs
                index_reel_ids = [reel.id for reel in all_reels]
                
                # Cache these objects (cache timeout set to one hour, adjust as needed)
                cache.set('faiss_index', index, timeout=3600)
                cache.set('index_reel_ids', index_reel_ids, timeout=3600)
                cache.set('reel_embeddings', embeddings, timeout=3600)
            
            # For each reel in the base set (if any), find similar reels using FAISS
            recommended_set = set()
            if base_reels.exists():
                for reel in base_reels:
                    # Create a description for the current reel
                    desc = f"{reel.location.location_name} {reel.area.area_name} {reel.property_type} {reel.description}"
                    query_embedding = self.embedding_model.encode([desc], convert_to_tensor=False)
                    query_embedding = np.array(query_embedding).astype('float32')
                    faiss.normalize_L2(query_embedding)
                    
                    k = 5  # Number of neighbors to retrieve
                    distances, indices = index.search(query_embedding, k)
                    for idx in indices[0]:
                        recommended_set.add(idx)
            else:
                # If no base reels provided, fallback: return top trending (highest inner product) reels
                k = 5
                distances, indices = index.search(np.expand_dims(embeddings.mean(axis=0), axis=0), k)
                for idx in indices[0]:
                    recommended_set.add(idx)
            
            # Convert FAISS indices back to reel IDs
            recommended_ids = [index_reel_ids[idx] for idx in recommended_set if idx < len(index_reel_ids)]
            recommended_reels = Reels.objects.filter(id__in=recommended_ids)
            serializer = ReelSerializers(recommended_reels, many=True)
            return Response({
                'message': 'No exact matches found. Showing similar recommendations.',
                'recommendations': serializer.data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': 'Internal server error in recommendation module.'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
