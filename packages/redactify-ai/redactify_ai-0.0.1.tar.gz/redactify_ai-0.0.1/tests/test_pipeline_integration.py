import os
import unittest
from pyspark.sql import SparkSession
from redactify_ai.config import load_config
from redactify_ai.processor import PresidioDLPProcessor
from redactify_ai.utils import anonymize_text_udf

class TestPipelineIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Assumes Spark and SpaCy model are installed and accessible in the Docker container
        os.environ["PYSPARK_PYTHON"] = "python"
        os.environ["PYSPARK_DRIVER_PYTHON"] = "python"
        cls.spark = SparkSession.builder.master("local[1]").appName("PresidioDLP-Integration").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_redaction_pipeline(self):
        # Load pipeline config
        config = load_config("tests/test_config.yaml")  # ensures entities like EMAIL_ADDRESS and PERSON

        # Create processor
        processor = PresidioDLPProcessor(config)

        # Create sample data
        data = [
            ("Hi, I'm John Doe and my email is john.doe@gmail.com.",),
        ]
        df = self.spark.createDataFrame(data, ["transcripts"])

        # Define the UDF for anonymization
        anonymize_udf = anonymize_text_udf(processor)

        # Apply UDF to DataFrame
        df_redacted = df.withColumn("transcripts_redacted", anonymize_udf(df["transcripts"]))
        result = df_redacted.collect()

        # Extract and test result
        redacted_text = result[0]["transcripts_redacted"]
        # You may need to adjust the expected output depending on mask_character/config.yaml
        self.assertNotIn("John Doe", redacted_text)
        self.assertNotIn("john.doe@gmail.com", redacted_text)
        # self.assertIn("*", redacted_text) # Default mask character
        print("Redacted output:", redacted_text)

if __name__ == "__main__":
    unittest.main()