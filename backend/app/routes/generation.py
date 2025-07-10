from fastapi.responses import FileResponse
from app.services.spreadsheet_parser import SpreadsheetHandler
from app.services.answer_generator import Generator
from app.services.ppt_generator import PresentationGenerator
from fastapi import APIRouter, UploadFile, File, HTTPException, status
import asyncio
import os

uploaded_files = []
allowed_extensions = [".xlsx"]
MAX_FILES = 5

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

        # Would store metadata here to db
        uploaded_files.append(file.filename)
        await generate_spreadsheet(file.filename)
        return {'message': "File uploaded"}


@router.get("/")
async def get_uploaded_files():
    return uploaded_files[-MAX_FILES:]

@router.get("/download/{filename}")
async def download_file(filename: str):
    file_path = "files/" + filename
    print("We are in download!")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)

async def generate_spreadsheet(file):
    handler = SpreadsheetHandler(file)
    llm = Generator()

    questions = handler.extract_questions()
    qlist = questions["Questions"].to_list()

    tasks = [llm.generate_response(question) for question in questions['Questions']]
    responses = await asyncio.gather(*tasks) # list of dicts {"Answer": ans}

    handler.write_to_sheet(responses)

    # PPT Agent's step
    # data = pack_data(qlist, responses)
    # gen_ppt(data)

def gen_ppt(content):
    pgen = PresentationGenerator("output")
    for i in content:
        pgen.add_slide(1, 20)
        pgen.add_content(i)
        pgen.save_presentation()

def pack_data(qlist, responses):
    # doing the agents job for now, basically returns a list of dicts {"Title": w/e, "Content": w/e}
    data = []
    for i in range(len(responses)):
        data.append({"Title": qlist[i], "Content": responses[i]["Answer"]})
    return data
