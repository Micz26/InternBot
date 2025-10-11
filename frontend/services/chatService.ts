import axios from 'axios';
import { BACKEND_URL } from '../lib/consts';

interface Location {
  lat: number;
  lng: number;
}

interface ChatRequest {
  query: string;
  location?: Location;
}

interface ChatAudioResponse {
  text: string;
  audio_base64: string;
}

interface ChatResponse {
  output: string;
  // Add other response fields as needed based on your API
}

export const chatService = {
  async sendMessage(query: string, location?: Location | null): Promise<string> {
    try {
      const requestData: ChatRequest = { query: query };
      
      if (location) {
        requestData.location = location;
      }
      
      const response = await axios.post<ChatResponse>(`${BACKEND_URL}/agent/invoke`, requestData);
      
      return response.data.output || 'Sorry, I received an empty response.';
    } catch {
      throw new Error('Failed to send message. Please try again.');
    }
  },
};