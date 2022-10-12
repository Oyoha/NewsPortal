from django.forms import DateInput
from django_filters import FilterSet, DateFilter, CharFilter, ChoiceFilter
from .models import Post


class PostSearch(FilterSet):
    SelectDateWidget = DateInput(format='%d.%m.%Y"', attrs={'type': 'date'})
    time_filter = DateFilter(field_name='public_time', lookup_expr='gt', label='Опубликованно после',
                             widget=SelectDateWidget)
    article = CharFilter(field_name='article', lookup_expr='icontains', label='Заголовок')
    #author = ChoiceFilter(field_name='author', label='Автор')

    class Meta:
        model = Post
        fields = ['time_filter', 'author', 'article']
