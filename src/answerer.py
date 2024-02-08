from utils import BaseAssistant
import openai
import os
import time


class Answerer(BaseAssistant):
    def __init__(self, resources_path, model):
        super().__init__(resources_path, model)
        self.answerer_assistant = self.client.beta.assistants.create(
            name="Answerer",
            instructions="You are an Answerer. Your job is to refer to the input resources and provide answers to the corresponding questions. You can use the retrieval to help you with this task. The response provided should be a list of answer. Do Not Add questions to the output. Only provide the answers.",
            tools=[{"type": "retrieval"}],
            model=self.model,
            file_ids=BaseAssistant.file_ids,
        )

    def generate_answers(self, questions, count, multiplier):

        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f" Generate answers for the input `questions` which contains a list of questions. The output should be just a list of answers and nothing else. For ex. ['What is the capital of Spain?'] is an example of the output.",
                }
            ]
        )
        # triggering the first run
        run = self.trigger_run(thread.id, self.answerer_assistant.id)
        # this `messages` will contain only the above prompt
        answers = []
        while len(answers) < count * multiplier:
            # checking if the current run to add a question has completed
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                time.sleep(1)
                print("Answering a question...")

            # getting the latest messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # adding the answer to the list
            answers.append(messages.data[0].content[0].text.value)

            # logging
            print("New answer added! Total answers:", len(answers))
            _ = self.client.beta.threads.messages.create(
                thread.id,
                role="user",
                content="Please generate a new answer. Make sure new answer is not similar to the earlier generated answers.",
            )
            # triggering the next run to add a new answer
            run = self.trigger_run(thread.id, self.answerer_assistant.id)

        # deleting the answerer assistant
        deletion_status = self.client.beta.assistants.delete(
            assistant_id=self.answerer_assistant.id
        )

        return answers, deletion_status
