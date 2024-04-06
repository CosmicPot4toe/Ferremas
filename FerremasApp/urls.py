from django.urls import path
from . import views as v

urlpatterns = [
    path('',v.test),

		path('login/',v.login,name="login"),
		path('signup/',v.signup,name="signup"),
]