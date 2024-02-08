from utils import BaseAssistant, save_dataset
import os
import time
from tqdm import tqdm


class Answerer(BaseAssistant):
    def __init__(self, resources_path, output_path, model):
        super().__init__(resources_path, output_path, model)
        self.answerer_assistant = self.client.beta.assistants.create(
            name="Answerer",
            instructions="You are an Answerer. Your job is to refer to the provided resources and answer the input question. You can use the retrieval to help you with this task. The response provided should be an answer. DO NOT ADD QUESTIONS IN THE RESPONSE. Only provide the answer to the given question. For ex. If 'What is the capital of Spain?' is the input question then 'The capital of Spain is Madrid' should be the output.",
            tools=[{"type": "retrieval"}],
            model=self.model,
            file_ids=BaseAssistant.file_ids,
        )

    def generate_answers(self, questions):
        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f" Answer the question {questions[0]}. The output should be just an answer and nothing else.",
                }
            ]
        )
        # triggering the first run
        run = self.trigger_run(thread.id, self.answerer_assistant.id)
        # this `messages` will contain only the above prompt
        answers = []

        print("Answering questions...")
        for question in tqdm(questions[1:]):
            # checking if the current run to add a question has completed
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                time.sleep(1)
                # print("Answering a question...")

            # getting the latest messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # adding the answer to the list
            answers.append(messages.data[0].content[0].text.value)

            # logging
            # print("New answer added! Total answers:", len(answers))
            _ = self.client.beta.threads.messages.create(
                thread.id,
                role="user",
                content=f"Answer the question {question}. The output should be just an answer and nothing else.",
            )
            # triggering the next run to add a new answer
            run = self.trigger_run(thread.id, self.answerer_assistant.id)

        # deleting the answerer assistant
        deletion_status = self.client.beta.assistants.delete(
            assistant_id=self.answerer_assistant.id
        )

        save_dataset(answers, os.path.join(self.output_path, "answers.jsonl"))

        return answers, deletion_status
