import { Config, RunResult, OptionResult } from "./types.tsx";

class Api {
  private getJson(endpoint: string) {
    return fetch(endpoint).then(response => response.json());
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

  async getAutocompleteOptions(data: { group: string, function: string, regions: string[] }): Promise<OptionResult> {
    const { group, function: functionName, regions } = data;

    const searchParams = new URLSearchParams({
      group,
      function: functionName,
      regions: regions.join(","),
    }).toString();


    return await this.getJson("/autocomplete?" + searchParams);
  }
}

export default Api;
