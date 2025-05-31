import subprocess
from pathlib import Path


def embed_thumbnail_in_audio(audio_file_path, thumbnail_path, force_replace_thumbnail=True, output_path=None):
    """
    Embeds a thumbnail image into an audio file using FFmpeg.
    Supports: MP3, M4A, FLAC, OGG, MP4, AAC, and more.
    Handles files that already have embedded thumbnails by replacing them.

    Args:
        audio_file_path (str): Path to the input audio file
        thumbnail_path (str): Path to the thumbnail image (jpg, png, webp, etc.)
        output_path (str, optional): Path for output file. If None, overwrites the original.

    Returns:
        bool: True if successful, False if failed
    """
    try:
        # Convert paths to Path objects for easier handling
        audio_path = Path(audio_file_path)
        thumb_path = Path(thumbnail_path)

        # Validate input files exist
        if not audio_path.exists():
            print(f"Error: Audio file not found: {audio_path}")
            return False

        if not thumb_path.exists():
            print(f"Error: Thumbnail file not found: {thumb_path}")
            return False

        # Check if file already has embedded thumbnail
        has_thumbnail = check_existing_thumbnail(audio_path)
        
        # Get file extension to determine format
        audio_ext = audio_path.suffix.lower()

        # Set output path - if not provided, create a temp file then replace original
        if output_path is None:
            temp_output = audio_path.with_suffix(f".temp{audio_ext}")
            final_output = audio_path
        else:
            temp_output = Path(output_path)
            final_output = temp_output

        if has_thumbnail:
            if force_replace_thumbnail:
                print(f"  → File already has embedded thumbnail, replacing...")
                # For files with existing thumbnails, we need to replace not add
                cmd = [
                    "ffmpeg",
                    "-i", str(audio_path),     # Input audio file
                    "-i", str(thumb_path),     # Input new thumbnail
                    "-map", "0:a",             # Map only audio from first input
                    "-map", "1:v",             # Map thumbnail from second input
                    "-c:a", "copy",            # Copy audio without re-encoding
                ]
        else:
            print(f"  → Adding new thumbnail...")
            # For files without thumbnails, add normally
            cmd = [
                "ffmpeg",
                "-i", str(audio_path),     # Input audio file
                "-i", str(thumb_path),     # Input thumbnail image
                "-map", "0",               # Map all streams from first input
                "-map", "1",               # Map thumbnail from second input
                "-c:a", "copy",            # Copy audio without re-encoding
            ]

        # Format-specific video codec settings
        if audio_ext in [".mp3"]:
            cmd.extend(["-c:v", "mjpeg"])
        elif audio_ext in [".m4a", ".mp4", ".aac"]:
            cmd.extend(["-c:v", "mjpeg", "-disposition:v:0", "attached_pic"])
        elif audio_ext in [".flac"]:
            cmd.extend(["-c:v", "mjpeg"])
        elif audio_ext in [".ogg"]:
            cmd.extend(["-c:v", "mjpeg"])
        else:
            cmd.extend(["-c:v", "mjpeg"])

        cmd.extend(["-y", str(temp_output)])  # Overwrite output file

        # Run FFmpeg command
        print(f"Embedding thumbnail into {audio_path.name} ({audio_ext.upper()})...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            # If using temp file, replace original
            if output_path is None:
                temp_output.replace(final_output)

            print(f"✓ Successfully embedded thumbnail in {final_output.name}")
            return True
        else:
            print(f"✗ FFmpeg error: {result.stderr}")
            # Clean up temp file if it exists
            if temp_output.exists() and output_path is None:
                temp_output.unlink()
            return False

    except Exception as e:
        print(f"✗ Error embedding thumbnail: {str(e)}")
        return False


def check_existing_thumbnail(audio_path):
    """
    Check if an audio file already has an embedded thumbnail.
    
    Args:
        audio_path (Path): Path to the audio file
        
    Returns:
        bool: True if thumbnail exists, False otherwise
    """
    try:
        cmd = ["ffprobe", "-v", "quiet", "-show_streams", "-select_streams", "v", str(audio_path)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        
        # If there's video stream output, the file has an embedded image
        return len(result.stdout.strip()) > 0
        
    except Exception:
        return False


def merge_thumbnails_with_audio_files(downloads_folder):
    """
    Finds audio files and their corresponding thumbnails, then embeds them.
    Supports: MP3, M4A, FLAC, OGG, AAC, MP4

    Args:
        downloads_folder (str): Path to the downloads folder
    """
    downloads_path = Path(downloads_folder)

    # Find all supported audio files
    audio_extensions = ["*.m4a", "*.mp3", "*.flac", "*.ogg", "*.aac", "*.mp4"]
    audio_files = []

    for pattern in audio_extensions:
        audio_files.extend(downloads_path.rglob(pattern))

    for audio_file in audio_files:
        print(f"\nProcessing: {audio_file.name}")

        # Look for corresponding thumbnail files
        thumbnail_extensions = [".jpg", ".jpeg", ".png", ".webp"]

        thumbnail_file = None
        for ext in thumbnail_extensions:
            potential_thumb = audio_file.with_suffix(ext)
            if potential_thumb.exists():
                thumbnail_file = potential_thumb
                break

        if thumbnail_file:
            success = embed_thumbnail_in_audio(audio_file, thumbnail_file)
            if success:
                print(f"  → Thumbnail embedded from {thumbnail_file.name}")
            else:
                print("  → Failed to embed thumbnail")
        else:
            print(f"  → No thumbnail found for {audio_file.name}")
