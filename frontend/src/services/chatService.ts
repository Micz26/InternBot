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

interface ChatResponseItem {
  content: string;
  additional_kwargs?: {
    refusal?: any;
  };
}

type ChatResponse = ChatResponseItem[];

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
      
      // Handle array response format from backend
      if (Array.isArray(response.data) && response.data.length > 0) {
        // Get the last item's content (the final AI response)
        const lastItem = response.data[response.data.length - 1];
        if (lastItem.content) {
          return lastItem.content;
        }
      }
      
      return 'Sorry, I received an empty response.';
    } catch (error) {
      console.error('Chat service error:', error);
      throw new Error('Failed to send message. Please try again.');
    }
  },

  // Audio functionality removed - not relevant for internship recommendations
};