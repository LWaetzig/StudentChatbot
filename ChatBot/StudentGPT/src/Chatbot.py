from transformers import BartTokenizer, BartForConditionalGeneration
# from kaggle.api.kaggle_api_extended import KaggleApi
import os
import logging

# # Set your Kaggle API key
# api_key = "009144790236b6dde63b464d116e4561"
# os.environ["KAGGLE_USERNAME"] = "skillinho"
# os.environ["KAGGLE_KEY"] = api_key

# # Specify the Kaggle dataset path
# kaggle_dataset_path = "skillinho/nlp-finetuning-bart"

# # Download the Kaggle dataset
# api = KaggleApi()
# # api.authenticate(api_key)
# api.dataset_download_files(kaggle_dataset_path, unzip=True)

def get_bot_response(message):
    # Load tokenizer and model
    model_path = "bart-samsum-model/bart_samsum_model"  # Update with your model path after extraction
    tokenizer = BartTokenizer.from_pretrained(model_path)
    model = BartForConditionalGeneration.from_pretrained(model_path)

    prompt = message
    # Tokenize and generate response
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    output_ids = model.generate(input_ids)
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    # Log the generated response
    logging.info("Generated Response: %s", output_text)

    # Return the generated response
    return output_text