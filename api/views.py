from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Location, Reels, Area
from .serializers import ReelSerializers
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# class FindReel(APIView):
#     def get(self, request):
        
#         query = request.GET.get('query').strip()
#         query = query.split(', ')
#         location = query[0]
#         locations = Location.objects.filter(location_name__icontains=location)[0]

#         if len(query) > 1:
#             area = query[1]
#             area = Area.objects.filter(area_name__icontains = area)[0]
#             reels = Reels.objects.filter(location = locations, area=area)
#             serializer = ReelSerializers(reels, many=True)
#         else:
#             reels = Reels.objects.filter(location = locations)
#             serializer = ReelSerializers(reels, many=True)

#         return Response(serializer.data, status=status.HTTP_200_OK)


class FindReel(APIView):
    def get(self, request):
        location = request.GET.get('location')
        area = request.GET.get('area').split(', ')
        p_type = request.GET.get('p_type')

        if not(location):
            return Response({'location': ['location is required']}, status=status.HTTP_400_BAD_REQUEST)      
    
        locations = Location.objects.filter(location_name__icontains=location)
        if not locations.exists():
            return Response({'location': ['location does not exists']}, status=status.HTTP_400_BAD_REQUEST)
        
        reels = Reels.objects.filter(location = locations.first())

        if area:
            areas = Area.objects.none()
            for i in area:
                print(i)                
                filtered_areas = Area.objects.filter(area_name__icontains = i)
                areas = areas | filtered_areas
                print(areas)

            area = areas
            if not area.exists():
                return self.recommend_reels(reels)
                return Response({'area': ['area does not exists']}, status=status.HTTP_400_BAD_REQUEST)
            reels = reels.filter(area__in = list(area))

        if p_type:
            ptp = reels.filter(property_type=p_type)
            if not ptp.exists():
                  return self.recommend_reels(reels)
            reels = ptp

        serializer = ReelSerializers(reels, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    def recommend_reels(self, reels):
        """Recommend similar reels based on description similarity."""
        all_reels = list(Reels.objects.all())
        print('===================================================')
        descriptions = [f'{reel.location}, {reel.area},{reel.property_type}' for reel in all_reels]

        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(descriptions)

        similarity_matrix = cosine_similarity(tfidf_matrix)

        reel_indices = {reel.id: i for i, reel in enumerate(all_reels)}
        print(len(reels))
        recommended_reels = set()
        for reel in reels:
            index = reel_indices.get(reel.id)
            if index is not None:
                similar_indices = similarity_matrix[index].argsort()[-3:][::-1] 
                print(similar_indices)
                for idx in similar_indices:
                    recommended_reels.add(all_reels[idx])

        recommended_reels = list(recommended_reels)
        serializer = ReelSerializers(recommended_reels, many=True)
        return Response({'message': 'No exact matches found. Showing similar recommendations.', 'recommendations': serializer.data}, status=status.HTTP_200_OK)

     