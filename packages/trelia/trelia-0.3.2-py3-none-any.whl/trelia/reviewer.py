import os
import re
import json
from typing import Optional
import importlib.resources
from kynex.LLMTools import LLMConnector


class TreliaCodeReviewer:
    def __init__(self, llm_type: str, model_name: str, grading_prompt: str, feedback_prompt: str, host: str = ""):
        self.llm_type = llm_type
        self.model_name = model_name
        self.host = host
        self.grading_prompt_template = grading_prompt
        self.feedback_prompt_template = feedback_prompt
        self.code_signals, self.regex_patterns = self._load_code_signals_and_patterns()

        # Validate LLM configuration
        if self.llm_type == LLMConnector.LLM_GEMINI:
            if not self.model_name or not os.getenv("GEMINI_API_KEY"):
                raise ValueError("Gemini requires model_name and GEMINI_API_KEY environment variable.")
        elif self.llm_type == LLMConnector.LLM_OLLAMA:
            if not self.model_name or not self.host:
                raise ValueError("Ollama requires model_name and host.")
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")

    @staticmethod
    def _load_code_signals_and_patterns() -> tuple[list, dict]:
        """Load code signals and regex patterns from embedded JSON."""
        try:
            with importlib.resources.open_text("trelia.data", "code_signals.json") as f:
                data = json.load(f)
                return data.get("code_signals", []), data.get("regex_patterns", {})
        except Exception as e:
            print(f"[ERROR] Failed to load code signals: {e}")
            return [], {}

    @staticmethod
    def _load_spam_patterns() -> list:
        """Load spam patterns from the embedded JSON file."""
        try:
            with importlib.resources.open_text("trelia.data", "spam_patterns.json") as f:
                data = json.load(f)
                return data.get("spam_patterns", [])
        except Exception as e:
            print(f"Failed to load spam patterns: {e}")
            return []

    def remove_spam_lines(self, code: str) -> str:
        """Remove spammy or irrelevant lines from student code."""
        spam_patterns = self._load_spam_patterns()
        return "\n".join([
            line for line in code.splitlines()
            if not any(re.search(p, line, re.IGNORECASE) for p in spam_patterns)
        ])

    def looks_like_code(self, code: str) -> bool:
        """Check if the submission looks like valid code."""
        return any(re.search(sig, code, re.IGNORECASE) for sig in self.code_signals)

    def grade_code(self, student_code: str, task_description: str, deliverables: str, role: str) -> dict:
        """
        Grade student code using the configured LLM.
        Returns a dictionary with rating and feedback.
        """
        clean_code = self.remove_spam_lines(student_code)

        if not clean_code or not self.looks_like_code(clean_code):
            return {"rating": "0.0", "feedback": "Invalid or non-code submission."}

        # Prepare grading prompt
        prompt = self.grading_prompt_template \
            .replace("{task_description}", task_description) \
            .replace("{deliverables}", deliverables) \
            .replace("{code}", clean_code) \
            .replace("{role}", role)

        # Get LLM response
        response = LLMConnector.get_llm_response(
            prompt=prompt,
            model_name=self.model_name,
            llm_type=self.llm_type,
            host=self.host
        ).strip()

        # print(f"[DEBUG] LLM Grading Response: {response}")  # Optional debug

        # Try extracting rating from the response
        rating_val = self._extract_rating_from_response(response)

        if rating_val is None:
            return {"rating": "N/A", "feedback": "Unable to parse rating."}

        rating_str = f"{rating_val:.1f}"
        feedback = "Accepted" if rating_val > 2.0 else self.generate_feedback(clean_code)

        return {"rating": rating_str, "feedback": feedback}

    @staticmethod
    def _extract_rating_from_response(response: str) -> Optional[float]:  # or float | None for Python 3.10+
        """
        Extract a rating value from the LLM response.
        """
        match = re.search(r'Rating[:\-]?\s*([0-5](?:\.\d+)?)\s*/\s*5', response, re.IGNORECASE)
        if match:
            return float(match.group(1))

        # Try backup method
        numbers = re.findall(r'([0-5](?:\.\d+)?)\s*/\s*5', response)
        if numbers:
            return float(numbers[0])

        return None

    def generate_feedback(self, clean_code: str) -> str:
        """
        Generate feedback using the LLM if the rating is low.
        """
        prompt = self.feedback_prompt_template.replace("{code}", clean_code)
        response = LLMConnector.get_llm_response(
            prompt=prompt,
            model_name=self.model_name,
            llm_type=self.llm_type,
            host=self.host
        ).strip()

        # Remove tags like [Feedback] or [Response] from beginning
        response = re.sub(r'^\s*\[[^\]]+\]\s*', '', response)
        return response

