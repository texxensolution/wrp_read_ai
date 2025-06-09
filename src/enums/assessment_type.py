class AssessmentType:
    SCRIPT_READING="Script Reading"
    PHOTO_TRANSLATION="Photo Translation"
    QUOTE_TRANSLATION="Quote Translation"
    ENHANCED_SCRIPT_READING="Enhanced Script Reading"

    def __str__(self) -> str:
        return self.value