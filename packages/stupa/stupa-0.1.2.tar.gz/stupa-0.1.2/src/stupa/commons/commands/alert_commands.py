import logging
import requests
import os


class AlertHandler:
    """
    Generic Alert Handler class to handle various alert destinations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
        self.discord_bot_username = os.getenv(
            "DISCORD_BOT_USERNAME")  # Default fallback

        if not self.discord_webhook_url:
            self.logger.warning(
                "DISCORD_WEBHOOK_URL environment variable not set")

    def send_discord_alert(self, message):
        """
        Send alert to Discord channel via webhook.
        """
        if not self.discord_webhook_url:
            self.logger.error("Discord webhook URL not configured")
            return False

        data = {
            "content": message,
            "username": self.discord_bot_username
        }

        self.logger.info(f"Sending Discord alert")
        try:
            response = requests.post(self.discord_webhook_url, data=data)
            if response.ok:
                self.logger.info("Discord alert sent successfully")
                return True
            else:
                self.logger.error(
                    f"Failed to send Discord alert: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error sending Discord alert: {str(e)}")
            return False

    def send_alert(self, message, destinations=None):
        """
        Send alert to specified destinations or default to Discord.

        Args:
            message (str): Alert message to send
            destinations (list): List of destinations ['discord', 'slack', 'email']
                               If None, defaults to ['discord']
        """
        if destinations is None:
            destinations = ['discord']

        results = {}

        for destination in destinations:
            if destination.lower() == 'discord':
                results['discord'] = self.send_discord_alert(message)
            elif destination.lower() == 'slack':
                # Placeholder for future Slack implementation
                self.logger.warning("Slack alerts not yet implemented")
                results['slack'] = False
            elif destination.lower() == 'email':
                # Placeholder for future Email implementation
                self.logger.warning("Email alerts not yet implemented")
                results['email'] = False
            else:
                self.logger.warning(
                    f"Unknown alert destination: {destination}")
                results[destination] = False

        return results
