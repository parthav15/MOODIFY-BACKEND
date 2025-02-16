from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from deepface import DeepFace

from emotion.models import CustomUser, UploadedImage, Recommendation

from googleapiclient.discovery import build

from emotion.utils import jwt_decode, auth_user

# =============================== #
# ======== Emotion API's ========== #
# =============================== #

def detect_emotion(image_path):
    obj = DeepFace.analyze(img_path=image_path, actions=['emotion'])
    if obj:
        face_details = obj[0]['region']
        emotion = obj[0]['dominant_emotion']
        return emotion, face_details
    return None, None

YOUTUBE_API_KEY = "AIzaSyD5x2NiD18HrW361g4WN8YsRCsJ_-TU3CM"

def get_youtube_recommendations(emotion, language):
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    query = f"{emotion} music playlist {language}"
    request = youtube.search().list(
        q=query,
        part='snippet',
        type='video',
        maxResults=10
    )
    response = request.execute()
    results = []
    for item in response['items']:
        results.append({
            'title': item['snippet']['title'],
            'video_url': f"https://www.youtube.com/watch?v={item['id']['videoId']}",
            'thumbnail': item['snippet']['thumbnails']['high']['url']
        })
    return results

@csrf_exempt
@require_http_methods(["POST"])
def emotion_detection_view(request):
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
    
    uploaded_file = request.FILES.get('image')
    language = request.POST.get('language')
    if not language:
        return JsonResponse({"success": False, "message": "No language selected"}, status=400)
    if not uploaded_file:
        return JsonResponse({"success": False, "message": "No image uploaded"}, status=400)

    try:
        image = UploadedImage.objects.create(
            user=user,
            image=uploaded_file
        )
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error uploading image: {e}"}, status=400)

    try:
        emotion, face_details = detect_emotion(image.image.path)
        emotion = emotion.capitalize()
        face_coordinates = {
            "x": face_details['x'],
            "y": face_details['y'],
            "width": face_details['w'],
            "height": face_details['h']
        }
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Emotion detection failed: {e}"}, status=400)

    try:
        recommendations = get_youtube_recommendations(emotion, language)
    except Exception as e:
        return JsonResponse({"success": False, "message": f"Error getting youtube recommendations: {e}"}, status=500)
    saved_recommendations = []
    for recommendation in recommendations:
        try:
            saved_recommendation = Recommendation.objects.create(
                user=user,
                uploaded_image=image,
                song_title=recommendation['title'],
                song_url=recommendation['video_url'],
                song_thumbnail=recommendation['thumbnail']
            )
            saved_recommendations.append({
                "id": saved_recommendation.id,
                "song_title": saved_recommendation.song_title,
                "song_url": saved_recommendation.song_url,
                "song_thumbnail": saved_recommendation.song_thumbnail,
            })
        except Exception as e:
            return JsonResponse({"success": False, "message": f"Error creating recommendation: {e}"}, status=500)

    return JsonResponse({
        "success": True,
        "face_coordinates": face_coordinates,
        "emotion": emotion,
        "recommendations": saved_recommendations
    }, status=200)

