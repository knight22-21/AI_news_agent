from fastapi import FastAPI
from pydantic import BaseModel
from main import crew  

app = FastAPI()

class Command(BaseModel):
    command: str

@app.post("/news")
async def get_ai_news(cmd: Command):
    if cmd.command.lower() == "get ai news":
        try:
            summary = crew.kickoff()
            return {"success": True, "summary": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}
    return {"success": False, "error": "Unknown command"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
