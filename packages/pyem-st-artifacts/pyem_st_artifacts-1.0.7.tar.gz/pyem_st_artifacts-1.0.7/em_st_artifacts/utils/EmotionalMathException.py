class EmotionalMathException(Exception):
    def __init__(self, message="There was an error in the em_st_artifactslib"):
        self.message = message
        super().__init__(self.message)