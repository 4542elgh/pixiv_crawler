# pixiv_crawler
Pull with `docker pull ghcr.io/4542elgh/pixiv_crawler:main`

## Environmental Variable:<br/>
-e ZIP_PASSWORD=123456

## Volume Mount variable:<br/>
-v ./cookies.pkl:/app/cookies.pkl<br/>
-v /mnt/Download:/download

## Sample Docker-Compose.yaml
```yaml
version: "3"

services:
  pixiv_crawler:
    image: ghcr.io/4542elgh/pixiv_crawler:main
    environment:
      ZIP_PASSWORD: /run/secrets/zip-pass
    volumes:
      - /mnt/Download:/download
      - /mnt/Download/pixiv_crawler/cookies.pkl:/app/cookies.pkl
    secrets:
      - zip-pass

secrets:
  zip-pass:
    external: true
```
