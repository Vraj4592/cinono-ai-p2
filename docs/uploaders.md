# Uploaders guide

This document explains how the uploader scripts work and how to set up the required credentials.

Instagram uploader (recommended flow)
- Requirements:
  - Instagram Business or Creator account linked to a Facebook Page
  - A Facebook App with the "instagram_content_publish" and related permissions
  - A long-lived Instagram access token (INSTAGRAM_ACCESS_TOKEN) and your Instagram user id (INSTAGRAM_USER_ID)
  - Optionally: an S3-compatible storage account (S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET)

- Recommended flow:
  1) The uploader uploads the local MP4 to your S3 bucket (public-read) and obtains a public video URL.
  2) It creates an IG media container using the Graph API:
     POST https://graph.facebook.com/{api_version}/{ig_user_id}/media
     params: video_url, caption, access_token
  3) It publishes the container:
     POST https://graph.facebook.com/{api_version}/{ig_user_id}/media_publish
     params: creation_id, access_token

- If you cannot use S3, you must host the video somewhere publicly accessible and provide --video-url to the uploader.

TikTok uploader (template)
- TikTok's developer offerings vary by partner and region. There are several APIs (Open API, Business API) each with their own upload flows.
- Recommended practical approach:
  - Upload the video to S3 (public URL).
  - Use your TikTok developer app's API to create/register the video using the public video URL.
  - If your app supports direct multipart upload, adapt uploader/tiktok.py to post the file to the upload endpoint. You will need TIKTOK_ACCESS_TOKEN and possibly OPEN_ID.

Notes and security
- The uploader scripts do not contain secrets. Provide the required environment variables per .env.example.
- Do not commit your app secrets to Git.

If you want, I can help with the exact OAuth app setup steps for Instagram and TikTok and test uploads once you provide credentials.
