from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Reel, Location, Area, User, Interaction
from .serializers import ReelSerializer
from .recommendation_engine import recommend_reels

class ReelRecommendationView(APIView):
    def get(self, request, user_id):
        recommended_ids = recommend_reels(user_id)
        print(recommended_ids)
        reels = Reel.objects.filter(id__in=recommended_ids)
        reels_dict = {reel.id: reel for reel in reels}
        ordered_reels = [reels_dict[reel_id] for reel_id in recommended_ids if reel_id in reels_dict]
        serializer = ReelSerializer(ordered_reels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class LikeReel(APIView):
    def post(self, request):
        print('------------------------------------------------------------------------------')
        data = request.data.get('reel_id')
        reel = Reel.objects.get(id = data)
        user = User.objects.get(id=1)
        data, created = Interaction.objects.get_or_create(user=user, reel=reel)
        like = data.liked
        data.liked = not like
        data.save()
        return Response({'success' : 'done'}, status=status.HTTP_200_OK)
    
class SearchReel(APIView):
    def get(self, request):
        query = request.GET.get('search')
        query = query.split(",")   
        print(query)

        reels = Reel.objects.filter(location__location_name__icontains = query[0].strip())
        if len(query) == 3:
            reels = reels.filter(property_type = query[2].strip())
        if len(query) > 1:
            reels = reels.filter(area__area_name__icontains = query[1].strip())

        print(reels)
        serializer = ReelSerializer(reels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# import random
# from datetime import datetime, timedelta

# property_types = ['villa', 'flat', 'house', 'apartment', 'studio', 'office']
# locations = ['Ahmedabad', 'Surat', 'Rajkot', 'Jamnagar', 'Gandhinagar']
# tags_pool = ['luxury', 'budget', 'city view', 'garden', 'pool', 'near school', 'near hospital', 'downtown', 'spacious', 'modern']


# for i in range(1000):
#     location = Location.objects.get(location_name = random.choice(locations))
#     area = Area.objects.filter(location = location)

#     Reel.objects.create(
#         property_type = random.choice(property_types),
#         location = location,
#         area = random.choice(area),
#         tags = ','.join(random.sample(tags_pool, 3)),
#         likes = random.randint(0, 1000),
#         comments = random.randint(0, 500),
#         shares = random.randint(0, 200)
#     )

