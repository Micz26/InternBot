import axios from 'axios';
import { BACKEND_URL, API_ENDPOINTS } from '../lib/consts';

interface Location {
  lat: number;
  lng: number;
}

interface ChatRequest {
  query: string;
  config?: Record<string, any>;
  location?: Location;
}

// interface ChatAudioResponse {
//   text: string;
//   audio_base64: string;
// }

interface ChatResponse {
  output?: string;
  content?: string;
  messages?: Array<{
    content: string;
    type?: string;
  }>;
}

export const chatService = {
  async sendMessage(query: string, location?: Location | null): Promise<string> {
    try {
      const requestData: ChatRequest = { 
        query: query,
        config: {}
      };
      
      if (location) {
        requestData.location = location;
      }
      
      const response = await axios.post<ChatResponse>(`${BACKEND_URL}${API_ENDPOINTS.AGENT_INVOKE}`, requestData);
      
      // Handle different response formats
      if (response.data.output) {
        return response.data.output;
      }
      
      if (response.data.content) {
        return response.data.content;
      }
      
      if (response.data.messages && response.data.messages.length > 0) {
        // Find the last message with content
        const lastMessage = response.data.messages[response.data.messages.length - 1];
        return lastMessage.content || 'Sorry, I received an empty response.';
      }
      
      return 'Sorry, I received an empty response.';
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message. Please try again.');
    }
  },

  // Audio functionality removed - not relevant for internship recommendations
};