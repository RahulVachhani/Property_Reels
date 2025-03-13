from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .models import Location, Reels

class FindReel(APIView):
    def get(self, request):

        query = request.GET.get('query').strip()
        locations = Location.objects.filter(query)
        return Response(query, status=status.HTTP_200_OK)