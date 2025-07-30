from pathlib import Path
from typing import Optional, Sequence, Generator, Iterable

from classconfig import ConfigurableValue, ConfigurableFactory, ConfigurableSubclassFactory
import torch
from tqdm import tqdm
from transformers import AutoTokenizer

from sofairfilter.model_factory import SequenceClassificationModelFactory
from sofairfilter.tokenizer_factory import TokenizerFactory


class Filter:
    """
    A class that identifies candidate documents for software mention extraction.
    """

    model_factory: SequenceClassificationModelFactory = ConfigurableFactory(SequenceClassificationModelFactory, "Model configuration.")
    tokenizer_factory: Optional[TokenizerFactory] = ConfigurableSubclassFactory(TokenizerFactory,
                                                                            desc="Hugging Face tokenizer for the model. Leave empty if you wish to initialize it from the model.",
                                                                            name="tokenizer",
                                                                            voluntary=True)
    threshold: Optional[float] = ConfigurableValue(
        "The threshold for the model's confidence probability. Documents with a probability below this threshold will be filtered out. By default, no threshold is applied and a class with the highest probability is selected.",
        user_default=None,
        voluntary=True
    )
    batch_size: int = ConfigurableValue("Batch size for processing documents.", user_default=8)

    def __init__(self, model_factory: SequenceClassificationModelFactory, tokenizer_factory: Optional[TokenizerFactory] = None, threshold: Optional[float] = None, batch_size: int = 32):
        """
        Initializes the filter with a model and an optional threshold.
        """
        self.model_factory = model_factory
        self.tokenizer_factory = tokenizer_factory

        self.threshold = threshold
        self.batch_size = batch_size

        self.model = model_factory.create()


        self.tokenizer = AutoTokenizer.from_pretrained(self.model_factory.model_path, use_fast=True,
                                                       cache_dir=self.model_factory.cache_dir) \
            if self.tokenizer_factory is None else self.tokenizer_factory.create()

    @torch.no_grad()
    def filter_single_batch(self, documents: Sequence[str]) -> list[int]:
        """
        Filters the documents based on the model's predictions.

        :param documents: A sequence of documents to be filtered.
        :return: A list of indices of documents that are considered candidates for software mention extraction.
        """
        inputs = self.tokenizer(documents, return_tensors="pt", padding=True, truncation=True)

        if self.model_factory.device is not None:
            inputs = {k: v.to(self.model_factory.device) for k, v in inputs.items()}

        outputs = self.model(**inputs)

        if self.threshold is None:
            # Select the class with the highest probability
            selected_indices = outputs.logits.argmax(dim=-1).nonzero().flatten().tolist()
        else:
            probabilities = outputs.logits.softmax(dim=-1)
            selected_indices = (probabilities[:, 1] >= self.threshold).nonzero().flatten().tolist()

        return selected_indices

    @staticmethod
    def load_batch(document_paths: Sequence[str | Path]) -> list[str]:
        """
        Loads a batch of documents from the given paths.

        :param document_paths: A sequence of paths to documents.
        :return: A list of document contents.
        """
        batch = []
        for path in document_paths:
            with open(path, 'r', encoding='utf-8') as file:
                batch.append(file.read())
        return batch

    def filter(self, document_paths: Iterable[str | Path]) -> Generator[str | Path, None, None]:
        """
        Filters the documents based on the model's predictions.

        :param document_paths: A sequence of paths to documents to be filtered.
        :return: A list of paths of documents that are considered candidates for software mentions extraction.
        """
        batch_files = []

        for i, p in enumerate(tqdm(document_paths, desc="Filtering documents", unit="document")):
            batch_files.append(p)

            if (i + 1) % self.batch_size == 0:
                batch = self.load_batch(batch_files)
                res = self.filter_single_batch(batch)
                for idx in res:
                    yield batch_files[idx]

                batch_files = []




