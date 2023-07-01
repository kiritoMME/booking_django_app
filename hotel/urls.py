from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('search', views.search, name='search'),
    path('show_hotel_in_duration/<str:hotel_id>/<str:check_in>/<str:check_out>/<str:rooms>', views.show_hotel_in_duration, name='show_hotel_in_duration'),
    path('signup_page', views.signup_page, name='signup_page'),
    path('logout', views.logout, name='logout'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    # path('control_panel', views.control_panel, name='control_panel'),
    path('add_page/<str:category>/<str:id>', views.add_page, name='add_page'),
    path('add_region/<str:id>', views.add_region, name='add_region'),
    path('add_hotel/<str:id>', views.add_hotel, name='add_hotel'),
    path('add_room/<str:id>', views.add_room, name='add_room'),
    path('edit_page/<str:category>/<str:item_id>', views.edit_page, name='edit_page'),
    path('edit_region/<str:id>', views.edit_region, name='edit_region'),
    path('edit_hotel/<str:id>', views.edit_hotel, name='edit_hotel'),
    path('edit_room/<str:id>', views.edit_room, name='edit_room'),
    path('delete_region/<str:id>', views.delete_region, name='delete_region'),
    path('delete_hotel/<str:id>', views.delete_hotel, name='delete_hotel'),
    path('delete_room/<str:id>', views.delete_room, name='delete_room'),
    path('add_booking/<str:id>/<str:check_in>/<str:check_out>', views.add_booking, name='add_booking'),
    path('confirmed', views.confirmed, name='confirmed'),
    # path('add_booking_from_explore_page/<str:room>/<str:check_in>/<str:check_out>', views.add_booking_from_explore_page, name='add_booking_from_explore_page'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('show/', views.show_regions , name='show_regions'),
    path('show/<int:region>/', views.show_hotels , name='show_hotels'),
    path('show/<str:region>/<str:hotel>/', views.show_rooms , name='show_rooms'),
    path('show/<str:region>/<str:hotel>/<str:room>/', views.show_room , name='show_room'),
]
