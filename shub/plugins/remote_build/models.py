from django.db import models

class BuildContainers(models.Model):
    buildid = models.CharField(max_length=32)

    def __str__(self):
        return self.buildid
