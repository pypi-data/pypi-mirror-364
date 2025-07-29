import torch.distributed as dist
import os
import argparse
import torch
from datetime import datetime


def create_gpu_groups(num_nodes, gpus_per_node):
    """
    Creates process groups for GPUs with the same index across all nodes.

    This function creates distinct groups of GPUs that share the same index across different nodes. 
    This is useful when you want to divide your distributed training process into smaller groups 
    that each work on the same GPU index across nodes, ensuring efficient communication.

    Args:
        num_nodes (int): Number of nodes in the distributed setup.
        gpus_per_node (int): Number of GPUs available on each node.

    Returns:
        List: A list of process groups for each unique GPU index.
    """
    world_size = num_nodes * gpus_per_node
    rank = dist.get_rank()  # Get the rank of the current process
    groups = []

    for gpu_idx in range(gpus_per_node):
        # Collect ranks corresponding to the same GPU index across nodes
        ranks = [node * gpus_per_node + gpu_idx for node in range(num_nodes)]
        # Create a new process group for this set of ranks
        group = dist.new_group(ranks=ranks)
        groups.append(group)

    return groups




def str2bool(v):
    """
    Converts a string representation of a boolean value to a boolean.

    Args:
        v (str): A string to be converted to a boolean value.

    Returns:
        bool: The corresponding boolean value.
    
    Raises:
        argparse.ArgumentTypeError: If the string doesn't match any recognized boolean value.
    """
    if isinstance(v, bool):
        return v
    if v.lower() in ("True", "true", "t", "1"):
        return True
    elif v.lower() in ("False", "false", "f", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def lprint(log: str) -> None:
    """
    Prints a log message only from the process with rank 0 in a distributed setup.

    This function ensures that only the main process (rank 0) prints logs to the console,
    avoiding cluttering the output with redundant log messages from other processes.

    Args:
        log (str): The log message to print.
    """
    if torch.distributed.get_rank() == 0:
        print(log)


def tokenize_function(tokenizer, data):
    """
    Tokenizes the input data using the provided tokenizer.

    This function takes raw input data and uses the provided tokenizer to tokenize the text,
    padding and truncating to a fixed length of 12 tokens.

    Args:
        tokenizer (transformers.PreTrainedTokenizer): The tokenizer to use for tokenization.
        data (dict): A dictionary containing the text to tokenize.

    Returns:
        dict: A dictionary containing the tokenized inputs.
    """
    return tokenizer(data["text"], padding="max_length", truncation=True, max_length=12)


def collate(elements):
    """
    Pads and collates a list of tokenized inputs into a batch.

    This function takes a list of tokenized elements (e.g., input_ids), pads them to the same length
    (based on the longest tokenized input), and creates a batch containing input_ids, labels, and attention masks.

    Args:
        elements (list): A list of tokenized elements to collate.

    Returns:
        dict: A dictionary containing the batched input_ids, labels, and attention_mask tensors.
    """
    tokenlist = [e["input_ids"] for e in elements]
    tokens_maxlen = max([len(t) for t in tokenlist])  # Length of the longest input

    input_ids, labels, attention_masks = [], [], []
    for tokens in tokenlist:
        # How many pad tokens to add for this sample
        pad_len = tokens_maxlen - len(tokens)

        # Pad input_ids with pad_token, labels with ignore_index (-100), and set attention_mask to 1 where content, otherwise 0
        input_ids.append(tokens + [tokenizer.pad_token_id] * pad_len)
        labels.append(tokens + [-100] * pad_len)
        attention_masks.append([1] * len(tokens) + [0] * pad_len)

    batch = {
        "input_ids": torch.tensor(input_ids),
        "labels": torch.tensor(labels),
        "attention_mask": torch.tensor(attention_masks)
    }
    return batch


def save_dataset(dataset_name, dir_name, n_files=10):
    """
    Downloads and saves a dataset to disk.

    This function loads the specified dataset from HuggingFace, saves it to the provided directory,
    and splits the dataset into multiple parts if needed.

    Args:
        dataset_name (str): The name of the dataset to download.
        dir_name (str): The directory to save the dataset to.
        n_files (int): The number of files to save from the dataset (default is 10).
    """
    from datasets import load_dataset
    import datasets
    datasets.builder.has_sufficient_disk_space = lambda needed_bytes, directory='.': True
    cache_dir = dir_name
    for i in range(n_files):
        dataset = load_dataset(dataset_name, data_files={'train': f'en/c4-train.0000{i}-of-01024.json.gz'}, split='train', cache_dir=cache_dir)
        dataset.save_to_disk(dir_name)


def save_model(model_name, tokenizer_name, local_dir="."):
    """
    Downloads and saves a pre-trained model and tokenizer to a local directory.

    This function downloads a specified model and its tokenizer from HuggingFace's hub, 
    and saves them locally in the specified directory.

    Args:
        model_name (str): The name of the model to download.
        tokenizer_name (str): The name of the tokenizer to download.
        local_dir (str): The local directory to save the model and tokenizer (default is the current directory).
    """
    from huggingface_hub import snapshot_download
    from transformers import AutoTokenizer

    snapshot_download(repo_id=model_name, allow_patterns="*.safetensors", cache_dir=model_name)
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, cache_dir=tokenizer_name)
    tokenizer.save_pretrained(local_dir)

