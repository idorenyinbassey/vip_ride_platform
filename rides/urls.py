from django.urls import path, include

app_name = 'rides'

urlpatterns = [
    # Include matching URLs
    path('matching/', include('rides.matching_urls')),
    
    # Include workflow URLs
    path('workflow/', include('rides.workflow_urls')),
    
    # Other ride URLs will be implemented here
]
