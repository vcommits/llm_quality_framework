# File: agentic_red_team/driver/interceptors.py
import logging

logger = logging.getLogger("NetworkInterceptor")

class NetworkPoisoner:
    def __init__(self, poison_html):
        self.poison_html = poison_html

    async def intercept_and_inject(self, route, request):
        """
        The Handler for page.route().
        It fetches the real page, injects the poison, and serves the modified version.
        """
        # 1. Fetch the actual response from the real server
        try:
            response = await route.fetch()
        except Exception as e:
            # If request fails (e.g. ad blocker), just abort
            await route.abort()
            return

        # 2. Get the original body
        # We assume text/html for simplicity here.
        # In a full framework, you'd check headers['content-type'].
        original_body = await response.text()

        # 3. MUTATION: Inject the poison
        # We look for the closing body tag to append our payload
        if "</body>" in original_body:
            logger.info(f"[Network] Injecting poison into {request.url}")
            modified_body = original_body.replace(
                "</body>",
                f"{self.poison_html}</body>"
            )
        else:
            modified_body = original_body

        # 4. Fulfill the request with the MODIFIED data
        await route.fulfill(
            response=response,
            body=modified_body,
            headers=response.headers
        )