from django.urls import path
from .views import NewList, NewDetail, NewSearch, NewCreate, NewDelete, NewUpdate, upgrade_me


urlpatterns = [
    path('', NewList.as_view()),
    path('<int:pk>', NewDetail.as_view(), name='new_detail'),
    path('search/', NewSearch.as_view()),
    path('add/', NewCreate.as_view(), name='new_create'),
    path('<int:pk>/edit', NewUpdate.as_view(), name='new_update'),
    path('<int:pk>/delete', NewDelete.as_view(), name='new_delete'),
    path('upgrade/', upgrade_me, name='upgrade')
]