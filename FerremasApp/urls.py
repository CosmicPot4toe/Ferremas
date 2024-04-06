from django.urls import path
from . import views as v

urlpatterns = [
    path('',v.test,name='client'),

		path('login/',v.loginP,name="login"),
		path('logout/',v.logoutP,name="logout"),
		path('signup/',v.signup,name="signup"),
]