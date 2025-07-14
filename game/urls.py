from django.urls import path
from . import views

urlpatterns = [
    path('', views.GameSessionCreateView.as_view(), name='game_start'),
    path('ante/<int:ante_num>/', views.AnteStartView.as_view(), name='ante_start'),
    path('guess/<int:ante_num>/', views.GuessView.as_view(), name='guess_start'),
    path('ante/<int:ante_num>/summary/', views.ScoreSummaryView.as_view(), name='score_summary'),
    path('shop/<int:ante_num>/', views.ShopView.as_view(), name='shop'),
    path('buy_card/', views.buy_card_view, name='buy_card'),
    path('buy_pack/', views.buy_pack_view, name='buy_pack'),
    path('reset_game/', views.reset_game, name='reset_game'),
    path('use_card/item/', views.use_item_card_view, name='use_item_card'),
    path('use_card/tarot/', views.use_tarot_card_view, name='use_tarot_card'),
    path('use_card/spectral/', views.use_spectral_card_view, name='use_spectral_card'),
    path("select_number/", views.SelectNumberView.as_view(), name="select_number"),
]