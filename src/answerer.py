from utils import BaseAssistant, save_dataset
import os
from tqdm import tqdm


class Answerer(BaseAssistant):
    def __init__(self, resources_path, output_path, local_url, model):
        super().__init__(resources_path, output_path, local_url, model)
        if self.local_url:
            self.answerer_assistant = None
        else:
            self.answerer_assistant = self.client.beta.assistants.create(
                name="Answerer",
                instructions="You are an Answerer. Your job is to refer to the provided resources and answer the input question. You can use the retrieval to help you with this task. The response provided should be an answer. DO NOT ADD QUESTIONS IN THE RESPONSE. Only provide the answer to the given question. For ex. If 'What is the capital of Spain?' is the input question then 'The capital of Spain is Madrid' should be the output.",
                tools=[{"type": "retrieval"}],
                model=self.model,
                file_ids=BaseAssistant.file_ids,
            )

    def generate_answers(self, questions):
        answers = []
        if self.answerer_assistant is None:
            for question in questions:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an Answerer. Your job is to refer to the provided resources and answer the input question. You can use the retrieval to help you with this task. The response provided should be an answer. DO NOT ADD QUESTIONS IN THE RESPONSE. Only provide the answer to the given question. For ex. If 'What is the capital of Spain?' is the input question then 'The capital of Spain is Madrid' should be the output.",
                        },
                        {
                            "role": "user",
                            "content": f" Answer the question {question}. The output should be just an answer and nothing else.",
                        },
                    ],
                )
                answers.append(response.choices[0].message.content)
        else:
            thread = None
            print("Answering questions...")
            for question in tqdm(questions):
                if not thread:
                    thread = self.client.beta.threads.create(
                        messages=[
                            {
                                "role": "user",
                                "content": f" Answer the question {question}. The output should be just an answer and nothing else.",
                            }
                        ]
                    )
                    # triggering the first run
                    run = self.trigger_run(thread.id, self.answerer_assistant.id)
                else:
                    answers = self.update_list(run, self.client, thread.id, answers)

                    # logging
                    # print("New answer added! Total answers:", len(answers))
                    _ = self.client.beta.threads.messages.create(
                        thread.id,
                        role="user",
                        content=f'Answer the question "{question}". The output should be just an answer and nothing else.',
                    )
                    # triggering the next run to add a new answer
                    run = self.trigger_run(thread.id, self.answerer_assistant.id)

            answers = self.update_list(
                run, self.client, thread.id, answers
            )  # to update the last answer after the loop ends

        # deleting the answerer assistant
        deletion_status = (
            self.client.beta.assistants.delete(assistant_id=self.answerer_assistant.id)
            if self.answerer_assistant
            else "No assistant used"
        )

        save_dataset(answers, os.path.join(self.output_path, "answers.jsonl"))
        print("Answers generated and saved to answers.jsonl\n")

        return answers, deletion_status
