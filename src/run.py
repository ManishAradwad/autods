import openai
from manager import Manager
import os

if __name__ == "__main__":
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    prompt = "Generate a dataset for football"  # input(
    #     "Enter the prompt for the dataset you want to generate. Ex. Generate a dataset for QnA based on football:\n"
    # )
    resources_path = "resources"
    manager = Manager(resources_path, prompt)
    output_file, status = manager.generate_dataset()

    print(
        f"Dataset generated and saved to {output_file} and file deletion status is {status}"
    )
