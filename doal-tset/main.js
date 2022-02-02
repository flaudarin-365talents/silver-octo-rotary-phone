#!/usr/bin/env node
import process, { exit } from "process";
import * as http from "http";

const cliArgs = process.argv;

if (cliArgs.length != 4) {
  console.error(
    "Bad number of arguments:\n",
    "SYNTAX:\n  main.js <client> <number of requests>"
  );
  exit(1);
}

const client = cliArgs[2];
const numberOfRequest = cliArgs[3];
const reqDelay = 2500; // ms

console.log("Number of API calls requested:", numberOfRequest);
console.log(`Delay between API calls: ${reqDelay} ms`);

// Starts a timer
const startTime = performance.now();

const sleepNow = (delay) =>
  new Promise((resolve) => setTimeout(resolve, delay));

async function repeatedGreetingsLoop() {
  for (let count = 1; count <= numberOfRequest; count++) {
    // HTTP request's setup
    const options = {
      hostname: "localhost",
      port: 9090,
      path: `/${client}/get_ref`,
      method: "GET",
      headers: {
        Accept: "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        Connection: "keep-alive",
        "User-Agent": "Doal-Tset/1.0.0",
      },
      timeout: 20000,
    };

    // Creates the HTTP request
    const req = http.request(options, (res) => {
      const status = res.statusCode;
      console.log(`Response #${count} status ${status}`);
      let respBodyChunks = [];
      let respBodyChunksSizes = [];
      res
        .on("data", (chunk) => {
          // console.log(`reveived: ${chunk.length} chars`);
          respBodyChunks.push(chunk);
          respBodyChunksSizes.push(chunk.length);
        })
        .on("end", () => {
          const endTime = performance.now() - startTime;
          const respBody = Buffer.concat(respBodyChunks).toString();
          const respBodySize = respBodyChunksSizes.reduce((s0, s1) => s0 + s1);
          // console.log(respBody);
          console.log(
            `Response #${count}: received ${
              respBodySize / 1024
            } kB; elapsed time ${endTime.toFixed(3)} ms`
          );
        });
    });

    // Handles HTTP errors
    req.on("error", (e) => {
      console.error(`problem with request: ${e.message}`);
    });

    // Send data
    req.end();
    console.log(`Sent request #${count}`);
    await sleepNow(reqDelay);
  }
}

repeatedGreetingsLoop();
