from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.cdn.v20180606 import cdn_client, models
import json
import os


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
    assert len(paths) >= 1, "Please specify at least one path to refresh"
    flush_type = os.getenv("FLUSH_TYPE", "flush")
    # print event details
    event_file = open(os.getenv("GITHUB_EVENT_PATH", "/github/workflow/event.json"),"r")
    print(event_file.read())
    event_file.close()
    # print all envs
    for key in os.environ:
        print(key + ' : ' + os.environ[key])
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
