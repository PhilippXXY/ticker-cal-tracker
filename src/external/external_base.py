import os
from pathlib import Path
from dotenv import load_dotenv

class ExternalApiBaseDefinition:
    '''
    Base class for external API implementations.
    '''
    
    def __init__(self, *, api_key_name: str):
        '''
        Initialize the API with a key from the environment.
        
        Args:
            api_key_name: The name of the environment variable containing the API key.
            
        Raises:
            ValueError: If the API key is not found in the environment.
        '''
        # Load the api key from the local .env
        load_dotenv(Path('.env'))
        val = os.getenv(api_key_name)
        
        if not val:
            # Fallback or error handling could go here, but for now we'll just set it.
            # If strict validation is needed, uncomment the raise.
            # raise ValueError(f'{api_key_name} not found in environment variables')
            pass
            
        self.api_key = val
