# Guide: Obtain a long-lived Instagram Graph API token for publishing

This document lists the exact steps and example curl commands to obtain a long-lived Instagram access token (INSTAGRAM_ACCESS_TOKEN) and your Instagram Business user ID (INSTAGRAM_USER_ID). You must perform some steps in a browser and some via curl.

Pre-reqs:
- An Instagram Business or Creator account linked to a Facebook Page
- A Facebook App created at https://developers.facebook.com with the "instagram_content_publish" permission (and instagram_basic)
- Your app must be in Development mode to test; production use may require App Review.

Steps:
1) Obtain a short-lived user access token via the OAuth dialog
   Replace {app-id} and {redirect-uri} with your app values and open in your browser:

   https://www.facebook.com/v17.0/dialog/oauth?client_id={app-id}&redirect_uri={redirect-uri}&scope=instagram_basic,instagram_content_publish,pages_read_engagement,pages_show_list

   After granting permissions you'll be redirected to {redirect-uri}?code={code}

2) Exchange the code for a short-lived token (use your app secret)
   curl -X GET "https://graph.facebook.com/v17.0/oauth/access_token?client_id={app-id}&redirect_uri={redirect-uri}&client_secret={app-secret}&code={code}"

   Response contains access_token (short-lived).

3) Exchange the short-lived token for a long-lived token
   curl -X GET "https://graph.facebook.com/v17.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short_lived_token}"

   Response contains access_token (long-lived, usually ~60 days).

4) (Optional) Extend long-lived token for pages if needed (see Facebook docs)

5) Get your Instagram user ID linked to your Facebook Page
   - First get a Page access token and list connected Instagram account:
   curl -X GET "https://graph.facebook.com/v17.0/{page_id}?fields=instagram_business_account&access_token={page_access_token}"

   The response will include instagram_business_account {"id": "<INSTAGRAM_USER_ID>"}

6) Set environment variables on your server (do NOT commit):
   export INSTAGRAM_ACCESS_TOKEN="<long_lived_token>"
   export INSTAGRAM_USER_ID="<instagram_user_id>"

Notes:
- Tokens eventually expire. For long-running automation, store tokens securely and refresh as needed. Facebook provides token exchange and page token flows.
- Ensure your Facebook App has the necessary permissions and that the user granting tokens is an admin of the connected Page.

If you want, I can produce exact, filled-in curl commands once you provide your app-id, app-secret, page_id, and redirect-uri (you can paste them privately on your server, not in chat).