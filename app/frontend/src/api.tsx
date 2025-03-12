import {Config} from './types.tsx'

class Api {
  private useMockData: boolean;

  constructor(useMockData: boolean = false) {
    this.useMockData = useMockData;
  }

  private fetchMockData(endpoint: string): any {
    const mockResponses: {[key: string]: any} = {
      '/config': { data: {'regions': ['us', 'de', 's4s', 'c1', 'c2'], 'functions': []}},
      '/run': { success: true },
    };
    return mockResponses[endpoint] || { message: 'Unknown endpoint' };
  }

  private getJson(endpoint: string) {
    if (this.useMockData === true) {
      return this.fetchMockData(endpoint)
    }

    return fetch(endpoint).then(response => response.json())
  }

  private postJson(endpoint: string, data: any) {
    return fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
    })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => {
            return Promise.reject(err);
        });
      }
      return response.json();
    })
  }

  async getConfig(): Promise<Config> {
    return await this.getJson('/config')
  }

  async run(data: any): Promise<any> {
    return await this.postJson('/run', data)
  }

}

export default Api
