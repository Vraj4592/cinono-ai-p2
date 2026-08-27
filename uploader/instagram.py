"""Instagram uploader script.

Usage:
  python uploader/instagram.py --file /path/to/video.mp4 --caption "Your caption"

This script supports two modes:
- S3 mode: if S3_* environment variables are present, it uploads the file to the specified S3 bucket (public-read) and uses the resulting URL as video_url for the IG Graph API.
- Direct URL mode: if you already host the video and provide --video-url, the script will use that URL.

Requirements:
- INSTAGRAM_USER_ID    (Instagram Business Account ID)
- INSTAGRAM_ACCESS_TOKEN  (Long-lived access token with content_publish permission)
- If using S3: S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET

Important:
- Instagram Content Publishing requires an Instagram Business or Creator account connected to a Facebook Page and a Facebook App with the required permissions. See docs/uploaders.md for steps.

Note: This script does not store credentials in the repo. Provide them via environment variables.
"""
import os
import argparse
import requests
from urllib.parse import urljoin

try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except Exception:
    HAS_BOTO3 = False

GRAPH_VERSION = os.getenv("FACEBOOK_GRAPH_VERSION", "v17.0")
GRAPH_BASE = f"https://graph.facebook.com/{GRAPH_VERSION}/"


def upload_to_s3(file_path):
    if not HAS_BOTO3:
        raise RuntimeError("boto3 is required for S3 uploads. Install boto3 or provide a public video URL.")
    endpoint = os.getenv("S3_ENDPOINT")
    access_key = os.getenv("S3_ACCESS_KEY")
    secret_key = os.getenv("S3_SECRET_KEY")
    bucket = os.getenv("S3_BUCKET")
    if not (endpoint and access_key and secret_key and bucket):
        raise RuntimeError("Missing S3 configuration environment variables.")

    session = boto3.session.Session()
    s3 = session.client("s3", endpoint_url=endpoint, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    key = os.path.basename(file_path)
    try:
        s3.upload_file(file_path, bucket, key, ExtraArgs={"ACL":"public-read", "ContentType":"video/mp4"})
    except ClientError as e:
        raise
    # Construct URL
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
    # If endpoint is S3 compatible like https://s3.amazonaws.com, build URL
    if "amazonaws" in endpoint:
        url = f"https://{bucket}.s3.amazonaws.com/{key}"
    else:
        # generic endpoint: many S3-compatible providers expose files at endpoint/bucket/key
        url = f"{endpoint}/{bucket}/{key}"
    return url


def create_ig_container(ig_user_id, access_token, video_url, caption=""):
    url = urljoin(GRAPH_BASE, f"{ig_user_id}/media")
    params = {
        "video_url": video_url,
        "caption": caption,
        "access_token": access_token
    }
    resp = requests.post(url, data=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def publish_ig_container(ig_user_id, access_token, creation_id):
    url = urljoin(GRAPH_BASE, f"{ig_user_id}/media_publish")
    params = {"creation_id": creation_id, "access_token": access_token}
    resp = requests.post(url, data=params, timeout=60)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser("Instagram uploader")
    parser.add_argument("--file", help="Local video file to upload (mp4)")
    parser.add_argument("--video-url", help="If you already host the video publicly, provide its URL instead of --file")
    parser.add_argument("--caption", default="", help="Caption for the post")
    args = parser.parse_args()

    ig_user_id = os.getenv("INSTAGRAM_USER_ID")
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    if not (ig_user_id and access_token):
        raise RuntimeError("Set INSTAGRAM_USER_ID and INSTAGRAM_ACCESS_TOKEN environment variables before running this script.")

    video_url = args.video_url
    if not video_url:
        if not args.file:
            raise RuntimeError("Provide either --file or --video-url")
        # Try S3 upload
        video_url = upload_to_s3(args.file)
        print("Uploaded to S3, video_url=", video_url)

    # Create container
    print("Creating IG media container...")
    res = create_ig_container(ig_user_id, access_token, video_url, caption=args.caption)
    creation_id = res.get("id")
    if not creation_id:
        raise RuntimeError(f"Failed to create media container: {res}")
    print("Container created:", creation_id)

    # Publish
    print("Publishing container...")
    pub = publish_ig_container(ig_user_id, access_token, creation_id)
    print("Publish response:", pub)
    print("Done. Note: it may take a few minutes for the post to appear on Instagram.")

if __name__ == "__main__":
    main()
