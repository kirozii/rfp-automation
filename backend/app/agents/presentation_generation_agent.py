import logging
import pandas as pd
from ..database import async_session_factory
from ..models import RFPStatus
from ..crud import rfps, presentations
from ..services.ppt_generator import PresentationGenerator

logger = logging.getLogger("rfpai.agents.presentation_generation_agent")


class PresentationGenerationAgent:
    """
    Agent which generates a PowerPoint presentation for an RFP.
    """

    def __init__(self):
        logger.info("Presentation generation agent initialized.")

    async def process(self, rfp_id: int):
        """
        Generates a PowerPoint presentation for the given RFP.

        Args:
            rfp_id (int): The rfp_id of the RFP to generate a presentation for.
        """
        logger.info("Starting PPT generation for rfp_id: %s", rfp_id)

        async with async_session_factory() as session:
            db_rfp = await rfps.get_rfp(session, rfp_id)
            if db_rfp is None:
                logger.error("Could not find RFP with rfp_id: %s", rfp_id)
                return

            try:
                await rfps.update_rfp_status(
                    session, rfp_id, RFPStatus.GENERATING_PRESENTATION
                )

                filepath = db_rfp.storage_path
                filepath = (
                    "revised" + filepath
                )  # turns files/123.xlsx to revisedfiles/123.xlsx
                df = pd.read_excel(filepath, engine="openpyxl")

                df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

                required_cols = {"questions", "answers"}
                if not required_cols.issubset(df.columns):
                    missing = required_cols - set(df.columns)
                    raise ValueError(f"Missing required columns: {missing}")

                qlist = df["questions"].fillna("").tolist()
                answers = df["answers"].fillna("").tolist()

                content_for_ppt = self._pack_data(qlist, answers)

                self._gen_ppt(content_for_ppt, str(db_rfp.rfp_id))

                await presentations.create_presentation(
                    session,
                    rfp_id,
                    str(rfp_id) + ".pptx",
                    "ppts/" + str(rfp_id) + ".pptx",
                )

                await rfps.update_rfp_status(session, rfp_id, RFPStatus.COMPLETED)

                logger.info("Successfully generated PPT for rfp_id: %s", rfp_id)

            except Exception as e:
                logger.error(
                    "Failed to generate PPT for rfp_id %s: %s", rfp_id, e, exc_info=True
                )
                await rfps.update_rfp_status(session, rfp_id, RFPStatus.FAILED)

    def _pack_data(self, questions, answers):
        """
        Packs questions and answers into slide content format.
        """
        data = []
        for q, a in zip(questions, answers):
            data.append({"Title": q, "Content": a})
        return data

    def _gen_ppt(self, content, filename):
        """
        Generates a PPT file using PresentationGenerator.
        """
        pgen = PresentationGenerator(filename.rstrip(".xlsx"))
        for item in content:
            pgen.add_slide(
                1, 0
            )  # magic numbers but its basically slide master number, slide number (in the master)
            pgen.add_content(item)
        pgen.save_presentation()
