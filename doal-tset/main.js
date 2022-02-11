#!/usr/bin/env node
import process from "process";
import * as http from "http";
import _yargs from "yargs";
import { hideBin } from "yargs/helpers";

import { jsonLog, sleepNow } from "./utils.js";

const yargs = _yargs(hideBin(process.argv));

yargs
  .option("client", {
    describe: "client's name",
    type: "string",
    demandOption: true,
  })
  .option("num-requests", {
    describe: "number of requests to send",
    type: "number",
    default: 1,
    demandOption: false,
  })
  .option("delay", {
    describe: "delay between two requests in ms",
    type: "number",
    default: 0,
    demandOption: false,
  })
  .option("host", {
    describe: "send HTTP to this host",
    type: "string",
    default: "localhost",
    demandOption: false,
  })
  .option("port", {
    describe: "send HTTP requests to this port",
    type: "number",
    default: 80,
    demandOption: false,
  })
  .option("json", {
    describe: "set the format of output logs to JSON",
    type: "boolean",
    default: false,
    demandOption: false,
  });

const client = yargs.argv.client;
const numberOfRequests = yargs.argv.numRequests;
const reqDelay = yargs.argv.delay; // ms
const enableJsonLogs = yargs.argv.json;

if (enableJsonLogs) {
  jsonLog({
    event: "start",
    numberOfRequests: numberOfRequests,
    delayBetwRequests: reqDelay,
    units: {
      time: "ms",
      size: "kByte",
    },
  });
} else {
  console.log("Number of API calls requested:", numberOfRequests);
  console.log(`Delay between API calls: ${reqDelay} ms`);
}
async function repeatedGreetingsLoop() {
  for (let count = 1; count <= numberOfRequests; count++) {
    // Starts a timer
    const startTime = performance.now();

    // HTTP request's setup
    const options = {
      hostname: yargs.argv.host,
      port: yargs.argv.port,
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
      if (!enableJsonLogs) {
        console.log(`Response #${count} status ${status}`);
      }

      // Response data chunks
      let respBodyChunks = [];

      // Size of data chunks
      let respBodyChunksSizes = [];
      res
        // On getting response body chunks
        .on("data", (chunk) => {
          respBodyChunks.push(chunk);
          respBodyChunksSizes.push(chunk.length);
        })
        // On the transaction's end
        .on("end", () => {
          const endTime = performance.now() - startTime;
          /* Concatenates the response body and converts to string
          const respBody = Buffer.concat(respBodyChunks).toString(); */
          const respBodySize = respBodyChunksSizes.reduce((s0, s1) => s0 + s1);

          // Writes response log to STDOUT
          if (enableJsonLogs) {
            jsonLog({
              event: "response",
              number: count,
              status,
              size: respBodySize / 1024,
              time: endTime.toFixed(3),
            });
          } else {
            console.log(
              `Response #${count}: received ${
                respBodySize / 1024
              } kB; elapsed time ${endTime.toFixed(3)} ms`
            );
          }
        });
    });

    // Handles HTTP errors
    req.on("error", (err) => {
      if (enableJsonLogs) {
        jsonLog({
          event: "error",
          message: err.message,
        });
      } else {
        console.error(`problem with request: ${err.message}`);
      }
    });

    // Sends request
    req.end();

    // Writes log 'A request was sent' to STDOUT
    if (enableJsonLogs) {
      jsonLog({
        event: "sent",
        number: count,
      });
    } else {
      console.log(`Sent request #${count}`);
    }
    if (reqDelay > 0) {
      await sleepNow(reqDelay);
    }
  }
}

repeatedGreetingsLoop();
