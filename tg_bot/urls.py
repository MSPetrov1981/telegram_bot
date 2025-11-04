"""
URL configuration for tg_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Простая домашняя страница


def home_view(request):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot Constructor API</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #007cba; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Bot Constructor API</h1>
            <p>Добро пожаловать в систему управления ботами!</p>
            
            <h2>🔗 Доступные endpoints:</h2>
            <div class="endpoint">
                <strong>Admin Panel:</strong> <a href="/admin/">/admin/</a>
            </div>
            <div class="endpoint">
                <strong>API Bots:</strong> <a href="/api/bots/">/api/bots/</a>
            </div>
            <div class="endpoint">
                <strong>API Scenarios:</strong> <a href="/api/scenarios/">/api/scenarios/</a>
            </div>
            <div class="endpoint">
                <strong>API Steps:</strong> <a href="/api/steps/">/api/steps/</a>
            </div>
            
            <h2>📚 Документация:</h2>
            <p>Для работы с API используйте следующие endpoints:</p>
            <ul>
                <li><code>GET/POST /api/bots/</code> - Управление ботами</li>
                <li><code>GET/POST /api/scenarios/</code> - Управление сценариями</li>
                <li><code>GET/POST /api/steps/</code> - Управление шагами сценариев</li>
                <li><code>POST /webhook/telegram/&lt;bot_token&gt;/</code> - Webhook для Telegram</li>
            </ul>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html)


urlpatterns = [
    path("", home_view),  # Домашняя страница
    path("admin/", admin.site.urls),
    path("api/", include("bot.urls")),  # API endpoints
    # Или если хотите перенаправлять сразу в админку:
    # path('', RedirectView.as_view(url='/admin/')),
]
