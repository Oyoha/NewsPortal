from datetime import datetime
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, CreateView
from .models import *
from .filters import PostSearch
from .forms import PostForm
from django.shortcuts import redirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


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
        context['user_auth'] = self.request.user.is_authenticated
        id = self.kwargs.get('pk')
        post = Post.objects.get(pk=id)
        is_subscriber = True
        for category in post.category.all():
            if self.request.user not in category.user.all():
                is_subscriber = False
        context['is_subscriber'] = is_subscriber
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

    def post(self, request, *args, **kwargs):
        new = Post(
            article=request.POST['article'],
            text=request.POST['text'],
            # category=request.POST['category']
        )

        html_content = render_to_string(
            'new_send_to_email.html',
            {'new': new}
        )

        msg = EmailMultiAlternatives(
            subject=f'{new.article}',
            body=f'Здравствуй. Новая статья в твоем любимом разделе!',
            from_email='vasal3000@mail.ru',
            to=['vasal30000@mail.ru']
        )
        msg.attach_alternative(html_content, 'text/html')
        msg.send()

        return redirect('/news/')


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
def check_subscribe(request, pk):
    user = User.objects.get(pk=request.user.id)
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    for category in categories:
        if user not in category.user.all():
            category.user.add(user)
    return redirect('/news/')


@login_required
def check_unsubscribe(request, pk):
    user = User.objects.get(pk=request.user.id)
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    for category in categories:
        if user in category.user.all():
            category.user.remove(user)
    return redirect('/news/')
