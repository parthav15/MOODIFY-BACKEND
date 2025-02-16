import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from emotion.models import CustomUser, Recommendation, Playlist, PlaylistSong

from googleapiclient.discovery import build

from emotion.utils import jwt_decode, auth_user

# =============================== #
# ======== Playlist API's ======= #
# =============================== #
@csrf_exempt
@require_http_methods(["POST"])
def create_playlist_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    name = data.get('name')
    if not name:
        return JsonResponse({'success': False, 'message': 'Playlist name is required.'}, status=400)

    try:
        playlist = Playlist.objects.create(
            user=user,
            name=name
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error creating playlist: {e}"}, status=500)

    return JsonResponse({
        "id": playlist.id,
        "name": playlist.name,
        "created_at": playlist.created_at.isoformat(),
        "updated_at": playlist.updated_at.isoformat()
    }, status=201)

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_playlist_view(request, playlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    try:
        playlist = Playlist.objects.get(id=playlist_id, user=user)
    except Playlist.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Playlist not found.'}, status=404)
    
    playlist.delete()
    return JsonResponse({
        'success': True,
        'message': 'Playlist deleted successfully.',
        'id': playlist_id,
        'name': playlist.name,
        'created_at': playlist.created_at.isoformat(),
        'updated_at': playlist.updated_at.isoformat()
    }, status=200)

@csrf_exempt
@require_http_methods(["GET"])
def get_playlists_view(request):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)
    
    playlists = Playlist.objects.filter(user=user)
    data = []
    for playlist in playlists:
        data.append({
            "id": playlist.id,
            "name": playlist.name,
            "created_at": playlist.created_at.isoformat(),
            "updated_at": playlist.updated_at.isoformat()
        })
    return JsonResponse({
        "success": True,
        "message": "Playlists fetched successfully.",
        "playlists": data
    }, safe=False)

@csrf_exempt
@require_http_methods(["GET"])
def get_playlist_details_view(request, playlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        playlist = Playlist.objects.get(id=playlist_id, user=user)
    except Playlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Playlist not found."}, status=404)

    songs = PlaylistSong.objects.filter(playlist=playlist)
    data = []
    for song in songs:
        data.append({
            "id": song.id,
            "title": song.title,
            "url": song.url,
            "thumbnail_url": song.thumbnail_url,
            "added_at": song.added_at.isoformat()
        })
    return JsonResponse({
        "success": True,
        "message": "Playlist details fetched successfully.",
        "songs": data
    }, safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def add_song_to_playlist_view(request, playlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        playlist = Playlist.objects.get(id=playlist_id, user=user)
    except Playlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Playlist not found."}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    recommendation_id = data.get('recommendation_id')

    if not recommendation_id:
        return JsonResponse({'success': False, 'message': 'Recommendation id is required.'}, status=400)

    try:
        recommendation = Recommendation.objects.get(id=recommendation_id)
    except Recommendation.DoesNotExist:
        return JsonResponse({"success": False, "message": "Recommendation not found."}, status=404)

    try:
        song = PlaylistSong.objects.create(
            playlist=playlist,
            title=recommendation.song_title,
            url=recommendation.song_url,
            thumbnail_url=recommendation.song_thumbnail
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error adding song to playlist: {e}"}, status=500)

    return JsonResponse({
        "id": song.id,
        "title": song.title,
        "url": song.url,
        "thumbnail_url": song.thumbnail_url,
        "added_at": song.added_at.isoformat()
    }, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def delete_song_from_playlist_view(request, playlist_id):
    bearer = request.headers.get('Authorization')
    if not bearer:
        return JsonResponse({'success': False, 'message': 'Authentication header is required.'}, status=401)
    
    token = bearer.split()[1]
    if not auth_user(token):
        return JsonResponse({'success': False, 'message': 'Invalid token data.'}, status=401)
    
    decoded_token = jwt_decode(token)
    user_email = decoded_token.get('email')

    try:
        user = CustomUser.objects.get(email=user_email)
    except CustomUser.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found.'}, status=404)

    try:
        playlist = Playlist.objects.get(id=playlist_id, user=user)
    except Playlist.DoesNotExist:
        return JsonResponse({"success": False, "message": "Playlist not found."}, status=404)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON in request body.'}, status=400)
    
    song_id = data.get('song_id')

    if not song_id:
        return JsonResponse({'success': False, 'message': 'Song id is required.'}, status=400)

    try:
        song = PlaylistSong.objects.get(id=song_id, playlist=playlist)
        song.delete()
    except PlaylistSong.DoesNotExist:
        return JsonResponse({"success": False, "message": "Song not found in playlist."}, status=404)

    return JsonResponse({"success": True, "message": "Song deleted from playlist successfully."}, status=200)