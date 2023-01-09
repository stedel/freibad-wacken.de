# freibad-wacken.de

Website for the Förderverein Freibad Wacken created with hugo static site generator with Toha theme.

Hosted at <https://freibad-wacken.de>.

Before starting the dev server, get the theme hugo mod and npm dependencies:

```sh
hugo mod npm pack
hugo mod tidy
npm install
```

If the theme is updated, start the dev server:
```sh
hugo server --watch --enableGitInfo
```

