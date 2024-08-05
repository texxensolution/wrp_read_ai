
from src.dtos import ScriptReadingResultDTO
from src.lark import BitableManager


class ApplicantScriptReadingEvaluationStore:

    def __init__(self, table_id: str, base_manager: BitableManager):
        self.table_id: str = table_id
        self.base_manager: BitableManager = base_manager

    async def create(self, record: ScriptReadingResultDTO):
        try:
            await self.base_manager.create_record_async(
                table_id=self.table_id,
                fields=record.dict()
            )
        except Exception as err:
            raise Exception("Applicant Script Reading Evaluation: create record failed. error: ", err)