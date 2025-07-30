from pyspark.sql.functions import udf
from pyspark.sql.types import StringType

def anonymize_text_udf(processor):
    """
    Create a UDF for row-wise anonymization using Presidio.
    :param processor: An instance of PresidioDLPProcessor or a similar class.
    :return: A Spark UDF that can be applied to DataFrame columns.
    """
    @udf(returnType=StringType())
    def anonymize_udf(text):
        return processor.anonymize_text(text)

    return anonymize_udf
