"""
Mixpanel telemetry implementation for bot tracking
"""

from mixpanel import Mixpanel
import logging
from datetime import datetime
from typing import Optional, Dict, Any


class BotTelemetry:
    """Handles tracking and telemetry for bots using Mixpanel"""

    def __init__(self, token: str, api_secret: Optional[str] = None):
        """
        Initialize the telemetry client

        Args:
            token (str): Mixpanel project token
            api_secret (str): Optional Mixpanel API secret for identity merges
        """
        self.mp = Mixpanel(token)
        self.api_secret = api_secret
        logging.info(f"Telemetry initialized with token: {token[:4]}...{token[-4:]}")

    def track(
        self, event: str, distinct_id: str, properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track an event in Mixpanel

        Args:
            event (str): Event name
            distinct_id (str): User identifier
            properties (Dict): Additional properties to track

        Returns:
            bool: Success status
        """
        try:
            props = properties or {}
            # Add timestamp if not present
            if "timestamp" not in props:
                props["timestamp"] = datetime.now().isoformat()

            # Add source information
            props["source"] = "Teams Bot"

            logging.info(f"Tracking event: {event} for user: {distinct_id}")
            self.mp.track(distinct_id, event, props)
            return True
        except Exception as e:
            logging.error(f"Error tracking event {event}: {str(e)}")
            return False

    def track_bot_installed(
        self, team_id: str, user_id: str, channel_id: Optional[str] = None
    ) -> bool:
        """
        Track bot installation event

        Args:
            team_id (str): Teams team ID
            user_id (str): User who added the bot
            channel_id (str): Channel where bot was added

        Returns:
            bool: Success status
        """
        properties = {
            "team_id": team_id,
            "installer_id": user_id,
            "event_type": "installation",
        }

        if channel_id:
            properties["channel_id"] = channel_id

        return self.track("Bot Installed", user_id, properties)

    def track_message_received(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        copilot_id: Optional[str] = None,
        has_text: bool = False,
        has_image: bool = False,
        text_length: Optional[int] = None,
    ) -> bool:
        """
        Track when a message is received from a user

        Args:
            user_id (str): User who sent the message
            session_id (str): Active session ID
            copilot_id (str): Active copilot ID
            has_text (bool): Whether message contains text
            has_image (bool): Whether message contains an image
            text_length (int): Length of text if present

        Returns:
            bool: Success status
        """
        properties = {
            "has_text": has_text,
            "has_image": has_image,
            "event_type": "message",
        }

        if text_length is not None:
            properties["text_length"] = text_length

        if session_id:
            properties["session_id"] = session_id

        if copilot_id:
            properties["agent_code"] = copilot_id

        return self.track("Message Received", user_id, properties)

    def track_response_sent(
        self,
        user_id: str,
        session_id: Optional[str] = None,
        copilot_id: Optional[str] = None,
        response_time_ms: Optional[int] = None,
        has_image: bool = False,
        success: bool = True,
        text_length: Optional[int] = None,
    ) -> bool:
        """
        Track when a response is sent to a user

        Args:
            user_id (str): User who received the response
            session_id (str): Active session ID
            copilot_id (str): Active copilot ID
            response_time_ms (int): Response time in milliseconds
            has_image (bool): Whether response contains an image
            success (bool): Whether the request was successful
            text_length (int): Length of response text

        Returns:
            bool: Success status
        """
        properties = {
            "has_image": has_image,
            "success": success,
            "event_type": "response",
        }

        if text_length is not None:
            properties["text_length"] = text_length

        if response_time_ms is not None:
            properties["response_time_ms"] = response_time_ms

        if session_id:
            properties["session_id"] = session_id

        if copilot_id:
            properties["agent_code"] = copilot_id

        return self.track("Response Sent", user_id, properties)

    def track_command_used(
        self, user_id: str, command_name: str, success: bool = True
    ) -> bool:
        """
        Track when a command is used

        Args:
            user_id (str): User who used the command
            command_name (str): Name of the command
            success (bool): Whether the command was successful

        Returns:
            bool: Success status
        """
        properties = {
            "command": command_name,
            "success": success,
            "event_type": "command",
        }

        return self.track("Command Used", user_id, properties)

    ##New code starts here
    def extract_user_identifiers(self, activity):
        """
        Extract user identifiers from Teams activity

        Args:
            activity: Teams activity object

        Returns:
            dict: Dictionary containing user identifiers
        """
        identifiers = {
            "teams_id": None,
            "aad_id": None,
            "email": None,
            "name": None,
            "conversation_id": None,
        }

        # Extract Teams ID
        if hasattr(activity, "from_property") and hasattr(activity.from_property, "id"):
            identifiers["teams_id"] = activity.from_property.id

        # Extract AAD ID
        if hasattr(activity, "from_property") and hasattr(
            activity.from_property, "aad_object_id"
        ):
            identifiers["aad_id"] = activity.from_property.aad_object_id

        # Extract name
        if hasattr(activity, "from_property") and hasattr(
            activity.from_property, "name"
        ):
            identifiers["name"] = activity.from_property.name

        # Try to extract email
        if hasattr(activity, "channel_data") and activity.channel_data:
            channel_data = activity.channel_data
            if isinstance(channel_data, dict):
                if "email" in channel_data:
                    identifiers["email"] = channel_data["email"]
                elif (
                    "from" in channel_data
                    and isinstance(channel_data["from"], dict)
                    and "email" in channel_data["from"]
                ):
                    identifiers["email"] = channel_data["from"]["email"]

        # Extract conversation ID
        if hasattr(activity, "conversation") and hasattr(activity.conversation, "id"):
            identifiers["conversation_id"] = activity.conversation.id
        return identifiers

    def set_user_profile(self, distinct_id: str, user_info: Dict[str, Any]) -> bool:
        """
        Set properties for a user profile in Mixpanel

        Args:
            distinct_id: User identifier
            user_info: User properties to set

        Returns:
            bool: Success status
        """
        try:
            self.mp.people_set(distinct_id, user_info)
            return True
        except Exception as e:
            logging.error(f"Error setting user profile: {str(e)}")
            return False

    def merge_user_identities(self, distinct_id1: str, distinct_id2: str) -> bool:
        """
        Merge two user identities in Mixpanel

        Args:
            distinct_id1: First distinct ID
            distinct_id2: Second distinct ID

        Returns:
            bool: Success status
        """
        if not self.api_secret:
            logging.warning("Cannot merge identities: API secret not provided")
            return False

        try:
            self.mp.merge(
                api_key=None,  # Deprecated but required parameter
                distinct_id1=distinct_id1,
                distinct_id2=distinct_id2,
                api_secret=self.api_secret,
            )
            logging.info(f"Merged user identities: {distinct_id1} and {distinct_id2}")
            return True
        except Exception as e:
            logging.error(f"Error merging user identities: {str(e)}")
            return False

    def identify_and_track(
        self, event: str, activity, properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Identify user, update profile, and track event

        Args:
            event: Event name
            activity: Teams activity object
            properties: Event properties

        Returns:
            bool: Success status
        """
        # Extract user identifiers
        user_ids = self.extract_user_identifiers(activity)

        # Choose best identifier as distinct_id (prefer email > aad_id > teams_id)
        distinct_id = (
            user_ids.get("email") or user_ids.get("aad_id") or user_ids.get("teams_id")
        )

        if not distinct_id:
            logging.warning("Could not determine distinct_id for user")
            return False

        # Update user profile
        profile_props = {
            "$last_seen": datetime.now().isoformat(),
            "platform": "MS Teams",
        }

        if user_ids.get("name"):
            profile_props["$name"] = user_ids.get("name")
        if user_ids.get("email"):
            profile_props["$email"] = user_ids.get("email")
        if user_ids.get("teams_id"):
            profile_props["teams_id"] = user_ids.get("teams_id")
        if user_ids.get("aad_id"):
            profile_props["aad_id"] = user_ids.get("aad_id")
        # Add conversation ID to profile properties
        if user_ids.get("conversation_id"):
            profile_props["conversation_id"] = user_ids.get("conversation_id")

        self.set_user_profile(distinct_id, profile_props)

        # Try to merge identities if we have both email and teams_id
        if self.api_secret and user_ids.get("email") and user_ids.get("teams_id"):
            self.merge_user_identities(user_ids.get("email"), user_ids.get("teams_id"))

        # Track the event
        event_props = properties or {}
        # Add conversation ID to event properties
        if user_ids.get("conversation_id") and "conversation_id" not in event_props:
            event_props["conversation_id"] = user_ids.get("conversation_id")
        return self.track(event, distinct_id, event_props)
