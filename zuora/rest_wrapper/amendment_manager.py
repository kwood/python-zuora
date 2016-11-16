import logging

import requests

from request_base import RequestBase, rest_client_reconnect


# This hack suppresses a `urllib3.InsecureRequestWarning` warning; This noisy
# warning is only introduced here. Instead of printing this out on each request
# to Zuora's amendment endpoint. See this note for details: https://urllib3.readthedocs.io/en/latest/security.html
logging.captureWarnings(True)


class AmendmentManager(RequestBase):
    """
    Request class that allows users to fetch Amendment data from Zuora.
    """
    @rest_client_reconnect
    def get_amendment_by_subscription_id(self, subscription_id, page_size=20):
        """
        Returns a dictionary of Amendment data given a specific Subscription ID (or key).
        References:
            * https://knowledgecenter.zuora.com/DC_Developers/REST_API/B_REST_API_reference/Amendments/Get_Amendments_By_Subscription_Id
        Usage:
            * zuora_client.rest_client.amendment.get_amendment_by_subscription_id('2c92a0fd57e07d490157e3889ff837f4')
            * zuora_client.rest_client.amendment.get_amendment_by_subscription_id('A-S00001503')
        Notes:
            The Zuora API only returns a single Amendment for each version of
            a subscription.
        """
        full_url = '{}amendments/subscriptions/{}'.format(
            self.zuora_config.base_url,
            subscription_id
        )

        response = requests.get(
            full_url,
            params={'pageSize': page_size},
            headers=self.zuora_config.headers,
            verify=False
        )
        return self.get_json(response)
