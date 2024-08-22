from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from transformers import pipeline
import PyPDF2
import io
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

qa_pipeline = pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

pdf_text_storage = {}

class Query(BaseModel):
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    try:
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        logger.error(f"Error in read_root: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

extracted_text = ""
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    global extracted_text
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a PDF file.")
    
    try:
      
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(await file.read()))
       
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            page_text = page.extract_text() or ""  
            extracted_text += page_text
        logger.info(f"Extracted text: {extracted_text[:500]}...") 

        return {"text": extracted_text}
    
    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"PDF read error: {e}")
        raise HTTPException(status_code=400, detail=f"PDF read error: {str(e)}")
    except Exception as e:
        logger.error(f"Error in upload_pdf: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")


@app.post("/ask/")
async def ask_question(query: Query):
    global extracted_text
    question = query.question
    
    try:
        if not extracted_text:
            raise HTTPException(status_code=400, detail="No PDF text available for answering questions.")
        if not question.strip():
            raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
        result = qa_pipeline(question=question, context=extracted_text)
        logger.info(f"result: {result}")
        answer = result.get('answer', 'No answer found.')
        
        return JSONResponse(content={"answer": answer})
    except Exception as e:
        logger.error(f"Error in ask_question: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the question.")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
