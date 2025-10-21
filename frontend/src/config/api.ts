// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  BACKEND_URL: BACKEND_URL,
  ENDPOINTS: {
    // Message endpoints
    GET_TITLES: `${API_BASE_URL}/get_titles`,
    LOAD_MESSAGE: `${API_BASE_URL}/load_message`,
    DELETE_MESSAGE: `${API_BASE_URL}/delete_message`,
    APPEND_MESSAGE: `${API_BASE_URL}/append_message`,
    
    // File endpoints
    FOLDER_LIST: `${API_BASE_URL}/folder_list`,
    CREATE_FOLDER: `${API_BASE_URL}/create_folder`,
    DELETE_FOLDER: `${API_BASE_URL}/delete_folder`,
    DELETE_FILE: `${API_BASE_URL}/delete_file`,
    UPLOAD_FILE: `${API_BASE_URL}/upload_file`,
    DOWNLOAD_FILE: `${API_BASE_URL}/download_file`,
    SELECT_FOLDER: `${API_BASE_URL}/select_folder`,
    
    // Agent endpoints
    GET_CONFIG: `${API_BASE_URL}/get_config`,
    AGENTS_SELECTION: `${API_BASE_URL}/agents_selection`,
    
    // Search endpoints
    NEWS: `${API_BASE_URL}/news`,
    REPORT: `${API_BASE_URL}/report`,
    STREAM_COMPLETION: `${API_BASE_URL}/stream_completion`,
    STREAM_COMPLETION_ACADEMIC: `${API_BASE_URL}/stream_completion_academic`,
    STREAM_DATA: `${API_BASE_URL}/stream_data`,
  }
};

export default API_CONFIG;
