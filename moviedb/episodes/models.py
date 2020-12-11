# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Episode(models.Model):
    uid = models.CharField(max_length=511, primary_key=True)
    season_number = models.IntegerField(blank=False)
    episode_number = models.IntegerField(blank=False)
    title = models.CharField(max_length=511,blank=True)
    rating = models.FloatField(default=0.0)
    release_date = models.CharField(max_length=511)
    director = models.CharField(max_length=511)
    actors = models.CharField(max_length=511)
    runtime = models.CharField(max_length=511)
    plot = models.TextField(blank=True)
    votes = models.CharField(max_length=511)


class Comments(models.Model):
    episode = models.ForeignKey(Episode, related_name='episodes' , on_delete=models.CASCADE)
    comment_text = models.TextField(blank=True)
    created_at = models.DateTimeField(editable=False)






