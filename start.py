import os
import uvicorn
from main_webhook import webhook_app

# Render sẽ tự truyền PORT qua biến môi trường, không cần set cứng
port = int(os.environ.get("PORT", 8000))

uvicorn.run(webhook_app, host="0.0.0.0", port=port)
