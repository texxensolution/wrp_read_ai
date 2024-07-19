from src.dtos import QuoteTranslationResultDTO
from src.lark import BitableManager


class ApplicantQuoteTranslationEvaluationStore:
    def __init__(self, table_id: str, base_manager: BitableManager):
        self.table_id = table_id
        self.base_manager = base_manager

    async def create(self, payload: QuoteTranslationResultDTO):
        try:
            await self.base_manager.create_record_async(
                table_id=self.table_id,
                fields=payload.dict()
            )
        except Exception as err:
            raise Exception(f"ApplicantQuoteTranslationEvaluation: cant create a record, reason: {err}\n payload: {payload.model_dump_json(indent=4)}")