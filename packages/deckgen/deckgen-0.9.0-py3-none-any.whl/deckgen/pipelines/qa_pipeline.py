from deckgen.generation.openai_client import OpenAIClient
from deckgen.templates import TOPIC_FINDER
from deckgen.templates import QUESTION_ASKING
from typing import Optional
from typing import List
from typing import Dict
import json
import re


class QAParser:

    def __init__(self, text: Optional[str]) -> None:
        """
        Initializes the QAParser with the provided text.

        :param text: The text to be parsed for questions and answers.
        """
        self.text = text

    def parse(self, text: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Parses the provided text to extract questions and answers.

        :param text: Optional text to parse. If not provided, uses the text initialized in the constructor.
        :return: A list of dictionaries containing questions and their corresponding answers.
        :raises ValueError: If no text is provided for parsing.
        :raises ValueError: If no valid question-answer pairs are found in the text.
        """
        if text is not None:
            self.text = text

        if not self.text:
            raise ValueError("No text provided for parsing.")

        # Regex pattern to match question-answer pairs (question ends with '?', answer follows)
        pattern = r"(?P<question>.*?\?)\s+(?P<answer>.*?)(?=\n\d+\.|\Z)"

        matches = re.finditer(pattern, self.text, re.DOTALL)
        qa_list = [
            {
                "question": m.group("question").strip(),
                "answer": m.group("answer").strip(),
            }
            for m in matches
        ]

        # Remove leading index (e.g., "1. ", "2. ") from each question in qa_list
        for qa in qa_list:
            qa["question"] = (
                qa["question"].lstrip().split(" ", 1)[-1]
                if qa["question"].lstrip()[0].isdigit() and "." in qa["question"]
                else qa["question"]
            )
            qa["answer"] = qa["answer"].strip()
        # Ensure that each question and answer is stripped of leading/trailing whitespace
        qa_list = [
            {"question": qa["question"].strip(), "answer": qa["answer"].strip()}
            for qa in qa_list
        ]
        # Ensure that the list is not empty
        if not qa_list:
            raise ValueError("No valid question-answer pairs found in the text.")
        return qa_list


class QAToolKit:
    def __init__(
        self, input_text: Optional[str] = None, openai_api_key: Optional[str] = None
    ):
        self.input_text = input_text
        self.openai_client = OpenAIClient(api_key=openai_api_key)

    def _get_topics(self, text: Optional[str] = None) -> str:
        """
        Extracts topics from the input text.
        This is a placeholder for topic extraction logic.
        """
        if text is not None:
            self.input_text = text

        if not self.input_text:
            raise ValueError("No text provided for topic extraction.")

        topic_response = self.openai_client.request(
            method="POST",
            endpoint="responses",
            data=json.dumps(
                {
                    "model": "gpt-3.5-turbo",
                    "input": TOPIC_FINDER.replace("{{", "{")
                    .replace("}}", "}")
                    .format(text=self.input_text),
                }
            ),
        )

        if topic_response.status_code != 200:
            raise ValueError(f"Failed to extract topics: {topic_response.text}")

        topics = topic_response.json()["output"][0]["content"][0]["text"]
        return topics

    def _generage_qa_string(self, topics: str) -> str:
        """
        Generates a question-answer string based on the input text and identified topics.
        :param topics: A string containing the identified topics.
        """
        qa_response = self.openai_client.request(
            method="POST",
            endpoint="responses",
            data=json.dumps(
                {
                    "model": "gpt-4o-mini",
                    "input": QUESTION_ASKING.replace("{{", "{")
                    .replace("}}", "}")
                    .format(expertise=topics, text=self.input_text),
                }
            ),
        )

        qa_string = qa_response.json()["output"][0]["content"][0]["text"]
        return qa_string

    def generate_qa(self) -> List[Dict[str, str]]:
        """
        Generates a list of questions and answers based on the input text.
        :return: A list of dictionaries containing questions and their corresponding answers.
        """
        if not self.input_text:
            raise ValueError("No input text provided for question generation.")

        topics = self._get_topics(self.input_text)
        qa_string = self._generage_qa_string(topics)

        parser = QAParser(qa_string)
        qa_list = parser.parse()
        return qa_list
