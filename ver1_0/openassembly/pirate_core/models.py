from django.db import models


class RankingDimension(models.Model):
    #Dimensions store
    name = models.CharField(max_length=70)
    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)


class BaseRankingAbstractModel(models.Model):
    # Generic ranking object that can be used by other
    #Models to instantiate the ranking objects

    score = models.IntegerField()
    dimension = models.ForeignKey(RankingDimension)

    created_dt = models.DateTimeField(auto_now_add=True)
    modified_dt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("score", "dimension")
        abstract = True

