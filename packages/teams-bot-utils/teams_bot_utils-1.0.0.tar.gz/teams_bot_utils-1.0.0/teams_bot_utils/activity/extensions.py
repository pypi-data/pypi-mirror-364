"""
Extensions for Activity class to add helper methods
"""

from botbuilder.schema import Activity
from typing import Tuple, Set
import logging


def extend_activity_class():
    """
    Add helper methods to the Activity class
    """
    # Add check_message_contents method to Activity
    Activity.check_message_contents = check_message_contents


def check_message_contents(
    activity: Activity,
) -> Tuple[bool, int, int, Set[str]]:
    """
    Determine if a message contains text, images, and files in general.

    Args:
        activity (Activity): The activity object containing message information.

    Returns:
        Tuple[bool, int, int, Set[str]]: A tuple containing:
            - A boolean indicating if the message contains text.
            - The count of files in the message.
            - The count of image files in the message.
            - The extensions of the files in the message.
    """
    extensions: Set[str] = set()
    file_count = 0
    image_count = 0
    has_text = isinstance(activity.text, str) and len(activity.text.strip()) > 0

    if not activity.attachments:
        return has_text, 0, 0, extensions

    for attachment in activity.attachments:
        # Handle HTML content type specifically
        if attachment.content_type == "text/html":
            logging.info(f"Received HTML content: {attachment.content}")
            continue

        # Check if the attachment has a name
        if attachment.name:
            ext = attachment.name.split(".")[-1].lower()  # Normalize the extension
            file_count += 1

            # Check for supported image extensions
            if ext in {"jpeg", "jpg", "png", "gif", "webp"}:
                image_count += 1

            extensions.add(ext)

            # Check for specific content type for images
            if attachment.content_type in [
                "image/png",
                "image/jpeg",
                "image/gif",
                "image/webp",
            ]:
                image_count += 1  # Ensure images are counted correctly
        else:
            # Handle cases where the name is not present but content type indicates an image
            if attachment.content_type and attachment.content_type.startswith("image/"):
                image_count += 1
                file_count += 1
                ext = attachment.content_type.split("/")[1]
                extensions.add(ext)
            elif (
                attachment.content_type
                == "application/vnd.microsoft.teams.file.download.info"
            ):
                # Teams file download information
                file_count += 1
                if isinstance(attachment.content, dict) and attachment.content.get(
                    "downloadUrl", ""
                ).lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
                    image_count += 1
                    url = attachment.content.get("downloadUrl", "")
                    ext = url.split(".")[-1].lower()
                    extensions.add(ext)

    return has_text, file_count, image_count, extensions
