from typing import Optional, Dict, Any, List
from abc import ABC, abstractmethod
from .groq_client import GroqClient


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        pass


class GroqProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/llama-4-scout-17b-16e-instruct",
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        self.client = GroqClient(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        return self.client.generate(prompt, system_prompt, **kwargs)
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        return self.client.chat(messages, **kwargs)
    
    def analyze_resume(
        self,
        resume_text: str,
        job_description: str
    ) -> Dict[str, Any]:
        system_prompt = """You are an expert ATS (Applicant Tracking System) analyzer. 
        Analyze the resume against the job description and provide detailed insights."""
        
        prompt = f"""Analyze this resume against the job description:
        
        Resume:
        {resume_text}
        
        Job Description:
        {job_description}
        
        Provide analysis in JSON format with:
        1. match_score (0-100)
        2. matched_keywords
        3. missing_keywords
        4. suggestions for improvement
        """
        
        response = self.client.generate(prompt, system_prompt, temperature=0.3)
        return response
    
    def extract_keywords(
        self,
        text: str,
        context: str = "job_description"
    ) -> List[str]:
        system_prompt = f"You are an expert at extracting relevant keywords from {context}."
        
        prompt = f"""Extract the most important keywords from this text:
        
        {text}
        
        Return only a comma-separated list of keywords, nothing else.
        """
        
        response = self.client.generate(prompt, system_prompt, temperature=0.2, max_tokens=200)
        keywords = [kw.strip() for kw in response.split(',')]
        return keywords
    
    def improve_resume_section(
        self,
        section_text: str,
        section_type: str,
        job_keywords: List[str]
    ) -> str:
        system_prompt = "You are a professional resume writer specializing in ATS optimization."
        
        prompt = f"""Improve this {section_type} section to better match these job keywords: {', '.join(job_keywords)}
        
        Original text:
        {section_text}
        
        Provide an improved version that naturally incorporates relevant keywords while maintaining professionalism.
        """
        
        return self.client.generate(prompt, system_prompt, temperature=0.5)