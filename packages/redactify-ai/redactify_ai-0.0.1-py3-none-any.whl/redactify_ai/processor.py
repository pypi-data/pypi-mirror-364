import spacy
from pathlib import Path
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.nlp_engine import SpacyNlpEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from redactify_ai.custom_recognizers import CustomPhoneNumberRecognizer
from redactify_ai.download_model import ensure_model_downloaded
import pandas as pd


class PresidioDLPProcessor:
    def __init__(self, config):
        self.config = config["presidio"]
        self.entities = self.config["entities"]
        self.language = self.config.get("language", "en")
        self.score_threshold = self.config.get("score_threshold", 0.5)
        self.mask_char = self.config.get("mask_character", "*")

        # Retrieve the spaCy model name and directory from config
        self.spacy_model = self.config.get("spacy_model", "en_core_web_lg-3.8.0")
        self.spacy_model_dir = self.config.get("spacy_model_dir", "./models/spacy")

        # Ensure the model is downloaded/unpacked
        model_root = ensure_model_downloaded(self.spacy_model, self.spacy_model_dir)

        # Load the spaCy model explicitly from the directory
        spacy_model_path = Path(model_root)
        print(f"Loading spaCy model from: {spacy_model_path.resolve()}")

        try:
            spacy_model = spacy.util.load_model_from_path(spacy_model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load spaCy model from path {spacy_model_path}: {e}")

        # Configure SpacyNlpEngine with the loaded spaCy model
        nlp_engine = SpacyNlpEngine()
        nlp_engine.nlp = {"en": spacy_model}  # Explicitly assign the loaded spaCy model

        # Initialize RecognizerRegistry and load predefined recognizers
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers()

        # Add the custom recognizer
        custom_phone_recognizer = CustomPhoneNumberRecognizer()
        registry.add_recognizer(custom_phone_recognizer)


        # Initialize AnalyzerEngine & AnonymizerEngine with custom NLP engine and recognizers
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine, registry=registry)
        self.anonymizer = AnonymizerEngine()


    def anonymize_text(self, text: str) -> str:
        """
        Anonymize a single text input using Presidio.
        """
        if not isinstance(text, str) or not text.strip():
            return text

        try:
            # Analyze the text for sensitive entities
            results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=self.entities,
                score_threshold=self.score_threshold,
            )

            # Anonymize the detected entities
            return self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
            ).text

        except Exception as e:
            # Log and return the original text in case of failure
            print(f"Error during anonymization: {e}")
            return text

    def process_dataframe(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        # Apply anonymization to the specified column of the dataframe
        df = df.copy()

        def anonymize_text(text):
            if not isinstance(text, str):  # Skip if text is not a string
                return text

            # Analyze the input text for sensitive entities
            results = self.analyzer.analyze(
                text=text,
                language=self.language,
                entities=self.entities,
                score_threshold=self.score_threshold,
            )

            # Anonymize detected entities
            return self.anonymizer.anonymize(
                text=text,
                analyzer_results=results,
                #operators={"DEFAULT": OperatorConfig("mask", {"masking_char": self.mask_char})}
            ).text

        # Apply anonymization to the column
        df[f"{column}_redacted"] = df[column].apply(anonymize_text)
        return df