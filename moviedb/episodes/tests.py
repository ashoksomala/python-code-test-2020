# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.test import TestCase
from .models import Episode, Comments
import json
from django.utils.timezone import now

# Create your tests here.
class CommentTest(TestCase):
    """unit test to test the CRUD of comments apis """
    def setUp(self):
        self.episode = Episode.objects.create(
            uid="tt1480055",
            episode_number=1,
            season_number=2,
            title="testing show",
            rating=9.1,
            release_date="10 Dec 2020",
            director="Darry",
            actors="ashok",
            runtime="4 hours",
            votes="2",
            plot="testing python skill"
        )
        self.episode.save()

        self.comment = Comments.objects.create(
            episode = self.episode,
            comment_text = "good work",
            created_at = now()
        )
        self.comment.save()

    def tearDown(self):
        self.client.delete("/comment-entity/"+str(self.comment.id))
        Episode.objects.filter(uid="tt1480055").delete()

    def test_comment_update(self):
        comment_res = self.client.put("/comment-entity/"+str(self.comment.id), data={"text":"very good work"}, content_type="application/json")
        self.assertEqual(comment_res.status_code, 200)

    def test_updated_comment(self):
        comment_resp = self.client.get("/comment-entity/"+str(self.comment.id))
        self.assertContains(comment_resp, "good work")


