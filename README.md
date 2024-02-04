# Automated Tool for Creating Datasets

This project contains an automated tool for creating datasets for fine-tuning Language Learning Models (LLMs). The tool is inspired by AutoGPT and uses the OpenAI API to generate a Question-Answer dataset on a specific topic provided by the user. You can add files (pdf only for now) in the `resources` folder. These files will be used for dataset creation using Retrieval Augmented Generation.

NOTE: (According to OpenAI)[https://platform.openai.com/docs/assistants/how-it-works/creating-assistants],

> You can attach a maximum of 20 files per Assistant, and they can be at most 512 MB each. The size of all the files uploaded by your organization should not exceed 100 GB. You can request an increase in this storage limit using our help center. In addition to the 512 MB file size limit, each file can only contain 2,000,000 tokens. Assistant or Message creation will fail if any attached files exceed the token limit.

Please keep this in mind while adding the files

## Project Structure

The project is structured as follows:

- `src/questioner.py`: Contains the `Questioner` class for generating questions related to a given topic.
- `src/answerer.py`: Contains the `Answerer` class for generating answers to the provided questions.
- `src/manager.py`: Contains the `Manager` class for coordinating the `Questioner` and `Answerer` classes and validating the generated answers.
- `src/utils.py`: Contains utility functions used by the `Questioner`, `Answerer`, and `Manager` classes.
- `tests`: Contains unit tests.
- `resources`: Directory for storing the text resources provided by the user.

## Setup

1. Clone the repository.
2. Install the required Python dependencies listed in `requirements.txt`.
3. Place your text resources in the `resources` directory.

## Usage

1. Import the `Manager` class from `src/manager.py`.
2. Create an instance of the `Manager` class.
3. Call the `generate_dataset` method with your topic and resources as arguments. The method will return a .jsonl file with the generated dataset.

## Testing

To run the unit tests, navigate to the `tests` directory and run the following command:

```bash
python -m unittest
```

## Contributing

Contributions are welcome. Please submit a pull request with your changes.

## License

This project is licensed under the MIT License.