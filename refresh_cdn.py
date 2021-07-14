from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models
import json
import os
import requests


def refresh_cdn(secret_id, secret_key, paths, flush_type="flush"):
    cred = credential.Credential(secret_id, secret_key)
    http_profile = HttpProfile()
    http_profile.endpoint = "cdn.tencentcloudapi.com"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    client = cdn_client.CdnClient(cred, "", client_profile)

    req = models.PurgeUrlsCacheRequest()
    params = {
        "Urls": paths,
        "UrlEncode": True
    }
    req.from_json_string(json.dumps(params))

    return client.PurgeUrlsCache(req)


def parse_env():
    secret_id = os.getenv("SECRET_ID", None)
    assert secret_id is not None, "Please provide Secret ID"
    secret_key = os.getenv("SECRET_KEY", None)
    assert secret_key is not None, "Please provide Secret Key"
    paths = os.getenv("PATHS", "")
    # split and only keep non-whitespaces
    paths = filter(lambda pth: len(pth) > 0, map(str.strip, paths.split(",")))
    paths = list(paths)
    # get lateset update files
    response = json.loads(requests.get(url='https://api.github.com/repos/'+os.getenv("GITHUB_REPOSITORY")+'/commits/'+os.getenv("GITHUB_ACTION_REF")).text)
    if response.get("files") != None and len(response.get("files")) != 0:
        paths = []
        for entry in response["files"]:
            paths.append("https://wiki.blocklynukkit.com/"+entry["filename"].replace(".md",".html"))
            paths.append("https://wiki.blocklynukkit.com/"+entry["filename"])
    assert len(paths) >= 1, "Please specify at least one path to refresh"
    flush_type = os.getenv("FLUSH_TYPE", "flush")
    print(paths)
    return secret_id, secret_key, paths, flush_type


if __name__ == '__main__':
    try:
        resp = refresh_cdn(*parse_env())
        print("Successfully purged!")
        print(resp)
    except TencentCloudSDKException as err:
        print("Failed to purge:")
        print(err)
        exit(-1)
