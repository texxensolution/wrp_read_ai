import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
import os
import json
from src.lark import Lark
from lark_oapi.api.drive.v1 import *
from loguru import logger


class BitableManager:
    def __init__(self, lark_client: Lark, bitable_token=None, bitable_id=None):
        self.lark = lark_client.client
        self.BITABLE_TOKEN = bitable_token
        self.BITABLE_ID = bitable_id

    def set_table_id(self, table_id):
        self.BITABLE_ID = table_id

    async def find_record(self, table_id: str, record_id: str, with_shared_url: bool = True):
        request = GetAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(table_id) \
            .record_id(record_id) \
            .with_shared_url(True) \
            .build()
        
        response: GetAppTableRecordResponse = await self.lark.bitable.v1.app_table_record.aget(request)

        if not response.success():
            raise Exception(f"bitable http request error: code={response.code} message={response.msg}")
        
        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

        return response


    async def list_records(self, filter=None, page_token=None, text_field_as_array=False, display_formula_ref=False,
                           page_size=100):
        partial_bitable_request = ListAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(self.BITABLE_ID) \

        if filter:
            partial_bitable_request = partial_bitable_request.filter(filter) \
                .text_field_as_array(text_field_as_array)

        if page_token:
            partial_bitable_request = partial_bitable_request.page_token(page_token=page_token)

        partial_bitable_request = partial_bitable_request.display_formula_ref(display_formula_ref=display_formula_ref)

        partial_bitable_request = partial_bitable_request.page_size(page_size).build()

        response = await self.lark.bitable.v1.app_table_record.alist(partial_bitable_request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")
        # lark.logger.info(lark.JSON.marshal(response.data, indent=4))

        return response.data

    def sync_list_records(self, filter=None, page_token=None, text_field_as_array=False, display_formula_ref=False,
                          page_size=100) -> ListAppTableRecordResponseBody:
        partial_bitable_request = ListAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(self.BITABLE_ID)

        if filter:
            partial_bitable_request = partial_bitable_request.filter(filter) \
                .text_field_as_array(text_field_as_array)

        if page_token:
            partial_bitable_request = partial_bitable_request.page_token(page_token=page_token)

        partial_bitable_request = partial_bitable_request.display_formula_ref(display_formula_ref=display_formula_ref)
        partial_bitable_request = partial_bitable_request.page_size(page_size).build()

        response = self.lark.bitable.v1.app_table_record.list(partial_bitable_request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        return response.data

    def _get_records(self, table_id: str, filter=None, page_token=None, page_size=500):
        request = ListAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(table_id)
        if filter:
            request = request.filter(filter)
        if page_token:
            request = request.page_token(page_token)
        request = request.page_size(page_size).build()

        response = self.lark.bitable.v1.app_table_record.list(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        return response
    
    async def async_get_records(self, table_id: str, filter=None, page_token=None, page_size=500):
        request = ListAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(table_id)
        if filter:
            request = request.filter(filter)
        if page_token:
            request = request.page_token(page_token)
        request = request.page_size(page_size).build()

        response = await self.lark.bitable.v1.app_table_record.alist(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        if response.data.total == 0:
            return []

        return response.data.items
    

    def get_records(self, table_id, filter=None) -> List[AppTableRecord]:
        has_more = True
        page_token = None
        records = []

        while has_more:
            if page_token:
                response = self._get_records(filter=filter, page_token=page_token, table_id=table_id)
            else:
                response = self._get_records(filter=filter, table_id=table_id)

            has_more = response.data.has_more
            page_token = response.data.page_token if has_more else None
            if response.data.items is not None:
                records.extend(response.data.items)
            else: 
                return []

        return records

    async def create_record_async(self, table_id: str, fields):
        request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
        .app_token(self.BITABLE_TOKEN) \
        .table_id(table_id) \
        .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
        .build()

        response: CreateAppTableRecordResponse = await self.lark.bitable.v1.app_table_record.acreate(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response

    def create_record(self, table_id: str, fields):
        request: CreateAppTableRecordRequest = CreateAppTableRecordRequest.builder() \
        .app_token(self.BITABLE_TOKEN) \
        .table_id(table_id) \
        .request_body(AppTableRecord.builder()
                    .fields(fields)
                    .build()) \
        .build()

        response: CreateAppTableRecordResponse = self.lark.bitable.v1.app_table_record.create(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response
    
    def update_record(self, table_id: str, record_id: str, fields):
        request: UpdateAppTableRecordRequest = UpdateAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(table_id or self.BITABLE_ID) \
            .record_id(record_id) \
            .request_body(AppTableRecord.builder()
                        .fields(fields)
                        .build()) \
            .build()

        response: UpdateAppTableRecordResponse = self.lark.bitable.v1.app_table_record.update(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response
    
    async def update_record_async(self, table_id: str, record_id: str, fields: Dict[str, Any]):
        request: UpdateAppTableRecordRequest = UpdateAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(table_id or self.BITABLE_ID) \
            .record_id(record_id) \
            .request_body(AppTableRecord.builder()
                        .fields(fields)
                        .build()) \
            .build()

        response: UpdateAppTableRecordResponse = await self.lark.bitable.v1.app_table_record.aupdate(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response

    def batch_create_record(self, records):
        request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(self.BITABLE_ID) \
            .request_body(BatchCreateAppTableRecordRequestBody.builder()
                          .records(records)
                          .build()) \
            .build()

        response: BatchCreateAppTableRecordResponse = self.lark.bitable.v1.app_table_record.batch_create(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")

        lark.logger.info(lark.JSON.marshal(response.data, indent=4))
        return response

    async def abatch_create_record(self, records):
        request: BatchCreateAppTableRecordRequest = BatchCreateAppTableRecordRequest.builder() \
            .app_token(self.BITABLE_TOKEN) \
            .table_id(self.BITABLE_ID) \
            .request_body(BatchCreateAppTableRecordRequestBody.builder()
                          .records(records)
                          .build()) \
            .build()

        response: BatchCreateAppTableRecordResponse = await self.lark.bitable.v1.app_table_record.abatch_create(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")


        lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    async def adownload(self, payload, folder_name, destination_folder=None):
        extra = {"bitablePerm": {"tableId": "tblpBRLDctSvsSQy",
                                 "attachments": {"fldQeAROnz": {payload["record_id"]: [payload["file_token"]]}}}}
        request: DownloadMediaRequest = DownloadMediaRequest.builder() \
            .file_token(payload["file_token"]) \
            .extra(json.dumps(extra)) \
            .build()

        response: DownloadMediaResponse = await self.lark.drive.v1.media.adownload(request)

        if not response.success():
            raise Exception(f"Request failed: code={response.code}, msg={response.msg}, log_id={response.get_log_id()}")
            
        if destination_folder:
            filename = f"/{destination_folder}/{response.file_name}"
        else:
            filename = f"/downloaded_resources/medias/{folder_name}/{response.file_name}"

        if os.path.exists(filename):
            os.makedirs(filename)

        f = open(filename, "wb")
        f.write(response.file.read())
        f.close()