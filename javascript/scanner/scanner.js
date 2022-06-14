#!/usr/bin/env node

"use strict";

import fs from "fs";
import process from "process";
import fetch from "node-fetch";
import FormData from "form-data";
import sleep from "sleep-promise";
import { URLSearchParams } from "url";

class APIError extends Error {
    name = "APIError";
}

async function fetchToken(address, clientId, clientSecret, scopes) {
    const params = new URLSearchParams();
    params.append("grant_type", "client_credentials");
    params.append("client_id", clientId);
    params.append("client_secret", clientSecret);
    params.append("audience", "f-secure-atlant");
    if (scopes != null) {
        params.append("scope", scopes.join(" "));
    }
    const response = await fetch(
        `https://${address}/api/token/v1`,
        {
            method: "POST",
            body: params
        }
    );
    const data = await response.json();
    if (response.status === 200) {
        return data;
    }
    throw new APIError(`${data["error"]}: ${data["error_description"]}`);
}

async function scanFile(address, token, path) {
    const metadata = {};
    const formData = new FormData();
    formData.append("metadata", JSON.stringify(metadata));
    formData.append("data", fs.createReadStream(path));
    let headers = formData.getHeaders();
    headers["Authorization"] = `Bearer ${token}`;
    const response = await fetch(
        `https://${address}/api/scan/v1`,
        {
            method: "POST",
            body: formData,
            headers: headers
        }
    );
    if (response.status === 200 || response.status === 202) {
        let data = await response.json();
        let retryAfter = response.headers.get("Retry-After");
        if (retryAfter != null) {
            retryAfter = parseInt(retryAfter, 10);
        }
        data["retry_after"] = retryAfter;
        data["poll_url"] = response.headers.get("Location");
        return data;
    }
    throw new APIError(`scan error (${response.status})`);
}

async function pollTask(address, token, taskURL) {
    const response = await fetch(
        `https://${address}${taskURL}`,
        {
            headers: {
                "Authorization": `Bearer ${token}`
            }
        }
    );
    if (response.status === 200) {
        return await response.json();
    }
    throw new APIError(`poll error (${response.status})`);
}

async function scanAndPollUntilDone(address, token, path) {
    let response = await scanFile(address, token, path);
    switch (response["status"]) {
    case "complete":
        return response;
    case "pending":
        const taskURL = response["task_url"];
        await sleep(response["retry_after"]);
        pending:
        while (true) {
            response = await pollTask(address, token, taskURL);
            switch (response["status"]) {
            case "complete":
                return response;
            case "pending":
                await sleep(response["retry_after"]);
                continue;
            default:
                break pending;
            }
        }
    }
    throw new APIError(`scan error (${response.status})`);
}

async function main() {
    if (process.argv.length != 7) {
        console.error("usage: atlant-scanner AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE");
        process.exit(1);
    }

    const [,, authAddress, scanAddress, clientID, clientSecret, filePath] = process.argv;

    try {
        const tokenResponse = await fetchToken(authAddress, clientID, clientSecret, ["scan"]);
        const token = tokenResponse["access_token"];
        const scanResponse = await scanAndPollUntilDone(scanAddress, token, filePath);
        console.log(scanResponse);
    } catch (err) {
        console.error(err);
        process.exit(1);
    }
}

main();
