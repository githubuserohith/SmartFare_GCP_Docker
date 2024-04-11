from django.urls import path
from . import views


urlpatterns = [
    path('layout/', views.layout, name='layout'),
    path('login_view/', views.login_view, name='login_view'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('signup/', views.signup, name='signup'),
    # path('register/', views.layout, name='register'),
    path('otp/', views.otp, name='otp'),
    path('review/', views.layout, name='review'),
    path('change_pwd/', views.change_pwd, name='change_pwd'),
    path('forgot_pwd/', views.forgot_pwd, name='forgot_pwd'),

    # path('payment/', views.payment, name="payment"),
    path('payment/', views.payment, name='payment'),
    # path('success/<str:args>/', views.successMsg, name='success'),
    # path('failure/<str:args>/', views.failureMsg, name='failure'),
    path('wallet/', views.wallet, name='wallet'),
    path('register/', views.register, name='register'),
    path('admin/', views.admin, name='admin')

]


