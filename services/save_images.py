import os
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, requests


async def save_image(image, route_name:str, name:str) -> Optional[str]:
    """
    Saves an image in the media directory under the specified route name folder.

    Args:
        image: The image file to save (either a file object or a string path).
        route_name: The name of the route/folder where the image should be saved.
        name: Name to append to the file (default: None).

    Returns:
        str: The relative path where the image was saved, or None on error.
    """
    if not image:
        return None

    # Create media/{route_name} directory if it doesn't exist
    save_path = Path(f"./media/{route_name}")
    save_path.mkdir(parents=True, exist_ok=True)

    try:
        if isinstance(image, str):
            # Check if it's a URL
            if image.startswith(('http://', 'https://')):
                response = requests.get(image)
                response.raise_for_status()

                # Extract file extension and name from URL
                url_path = Path(image.split('?')[0])  # Remove query parameters
                file_extension = url_path.suffix
                safe_name = url_path.stem[:50] + f"_{name}{file_extension}"
                file_path = save_path / safe_name

                # Save the downloaded image
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return f"./media/{route_name}/{safe_name}"
            else:
                # Handle local file path
                source_path = Path(image)
                file_extension = source_path.suffix
                safe_name = source_path.stem + f"_{name}{file_extension}"
                file_path = save_path / safe_name

                # Copy the image
                with open(source_path, "rb") as src, open(file_path, "wb") as dst:
                    dst.write(src.read())
                return f"./media/{route_name}/{safe_name}"
        else:
            # Handle uploaded file objects
            filename = image.filename
            file_extension = Path(filename).suffix
            safe_name = Path(filename).stem + f"_{name}{file_extension}"
            file_path = save_path / safe_name

            # Save the image
            with open(file_path, "wb") as f:
                f.write(image.file.read())
            return f"./media/{route_name}/{safe_name}"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")


async def save_images( image_files, route_name):
    """
    Saves product images to the filesystem and stores their paths
    Handles both string file paths and uploaded file objects
    """
    # Create media/goods directory if it doesn't exist
    save_path = Path(f"./media/{route_name}")
    save_path.mkdir(parents=True, exist_ok=True)
    
    saved_images = []
    for image in image_files:
        if isinstance(image, str):
            # Handle string file paths
            source_path = Path(image)
            safe_name = source_path.name + ".jpg"
            file_path = save_path / safe_name
            
            # Copy the image
            with open(source_path, "rb") as src, open(file_path, "wb") as dst:
                dst.write(src.read())
        else:
            # Handle uploaded file objects
            filename = image.filename
            safe_name = Path(filename).name + ".jpg"
            file_path = save_path / safe_name
            
            # Save the image
            with open(file_path, "wb") as f:
                f.write(image.file.read())
        
        # Store relative path in images column
        saved_images.append(f"./media/{route_name}/{safe_name}")
    
    images = saved_images
    return images


# #Example Usage
# async def example_usage():
#     images = [UploadFile(filename='bbbb.jpg', size=52413, headers=Headers({'content-disposition': 'form-data; name="images"; filename="bbbb.jpg"', 'content-type': 'image/jpeg'}))]
#     route_name = "goods" #Change this to the desired folder name.
#     saved_paths = await save_images(images, route_name)
#     print(f'{saved_paths}')

# import asyncio
# if __name__ == "__main__":
#     asyncio.run(example_usage())