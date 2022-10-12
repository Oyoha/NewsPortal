from allauth.account.forms import SignupForm
from django.contrib.auth.models import User, Group
from django.db import models


class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.FloatField(default=0.0)

    def update_rating(self):
        posts_rating = Post.objects.filter(author=self.pk).values('rating')
        posts_rating = sum([i['rating'] for i in posts_rating]) * 3
        comments_rating = Comment.objects.filter(user=self.user).values('rating')
        comments_rating = sum([i['rating'] for i in comments_rating])
        posts_comment_rating = Post.objects.filter(author=self.pk).values('comment__rating')
        posts_comment_rating = sum([i['comment__rating'] for i in posts_comment_rating])
        self.rating = comments_rating + posts_rating + posts_comment_rating
        self.save()

    def __str__(self):
        return f'{self.user}'


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f'{self.name}'


class Post(models.Model):
    news = 'NW'
    article = 'AT'
    KIND = [(news, 'Новости'), (article, 'Статья')]
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    kind = models.CharField(max_length=2, choices=KIND, default=news)
    public_time = models.DateTimeField(auto_now_add=True)
    category = models.ManyToManyField(Category, through='PostCategory')
    article = models.CharField(max_length=255)
    text = models.TextField()
    rating = models.FloatField(default=0.0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return self.text[:124] + '...'

    def __str__(self):
        return f'{self.article}: {self.text}'

    def get_absolute_url(self):
        return f'/news/{self.id}'


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    Category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    public_time = models.DateTimeField(auto_now_add=True)
    rating = models.FloatField(default=0.0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


class Subscriber(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class BasicSignupForm(SignupForm):

    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        basic_group = Group.objects.get(name='common')
        basic_group.user_set.add(user)
        return user


