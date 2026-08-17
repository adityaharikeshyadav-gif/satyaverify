import os
import sys
import logging
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inference import DeepfakePredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='SATYAVERIFY ML API', version='1.0.0')
predictor = DeepfakePredictor()

@app.get('/health')
def health():
    return {'status': 'ok'}

@app.post('/analyze')
async def analyze(file: UploadFile = File(...)):
    try:
        suffix = Path(file.filename).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        if suffix in ('.mp4', '.avi', '.mov', '.mkv'):
            result = predictor.analyze_video(tmp_path)
        elif suffix in ('.jpg', '.jpeg', '.png', '.bmp'):
            result = predictor.analyze_image(tmp_path)
        else:
            result = {'error': f'Unsupported format: {suffix}'}
        import os as os_mod
        os_mod.unlink(tmp_path)
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f'Error in /analyze: {e}', exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)