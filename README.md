# Real or AI?

A simple browser game: can you tell a real photo from an AI-generated image?

**Play it here:** https://danhammo6.github.io/realOrAi

## Run locally

Just open `index.html` in a browser — or for best results run a tiny local server (some browsers block local file `fetch`/image loads):

```bash
python3 -m http.server 8000
# then open http://localhost:8000
```

## Deploy to GitHub Pages

1. Create a new GitHub repo and push this folder to it.
2. In the repo → **Settings** → **Pages** → set **Source** to `Deploy from a branch`, branch `main`, folder `/ (root)`.
3. Your game will be live at `https://<username>.github.io/<repo-name>/`.

## Add more images

Drop files into `images/real/` or `images/ai/`, then add an entry in `images.js`:

```js
{ src: "images/ai/my_image.png", isAI: true, alt: "...", caption: "..." },
```

## Image credits

All starter images are from [Wikimedia Commons](https://commons.wikimedia.org) under free licenses (CC-BY / CC-BY-SA / public domain). AI images are drawn from Commons' AI-generated categories; real photos are from the Featured Pictures categories.
