from django.urls import path
from emotion.views import emotion_views, feedback_views, playlist_views, user_views

urlpatterns = [
    # USER URL'S
    path('user_register/', user_views.user_register, name='user_register'),
    path('user_login/', user_views.user_login, name='user_login'),
    path('user_details/', user_views.get_user_details_view, name='user_details'),
    path('edit_user_details/', user_views.edit_user_details_view, name='edit_user_details'),
    path('edit_profile_picture/', user_views.edit_profile_picture_view, name='edit_profile_picture'),

    # EMOTION DETECTION URL'S
    path('emotion_detection/', emotion_views.emotion_detection_view, name='emotion_detection_view'),
    
    # FEEDBACK URL'S
    path('add_feedback/', feedback_views.add_feedback_view, name='add_feedback'),
    path('toggle_publish_feedback/', feedback_views.toggle_publish_feedback_view, name='toggle_publish_feedback'),
    path('get_user_feedbacks/', feedback_views.get_feedbacks_view, name='get_user_feedbacks'),
    path('get_feedbacks/', feedback_views.get_all_feedbacks_view, name='get_all_feedbacks_view'),
    
    # PLAYLIST URL'S
    path('create_playlist/', playlist_views.create_playlist_view, name='create_playlist'),
    path('delete_playlist/<int:playlist_id>/', playlist_views.delete_playlist_view, name='delete_playlist'),
    path('get_playlists/', playlist_views.get_playlists_view, name='get_playlists'),
    path('get_playlist_details/<int:playlist_id>/', playlist_views.get_playlist_details_view, name='get_playlist_details'),
    path('add_song_to_playlist/<int:playlist_id>/', playlist_views.add_song_to_playlist_view, name='add_song_to_playlist'),
    path('delete_song_from_playlist/<int:playlist_id>/', playlist_views.delete_song_from_playlist_view, name='delete_song_from_playlist'),
]
