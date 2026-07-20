import asyncio
from urllib.parse import unquote

import aiohttp

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

DISK_PATH_PREFIX = 'disk:/YaCut_uploads/'
OVERWRITE_PARAM = 'True'
TIMEOUT_TOTAL = 60
DISK_PREFIX_TO_REMOVE = '/disk'

HTTP_OK = 200
HTTP_CREATED = 201
SUCCESS_STATUSES_PUT = (HTTP_OK, HTTP_CREATED)

ERR_GET_UPLOAD_URL = 'Ошибка получения URL: {status} {text}'
ERR_UPLOAD_FILE = 'Ошибка загрузки: {status} {text}'
ERR_NO_LOCATION = 'Не получен Location в ответе'
ERR_GET_DOWNLOAD_LINK = 'Ошибка получения ссылки скачивания: {status} {text}'
ERR_EXCEPTION = '{error}'

KEY_FILENAME = 'filename'
KEY_SUCCESS = 'success'
KEY_ERROR = 'error'
KEY_DOWNLOAD_LINK = 'download_link'
KEY_DISK_PATH = 'disk_path'


async def upload_file(session, token, filename, file_bytes):
    """Загружает один файл на Яндекс.Диск и возвращает результат."""
    disk_path = f'{DISK_PATH_PREFIX}{filename}'

    try:
        headers = {'Authorization': f'OAuth {token}'}
        params = {'path': disk_path, 'overwrite': OVERWRITE_PARAM}
        async with session.get(
            UPLOAD_URL,
            headers=headers,
            params=params
        ) as resp:
            if resp.status != HTTP_OK:
                error_text = await resp.text()
                return {
                    KEY_FILENAME: filename,
                    KEY_SUCCESS: False,
                    KEY_ERROR: ERR_GET_UPLOAD_URL.format(
                        status=resp.status,
                        text=error_text
                    )
                }
            data = await resp.json()
            upload_href = data['href']

        async with session.put(upload_href, data=file_bytes) as resp:
            if resp.status not in SUCCESS_STATUSES_PUT:
                error_text = await resp.text()
                return {
                    KEY_FILENAME: filename,
                    KEY_SUCCESS: False,
                    KEY_ERROR: ERR_UPLOAD_FILE.format(
                        status=resp.status,
                        text=error_text
                    )
                }
            location = resp.headers.get('Location')
            if not location:
                return {
                    KEY_FILENAME: filename,
                    KEY_SUCCESS: False,
                    KEY_ERROR: ERR_NO_LOCATION
                }

        decoded_path = unquote(location)
        if decoded_path.startswith(DISK_PREFIX_TO_REMOVE):
            decoded_path = decoded_path[len(DISK_PREFIX_TO_REMOVE):]

        params = {'path': decoded_path}
        async with session.get(
            DOWNLOAD_URL,
            headers=headers,
            params=params
        ) as resp:
            if resp.status != HTTP_OK:
                error_text = await resp.text()
                return {
                    KEY_FILENAME: filename,
                    KEY_SUCCESS: False,
                    KEY_ERROR: ERR_GET_DOWNLOAD_LINK.format(
                        status=resp.status,
                        text=error_text
                    )
                }
            data = await resp.json()
            download_link = data['href']

        return {
            KEY_FILENAME: filename,
            KEY_SUCCESS: True,
            KEY_DOWNLOAD_LINK: download_link,
            KEY_DISK_PATH: decoded_path
        }

    except Exception as e:
        return {
            KEY_FILENAME: filename,
            KEY_SUCCESS: False,
            KEY_ERROR: ERR_EXCEPTION.format(error=str(e))
        }


async def upload_files_async(files_data, token):
    """Асинхронно загружает несколько файлов."""
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_TOTAL)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = []
        for filename, file_bytes in files_data:
            task = asyncio.create_task(upload_file(
                session,
                token,
                filename,
                file_bytes
            ))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=True)

    processed_results = []
    for res in results:
        if isinstance(res, Exception):
            processed_results.append({KEY_SUCCESS: False, KEY_ERROR: str(res)})
        else:
            processed_results.append(res)
    return processed_results


def sync_upload_files(files_data, token):
    """Синхронная обёртка для вызова из Flask."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(upload_files_async(files_data, token))
    finally:
        loop.close()
