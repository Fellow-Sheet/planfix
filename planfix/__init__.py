from typing import Optional, Mapping, Any
from pydantic import ValidationError
from .types import *
import aiohttp


class PlanfixApi:
    def __init__(self, token: str, url: str):
        self.headers = {"Authorization": f"Bearer {token}"}
        self.url = url + 'rest/'

    async def base_request(
            self,
            method: str,
            path: str,
            params: Optional[Mapping[str, str]] = None,
            data: dict | aiohttp.FormData | Any | None = None,
    ):
        """
        Базовый запрос к ПФ.
        :param params: Query параметры запроса
        :param method: Метод запроса
        :param path: Путь запроса
        :param data: Тело запроса
        :return:
        """
        if isinstance(data, aiohttp.FormData):
            async with aiohttp.request(
                    method=method,
                    headers=self.headers,
                    url=self.url + path,
                    params=params,
                    data=data
            ) as resp:
                return await resp.json()
        else:
            async with aiohttp.request(
                    method=method,
                    headers=self.headers,
                    url=self.url + path,
                    params=params,
                    json=data
            ) as resp:
                return await resp.json()

    async def create_task(self, data: dict
                          ) -> ApiResponse | ApiResponseError:
        """
        Создание задачи
        :param data: TaskCreateRequest
        :return: {
            "result": "success",
            "id": 1491743
        }
        """
        result = await self.base_request(method='POST', path='task/', data=data)
        try:
            return ApiResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)

    async def update_task(self, task_id: int,  data: dict
                          ) -> ApiResponse | ApiResponseError | dict:
        """
        Обновление задачи
        :param task_id: ID задачи в ПФ
        :param data: TaskCreateRequest
        :return: {
            "result": "success"
        }
        """
        return await self.base_request('POST', f'task/{task_id}', data=data)

    async def get_task_list(
            self, data: dict
    ) -> ApiResponse | ApiResponseError | TaskListResponse:
        """
        Получение списка задач
        :param data: TaskListRequest
        :return: TaskListResponse
        """
        result = await self.base_request(method='GET', path='task/', data=data)
        try:
            return TaskListResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)

    async def load_files(self, files: list[tuple[str, bytes]]) -> list[int]:
        """
        Загрузка файлов в Slack
        :param files: Файлы для отправки
        :return: Список ID загруженных файлов
        """
        loaded_files_id: list[int] = []
        for file in files:
            name, file_bytes = file
            data = aiohttp.FormData()
            data.add_field('file',
                           file_bytes,
                           filename=name,
                           content_type='multipart/form-data')

            response = await self.base_request(
                method='POST', path='file/', data=data)
            if response['result'] == 'success':
                loaded_files_id.append(response.get('id'))
        return loaded_files_id

    async def send_comment(
            self,
            task_id: int,
            user_id: int | None = None,
            recipients: dict | None = None,
            files: list[tuple[str, bytes]] | None = None,
            text: str = '',
            is_pinned: bool = False,
            comment_id: int | None = None
    ) -> ApiResponse | ApiResponseError | dict:
        """
        Отправка комментария в ПФ
        :param task_id: ID задачи
        :param user_id: ID Пользователя
        :param recipients: Упомянутые
        :param files: файлы для отправки
        :param text: текст комментария
        :param is_pinned: Закреплён
        :param comment_id: ID комментарий для обновления
        :return:
        """
        if recipients is None:
            recipients = {}

        data = {
            "description": f"<span>#slack-message#</span><p>{text}</p>",
            "isPinned": is_pinned,
            "recipients": recipients,
            "files": []
        }

        if files is not None:
            loaded_files_id = await self.load_files(files)
            for file_id in loaded_files_id:
                data['files'].append({'id': file_id})

        if user_id is not None:
            data['owner'] = {"id": user_id}

        url = f'task/{task_id}/comments/'
        if comment_id is not None:
            url = url + str(comment_id)

        return await self.base_request(method='POST', path=url, data=data)

    async def comment_get(self, comment_id: int, fields: dict
                          ) -> ApiCommentResponse | ApiResponseError:
        """
        GET /comment/{id}
        :param comment_id: ID комментария
        :param fields: query параметры
        """
        result = await self.base_request(
            method='GET',
            path="comment/" + str(comment_id),
            params=fields
        )
        try:
            return ApiCommentResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)

    async def user_get(self, user: int | str, fields: dict
                       ) -> ApiUserResponse | ApiResponseError:
        """
        GET /user/{id}
        :param user: user:1 OR 1
        :param fields: fields returned - custom field identifiers,
        system field names, comma-delimited
        """
        result = await self.base_request(
            method='GET',
            path="user/" + str(user),
            params=fields
        )
        try:
            return ApiUserResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)

    async def contact_get(self, contact: int | str, fields: dict
                          ) -> ApiContactResponse | ApiResponseError:
        """
        GET /contact/{id}
        :param contact: contact:1 OR 1
        :param fields: fields returned - custom field identifiers,
        system field names, comma-delimited
        """
        result = await self.base_request(
            method='GET',
            path="contact/" + str(contact),
            params=fields
        )
        try:
            return ApiContactResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)

    async def file_download(self, file_id: int) -> tuple[bytes, str] | None:
        """
        Получение файла из ПФ
        :param file_id: ID файла
        :return: тело(bytes)
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(self.url + f"file/{file_id}/download") as \
                    resp:
                if resp.status == 200:
                    file = await resp.read()
                    extension = resp.content_type
                    return file, extension

    async def file_get(self, file_id: int, fields: dict
                       ) -> ApiFileResponse | ApiResponseError:
        result = await self.base_request(
            method='GET',
            path="file/" + str(file_id),
            params=fields
        )
        try:
            return ApiFileResponse(**result)
        except ValidationError:
            return ApiResponseError(**result)


async def file_download(url: str) -> bytes | None:
    async with aiohttp.request(method='GET', url=url) as resp:
        if resp.status == 200:
            return await resp.read()
