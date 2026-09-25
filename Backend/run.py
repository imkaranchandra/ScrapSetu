import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting ScrapSetu Backend Server...")
    print("📖 API Documentation available at: http://127.0.0.1:8000/docs")
    print("🌐 Health check at: http://127.0.0.1:8000/")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
