from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (UserViewSet, QuestionViewSet, ChoiceViewSet, QuestionPaperViewSet, AnswerSheetViewSet,QuestionPaperDetailView
,FilterQuestionsAPI, upload_questions,
ActiveQuestionPaperDetailViewSet,ActiveQuestionPaperListView,
ListAllAPIsView,
CheckAnswersAPIView,CustomTokenObtainPairView)
# from .views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static
from djoser import views as djoser_views
# from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'choices', ChoiceViewSet)
router.register(r'question-papers', QuestionPaperViewSet)
router.register(r'answer-sheets', AnswerSheetViewSet)
router.register(r'active-question-papers-data', ActiveQuestionPaperDetailViewSet,basename="active-question-papers-data")

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    # path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    # JWT token URLs for login and refresh token
    path('auth/', include('djoser.urls.jwt')),
    path('question-papers/<int:pk>/', QuestionPaperDetailView.as_view(), name='question-paper-detail'),
    # path('active-question-papers/<slug:slug>/', ActiveQuestionPaperDetailView.as_view(), name='active-question-paper-detail'),
    # path('active-question-papers-list/', ActiveQuestionPaperListView.as_view(), name='active-question-papers'),

    path('upload-questions/', upload_questions, name='upload_questions'),
    path('filter-questions/', FilterQuestionsAPI.as_view(), name='filter_questions_api'),
    path('check-answers/', CheckAnswersAPIView.as_view(), name='check-answers'),
    path('list-all-apis/', ListAllAPIsView.as_view(), name='list_all_apis'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)