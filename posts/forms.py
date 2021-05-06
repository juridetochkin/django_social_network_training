from django.forms import ModelForm
from posts.models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': 'Введите текст',
            'group': 'Выберите сообщество',
            'image': 'Загрузите изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']