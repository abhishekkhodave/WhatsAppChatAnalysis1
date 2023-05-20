from django.db import models


class DatasetModel(models.Model):
    index = models.BigIntegerField(primary_key=True)
    reviewdate = models.TextField()
    reviewtitle = models.TextField()
    author = models.TextField()
    rating = models.BigIntegerField()
    reviewtext = models.TextField()
    helpful = models.BigIntegerField()

    class Meta:
        db_table = 'tblDataset'
