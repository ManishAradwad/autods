from utils import BaseAssistant
import openai
import os

openai.api_key = os.environ.get("OPENAI_API_KEY")


class Answerer(BaseAssistant):
    def __init__(self, resources_path):
        super().__init__(resources_path)
        self.answerer_assistant = self.client.beta.assistants.create(
            name="Answerer",
            instructions="You are an Answerer. Your job is to refer to the input resources and provide answers to the corresponding questions. You can use the retrieval to help you with this task. The response provided should be a list of answer. Do Not Add questions to the output. Only provide the answers.",
            tools=[{"type": "retrieval"}],
            model="gpt-3.5-turbo-1106",
            file_ids=self.file_ids,
        )

    def generate_answers(self, questions):
        thread = self.client.beta.threads.create()
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"I want to generate answers for the given questions in the below list: {questions}. Refer to the resources provided using Retrieval to generate the answers. The response provided should be a list of answer. Do Not Add questions to the output. Only provide the answers.",  # the prompt might need some work
        )
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=self.answerer_assistant.id,
        )
        # this will need some formatting to make it work
        answers = self.client.beta.threads.messages.list(thread_id=thread.id)
        return answers
