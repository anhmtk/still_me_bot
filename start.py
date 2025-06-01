import os
import uvicorn
from main_webhook import webhook_app

port = int(os.environ.get("PORT", 10000))
uvicorn.run(webhook_app, host="0.0.0.0", port=port)
