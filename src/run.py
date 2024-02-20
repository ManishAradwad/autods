import openai
from manager import Manager
import os

if __name__ == "__main__":
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    prompt = "Generate a dataset for football"  # input(
    #     "Enter the prompt for the dataset you want to generate. Ex. Generate a dataset for QnA based on football:\n"
    # )
    resources_path = "resources"
    output_path = "output"
    manager = Manager(
        resources_path,
        output_path,
        prompt,
        local_url="http://localhost:8080/v1/",
        model="phi-2.Q2_k",
    )
    output_file = manager.generate_dataset()

    print(f"Dataset generated and saved to {output_file}")
