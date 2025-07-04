import logging
import os
from typing import Optional, Tuple, List, Dict
import boto3
import docx
import fitz  # PyMuPDF
import openai
from sqlalchemy.orm import Session
from app.models.user import Resume
from app.services.s3_service import s3_service
from uuid import UUID
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# It's recommended to manage the OpenAI client in a more centralized way if used elsewhere
# For this example, we initialize it here.
# Ensure OPENAI_API_KEY is set in your environment variables.
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    logger.warning("OPENAI_API_KEY environment variable not set. OpenAI API calls will fail.")

class ResumeProcessingService:
    """
    A service to handle the processing of a resume after it has been uploaded.
    This includes downloading from S3, parsing content, and extracting info using AI.
    """

    @staticmethod
    def _download_file_from_s3(resume: Resume) -> Optional[str]:
        """Downloads a file from S3 to a temporary local path."""
        # Ensure the /tmp directory exists
        if not os.path.exists("/tmp"):
            os.makedirs("/tmp")
            
        local_filename = f"/tmp/{resume.s3_key.split('/')[-1]}"
        try:
            logger.info(f"Downloading s3://{resume.s3_bucket}/{resume.s3_key} to {local_filename}")
            s3_service.s3_client.download_file(
                Bucket=resume.s3_bucket,
                Key=resume.s3_key,
                Filename=local_filename
            )
            return local_filename
        except Exception as e:
            logger.error(f"Failed to download {resume.s3_key} from S3: {e}")
            return None

    @staticmethod
    def _parse_resume_content(local_path: str, content_type: str) -> str:
        """Parses text content from a resume file (PDF or DOCX)."""
        text = ""
        try:
            logger.info(f"Parsing content from {local_path} with content_type {content_type}")
            if content_type == 'application/pdf':
                with fitz.open(local_path) as doc:
                    for page in doc:
                        text += page.get_text()
            elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                doc = docx.Document(local_path)
                for para in doc.paragraphs:
                    text += para.text + "\n"
            else:
                raise ValueError(f"Unsupported content type for parsing: {content_type}")
            
            logger.info(f"Successfully parsed {len(text)} characters from {local_path}")
            return text
        except Exception as e:
            logger.error(f"Failed to parse file {local_path}: {e}")
            raise
        finally:
            # Clean up the temporary file
            if os.path.exists(local_path):
                os.remove(local_path)

    @staticmethod
    def _get_ai_analysis(content: str) -> Tuple[Optional[str], Optional[List[str]], Optional[List[str]]]:
        """
        Uses OpenAI to generate a summary, list of skills, and potential job titles.
        """
        if not openai.api_key:
            raise ValueError("OpenAI API key is not configured.")

        prompt = f'''
        Analyze the following resume content and extract the information in JSON format.
        The JSON object should have three keys: "professional_summary", "skills", and "potential_job_titles".
        - "professional_summary": A concise professional summary of the candidate (2-4 sentences).
        - "skills": A list of key technical and soft skills.
        - "potential_job_titles": A list of 3-5 suitable job titles for this candidate.

        Resume Content:
        ---
        {content[:8000]}
        ---
        '''
        try:
            logger.info("Calling OpenAI ChatCompletion API...")
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert HR assistant specializing in resume analysis."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            
            response_data = json.loads(response.choices[0].message.content)
            
            summary = response_data.get("professional_summary")
            skills = response_data.get("skills")
            job_titles = response_data.get("potential_job_titles")

            logger.info("Successfully received and parsed AI analysis.")
            return summary, skills, job_titles

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    @staticmethod
    def _get_embedding(content: str) -> Optional[List[float]]:
        """Generates a vector embedding for the resume content."""
        if not openai.api_key:
            raise ValueError("OpenAI API key is not configured.")
            
        try:
            logger.info("Calling OpenAI Embedding API...")
            response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=content[:8191] # Respect token limits
            )
            embedding = response.data[0].embedding
            logger.info(f"Successfully generated embedding of dimension {len(embedding)}.")
            return embedding
        except Exception as e:
            logger.error(f"OpenAI Embedding API call failed: {e}")
            raise

    @classmethod
    def process_resume(cls, db: Session, resume_id: UUID):
        """Main workflow for processing a single resume."""
        logger.info(f"Starting processing for resume_id: {resume_id}")
        
        resume = db.query(Resume).filter(Resume.id == resume_id).first()
        if not resume:
            logger.error(f"Resume with id {resume_id} not found.")
            return

        try:
            # 1. Update status to 'processing'
            resume.status = 'processing'
            resume.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Resume {resume_id} status updated to 'processing'.")

            # 2. Download from S3
            local_path = cls._download_file_from_s3(resume)
            if not local_path:
                raise RuntimeError("Failed to download file from S3.")

            # 3. Parse content
            parsed_content = cls._parse_resume_content(local_path, resume.content_type)
            resume.parsed_content = parsed_content
            
            # 4. Get AI analysis (Summary, Skills, Job Titles)
            summary, skills, job_titles = cls._get_ai_analysis(parsed_content)
            resume.summary = summary
            resume.skills = skills
            resume.job_titles = job_titles

            # 5. Generate embedding
            embedding = cls._get_embedding(parsed_content)
            resume.embedding = embedding

            # 6. Final update to 'parsed'
            resume.status = 'parsed'
            resume.parsed_at = datetime.utcnow()
            resume.updated_at = datetime.utcnow()
            resume.error_message = None
            logger.info(f"Successfully processed and parsed resume {resume_id}.")

        except Exception as e:
            logger.error(f"An error occurred during resume processing for {resume_id}: {e}", exc_info=True)
            resume.status = 'failed'
            resume.error_message = str(e)
            resume.updated_at = datetime.utcnow()
        
        finally:
            db.commit()
            logger.info(f"Finished processing for resume {resume_id}. Final status: {resume.status}")

# Instantiate the service for easy importing
resume_processing_service = ResumeProcessingService()
