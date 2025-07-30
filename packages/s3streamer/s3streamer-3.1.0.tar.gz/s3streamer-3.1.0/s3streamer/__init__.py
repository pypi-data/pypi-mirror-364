#!/usr/bin/env python3
# -*- coding: latin-1 -*-

"""Stream files to AWS S3 using multipart upload."""
import json
import ast
import os
import random
import string
import time
import argparse
from multiprocessing import Pool
from typing import Union
import requests
from tqdm import tqdm


__version__ = "3.1.0"
__author__ = "Ahmad Ferdaus Abd Razak"
__application__ = "s3streamer"


def check_read_access(
    file_name: str
) -> bool:
    """Check if file is readable."""
    return os.access(file_name, os.R_OK)


def check_write_access(
    path: str
) -> bool:
    """Check if path is writable."""
    return os.access(path, os.W_OK)


def create_file_name(
    file_name: str
) -> dict:
    """Create unique file name."""
    try:
        random_constructor = "".join(
            random.choices(
                (
                    f"{string.ascii_lowercase}"
                    f"{string.ascii_uppercase}"
                    f"{string.digits}"
                ),
                k=5
            )
        )
        random_token = (
            f"{str(int(time.time()))}_{random_constructor}"
        )
        file_extension = file_name.split(".")[-1]
        no_extension = file_name.replace(f".{file_extension}", "")
        new_file_name = f"{no_extension}_{random_token}.{file_extension}"
        status = {
            "status_code": 200,
            "status": new_file_name
        }
    except Exception as e:
        status = {
            "status_code": 400,
            "status": str(e)
        }
    return status


def get_presigned_url(
    request_url: str,
    request_api_key: str,
    file_name: str
) -> dict:
    """Get AWS S3 presigned URL."""
    response = requests.post(
        f"{request_url}?file_name={file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "geturl"
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def get_upload_id(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path: str,
    file_size: int,
    force: bool
) -> dict:
    """Get AWS S3 upload ID."""
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "create",
                "file_size": file_size,
                "force": force
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def add_multipart_chunk(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path: str,
    upload_id: str,
    chunked_file_name: str,
    chunked_file_num: int
) -> dict:
    """Add chunk to AWS S3 multipart upload."""
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "add",
                "upload_id": upload_id,
                "part_name": chunked_file_name,
                "part_number": chunked_file_num
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def purge_file(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path: str
) -> dict:
    """Purge file from AWS S3."""
    manifest_purge = [
        {
            "Key": f"{path}{file_name}"
        }
    ]
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "purge",
                "objects": json.dumps(manifest_purge)
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def abort_multipart_upload(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path: str,
    upload_id: str
) -> dict:
    """Abort AWS S3 multipart upload."""
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "abort",
                "upload_id": upload_id
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def delete_temp_file(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path: str,
    manifest_delete: list
) -> dict:
    """Delete temporary file from AWS S3."""
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "delete",
                "objects": json.dumps(manifest_delete)
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def complete_multipart_upload(
    request_url: str,
    request_api_key: str,
    file_name: str,
    path,
    upload_id: str,
    manifest: list
):
    """Complete AWS S3 multipart upload."""
    response = requests.post(
        f"{request_url}?file_name={path}{file_name}",
        headers={
            "x-api-key": request_api_key
        },
        data=json.dumps(
            {
                "action": "complete",
                "upload_id": upload_id,
                "parts": json.dumps(manifest)
            }
        )
    )
    return {
        "status_code": json.loads(response.text)["status_code"],
        "status": json.loads(response.text)["status"]
    }


def upload_chunk(
    request_url: str,
    request_api_key: str,
    chunked_file_name: str,
    files: dict
) -> dict:
    """Upload chunk to temporary location in AWS S3."""
    presigned_url = get_presigned_url(
        request_url,
        request_api_key,
        chunked_file_name
    )["status"]
    response = requests.post(
        ast.literal_eval(presigned_url)["url"],
        data=ast.literal_eval(presigned_url)["fields"],
        files=files
    )
    return {
        "status_code": response.status_code,
        "status": response.headers
    }


def create_chunk(
    chunk_dict: dict
) -> dict:
    """Create chunk for AWS S3 multipart upload."""
    upload_id = list(chunk_dict.keys())[-1]
    chunked_file_name = chunk_dict["chunked_file_name"]
    upload_id = chunk_dict["upload_id"]
    request_url = chunk_dict["request_url"]
    request_api_key = chunk_dict["request_api_key"]
    file_name = chunk_dict["file_name"]
    path = chunk_dict["path"]

    # Get file numbering from the new file names.
    file_num = int(chunked_file_name.split(".")[-1])

    try:
        # Attempt upload up to 3 times for each chunk.
        # Return 204 if chunk is good,
        # or anoother status code depending on the failure.
        upload_count = 1
        chunk_status = 1
        while upload_count < 4 and chunk_status != 204:
            with open(chunked_file_name, "rb") as m:
                files = {
                    'file': (chunked_file_name, m)
                }
                preresponse = upload_chunk(
                    request_url,
                    request_api_key,
                    chunked_file_name,
                    files
                )
                try:
                    assert preresponse["status_code"] == 204
                    response = preresponse["status"]
                    etag = response["ETag"].strip('"')
                    chunk_status = preresponse["status_code"]
                except Exception:
                    chunk_status = 400
                    upload_count += 1

        # Stop processing if chunk fails continuously, otherwise keep working.
        if chunk_status != 204:
            print(f"Upload attempt for {chunked_file_name} failed after 3 tries.")
            manifest_content = {
                "status": "failed"
            }
        else:
            # Add chunk to document manifest.
            preresponse = add_multipart_chunk(
                request_url,
                request_api_key,
                file_name,
                path,
                upload_id,
                chunked_file_name,
                file_num
            )

            try:
                assert preresponse["status_code"] == 200
            except Exception:
                # Abort multipart upload upon failure to clean storage from rogue Upload ID.
                preresponse = abort_multipart_upload(
                    request_url,
                    request_api_key,
                    file_name,
                    path,
                    upload_id
                )

                try:
                    assert preresponse["status_code"] == 200
                except Exception:
                    manifest_content = {
                        "status": "failed"
                    }

            # Create upload manifest.
            try:
                # Return current chunk into manifest.
                manifest_content = {
                    "ETag": etag,
                    "PartNumber": file_num,
                    "Key": f"tmp/{chunked_file_name}"
                }
            except Exception:
                # Abort multipart upload upon failure to clean storage from rogue Upload ID.
                preresponse = abort_multipart_upload(
                    request_url,
                    request_api_key,
                    file_name,
                    path,
                    upload_id
                )
                try:
                    assert preresponse["status_code"] == 200
                except Exception:
                    manifest_content = {
                        "status": "failed"
                    }

    # Abort and delete multiipart upload if failed.
    except Exception:
        manifest_content = {
            "status": "failed"
        }

    # Remove current chunk from local temporary storage and return manifest content.
    os.remove(chunked_file_name)
    return manifest_content


def create_pool(
    parts: int,
    name_list: list
) -> list:
    with Pool(parts) as p:
        results = p.map(
            create_chunk,
            name_list
        )
        if {"status": "failed"} in results:
            p.terminate()
    return results


def generator():
    """Generate progress bar."""
    while True:
        yield


def get_params():
    """Get parameters from script inputs."""
    myparser = argparse.ArgumentParser(
        add_help=True,
        allow_abbrev=False,
        description="Stream files to AWS S3 using multipart upload.",
        usage=f"{__application__} [options]"
    )
    myparser.add_argument(
        "-V", "--version", action="version", version=f"{__application__} {__version__}"
    )
    myparser.add_argument(
        "-f",
        "--local_file_path",
        action="store",
        help="Local file path to upload or purge.",
        nargs="?",
        required=True,
        type=str
    )
    myparser.add_argument(
        "-y",
        "--tgw_only",
        action="store_true",
        help="Transit Gateway details only, no other components.",
        required=False
    )
    myparser.add_argument(
        "-r",
        "--remote_file_path",
        action="store",
        help="Remote file path in S3 bucket. Default: empty string for root folder.",
        nargs="?",
        default="",
        required=False,
        type=str
    )
    myparser.add_argument(
        "-u",
        "--request_url",
        action="store",
        help="S3Streamer API endpoint URL. Default: S3STREAMER_ENDPOINT environment variable.",
        nargs="?",
        default=os.environ.get("S3STREAMER_ENDPOINT", None),
        required=False,
        type=str
    )
    myparser.add_argument(
        "-k",
        "--request_api_key",
        action="store",
        help="S3Streamer API key. Default: S3STREAMER_API_KEY environment variable.",
        nargs="?",
        default=os.environ.get("S3STREAMER_API_KEY", None),
        required=False,
        type=str
    )
    myparser.add_argument(
        "-p",
        "--parts",
        action="store",
        help="Number of parts to upload in parallel. Default: 10.",
        nargs="?",
        default=10,
        required=False,
        type=int
    )
    myparser.add_argument(
        "-s",
        "--part_size",
        action="store",
        help="Size of each part in MB. Default: 100.",
        nargs="?",
        default=100,
        required=False,
        type=str
    )
    myparser.add_argument(
        "-t",
        "--tmp_path",
        action="store",
        help="Temporary path for chunked files. Default: /tmp.",
        nargs="?",
        default="/tmp",
        required=False,
        type=str
    )
    myparser.add_argument(
        "-d",
        "--purge",
        action="store",
        help="Purge file from S3 storage. Default: False.",
        nargs="?",
        default=False,
        required=False,
        type=bool
    )
    myparser.add_argument(
        "-o",
        "--force",
        action="store",
        help="Force upload even if file already exists. Default: False.",
        nargs="?",
        default=False,
        required=False,
        type=bool
    )
    return myparser.parse_args()


def stream(
    local_file_path: str,
    path: str = "",
    request_url: Union[str, None] = os.environ.get("S3STREAMER_ENDPOINT", None),
    request_api_key: Union[str, None] = os.environ.get("S3STREAMER_API_KEY", None),
    parts: int = 10,
    part_size: int = 100,  # in MB
    tmp_path: str = "/tmp",
    purge: bool = False,
    force: bool = False
) -> dict:
    """Execute main function."""
    # Check if API endpoint and key are provided.
    assert request_url is not None
    assert request_api_key is not None

    # Parameter clean-up.
    local_file_path = local_file_path.strip().rstrip('/')
    file_dir = (
        os.path.dirname(local_file_path)
        if os.path.dirname(local_file_path) != ""
        else "."
    )
    file_name = os.path.basename(local_file_path)
    path = (
        f"{path.strip().strip('/')}/"
        if path != ""
        else ""
    )
    tmp_path = tmp_path.rstrip("/")
    part_size = part_size * 1048576
    request_url = request_url.rstrip("/")
    request_api_key = request_api_key.strip()

    # Check if locations have correct permissions.
    assert check_read_access(local_file_path)
    assert check_write_access(tmp_path)

    # Initialize data lists.
    names = []
    manifests = []

    # Purge object from storage.
    if purge:
        preresponse = purge_file(
            request_url,
            request_api_key,
            file_name,
            path
        )
        try:
            assert preresponse["status_code"] == 200
            return {
                "status_code": preresponse["status_code"],
                "status": preresponse["status"]
            }
        except Exception:
            return {
                "status_code": preresponse["status_code"],
                "status": preresponse["status"]
            }

    # Start multipart upload.
    try:

        # Get file size and upload ID.
        file_size = os.path.getsize(f"{file_dir}/{file_name}")
        with open(f"{file_dir}/{file_name}", 'rb') as f:
            preresponse = get_upload_id(
                request_url,
                request_api_key,
                file_name,
                path,
                file_size,
                force
            )
            try:
                assert preresponse["status_code"] == 200
                upload_id = preresponse["status"]
            except Exception:
                return {
                    "status_code": preresponse["status_code"],
                    "status": preresponse["status"]
                }

            # Create temporary file name for chunking.
            preresponse = create_file_name(file_name)
            try:
                assert preresponse["status_code"] == 200
                new_file_name = preresponse["status"]
            except Exception:
                # Abort multipart upload upon failure to clean storage from rogue Upload ID.
                preresponse = abort_multipart_upload(
                    request_url,
                    request_api_key,
                    file_name,
                    path,
                    upload_id
                )
                try:
                    assert preresponse['status_code'] == 200
                except Exception:
                    return {
                        "status_code": preresponse["status_code"],
                        "status": preresponse["status"]
                    }

            # Work through the file until all chunks are uploaded.
            chunk_num = 1
            for _ in tqdm(generator()):
                # while True:
                # print(f"Uploading chunk {chunk_num}...")
                data = f.read(part_size)
                if not data:
                    break
                with open(f"{tmp_path}/{new_file_name}.{str(chunk_num)}", "wb") as fchunk:
                    fchunk.write(data)
                names.append(
                    {
                        'request_url': request_url,
                        'request_api_key': request_api_key,
                        'file_name': file_name,
                        'path': path,
                        'upload_id': upload_id,
                        'chunked_file_name': f"{tmp_path}/{new_file_name}.{str(chunk_num)}"
                    }
                )
                chunk_num += 1
                if chunk_num > 1 and chunk_num % parts == 1:
                    results = create_pool(parts, names)
                    manifests.extend(results)
                    if {"status": "failed"} in manifests:
                        raise Exception('Failed to complete upload.')
            results = create_pool(parts, names)
            manifests.extend(results)
            if {"status": "failed"} in manifests:
                raise Exception('Failed to complete upload.')

        # Finalize if everything is good.
        try:
            try:
                manifest = [
                    {
                        "ETag": i["ETag"],
                        "PartNumber": i["PartNumber"]
                    }
                    for i in manifests
                ]
                manifest_delete = [
                    {"Key": i["Key"]}
                    for i in manifests
                ]
            # Abort multipart upload upon failure to clean storage from rogue Upload ID.
            except Exception:
                preresponse = abort_multipart_upload(
                    request_url,
                    request_api_key,
                    file_name,
                    path,
                    upload_id
                )
                try:
                    assert preresponse["status_code"] == 200
                except Exception:
                    return {
                        "status_code": preresponse["status_code"],
                        "status": preresponse["status"]
                    }

            # Complete multipart upload.
            preresponse = complete_multipart_upload(
                request_url,
                request_api_key,
                file_name,
                path,
                upload_id,
                manifest
            )
            try:
                assert preresponse["status_code"] == 200
            except Exception:
                # Abort multipart upload upon failure to clean storage from rogue Upload ID.
                preresponse = abort_multipart_upload(
                    request_url,
                    request_api_key,
                    file_name,
                    path,
                    upload_id
                )
                try:
                    assert preresponse["status_code"] == 200
                except Exception:
                    return {
                        "status_code": preresponse["status_code"],
                        "status": preresponse["status"]
                    }

            # Delete temporary files.
            preresponse = delete_temp_file(
                request_url,
                request_api_key,
                file_name,
                path,
                manifest_delete
            )
            try:
                assert preresponse["status_code"] == 200
                return {
                    "status_code": 200,
                    "status": f"Upload complete: {path}{file_name}."
                }
            except Exception:
                return {
                    "status_code": preresponse["status_code"],
                    "status": (
                        f"Upload complete: {path}{file_name}."
                        f" Temporary files could not be deleted: {preresponse['status']}"
                    )
                }
        except Exception as e:
            return {
                "status_code": 500,
                "status": f"Upload failed: {str(e)}"
            }

    # Abort if something's wrong.
    except Exception as e:
        # If failed on the first chunk.
        if manifests == [{"status": "failed"}]:
            # Abort multipart upload upon failure to clean storage from rogue Upload ID.
            preresponse = abort_multipart_upload(
                request_url,
                request_api_key,
                file_name,
                path,
                upload_id
            )
            try:
                assert preresponse["status_code"] == 200
            except Exception:
                return {
                    "status_code": preresponse["status_code"],
                    "status": preresponse["status"]
                }
        # If failed on a subsequent chunk.
        elif {"status": "failed"} in manifests:
            manifest_delete = [
                {
                    "Key": i["Key"]
                }
                for i in manifests
            ]
            # Abort multipart upload upon failure to clean storage from rogue Upload ID.
            preresponse = abort_multipart_upload(
                request_url,
                request_api_key,
                file_name,
                path,
                upload_id
            )
            try:
                assert preresponse["status_code"] == 200
            except Exception:
                return {
                    "status_code": preresponse["status_code"],
                    "status": preresponse["status"]
                }
            # Delete temporary files from storage.
            preresponse = delete_temp_file(
                request_url,
                request_api_key,
                file_name,
                path,
                manifest_delete
            )
            try:
                assert preresponse["status_code"] == 200
            except Exception:
                return {
                    "status_code": preresponse["status_code"],
                    "status": preresponse["status"]
                }
        else:
            return {
                "status_code": 500,
                "status": f"Upload failed: {str(e)}"
            }


def main():
    """Execute main function."""
    # Get parameters from script inputs.
    args = get_params()
    local_file_path = args.local_file_path
    path = args.remote_file_path
    request_url = args.request_url
    request_api_key = args.request_api_key
    parts = args.parts
    part_size = args.part_size
    tmp_path = args.tmp_path
    purge = args.purge
    force = args.force

    stream(
        local_file_path,
        path,
        request_url,
        request_api_key,
        parts,
        part_size,
        tmp_path,
        purge,
        force
    )
