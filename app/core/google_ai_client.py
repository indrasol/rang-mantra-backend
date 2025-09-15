# Core libs
import os
import base64
from io import BytesIO

# Third-party
import google.generativeai as genai
from PIL import Image

# Project settings
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
            "Colorize and restore the original photograph while keeping its authenticity. Tasks:  - Apply subtle, historically accurate colorization with natural skin tones, hair colors, and clothing hues.  - Remove blurriness and restore fine details in faces, clothing, and background.  - Repair discoloration, fading, stains, and spots while preserving the natural texture and grain.  - Avoid oversaturation or artificial enhancements.  - Should look like AI generated  Goal: Deliver a clean, sharp, and realistic version of the original photograph that feels historically authentic and emotionally true to its time."
        )
    

    async def colorize_image(self, image_bytes, prompt_override: str | None = None):
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
            
            # Validate and preprocess image
            if img.mode not in ['RGB', 'RGBA', 'L', 'P']:
                img = img.convert('RGB')
            
            # Resize if image is too large (max 2048x2048 for better API performance)
            max_size = 2048
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Create the generation config for image generation
            # Based on best practices from Nano Banana documentation
            generation_config = genai.GenerationConfig(
                temperature=0.2,  # Lower temperature for more accurate colorization
                candidate_count=1,
            )

            safety_settings = {
                "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
                "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
            }

            prompt_to_use = prompt_override or self.prompt
            response = self.model.generate_content(
                contents=[prompt_to_use, img],
                generation_config=generation_config,
                safety_settings=safety_settings,
            )

            # Extract the image data from the response
            for part in response.candidates[0].content.parts:
                inline = getattr(part, "inline_data", None)
                if not inline:
                    continue
                if inline.mime_type and not inline.mime_type.startswith("image/"):
                    continue
                if not inline.data:
                    continue

                data_blob = inline.data  # could be str (base64) or bytes (raw image or base64 bytes)

                # If it's already raw image bytes (PNG or JPEG signature), use it directly
                if isinstance(data_blob, (bytes, bytearray)):
                    if data_blob[:8] == b"\x89PNG\r\n\x1a\n" or data_blob[:2] == b"\xff\xd8":
                        raw_bytes = bytes(data_blob)
                    else:
                        # treat as base64 bytes and decode
                        try:
                            raw_bytes = base64.b64decode(data_blob)
                        except Exception as be:
                            continue
                else:
                    # data_blob is str
                    data_str = data_blob
                    if data_str.strip().startswith("data:") and "," in data_str:
                        data_str = data_str.split(",", 1)[1]
                    try:
                        raw_bytes = base64.b64decode(data_str)
                    except Exception as se:
                        continue

                # now have raw_bytes

                try:
                    pil_img = Image.open(BytesIO(raw_bytes))
                    buf = BytesIO()
                    pil_img.save(buf, format="PNG")
                    buf.seek(0)
                    png_bytes = buf.getvalue()
                    return png_bytes
                except Exception as conv_err:
                    return raw_bytes

            raise Exception("The AI model couldn't process this image. Please try with a different black and white photo.")
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error colorizing image: {error_msg}")
            
            # Provide specific error messages for better user experience
            if "cannot identify image file" in error_msg.lower():
                raise Exception("Invalid image format. Please upload a valid image file (JPEG, PNG, etc.)")
            elif "image file is truncated" in error_msg.lower():
                raise Exception("The image file appears to be corrupted. Please try uploading a different image.")
            elif "AI model couldn't process" in error_msg:
                raise Exception(error_msg)  # Pass through AI processing message
            else:
                raise Exception("Failed to process the image. Please try again with a black and white photo.")