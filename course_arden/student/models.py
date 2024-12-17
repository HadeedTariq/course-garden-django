from django.db import models
from authentication.models import User
from teacher.models import Course

# Create your models here.


class PlayList_Type(models.TextChoices):
    Private = "Private", "Private"
    Public = "Public", "Public"


class PlayList(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    user = models.ForeignKey(User, related_name="playlists", on_delete=models.CASCADE)
    type = models.CharField(
        max_length=20, choices=PlayList_Type.choices, default=PlayList_Type.Private
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "title"], name="unique_user_playlist_title"
            )
        ]


class Playlist_Course(models.Model):
    id = models.AutoField(primary_key=True)
    playlist = models.ForeignKey(
        PlayList, related_name="courses", on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course, related_name="playlists", on_delete=models.CASCADE
    )
