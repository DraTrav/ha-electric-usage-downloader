import aiohttp
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import base64
import re

_LOGGER = logging.getLogger(__name__)

class ElectricUsageAPI:
    """Handles communication with the PEC SmartHub portal."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str, login_url: str, usage_url: str):
        """Initialize the API client."""
        self.session = session
        self.username = username
        self.password = password
        self.login_url = login_url
        self.usage_url = usage_url
        self.cookies = None

    async def login(self):
        """Log in to the PEC SmartHub and retrieve session cookies."""
        payload = {
            "UserName": self.username,
            "Password": self.password
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        try:
            async with self.session.post(self.login_url, data=payload, headers=headers) as response:
                if response.status == 200:
                    _LOGGER.debug("Successfully logged in to PEC SmartHub")
                    self.cookies = response.cookies
                else:
                    _LOGGER.error(f"Failed to log in to PEC SmartHub: {response.status}")
                    raise Exception("Login failed")
        except Exception as e:
            _LOGGER.error(f"Error during login: {e}")
            raise

    async def get_usage_data(self):
        """Fetch electric usage data by scraping the PEC SmartHub portal."""
        if not self.cookies:
            await self.login()

        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        try:
            # Get yesterday's date
            yesterday = datetime.now() - timedelta(days=1)

            # Set the time to midnight (00:00:00)
            yesterday_midnight = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)

            # Convert to timestamp in milliseconds
            timestamp_ms = int(yesterday_midnight.timestamp() * 1000)


            url_query = f"start={timestamp_ms}&end={timestamp_ms}&systemOfRecord=UTILTIY&useOpenId=false&timeFrame=DAILY&industry=ELECTRIC&includeInactive=false&usageType=KWH"
            base64_url = base64.b64encode(url_query.encode()).decode()
            fixed_usage_url = self.usage_url[:-5]
            _LOGGER.debug(fixed_usage_url)

            async with self.session.get(f"{fixed_usage_url}{base64_url}", cookies=self.cookies, headers=headers) as response:
                _LOGGER.debug(f"{self.usage_url[:-5]}?{base64_url}")
                if response.status != 200:
                    _LOGGER.error(f"Failed to fetch usage data: {response.status}")
                    return None
                await asyncio.sleep(5)
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")

                # Parse the usage data
                usage_data = self._parse_usage_data(soup)
                return usage_data
        except Exception as e:
            _LOGGER.error(f"Error fetching usage data: {e}")
            return None

    def _parse_usage_data(self, soup):
        """Parse the electric usage data from the HTML soup."""
        try:
            text = soup.get_text()
            _LOGGER.debug(f"{text}")
            match = re.search(r"Total\s*\$?([0-9]+\.[0-9]{2})", text)

            usage_value = match.group(1)
            return {"usage": float(usage_value)}
        except Exception as e:
            _LOGGER.error(f"Error parsing usage data: {e}")
            return None
