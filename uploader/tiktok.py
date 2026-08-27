"""TikTok uploader template.

This is a best-effort template for uploading to TikTok. TikTok's official APIs and upload flows vary by partner and api version.

Two recommended modes:
- S3 mode: upload your video to S3 (see uploader/instagram.py for example) and then use TikTok's 'create video by URL' endpoint (if available to your app) to register the video.
- Direct-mode: if you have a direct upload URL and access token for your TikTok app, this script can POST the file with multipart/form-data to that URL. You must supply the correct upload endpoint and parameters for your TikTok application.

Environment variables expected (you will fill these from TikTok developer console):
- TIKTOK_ACCESS_TOKEN
- TIKTOK_OPEN_ID (if required)
- Optionally S3_* variables if you want S3 mode

IMPORTANT: TikTok has multiple developer offerings (Open API, Business API) and endpoints change. Treat this script as a template that you may need to adapt to the exact API your app has access to.
"""
import os
import argparse
import requests

try:
    import boto3
    HAS_BOTO3 = True
except Exception:
    HAS_BOTO3 = False


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
    s3.upload_file(file_path, bucket, key, ExtraArgs={"ACL":"public-read", "ContentType":"video/mp4"})
    if endpoint.endswith('/'):
        endpoint = endpoint[:-1]
    if "amazonaws" in endpoint:
        url = f"https://{bucket}.s3.amazonaws.com/{key}"
    else:
        url = f"{endpoint}/{bucket}/{key}"
    return url


def direct_upload(upload_url, access_token, file_path, extra_headers=None):
    headers = {}
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    if extra_headers:
        headers.update(extra_headers)
    with open(file_path, "rb") as fh:
        files = {"video": (os.path.basename(file_path), fh, "video/mp4")}
        resp = requests.post(upload_url, files=files, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser("TikTok uploader (template)")
    parser.add_argument("--file", help="Local video file to upload (mp4)")
    parser.add_argument("--video-url", help="If you already host the video publicly, provide its URL instead of --file")
    parser.add_argument("--upload-url", help="Direct TikTok upload URL for your app (if available)")
    parser.add_argument("--open-id", help="TikTok open_id (if required)")
    args = parser.parse_args()

    access_token = os.getenv("TIKTOK_ACCESS_TOKEN")

    video_url = args.video_url
    if not video_url:
        if not args.file:
            raise RuntimeError("Provide either --file or --video-url")
        # Prefer S3 mode if configured
        if os.getenv("S3_ENDPOINT"):
            video_url = upload_to_s3(args.file)
            print("Uploaded to S3, video_url=", video_url)
        elif args.upload_url:
            print("Performing direct upload to TikTok upload URL (app-specific)...")
            res = direct_upload(args.upload_url, access_token, args.file)
            print("Upload response:", res)
            print("NOTE: You must adapt this script to your app's exact TikTok API endpoints and parameters.")
            return
        else:
            raise RuntimeError("No S3 configured and no upload URL provided. Configure S3 or pass --upload-url for direct upload.")

    # If we have a public video_url, you may be able to register it with TikTok via your app's endpoint.
    # This part is app-specific; print instructions.
    print("Video is available at:", video_url)
    print("Next: call your TikTok app's 'create video by URL' endpoint with the video_url and required metadata. This step is specific to your app and API access level.")

if __name__ == "__main__":
    main()
