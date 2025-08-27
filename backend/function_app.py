import azure.functions as func
from backend.main import app  # FastAPI 앱 임포트

# Azure Functions v2 programming model을 사용하여 FastAPI 앱을 노출
app_func = func.AsgiFunctionApp(app=app, http_auth_level=func.AuthLevel.ANONYMOUS)
