#!/usr/bin/env node

import * as esbuild from "esbuild";
import process from "node:process";

const options = {
  entryPoints: ["src/index.jsx"],
  bundle: true,
  minify: true,
  sourcemap: true,
  outfile: "www/dist/bundle.js",
  platform: "browser",
  target: ["es2020"],
  logLevel: "info",
  loader: {
    ".js": "jsx",
  },
  define: {
    API_URL_BASE: JSON.stringify(process.env["API_URL_BASE"] ?? null),
  },
};

const build = async () => await esbuild.build(options);

const watch = async () => {
  let context = await esbuild.context(options);
  await context.watch();
};

const serve = async () => {
  let context = await esbuild.context(options);
  let { host, port } = await context.serve({
    servedir: "www",
    onRequest: (request) => {
      console.log(`${request.method} ${request.path} => ${request.status}`);
    },
  });
};

const actions = {
  build: build,
  serve: serve,
  watch: watch,
};

await actions[process.argv[2] ?? "build"]();
