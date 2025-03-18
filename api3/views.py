from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from rest_framework.pagination import PageNumberPagination
from api2.serializers import ReelSerializer
from api2.models import Reel

from .recommend_reels import recommend_reels
from .helper import run_offline_pipeline


class CustomPaginator(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'limit'
    max_page_size = 50

class get_recommendations(APIView):
    def get(self,request, user_id, top_n = 30):
        reels = recommend_reels(user_id, top_n)
        print(reels)
        reelss = Reel.objects.filter(id__in=reels)
        reels_dict = {reel.id: reel for reel in reelss}
        ordered_reels = [reels_dict[reel_id] for reel_id in reels if reel_id in reels_dict]
        paginator = CustomPaginator()
        paginated_reels = paginator.paginate_queryset(ordered_reels, request, view=self)
        serializer = ReelSerializer(paginated_reels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
