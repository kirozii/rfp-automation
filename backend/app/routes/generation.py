from fastapi.responses import FileResponse
import pandas as pd
from app.services.spreadsheet_parser import SpreadsheetHandler
from app.services.answer_generator import Generator
from app.services.ppt_generator import PresentationGenerator
from fastapi import APIRouter, UploadFile, File, HTTPException, status
import asyncio
import os

uploaded_files = []
allowed_extensions = [".xlsx"]

router = APIRouter(
    prefix="/files",
)

@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    if file.filename:
        if not os.path.isdir("files"):
            os.mkdir("files")

        file_location = "files/" + file.filename
        try:
            with open(file_location, "wb") as f:
                while contents := await file.read(1024 * 1024):
                    f.write(contents)
        except Exception:
            raise HTTPException(status_code=500, detail="Could not upload file")
        finally:
            await file.close()

        # Would store metadata here to db .
        uploaded_files.append({'name': file.filename, 'generated': False, 'pptGenerated': False})
        return {'message': "File uploaded"}

@router.post("/generate/{filename}")
async def generate_answers(filename: str):
    await generate_spreadsheet(filename)
    found = False
    for item in uploaded_files:
        if item['name'] == filename:
            if item['generated']:
                return {"message": f"File '{filename}' was already generated!", "status": "already_generated"}
            item['generated'] = True
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="File not found in in-memory database to update status")
    return {'message': 'File generated!'}

@router.get("/")
async def get_uploaded_files():
    return uploaded_files

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = "files/" + filename
    print("We are in download!")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)

@router.get("/downloadppt/{filename}")
async def download_ppt(filename: str):
    print("PPTDOWN: Downloading ppt for: ", filename)
    filename = filename.rstrip(".xlsx") + ".pptx"
    file_path = "ppts/" + filename
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)

@router.post("/generateppt/{filename}")
async def generate_ppt(filename: str):
    df = pd.read_excel("files/" + filename, engine='openpyxl')
    required_cols = ["Questions", "Answer"]
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        print(f"PPTGEN: '{filename}' is missing required columns: {missing_cols}.")
        return
    qlist = df["Questions"].fillna('').to_list()
    answers_raw = df["Answer"].fillna('').to_list()
    responses_for_packing = [{"Answer": ans} for ans in answers_raw]
    content_for_ppt = pack_data(qlist, responses_for_packing)
    gen_ppt(content_for_ppt, filename)
    found = False
    for item in uploaded_files:
        if item['name'] == filename:
            if item['pptGenerated']:
                return {"message": f"PPT '{filename}' was already generated!", "status": "already_generated"}
            item['pptGenerated'] = True
            found = True
            break
    if not found:
        raise HTTPException(status_code=404, detail="File not found in in-memory database to update status")
    print("PPTGEN: Finished generating ppt.")

async def generate_spreadsheet(file):
    handler = SpreadsheetHandler(file)
    llm = Generator()

    questions = handler.extract_questions()

    tasks = [llm.generate_response(question) for question in questions['Questions']]
    responses = await asyncio.gather(*tasks) # list of dicts {"Answer": ans}

    handler.write_to_sheet(responses)

    # PPT Agent's step 
    # data = pack_data(qlist, responses)
    # gen_ppt(data)


def gen_ppt(content, filename):
    pgen = PresentationGenerator(filename.rstrip(".xlsx"))
    for i in content:
        pgen.add_slide(1, 0)
        pgen.add_content(i)
        pgen.save_presentation()

def pack_data(qlist, responses):
    # doing the agents job for now, basically returns a list of dicts {"Title": w/e, "Content": w/e}
    data = []
    for i in range(len(responses)):
        data.append({"Title": qlist[i], "Content": responses[i]["Answer"]})
    return data
