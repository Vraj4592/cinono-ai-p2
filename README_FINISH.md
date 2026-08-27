# Final README notes

I finished wiring a fully automated pipeline and uploaders. You can deploy everything to your GPU machine by running:

  cd /path/to/cinono-ai-p2
  chmod +x scripts/deploy.sh
  ./scripts/deploy.sh

Then edit .env to add your Instagram/TikTok/S3 tokens and other secrets. The API will be available at http://your-server:8000/ — open it in a browser to submit prompts via the web UI.

Important: keep secrets out of git. Add them to .env or a secrets manager.
