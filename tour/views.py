from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from account.permissions import IsAdminOrReadOnly
from .permissions import IsAdminOrAuthorOrReadOnly, IsAdminOrManagerOrAuthorOrReadOnly

from .models import Rating, Tour, Favorite, TourDate
from .serializers import TourSerializer, TourRatingSerializer, \
                         FavoriteSerializer, TourDateSerializer


# работа с турами
class TourListCreateAPIView(ListCreateAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def get_queryset(self):
        return Tour.objects.all()

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)


# детальная информация по выбранному id тура
class TourDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = TourSerializer
    permission_classes = [IsAdminOrAuthorOrReadOnly]

    def get_queryset(self):
        return Tour.objects.all()


# работа с датами выездов в общем списке всех дат выездов
class TourDateListCreateView(ListCreateAPIView):
    serializer_class = TourDateSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return TourDate.objects.all()

    def perform_create(self, serializer):
        return serializer.save()


# детальная работа по каждой из дат выездов
class TourDateDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TourDateSerializer
    permission_classes = [IsAdminOrManagerOrAuthorOrReadOnly]

    def get_queryset(self):
        return TourDate.objects.all()


# работа с датами выездов определенного тура передаваемого в pk
class TourDateForTourListCreateView(ListCreateAPIView):
    serializer_class = TourDateSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        tour_id = self.kwargs.get("tour_id")
        return TourDate.objects.filter(tour__id=tour_id)

    def perform_create(self, serializer):
        return serializer.save()


# детальная работа с каждой датой выезда для выбранного тура
class TourDateForTourDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = TourDateSerializer
    permission_classes = [IsAdminOrManagerOrAuthorOrReadOnly]
    lookup_field = 'tour_id'

    def get_queryset(self):
        tour_id = self.kwargs.get("tour_id")
        date_id = self.kwargs.get("date_id")
        return TourDate.objects.filter(tour=tour_id,
                                       id=date_id)


# работа с каждым экземпляром избранных туров
class FavoriteDetailView(RetrieveUpdateDestroyAPIView):
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)


# список избранных туров
class FavoriteView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FavoriteSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=200)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        tour = serializer.validated_data['tour']
        favorite_tour, created = Favorite.objects.get_or_create(user=user,
                                                                tour=tour)
        response_serializer = self.get_serializer(favorite_tour)
        return Response(response_serializer.data, status=201)


class RatingView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TourRatingSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        rater = request.user
        tour = serializer.validated_data['tour']
        score = serializer.validated_data['score']

        rating, created = Rating.objects.update_or_create(
            rater=rater,
            tour=tour,
            defaults={'score': score}
        )

        total_score = tour.rating * tour.rating_counts
        tour.rating_counts += 1
        tour.rating = round((total_score + score) / tour.rating_counts, 2)
        tour.save()

        return Response(self.get_serializer(rating).data, status=201)

