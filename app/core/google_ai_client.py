import google.generativeai as genai
from PIL import Image
from io import BytesIO
import base64
import os
from app.config.settings import GOOGLE_API_KEY

# Initialize Google Generative AI client with API key
genai.configure(api_key=GOOGLE_API_KEY)

class ImageColorizer:
    """
    A class to handle colorization of black and white images using Google's Generative AI API
    """
    
    def __init__(self, model_name="gemini-2.5-flash-image-preview"):
        """
        Initialize the colorizer with a specific model
        """
        self.model = genai.GenerativeModel(model_name)
        self.prompt = (
            "You are an expert at colorizing black and white photographs. "
            "Please colorize this black and white photo with realistic, historically accurate colors. "
            "Focus on creating natural skin tones, accurate clothing colors for the time period, and "
            "realistic environmental colors. Make it look like it was originally shot in color. "
            "Keep the composition exactly the same - only add color."
        )
    
    async def colorize_image(self, image_bytes):
        """
        Process a black and white image and return the colorized version
        
        Args:
            image_bytes (bytes): Raw binary data of the image
            
        Returns:
            bytes: Colorized image data
        """
        try:
            # Create PIL image from bytes
            img = Image.open(BytesIO(image_bytes))
            
            # Create the generation config for image generation
            # Based on best practices from Nano Banana documentation
            generation_config = genai.GenerationConfig(
                temperature=0.2,  # Lower temperature for more accurate colorization
                candidate_count=1,
            )
            
            # Create the safety settings with proper import from the package
            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
            }
            
            # Generate the content
            response = self.model.generate_content(
                contents=[self.prompt, img],
                generation_config=generation_config,
                safety_settings=safety_settings,
            )
            
            # Extract the image data from the response
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data:
                    # Per the documentation, inline_data.data contains the base64 encoded image
                    return base64.b64decode(part.inline_data.data)
            
            # If no image data found in the response
            raise Exception("No colorized image was returned by the model")
            
        except Exception as e:
            print(f"Error colorizing image: {str(e)}")
            raise