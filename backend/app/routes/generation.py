from fastapi.responses import FileResponse
from ..crud import rfps, questions
from ..models import RFPStatus
from ..agents.question_processing_agent import QuestionProcessingAgent
from ..agents.data_contextualization_agent import DataContextualizationAgent
from ..agents.data_retrieval_agent import DataRetrievalAgent
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..database import get_db
import logging
import os

allowed_extensions = [".xlsx"]

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
)

@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if file.filename:
        if not os.path.isdir("files"):
            os.mkdir("files")

        db_rfp = rfps.create_rfp(db, file.filename)
        rfp_id = db_rfp.rfp_id

        filename_root, filename_ext = os.path.splitext(file.filename)

        new_filename = f"{rfp_id}{filename_ext}"
        file_location = os.path.join("files", new_filename)

        rfps.update_storage_path(db, rfp_id, file_location)

        logger.info("Attempting to save file: %s as %s", file.filename, new_filename)
        try:
            with open(file_location, "wb") as f:
                while contents := await file.read(1024 * 1024):
                    f.write(contents)
        except Exception:
            logger.error("Could not save file: %s", file.filename)
            raise HTTPException(status_code=500, detail="Could not upload file")
        finally:
            await file.close()

        logger.info("Created file: %s with rfp_id: %s", file.filename, rfp_id)
        return {'message': "File uploaded", 'rfp_id': rfp_id}


@router.post("/revise/{filename}")
async def update_answers(filename, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename or not a file")
    filepointer = False

    if not filepointer:
        raise HTTPException(status_code=404, detail="Could not locate original file in database.")

    if not os.path.isdir("revisedfiles"):
        os.mkdir("revisedfiles")
    file_location = "revisedfiles/" + filename
    try:
        with open(file_location, "wb") as f:
            while contents := await file.read(1024 * 1024):
                f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not upload file")
    finally:
        print("REVISE: File saved")
        await file.close()

    if (validate(filename)):
        filepointer['revised'] = True
        return {'message': "Revision saved"}
    else:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is invalid: It must have 'Questions' and 'Answer' columns, or is malformed/empty.",
        )

@router.post("/generate/{id}")
async def generate_answers(id: int, db: Session = Depends(get_db)):
    """
    Generate answers for all questions in the specified RFP by processing them through
    the data retrieval and data contextualization agents.
    """
    question_processing_agent = QuestionProcessingAgent(db)
    await question_processing_agent.process(id)
    try:
        rfp_questions = questions.get_questions_by_rfp(db, id)
        
        if not rfp_questions:
            logger.info(f"No questions found for RFP ID {id}")
            return {'message': f'No questions found for RFP ID {id}!'}
        
        logger.info(f"Found {len(rfp_questions)} questions for RFP ID {id}")
        
        # Initialize agents
        data_retrieval_agent = DataRetrievalAgent(db)
        contextualization_agent = DataContextualizationAgent(db)
        
        # Process each question through both agents
        for question in rfp_questions:
            question_id = question.question_id
            
            logger.info(f"Processing question ID {question_id} for RFP ID {id}")

            process_question(question_id, data_retrieval_agent, contextualization_agent)
        
        rfps.update_rfp_status(db, id, RFPStatus.PENDING_REVIEW)
        logger.info(f"Completed processing {len(rfp_questions)} questions for RFP ID {id}")
        return {'message': f'Successfully processed {len(rfp_questions)} questions for RFP ID {id}!'}
        
    except Exception as e:
        logger.error(f"Error in generate_answers: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating answers: {str(e)}")

async def process_question(question_id: int, data_retrieval_agent: DataRetrievalAgent, contextualization_agent: DataContextualizationAgent):
    # Process through data retrieval agent
    await data_retrieval_agent.process(question_id)
    logger.info(f"Data retrieval completed for question ID {question_id}")
    
    # Process through data contextualization agent
    await contextualization_agent.process(question_id)
    logger.info(f"Data contextualization completed for question ID {question_id}")

@router.get("/")
async def get_uploaded_files(db: Session = Depends(get_db)):
    files = rfps.get_rfps(db)
    file_list = []
    for rfp in files:
        rfp_json = {
            'rfp_id': rfp.rfp_id,
            'filename': rfp.filename,
            'uploaded_at': rfp.uploaded_at,
            'status': rfp.status
        }
        file_list.append(rfp_json)
    return file_list

@router.get("/download/{rfp_id}")
async def download_file(rfp_id: int, db: Session = Depends(get_db)):
    db_file = rfps.get_rfp(db, rfp_id)
    logger.info("Downloading file: %s", db_file.filename)
    if not os.path.exists(db_file.storage_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=db_file.storage_path, filename=db_file.filename)

@router.get("/downloadppt/{filename}")
async def download_ppt(filename: str):
    print("PPTDOWN: Downloading ppt for: ", filename)
    filename = filename.rstrip(".xlsx") + ".pptx"
    file_path = "ppts/" + filename
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)

# @router.post("/generateppt/{filename}")
# async def generate_ppt(filename: str):
#     df = pd.read_excel("revisedfiles/" + filename, engine='openpyxl')
#     required_cols = ["Questions", "Answer"]
#     if not all(col in df.columns for col in required_cols):
#         missing_cols = [col for col in required_cols if col not in df.columns]
#         print(f"PPTGEN: '{filename}' is missing required columns: {missing_cols}.")
#         return
#     qlist = df["Questions"].fillna('').to_list()
#     answers_raw = df["Answer"].fillna('').to_list()
#     responses_for_packing = [{"Answer": ans} for ans in answers_raw]
#     content_for_ppt = pack_data(qlist, responses_for_packing)
#     gen_ppt(content_for_ppt, filename)
#     found = False
#     for item in uploaded_files:
#         if item['name'] == filename:
#             if item['pptGenerated']:
#                 return {"message": f"PPT '{filename}' was already generated!", "status": "already_generated"}
#             item['pptGenerated'] = True
#             found = True
#             break
#     if not found:
#         raise HTTPException(status_code=404, detail="File not found in in-memory database to update status")
#     print("PPTGEN: Finished generating ppt.")
#
# def gen_ppt(content, filename):
#     pgen = PresentationGenerator(filename.rstrip(".xlsx"))
#     for i in content:
#         pgen.add_slide(1, 0)
#         pgen.add_content(i)
#         pgen.save_presentation()
#
# def pack_data(qlist, responses):
#     # doing the agents job for now, basically returns a list of dicts {"Title": w/e, "Content": w/e}
#     data = []
#     for i in range(len(responses)):
#         data.append({"Title": qlist[i], "Content": responses[i]["Answer"]})
#     return data

def validate(filename):
    try:
        path = "revisedfiles/" + filename
        print("VALIDATE: Validating the file")
        df = pd.read_excel(path)

        required_columns = ["Questions", "Answer"]
        if all(col in df.columns for col in required_columns):
            print(f"File '{filename}' is valid.")
            return True
        else:
            print(
                f"File '{filename}' is missing required columns. "
                f"Found: {df.columns.tolist()}, Required: {required_columns}"
            )
            return False
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return False
    except pd.errors.EmptyDataError:
        print(f"Error: File '{filename}' is empty.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
