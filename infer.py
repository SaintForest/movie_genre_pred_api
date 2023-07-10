import argparse
import torch
import os.path
import requests
import os
from transformers import BertTokenizer
from transformers import AdamW
from transformers import BertForSequenceClassification
from transformers import logging
import numpy as np
import torch
import re

logging.set_verbosity_error()

# Load BERT model from Huggingface library, and load the trained weights.
def load_model():
    if not os.path.exists("model-new.pt"):
        url = "https://www.googleapis.com/drive/v3/files/1lMMBOpV00Bgb5dNPv6YNXV1raqq-6e19?alt=media&key=AIzaSyAv78uOOaUaNf6DWT59VUhZX7ZqnZDsY8k"
        new_filename = "model-new.pt"

        print("File is not present, It's a 400 MB file, can take up to a minute, downloading...")
        response = requests.get(url)
        if response.status_code == 200:
            with open(new_filename, "wb") as file:
                file.write(response.content)
            print("File is downloaded and saved as", new_filename)
        else:
            print("Failed to download the file")
            return None
    
    model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=20)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    try:
        model.load_state_dict(torch.load("model-new.pt", map_location=device))
    except Exception as e:
        print("Failed to load the model:", str(e))
        return None
    
    model.eval()
    return model

def main(model, argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--description")

    args = vars(parser.parse_args(argv))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    tokenizer = BertTokenizer.from_pretrained("bert-base-uncased", do_lower_case=True)
    
    description = args["description"]

    if len(description) < 10:
        raise ValueError("Invalid description length. Description should be at least 10 characters.")
    if len(description) > 1000:
        raise ValueError("Invalid description length. Description should be at max 1000 characters.")
    if re.search(r"[^a-zA-Z0-9\s]", description):
        raise ValueError("Invalid description. Special characters are not allowed.")

    if model is None:
        raise ValueError("Invalid model. Model might not be loaded or is not provided")

    def test_main_invalid_model(self):
        model = None
        description = "This is a movie description"
        genres = main(model, [f"--description={description}"])
        self.assertIsNone(genres, "Inference should fail when model is not loaded")



    try:
        encoded = tokenizer.encode_plus(args["description"], padding=True)
    except Exception as e:
        print("Failed to encode the input:", str(e))
        return None
    
    seed_ids = encoded["input_ids"]
    seed_token_type_ids = encoded["token_type_ids"]
    seed_masks = encoded["attention_mask"]

    inp = torch.tensor(seed_ids)
    msk = torch.tensor(seed_masks)
    tok = torch.tensor(seed_token_type_ids)

    inp = inp.unsqueeze(0)
    msk = msk.unsqueeze(0)

    inp = inp.to(device)
    msk = msk.to(device)

    try:
        ot = model(inp, token_type_ids=None, attention_mask=msk)
    except Exception as e:
        print("Failed to perform forward pass:", str(e))
        return None

    b_logit_pred = ot[0]
    pred_label = torch.sigmoid(b_logit_pred)
    pred_bools = [pl > 0.50 for pl in pred_label]

    ar = pred_bools[0].cpu().detach().numpy()

    label_cols = [
        "Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy",
        "Foreign", "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "TV Movie",
        "Thriller", "War", "Western"
    ]
    label_cols = np.array(label_cols)
    t = np.array(np.where(ar)[0])
    genres = label_cols[t]

    return list(genres)

if __name__ == "__main__":
    model = load_model()
    
    if model is not None:
        main(model)
