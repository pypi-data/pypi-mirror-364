from presidio_analyzer import PatternRecognizer, Pattern

class CustomPhoneNumberRecognizer(PatternRecognizer):
    def __init__(self):
        patterns = [
            Pattern("Phone (XXX-XXX-XXXX)", r"\d{3}-\d{3}-\d{4}", score=0.85)
        ]
        super().__init__(
            supported_entity="PHONE_NUMBER",
            patterns=patterns
        )
