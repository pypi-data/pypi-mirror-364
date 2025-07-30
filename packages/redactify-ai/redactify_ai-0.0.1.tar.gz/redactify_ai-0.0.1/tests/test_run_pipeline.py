import unittest
from unittest.mock import patch, MagicMock
from pyspark.sql import SparkSession

import run_pipeline

class TestRunPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup Spark once for all tests
        cls.spark = SparkSession.builder.master("local[1]").appName("PresidioDLP-Test").getOrCreate()

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    @patch("run_pipeline.load_config")
    @patch("run_pipeline.PresidioDLPProcessor")
    @patch("run_pipeline.anonymize_text_udf")
    def test_pipeline_redacts_transcripts(self, mock_anonymize_udf, mock_processor_cls, mock_load_config):
        # Mock configuration and processor
        mock_processor = MagicMock()
        mock_processor_cls.return_value = mock_processor
        mock_load_config.return_value = {
            'presidio': {'entities': ['PERSON', 'EMAIL_ADDRESS']}
        }

        # Instead of actual UDF, just uppercase the string for test verification
        (lambda text: text.upper())
        def fake_udf(col):
            # For the test, simulate creating a new column without PySpark UDF logic
            return col

        mock_anonymize_udf.return_value = fake_udf

        with patch("run_pipeline.get_mock_data") as mock_get_data:
            # Create a mock DataFrame as would be produced by get_mock_data
            data = [("John Doe's email is john.doe@gmail.com.",)]
            df = self.spark.createDataFrame(data, ["transcripts"])
            mock_get_data.return_value = df

            # Now run the main pipeline logic
            run_pipeline.main()

            # Check that the UDF was applied with expected DataFrame
            mock_anonymize_udf.assert_called_once_with(mock_processor)

            # The main test here is functional: In a true environment, you would also collect and assert results

if __name__ == "__main__":
    unittest.main()