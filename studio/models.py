from django.db import models

class Video_Final(models.Model):
    title = models.CharField(max_length=255)
    data = models.BinaryField()  # Store raw video data directly in DB
    duration = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
class Video(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='videos/')
    duration = models.FloatField()
    uploaded_at = models.DateTimeField(auto_now_add=True)


class Frame(models.Model):
    video = models.ForeignKey(Video_Final, on_delete=models.CASCADE, related_name='frames')
    frame_number = models.IntegerField()
    frame_data = models.BinaryField()

    def __str__(self):
        return f"{self.video.title} - Frame {self.frame_number}"
