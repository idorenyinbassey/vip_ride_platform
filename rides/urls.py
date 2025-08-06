from django.urls import path, include

app_name = 'rides'

urlpatterns = [
    # Include matching URLs
    path('', include('rides.matching_urls')),
    
    # Other ride URLs will be implemented here
]
