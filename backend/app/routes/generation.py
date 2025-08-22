from app.agents.presentation_generation_agent import PresentationGenerationAgent
from openpyxl.styles import Alignment
from openpyxl import load_workbook
from app.crud import evaluations
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.services.spreadsheet_parser import SpreadsheetHandler
from fastapi.responses import FileResponse
import asyncio
from ..crud import rfps, questions, llm_responses
from ..models import RFPStatus
from ..agents.question_processing_agent import QuestionProcessingAgent
from ..agents.data_contextualization_agent import DataContextualizationAgent
from ..agents.data_retrieval_agent import DataRetrievalAgent
from ..database import async_session_factory
import pandas as pd
from sqlalchemy.orm import Session
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import logging
import os

from app import models

allowed_extensions = [".xlsx"]

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/files",
)


@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(...)):
    if file.filename:
        if not os.path.isdir("files"):
            os.mkdir("files")

        async with async_session_factory() as session:
            db_rfp = await rfps.create_rfp(session, file.filename)
            rfp_id = db_rfp.rfp_id

            filename_root, filename_ext = os.path.splitext(file.filename)

            new_filename = f"{rfp_id}{filename_ext}"
            file_location = os.path.join("files", new_filename)

            await rfps.update_storage_path(session, rfp_id, file_location)

            logger.info(
                "Attempting to save file: %s as %s", file.filename, new_filename
            )
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
        return {"message": "File uploaded", "rfp_id": rfp_id}


@router.post("/revise/{id}")
async def update_answers(id, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename or not a file")

    if not os.path.isdir("revisedfiles"):
        os.mkdir("revisedfiles")
    file_location = "revisedfiles/" + id + ".xlsx"
    try:
        with open(file_location, "wb") as f:
            while contents := await file.read(1024 * 1024):
                f.write(contents)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not upload file")
    finally:
        print("REVISE: File saved")
        await file.close()

    try:
        await register_revision_for_rfp("revisedfiles/" + id + ".xlsx", id)
        return {"message": "Revision saved"}
    except Exception as e:
        if os.path.exists(file_location):
            os.remove(file_location)
        raise HTTPException(
            status_code=400,
            detail=f"{e}",
        )


@router.post("/generate/{id}")
async def generate_answers(id: int):
    """
    Generate answers for all questions in the specified RFP by processing them through
    the data retrieval and data contextualization agents.
    """
    question_processing_agent = QuestionProcessingAgent()
    await question_processing_agent.process(id)
    async with async_session_factory() as session:
        try:
            rfp_questions = await questions.get_questions_by_rfp(session, id)

            if not rfp_questions:
                logger.info(f"No questions found for RFP ID {id}")
                return {"message": f"No questions found for RFP ID {id}!"}

            logger.info(f"Found {len(rfp_questions)} questions for RFP ID {id}")

            data_retrieval_agent = DataRetrievalAgent()
            contextualization_agent = DataContextualizationAgent()

            tasks = []

            for question in rfp_questions:
                if question is None:
                    logger.error(f"Encountered None in rfp_questions for RFP ID {id}")
                    continue

                question_id = question.question_id

                logger.info(f"Processing question ID {question_id} for RFP ID {id}")

                tasks.append(
                    orchestrate_processing(
                        question_id, data_retrieval_agent, contextualization_agent
                    )
                )

            await asyncio.gather(*tasks)
            await write_questions(id)

            await rfps.update_rfp_status(session, id, RFPStatus.PENDING_REVIEW)
            logger.info(
                f"Completed processing {len(rfp_questions)} questions for RFP ID {id}"
            )
            return {
                "message": f"Successfully processed {len(rfp_questions)} questions for RFP ID {id}!"
            }
        except Exception as e:
            logger.error(f"Error in generate_answers: {e}")
            raise HTTPException(
                status_code=500, detail=f"Error generating answers: {str(e)}"
            )


async def orchestrate_processing(
    question_id: int,
    data_retrieval_agent: DataRetrievalAgent,
    contextualization_agent: DataContextualizationAgent,
):
    # Process through data retrieval agent
    await data_retrieval_agent.process(question_id)
    logger.info(f"Data retrieval completed for question ID {question_id}")

    # Process through data contextualization agent
    await contextualization_agent.process(question_id)
    logger.info(f"Data contextualization completed for question ID {question_id}")


@router.get("/")
async def get_uploaded_files():
    async with async_session_factory() as session:
        files = await rfps.get_rfps(session)
        file_list = []
        for rfp in files:
            rfp_json = {
                "rfp_id": rfp.rfp_id,
                "filename": rfp.filename,
                "uploaded_at": rfp.uploaded_at,
                "status": rfp.status,
            }
            file_list.append(rfp_json)
        return file_list


@router.get("/download/{rfp_id}")
async def download_file(rfp_id: int):
    async with async_session_factory() as session:
        db_file = await rfps.get_rfp(session, rfp_id)
        logger.info("Downloading file: %s", db_file.filename)
        if not os.path.exists(db_file.storage_path):
            raise HTTPException(status_code=404, detail="File not found")

        return FileResponse(path=db_file.storage_path, filename=db_file.filename)


@router.get("/downloadppt/{rfp_id}")
async def download_ppt(rfp_id: str):
    logger.info("PPTDOWN: Downloading ppt for id: %s", rfp_id)
    filename = rfp_id + ".pptx"
    file_path = "ppts/" + filename
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, filename=filename)


@router.post("/generateppt/{rfp_id}")
async def generate_ppt(rfp_id: str):
    agent = PresentationGenerationAgent()
    try:
        await agent.process(int(rfp_id))
        return {"message": f"PPT generated successfully for RFP {rfp_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PPT: {str(e)}")


async def write_questions(rfp_id: int) -> None:
    """
    Fetches all questions for a given RFP ID and writes them to Excel.

    Args:
        rfp_id: The RFP ID to fetch questions for.
        writer: An instance of ExcelWriter.
        db_session: Database session/connection for fetching questions.
    """
    writer = SpreadsheetHandler(str(rfp_id) + ".xlsx")

    async with async_session_factory() as session:
        qlist = await questions.get_questions_by_rfp(session, rfp_id)

        if not qlist:
            print(f"No questions found for RFP ID {rfp_id}")
            return
        qlist = sorted(qlist, key=lambda q: q.question_id)

        question_dicts = []

        for idx, q in enumerate(qlist):
            ans = await llm_responses.get_llm_responses_by_question(
                session, q.question_id
            )
            anstext = ans.response
            question_dict = {
                "S.No": idx + 1,
                "Questions": q.question_text,
                "Answers": anstext,
                "Ratings": "",
                "Comments": "",
            }
            question_dicts.append(question_dict)
        writer.write_to_sheet(question_dicts)

        wb = load_workbook(writer.path)
        ws = wb.active

        for col in ws.columns:
            max_length = 0
            col_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        # Wrap text for all cells
                        cell.alignment = Alignment(wrap_text=True, vertical="top")
                        max_length = max(max_length, len(str(cell.value)))
                except Exception:
                    pass
            adjusted_width = min(
                max_length + 2, 60
            )  # cap width so it doesn't get too wide
            ws.column_dimensions[col_letter].width = adjusted_width

        wb.save(writer.path)

        logger.info("Questions for RFP %s written to %s", rfp_id, writer.path)


async def register_revision_for_rfp(file_path: str, rfp_id: int):
    """
    Reads an Excel file with questions, answers, ratings, comments,
    and creates/updates Evaluations for the given RFP.

    Args:
        file_path (str): Path to Excel file
        rfp_id (int): The RFP ID
    """
    df = pd.read_excel(file_path)

    df.columns = df.columns.str.strip().str.lower()

    required_columns = {"questions", "answers", "ratings", "comments"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Missing required columns: {required_columns - set(df.columns)}"
        )

    async with async_session_factory() as session:
        result = await session.execute(
            select(models.Question)
            .where(models.Question.rfp_id == rfp_id)
            .options(selectinload(models.Question.llm_responses))
        )
        question_list = result.scalars().all()

        question_map = {}
        for q in question_list:
            if q.llm_responses:
                llm_response = q.llm_responses[-1]
                question_map[q.question_text.strip().lower()] = llm_response

        created_ids = []

        for _, row in df.iterrows():
            q_text = str(row["questions"]).strip()
            q_key = q_text.lower()

            llm_response = question_map.get(q_key)

            if not llm_response:
                new_question = await questions.create_question(session, rfp_id, q_text)

                new_response = await llm_responses.create_llm_response(
                    session,
                    new_question.question_id,
                    str(row["answers"]) if not pd.isna(row["answers"]) else "",
                    retrieved_context="N/A Human provided question",
                )

                llm_response = new_response
                question_map[q_key] = llm_response

                logger.info(f"Created new Question + LLMResponse for: {q_text}")

            new_eval = await evaluations.create_evaluation(
                db=session,
                response_id=llm_response.response_id,
                original_response=llm_response.response,
                fine_tuned_response=str(row["answers"])
                if not pd.isna(row["answers"])
                else None,
                score=int(row["ratings"]) if not pd.isna(row["ratings"]) else None,
                sme_comments=str(row["comments"])
                if not pd.isna(row["comments"])
                else None,
            )
            created_ids.append(new_eval.eval_id)

        logger.info(
            f"Registered/updated {len(created_ids)} evaluations for RFP {rfp_id} from {file_path}"
        )

        await rfps.update_rfp_status(session, rfp_id, RFPStatus.REVIEWED)
        return created_ids
