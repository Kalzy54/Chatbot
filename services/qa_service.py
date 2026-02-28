import logging
import os
from typing import Optional

from rag.pipeline import RAGPipeline
from config.settings import settings
from models.schemas import ChatResponse
from utils.sanitizer import sanitize_input, detect_prompt_injection

logger = logging.getLogger(__name__)


class QAService:
    def __init__(self):
        self.pipeline = RAGPipeline()
        
        # Try to ingest from web if URL is configured
        web_url = os.environ.get("UNIVERSITY_WEB_URL", "")
        if web_url:
            try:
                logger.info(f"Ingesting from web: {web_url}")
                self.pipeline.ingest_from_web(web_url, max_pages=50)
            except Exception as e:
                logger.warning("web ingest failed: %s, falling back to local docs", e)
                # Fall back to local docs
                try:
                    self.pipeline.ingest_documents_from_folder("data")
                except Exception as e2:
                    logger.warning("local ingest also failed: %s", e2)
        else:
            # ingest docs at startup from local folder
            try:
                self.pipeline.ingest_documents_from_folder("data")
            except Exception as e:
                logger.warning("ingest at init failed: %s", e)

        # analytics
        self.total_queries = 0
        self.unanswered = 0

        self.guided = {
            "Browse Catalog": "You can search our online library catalog at the library portal. Search by title, author, ISBN, or subject. Use call numbers to locate items on the shelf.",
            "Loan Status": "Log into your library account on the portal to check your loans, due dates, and renewals. You can also renew items online or in person.",
            "Research Databases": "We provide access to multiple research databases including academic journals, e-books, and subject-specific resources. Visit the library website for database links and access instructions.",
            "Study Spaces": "Study areas include individual carrels, group study rooms, and collaborative spaces. Group study rooms can be reserved online. Library hours and current capacity are posted on our website.",
            "Library Services": "Services include reference desk assistance, research consultations, citation help, information literacy workshops, and interlibrary loan. Contact the reference desk or use our online chat for help.",
        }

        self.system_prompt = (
            "You are Rex's Lib Chat, the official AI assistant for Mewar International University Library.\n\n"
            "INSTRUCTIONS:\n"
            "1. You have access to official library documents with accurate, current information.\n"
            "2. Use the provided library information to answer the user's question comprehensively.\n"
            "3. When answering, provide specific details from the retrieved library documents.\n"
            "4. Only say 'I don't have that information' if the provided documents truly don't contain the answer.\n"
            "5. Do not make up or fabricate library policies, hours, or procedures.\n\n"
            "DOCUMENT CONTENT:\n"
            "The following information comes from official Mewar University Library sources and is current and accurate."
        )

    def get_menu(self):
        return list(self.guided.keys()) + ["Ask a Question"]

    def handle_guided(self, option: Optional[str]):
        if not option or option == "Main Menu":
            return {"answer": "Main menu", "confidence": 1.0}
        if option == "Ask a Question":
            return {"answer": "Please submit your question (mode: ask)", "confidence": 0.0}
        resp = self.guided.get(option)
        if resp:
            return {"answer": resp, "confidence": 1.0}
        return {"answer": "Option not recognized.", "confidence": 0.0}

    def handle_question(self, question: str):
        self.total_queries += 1
        q = sanitize_input(question)
        if detect_prompt_injection(q):
            logger.warning("prompt injection detected for query")
            self.unanswered += 1
            return ChatResponse(answer="I do not have that information. Please contact the relevant university office.", confidence=0.0)

        retrieved = self.pipeline.retrieve(q)
        logger.info(f"Retrieved {len(retrieved)} chunks. Best score: {max((s for _, s in retrieved), default=0):.3f}")
        
        if not retrieved:
            logger.info("no documents retrieved for question: %s", q)
            self.unanswered += 1
            return ChatResponse(answer="I do not have that information. Please contact the relevant university office.", confidence=0.0)
        
        answer, score = self.pipeline.generate_answer(q, retrieved, self.system_prompt)

        # Only reject if answer is explicitly None (threshold not met in generate_answer)
        if answer is None:
            logger.info("answer generation returned None (low score=%s): %s", score, q)
            self.unanswered += 1
            return ChatResponse(answer="I do not have that information. Please contact miulibrary2025@gmail.com for assistance.", confidence=float(score))

        # log successful
        logger.info("answered query (score=%s): %s", score, q)
        sources = [d for d, _ in retrieved[: settings.TOP_K]]
        return ChatResponse(answer=answer, confidence=float(score), source_documents=sources)
