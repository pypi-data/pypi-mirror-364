import datasets
from tw_textforge.config.settings import setting

def streaming_load_dataset(name:str):
    return datasets.load_dataset(name, split="train", streaming=True, token=setting.hf_token)