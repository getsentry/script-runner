import { Config, RunResult } from "./types.tsx";

class Api {
  private getJson(endpoint: string) {
    return fetch(endpoint).then((response) => {
      console.log("[getJson] Raw Response Status:", response.status);
      console.log("[getJson] Raw Response Headers:", response.headers);
      // Clone the response to log the body, as it can only be read once
      return response
        .clone()
        .text()
        .then((text) => {
          console.log("[getJson] Raw Response Body Text:", text);
          // Now call the original json() method
          return response.json();
        });
    });
  }

  private postJson(endpoint: string, data: unknown) {
    return fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    }).then((response) => {
      if (!response.ok) {
        return response.json().then((err) => {
          return Promise.reject(err);
        });
      }
      return response.json();
    });
  }

  async getConfig(): Promise<Config> {
    return await this.getJson("/config");
  }

  async run(data: unknown): Promise<RunResult> {
    return await this.postJson("/run", data);
  }
}

export default Api;
