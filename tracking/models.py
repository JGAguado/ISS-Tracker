from django.db import models

class ISSData(models.Model):
    user_latitude = models.FloatField()
    user_longitude = models.FloatField()
    iss_latitude = models.FloatField()
    iss_longitude = models.FloatField()
    azimuth = models.FloatField()
    elevation = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    iss_speed = models.FloatField(null=True)
