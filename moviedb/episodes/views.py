# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.shortcuts import render
from django.conf import settings
from .models import Episode, Comments
from rest_framework.decorators import api_view
from django.core.paginator import Paginator, EmptyPage
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.timezone import now

import requests
import json


# Create your views here.

def import_data(request):
    """
    Imports episodes data of all the seasons from the Game of Thrones TV series 
    :return: Status of the import 
    """
    base_url = "http://www.omdbapi.com/"
    # get_seasons = requests.get("http://www.omdbapi.com/?t=Game%20of%20Thrones&apikey="+settings.OMDB_API_KEY)
    get_seasons = requests.get(base_url + "?t=Game%20of%20Thrones&apikey=a2d012da")
    season_resp = json.loads(get_seasons.text)

    try:
        seasons = int(season_resp['totalSeasons'])
        series_id = season_resp['imdbID']
    except:
        print("No Data")

    for season in range(1, seasons + 1):
        get_episode = requests.get(base_url + "?i=" + series_id + "&season=" + str(season) + "&apikey=a2d012da")
        episode_res = json.loads(get_episode.text)

        try:
            episode_list = episode_res['Episodes']
        except:
            print("No data")

        for episode in episode_list:
            episode_id = episode['imdbID']
            get_details = requests.get(base_url + "?i=" + episode_id + "&apikey=a2d012da")
            resp = json.loads(get_details.text)

            try:
                episode_obj = Episode(
                    uid=resp['imdbID'],
                    episode_number= int(resp['Episode']),
                    season_number =int(resp['Season']),
                    title=resp['Title'],
                    rating=resp['imdbRating'],
                    release_date=resp['Released'],
                    director=resp['Director'],
                    actors=resp['Actors'],
                    runtime=resp['Runtime'],
                    votes=resp['imdbVotes'],
                    plot=resp['Plot'],
                )
                episode_obj.save()

            except Exception as e :
                print("Error occurred", e)
                return None
    return HttpResponse("Data is successfully imported, you can now use /episodes to get lists of episodes"
                        "/episodes/<id>/ to get specific episode details")


@api_view(["GET"])
def list_episodes(request):
    """
    View that returns list of episodes 
    :param request: 
    :return: 
    """
    page_number = request.GET.get("page")
    page_limit = request.GET.get("limit")
    rating_gt = request.GET.get("rating_gt")
    season = request.GET.get("season")

    filter_d=[]
    if rating_gt:
        rate_filter = {"filter_name":"rating__gt", "filter_value":rating_gt}
        filter_d.append(rate_filter)

    if season:
        season_filter ={"filter_name":"season_number", "filter_value":season}
        filter_d.append(season_filter)

    if page_number is None:
        page_number =1
    if page_limit is None:
        page_limit = 10
    q_obj = Q()

    if len(filter_d)>0:
        for f in filter_d:
            q_obj.add(Q(**{f['filter_name']:f['filter_value']}), Q.AND)
        get_list = Episode.objects.filter(q_obj).values()
    else:
        get_list = Episode.objects.all().values()
    if get_list:
        page_data = Paginator(get_list, int(page_limit))

        try:
            episode_list = page_data.page(int(page_number))

        except EmptyPage:
            episode_list = page_data.page(page_data.num_pages)

        return JsonResponse({"data":list(episode_list),"page":int(page_number), "limit":int(page_limit)}, status=200)
    else:
        return JsonResponse({"message":"There is no data , Please open /import-data url to fill the data"})



@api_view(["GET"])
def get_episode(request,id):
    """
    View that returns details of a particular episode.
    :param request: 
    :param id: episode id 
    :return: episode details
    """

    try:
        episode_obj = Episode.objects.filter(uid=id).values()
    except:
        return JsonResponse({"message":"Episode does not exist"}, status=404)

    return JsonResponse(list(episode_obj), status=200,safe=False)



@api_view(["POST","GET"])
def comment_handler(request,episode_id):
    """
    get or create  comment related to an episode.
    :param request: 
    :param episode: 
    :return: 
    """
    if request.method == 'POST':
        payload = request.data
        try:
            text = payload['text']
            try:
                episode_obj = Episode.objects.get(uid=episode_id)
            except:
                return JsonResponse({"message":"episode doesnt exist"}, status=404)

            created_at = now()
            comment = Comments(episode=episode_obj, comment_text=text, created_at=created_at)
            comment.save()
        except Exception as err:
            return JsonResponse({"message":str(err)}, status=400)

        return JsonResponse({"message":"posted successfully", "id":comment.id}, status=201)

    if request.method == 'GET':
        try:
            episode_obj = Episode.objects.get(uid=episode_id)
        except:
            return JsonResponse({"message": "episode doesnt exist"}, status=404)

        comments = Comments.objects.filter(episode=episode_obj).values()

        return JsonResponse({"data":list(comments)})


@api_view(['DELETE','PUT', 'GET'])
def commend_object_handler(request,comment_id):
    """
    API that can be used to delete ,  update  a particular comment
    :param request: 
    :param comment_id: 
    :return: 
    """
    if request.method == 'DELETE':
        try:
            comment_obj = Comments.objects.get(id = comment_id)
        except:
            return HttpResponse(status=404)
        comment_obj.delete()

        return HttpResponse(status=200)

    if request.method == 'PUT':
        payload = request.data
        text = payload['text']

        try:
            comment_obj = Comments.objects.get(id = comment_id)

        except:
            return HttpResponse(status=404)

        comment_obj.comment_text = text
        comment_obj.save()

        return HttpResponse(status=200)

    if request.method == 'GET':

        try:
            comment_obj = Comments.objects.get(id = comment_id)
            print(comment_obj.comment_text)

        except:
            return HttpResponse(status=404)

        return JsonResponse({"text":comment_obj.comment_text, "id":comment_obj.id})


