from sqlalchemy.orm import Session
import asyncio
import os
import fitz
from typing import Dict, List
from pptx import Presentation
from ..core.config import settings
from pydantic import SecretStr
import logging
from openai import AsyncAzureOpenAI
from ..models import QuestionStatus
from ..crud import questions

logger = logging.getLogger("rfpai.agents.presentation_generation_agent")
