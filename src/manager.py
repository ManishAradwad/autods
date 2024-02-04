from questioner import Questioner
from answerer import Answerer
from utils import BaseAssistant
import jsonlines
import openai
import os


class Manager(BaseAssistant):
    def __init__(self, resources_path, prompt):
        super().__init__(resources_path)
        self.questioner = Questioner(self.resources_path)
        self.answerer = Answerer(self.resources_path)
        self.topic = self.extract_topic(prompt)
        self.manager_assistant = self.client.beta.assistants.create(
            name="Manager",
            instructions="You are a Manager who oversees the creation of a dataset based on the {self.topic}. You are given a list of question-answer pairs. Your job is to refer to the input resources and verify whether the answers are correct for the correspoding questions. You can use the retrieval to help you with this task. The response provided should be a list of 0 and 1 values. The value should be 1 if it's a valid question-answer pair and 0 if it's not. The response should be in the same order as the input questions. For instance, if the input question is 'What is the capital of France?' and the answer is 'Paris', the response should be '1'. If the input question is 'What is the capital of France?' and the answer is 'Spain', the response should be '0'.",
            tools=[{"type": "retrieval"}],
            model="gpt-3.5-turbo-1106",
            file_ids=BaseAssistant.file_ids,
        )

    def extract_topic(self, prompt):
        completion = self.client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that helps people extract the main topic from a given prompt. In the response, please provide only the name of the topic and nothing else. For instance if the prompt is: 'Generate a dataset for QnA based on football', The main topic is: Football.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
        )

        topic = completion.choices[0].message
        return topic.content

    def generate_dataset(self, count=1, multiplier=10):
        print("The topic extracted from the given prompt is:", self.topic)
        questions = self.questioner.generate_questions(self.topic)
        answers = self.answerer.generate_answers(questions)
        validated_questions, validated_answers = self.validate_answers(
            questions, answers
        )
        # this formatting will also need to be changed. also decide whether to use `context` while generating qna row
        dataset = [
            {"text": f"\\nQ:{q}\\nA:{a}"}
            for q, a in zip(validated_questions, validated_answers)
        ]
        type_ds = "train.jsonl"
        with jsonlines.open(type_ds, mode="w") as writer:
            writer.write_all(dataset)

        file_deletion_status = self.client.beta.assistants.files.delete(
            assistant_id=self.manager_assistant.id, file_id=BaseAssistant.file_ids
        )
        return type_ds, file_deletion_status

    def validate_answers(self, questions, answers):
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"I want to validate this set of question-answer pairs: Questions-{questions}\nAnswers-{answers}. Refer to the resources provided using Retrieval to validate a pair.",  # the prompt might need some work
        )
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.manager_assistant.id,
        )
        # this will need some formatting to make it work
        result = self.client.beta.threads.messages.list(thread_id=thread.id)

        # Assuming result, questions, and answers are lists of the same length
        filtered_questions = [q for q, r in zip(questions, result) if r == 1]
        filtered_answers = [a for a, r in zip(answers, result) if r == 1]
        return filtered_questions, filtered_answers
