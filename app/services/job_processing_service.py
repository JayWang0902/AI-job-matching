import os
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.job import Job
from app.services.openai_service import get_openai_client

class JobProcessingService:
    """
    A service class for processing jobs, specifically for generating embeddings.
    """

    @staticmethod
    def _get_embedding(text: str, model="text-embedding-3-small") -> list[float]:
        """
        Generates an embedding for the given text using OpenAI's API.
        """
        client = get_openai_client()
        text = text.replace("\n", " ")
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding

    @classmethod
    def process_job_embedding(cls, db: Session, job: Job):
        """
        Processes a single job to generate and store its embedding.

        This method retrieves a job, checks if an embedding already exists,
        generates a new one if it doesn't, and updates the job record.
        It does not commit the transaction, allowing it to be part of a larger one.
        """
        if not job:
            # Or raise an exception, depending on desired error handling
            print("Received an invalid job object.")
            return

        if job.embedding is not None:
            print(f"Embedding for job {job.id} already exists. Skipping.")
            return

        # Concatenate relevant fields to create the content for embedding
        content_to_embed = f"Title: {job.title}\n"
        if job.tags:
            content_to_embed += f"Tags: {', '.join(job.tags)}\n"
        content_to_embed += f"Description: {job.description}"

        # Generate and save the embedding
        try:
            embedding = cls._get_embedding(content_to_embed)
            job.embedding = embedding
            print(f"Successfully generated embedding for job {job.id}.")
        except Exception as e:
            print(f"Failed to generate embedding for job {job.id}: {e}")
            # Optionally, re-raise the exception or handle it
            # For now, we just log and continue
            pass
