from questioner import Questioner
from answerer import Answerer
from utils import BaseAssistant, save_dataset
import time
import random
from tqdm import tqdm
import os


class Manager(BaseAssistant):
    def __init__(self, resources_path, output_path, prompt, model="gpt-3.5-turbo-1106"):
        super().__init__(resources_path, output_path, model)
        # in future can provide functionaluty to let user decide the model specific to both q and a
        self.questioner = Questioner(self.resources_path, self.output_path, self.model)
        self.answerer = Answerer(self.resources_path, self.output_path, self.model)
        self.topic = self.extract_topic(prompt)
        self.validater_assistant = self.client.beta.assistants.create(
            name="Manager",
            instructions=f"You are a Manager who oversees the creation of a dataset based on the {self.topic}. You are given a question-answer pair. Your job is to refer to the input resources and verify whether the answer is correct for the correspoding question. You can use the retrieval to help you with this task. The response provided should be a 0 or 1 values. The value should be 1 if the provided `answer` answers the given `question` and 0 if it does not. For instance, if the input question is 'What is the capital of France?' and the answer is 'Paris', the response should be '1'. If the input question is 'What is the capital of France?' and the answer is 'Spain', the response should be '0'.",
            tools=[{"type": "retrieval"}],
            model=self.model,
            file_ids=BaseAssistant.file_ids,
        )

    def extract_topic(self, prompt):
        completion = self.client.chat.completions.create(
            model=self.model,
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

    def generate_dataset(self, type_ds="train.jsonl", count=1, multiplier=5):
        print("The topic extracted from the given prompt is:", self.topic)
        questions, _ = self.questioner.generate_questions(self.topic, count, multiplier)
        answers, _ = self.answerer.generate_answers(questions)
        validated_questions, validated_answers = self.validate_answers(
            questions, answers
        )
        dataset = [
            {"text": f"\\nQ:{q}\\nA:{a}"}
            for q, a in zip(validated_questions, validated_answers)
        ]
        save_dataset(dataset, os.path.join(self.output_path, type_ds))

        return type_ds

    def validate_answers(self, questions, answers):
        # randomise the order of questions and answers list but the order should be same for both
        paired = list(zip(questions, answers))
        random.shuffle(paired)
        questions, answers = zip(*paired)

        thread = self.client.beta.threads.create(
            messages=[
                {
                    "role": "user",
                    "content": f"I want to validate this question-answer pair: Question-{questions[0]}\nAnswer-{answers[0]}. Remember the output should just be either 0 or 1 value and nothing else. For ex. 1 is an example of the output.",
                }
            ]
        )
        # triggering the first run
        run = self.trigger_run(thread.id, self.validater_assistant.id)
        # this `messages` will contain only the above prompt
        result = []

        print("Validating questions...")
        for question, answer in tqdm(zip(questions[1:], answers[1:])):
            # checking if the current run to add a question has completed
            while run.status != "completed":
                run = self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id, run_id=run.id
                )
                time.sleep(1)
                # print("Validating a QnA pair...")

            # getting the latest messages from the thread
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)

            # adding the question to the list
            result.append(messages.data[0].content[0].text.value)

            # logging
            # print("New question verified! Total verified:", len(questions))
            _ = self.client.beta.threads.messages.create(
                thread.id,
                role="user",
                content=f"Please verify this next question-answer pair:\nQuestion-{question}\nAnswer-{answer}\nRemember the output should just be either 0 or 1 value and nothing else. For ex. 1 is an example of the output.",
            )
            # triggering the next run to add a new question
            run = self.trigger_run(thread.id, self.validater_assistant.id)

        # deleting the questioner assistant
        deletion_status = self.client.beta.assistants.delete(
            assistant_id=self.validater_assistant.id
        )

        # deleting the files
        for file_id in BaseAssistant.file_ids:
            self.client.files.delete(file_id)
        print("Files deleted successfully")

        return result, deletion_status
