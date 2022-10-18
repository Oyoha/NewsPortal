from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from .models import *
from .filters import PostSearch
from .forms import PostForm
from django.shortcuts import redirect
from django.core.mail import send_mail


class NewList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-public_time')
    paginate_by = 1

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context


class NewDetail(DetailView):
    model = Post
    template_name = 'new.html'
    context_object_name = 'new'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        pk = self.kwargs.get('pk')
        context['is_not_subscriber'] = not Category.objects.filter(subscriber__Category=pk,
                                                                   subscriber__user=self.request.user.id).exists()

        return context


class NewSearch(ListView):
    model = Post
    template_name = 'search_news.html'
    context_object_name = 'news'
    queryset = Post.objects.order_by('-public_time')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filter'] = PostSearch(self.request.GET, queryset=self.get_queryset())
        return context


class NewCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'new_create.html'
    form_class = PostForm
    permission_required = ('portal.add_post')


class NewUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    template_name = 'new_create.html'
    form_class = PostForm
    permission_required = ('portal.change_post')

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)


class NewDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'new_delete.html'
    context_object_name = 'new'
    success_url = '/news/'
    permission_required = ('portal.delete_post')


@login_required
def upgrade_me(request):
    user = request.user
    premium_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors'):
        premium_group.user_set.add(user)
    return redirect('/news/')


@login_required
def check_subscribe(request, category_id):
    user = User.objects.get(pk=request.user.id)
    category = Category.objects.get(pk=category_id)
    if user not in category:
        category.subscriber.add(user)
    return redirect('/news/')
