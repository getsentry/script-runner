import {Config} from './types.tsx'

class Api {
  private getJson(endpoint: string) {
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
