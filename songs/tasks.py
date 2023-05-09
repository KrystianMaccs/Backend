from datetime import date, datetime, timedelta
import os
import json
import time
from typing import List, Dict
from django_q.tasks import async_task
from django.utils import timezone

from royalty.tasks import (
    confirm_royalty_mail, get_or_create_royalty, get_verififcation_details)
from systemcontrol.models import Outlet
from utils.api.djm.client import getFingerPlayed, getTestFingerPlayed
from utils.api.eveara.outlets import get_song_link
from utils.helper import get_next_month_ending, string2date

from .models import RadioPlay, RoyaltySplit, Genre, Song, SongDistributionLog, SongLink, SongMeta


def check_split_type(split): return split['share'] if type(
    split) is dict else split.share


def check_split_limit(splits):
    s = [check_split_type(split) for split in splits]

    total = sum(s)

    return total <= 100, total


def get_or_create_splitings(request, splits, song):
    objs = []
    for split in splits:
        objs.append(get_or_create_split(request, split, song))

    return objs


def get_or_create_split(request, split, song, exist=False):
    royalty, created = get_or_create_royalty(split)

    try:
        obj_split = RoyaltySplit.objects.get(
            song=song,
            royalty=royalty,
        )
    except RoyaltySplit.DoesNotExist:
        obj_split = RoyaltySplit.objects.create(
            song=song,
            royalty=royalty,
            share=split['share'],
            phone=split['phone'],
            email=split['email'],
            fullname=split['fullname'],
            description=split['description']
        )

    if not exist:
        obj_split.email = split['email']
        obj_split.phone = split['phone']
        obj_split.fullname = split['fullname']
        obj_split.share = split['share']
        obj_split.description = split['description']
        obj_split.save()

    split['id'] = str(obj_split.id)
    async_task('royalty.tasks.confirm_royalty_mail', get_verififcation_details(
        request, split, song))

    return obj_split


def brodcast_song(song):
    # Get How to Send File using request
    print('Brodcasting File')
    time.sleep(5)
    # How to Download a file
    print('File Downloaded')


def load_genre():
    try:
        data = None
        cwd = os.getcwd()
        path = cwd + '/songs/genres.json'
        print(path)
        with open(path, 'r') as f:
            data = json.load(f)

        genres = [Genre(title=g['genre_label'], code=g['genre_code'])
                  for g in data]

        Genre.objects.bulk_create(genres)
    except FileNotFoundError:
        print("Failed")


def populate_songlinks(results, song: Song):
    '''
        Process Eveara Smart Link API. 
        Create new SongLink from API and avoid Duplicates.
    '''
    store_datalink: Dict[str, str] = dict(
        map(lambda storeData: (storeData['storeName'], storeData['url']), results))
    result_stores: List[str] = list(store_datalink)

    songLinks_query = SongLink.objects.values(
        'storeName').filter(song_id=song.id)
    song_store: List[str] = [s['storeName'] for s in songLinks_query]

    unsaved_storeName: List[str] = list(
        filter(lambda store: store not in song_store, result_stores))

    def create_songlink(storeName, url): return SongLink(
        storeName=storeName, link=url, song=song)

    new_songlinks: List[SongLink] = [create_songlink(
        storeName, store_datalink[storeName]) for storeName in unsaved_storeName]

    SongLink.objects.bulk_create(new_songlinks)

    return new_songlinks


def update_songlink(song: Song):
    '''
        Check whether SongLink and Outlet count are the same
        else call eveara smart link to update SongLink

        return List[SongLink]
    '''
    outlets_count = Outlet.objects.count()
    songlink_query = SongLink.objects.filter(song_id=song.id)

    links: List[SongLink] = list(songlink_query)

    if outlets_count > songlink_query.count():
        song_meta: SongMeta = song.songmeta
        eveara_album_id = song_meta.eveara_album

        api_linkresult = get_song_link(eveara_album_id)
        results = api_linkresult.get('data', [])

        if len(results) > 0:
            links = populate_songlinks(results, song)

    return links


def check_radioplay(song_id: str, date: date):
    radio_play_query = RadioPlay.objects.filter(
        song_id=song_id, query_date__year=date.year, query_date__month=date.month)
    return radio_play_query.exists()


def query_radioplay(song: Song, start_date: date, months: int):
    all_dates = []
    today = timezone.now()
    current_date: date = start_date

    if months <= 12:
        for _ in range(months - 1):

            if today.year >= current_date.year:
                if (current_date.month < today.month and today.year == current_date.year) or (today.year > current_date.year):

                    rp_exists: bool = check_radioplay(song.id, current_date)
                    if not rp_exists:

                        all_dates.append(current_date)
                        async_task('songs.tasks.populate_radioplay',
                                   year=current_date.year, month=current_date.month, song=song)
                        # populate_radioplay(current_date.year, current_date.month, song)

                current_date = get_next_month_ending(current_date)
            else:
                break

        rp_query = RadioPlay.objects.filter(
            song=song, query_date__year=start_date.year, query_date__month=start_date.month)
        rp_query = rp_query.filter(
            query_date__year=start_date.year, query_date__month=start_date.month)
        rp_query = rp_query.filter(
            query_date__year__lte=current_date.year, query_date__month__lte=current_date.month)

        return rp_query


def populate_radioplay(year: int, month: int, song: Song):
    '''
        Call DJM API to populate RadioPlay
    '''

    songMeta: SongMeta = song.songmeta

    # played: List[dict] = getTestFingerPlayed(
    #     songMeta.djm_fingerprint_id, year, month)

    if songMeta.djm_fingerprint_id is not None:
        played: List[dict] = getFingerPlayed(
            songMeta.djm_fingerprint_id, year, month)

        if played is not None:

            played_data: Dict[str, List[dict]] = {}
            for p in played:
                p_radioId: str = p['radio_stream']['radio_stream_id']

                p_init_data = played_data.get(p_radioId, None)
                if p_init_data is None:
                    played_data[p_radioId] = [p]
                else:
                    p_init_data.append(p)

            play_radioIds = list(played_data)
            radioId_values: list = []

            radioplay_query = RadioPlay.objects.filter(
                song=song, radio_id__in=play_radioIds)
            radioplay_query = radioplay_query.filter(
                query_date__year=year, query_date__month=month)
            if radioplay_query.exists():
                radio_results = radioplay_query.values('radio_id')
                radioId_values = [r['radio_id'] for r in radio_results]

            filtered_new_radioIds = filter(
                lambda rId: rId not in radioId_values, play_radioIds)

            sum_duration = dict(map(lambda rId: (
                rId, {**form_playdata(played_data[rId]), 'duration': calculate_total_duration(played_data[rId])}), filtered_new_radioIds))

            new_radioplays = list(new_radioplay(
                song=song, radio_id=rId, play=sum_duration[rId]) for rId in sum_duration)

            print(new_radioplays)

            RadioPlay.objects.bulk_create(new_radioplays)
        
    else:
        print(f"Song not get finger print {songMeta.song_id}")


def form_playdata(plays: List[dict]):
    if len(plays) > 0:
        play = plays[0]
        start_time = string2date(play['start_time'])
        return {
            'radio_name': play['radio_stream']['name'],
            'radio_id': play['radio_stream']['radio_stream_id'],
            'date': date(year=start_time.year, month=start_time.month, day=start_time.day)
        }


def calculate_duration(start: str, end: str):
    dt_start = string2date(start)
    dt_end = string2date(end)

    return dt_end - dt_start


def calculate_total_duration(plays: List[dict]):
    calc = sum(map(lambda play: calculate_duration(
        start=play['start_time'], end=play['end_time']).seconds, plays))
    return timedelta(seconds=calc)


def new_radioplay(song: Song, radio_id: str, play: dict):
    date = play['date']
    radio_name = play['radio_name']
    duration = play['duration']
    return RadioPlay(
        song=song,
        query_date=date,
        duration=duration,
        radio_id=radio_id,
        radio_name=radio_name,
    )


def create_distro_log(song:Song, step: str, message: str):
    SongDistributionLog.objects.create(song=song, step=step, message=message)

