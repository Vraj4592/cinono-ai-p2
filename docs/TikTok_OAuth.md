# TikTok OAuth & upload guide (generic)

TikTok offers different APIs (Open API, Business API) and upload flows depending on your account/app. This guide explains common flows and how to adapt uploader/tiktok.py.

Common approaches:
1) S3 URL registration (recommended):
   - Upload the final.mp4 to S3 (public-read) and call your TikTok app's endpoint to create a video from URL. The endpoint and parameters depend on your TikTok app level.
2) Direct multipart upload:
   - If your app provides an upload URL, you can POST the video file as multipart/form-data. The response usually contains a media_id which you then publish.

Typical steps (example placeholders):
- Upload to S3: ensure S3_ENDPOINT, S3_BUCKET, etc. are set and uploader/tiktok.py will upload the file and print the video URL.
- Register video by URL (example POST):
  POST https://open-api.tiktok.com/video/create/ (this is app-specific)
  params: access_token, open_id, video_url, text

- If your app uses multipart direct upload, the flow may be:
  1) Obtain upload URL from TikTok: POST /video/upload/url/ (returns upload_url)
  2) Upload file to upload_url as multipart
  3) Call /video/create/complete/ or similar to finalize and publish

What I need to adapt uploader/tiktok.py exactly for your app:
- Paste the TikTok app docs or the exact endpoints and parameters your app provides, or
- Provide the name of the TikTok developer program (Open API / Business API) and I will adapt to the most common endpoints.

Security note: keep TIKTOK_ACCESS_TOKEN and any client secrets out of Git.
