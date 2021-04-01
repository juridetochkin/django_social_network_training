from django.forms import ModelForm
from posts.models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group"]
        labels = {
            "text": "Введите текст",
            "group": "Выберите сообщество"
        }
        help_texts = {
            "group": "Необязательно"
        }
