import os
from typing import Dict, Any
from volcengine.visual.VisualService import VisualService


def parse_seededit_response(response) -> Dict[str, Any]:
    """
    Parse the seededit API response and extract the image URL.
    
    :param response: The API response dictionary
    :return: JSON response with status, data (image URL), and message
    """
    try:
        # Handle both possible response formats
        if 'data' in response and 'image_urls' in response['data']:
            # Format 1: {'data': {'image_urls': [...]}}
            image_urls = response['data']['image_urls']
        elif 'image_urls' in response:
            # Format 2: {'image_urls': [...]}
            image_urls = response['image_urls']
        else:
            raise ValueError("No image_urls found in response")
        
        if not image_urls or len(image_urls) == 0:
            raise ValueError("Empty image_urls list")
        
        # Get the first URL and clean it
        url = image_urls[0]
        # Remove leading/trailing whitespace and backticks
        url = url.strip().strip('`').strip()
        
        return {
            "status": "success",
            "data": {"image_url": url},
            "message": "Image URL parsed successfully"
        }
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Failed to parse response: {e}"
        }


def seededit(image_url, prompt, charactor_keep=False, return_url=True, scale=1, seed=-1) -> Dict[str, Any]:
    """
    Perform image editing using the VisualService.

    :param image_url: URL of the input image.
    :param prompt: The editing prompt.
    :param charactor_keep: Whether to keep the main character in the image.
    :param return_url: Whether to return image URL or base64 string.
    :param scale: Text influence scale (0.1-1.0).
    :param seed: Random seed for reproducibility.
    :return: JSON response with status, data (image URL), and message.
    """
    try:
        visual_service = VisualService()

        # call below method if you don't set ak and sk in $HOME/.volc/config
        ak = os.getenv('VOLC_AK')
        sk = os.getenv('VOLC_SK')

        if not ak or not sk:
            return {
                "status": "error",
                "data": None,
                "message": "VOLC_AK and VOLC_SK environment variables must be set"
            }

        visual_service.set_ak(ak)
        visual_service.set_sk(sk)

        form = {
            "req_key": "seed3l_single_ip" if charactor_keep else "seededit_v3.0",
            "image_urls": [image_url],
            'prompt': prompt,
            'return_url': return_url,
            'scale': scale,
            'seed': seed,
        }

        response = visual_service.cv_process(form)
        return parse_seededit_response(response)
    except Exception as e:
        return {
            "status": "error",
            "data": None,
            "message": f"Error in seededit: {str(e)}"
        }


if __name__ == '__main__':
    print(seededit('https://carey.tos-ap-southeast-1.bytepluses.com/Art%20Portrait/Art%20Portrait/Art%20Portrait/Art%20Portrait%20(1).jpg', prompt='在和边钓鱼', charactor_keep=False))