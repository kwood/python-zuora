import json
import requests

import logging
log = logging.getLogger(__name__)

from request_base import RequestBase, rest_client_reconnect
from zuora.rest_wrapper.amendment_manager import AmendmentManager


class SubscriptionManager(RequestBase):

    @rest_client_reconnect
    def get_subscriptions_by_account(self, accountKey, pageSize=10, page=1):
        fullUrl = self.zuora_config.base_url + 'subscriptions/accounts/' + \
                  accountKey
        data = {'pageSize': pageSize, 'page': page}

        response = requests.get(fullUrl, params=data,
                                headers=self.zuora_config.headers)
        return self.get_json(response)

    @rest_client_reconnect
    def get_subscription_by_key(self, subsKey):
        fullUrl = self.zuora_config.base_url + 'subscriptions/' + subsKey
        response = requests.get(fullUrl, headers=self.zuora_config.headers)
        return self.get_json(response)

    @rest_client_reconnect
    def get_subscriptions_by_key(self, subsKey):
        return self.get_subscription_by_key(subsKey)

    @rest_client_reconnect
    def renew_subscription(self, subsKey,
                           jsonParams={'invoiceCollect': False}):
        fullUrl = self.zuora_config.base_url + 'subscriptions/' + subsKey + \
                  '/renew'
        data = json.dumps(jsonParams)
        response = requests.put(fullUrl, data=data,
                                headers=self.zuora_config.headers
        )
        return self.get_json(response)

    @rest_client_reconnect
    def cancel_subscription(self, subsKey, jsonParams={}):
        jsonParams.setdefault('cancellationPolicy',
                              self.zuora_config.default_cancellation_policy)
        fullUrl = self.zuora_config.base_url + 'subscriptions/' + subsKey + \
                  '/cancel'
        data = json.dumps(jsonParams)
        log.info("Zuora REST: Canceling subscription: %s" % subsKey)
        response = requests.put(fullUrl, data=data,
                                headers=self.zuora_config.headers)
        return self.get_json(response)

    @rest_client_reconnect
    def preview_subscription(self, jsonParams):
        fullUrl = self.zuora_config.base_url + 'subscriptions/preview'
        data = json.dumps(jsonParams)
        response = requests.post(fullUrl, data=data,
                                 headers=self.zuora_config.headers)
        return self.get_json(response)

    @rest_client_reconnect
    def create_subscription(self, jsonParams):
        fullUrl = self.zuora_config.base_url + 'subscriptions'
        data = json.dumps(jsonParams)
        response = requests.post(fullUrl, data=data,
                                 headers=self.zuora_config.headers)
        return self.get_json(response)

    @rest_client_reconnect
    def update_subscription(self, subsKey, jsonParams):
        fullUrl = self.zuora_config.base_url + 'subscriptions/' + subsKey
        data = json.dumps(jsonParams)
        response = requests.put(fullUrl, data=data,
                                headers=self.zuora_config.headers)
        return self.get_json(response)


    def get_each_subscription_version_and_all_mutating_amendments(self, subscription_key):
        """
        Returns a mixed list of subscriptions and amendments ordered by date.

        Esssentially, this returns a list of sub + amendment dictionaries, starting
        with the earliest version of the subscription and steps forward through
        each amendment until we reach the most current version of the subscription.

        The returned dict should look like:
        [
            {'type': 'subscritpion', 'subscritpion_id': '1'},
            {'type': 'amendment', 'amendment_id': '1', 'changes': ...},
            {'type': 'subscritpion', 'subscritpion_id': '2'},
            {'type': 'amendment', 'amendment_id': '2', 'changes': ...},
            {'type': 'subscritpion', 'subscritpion_id': '3'},
        ]
        """
        subscription_and_amendment_list = []

        # Fetch the most recent version of the subsription given a subscription key
        subscription_response = self.get_subscriptions_by_key(subscription_key)

        # Do not process unsuccessful responses
        if not subscription_response.get('success', False):
            raise Exception('Could not find a subscription for key: {}'.format(subscription_key))

        # The way that Zuora's API is structured, it always returns the most recent
        # version of a subscription first, then steps backwards through time
        # to fetch amendments + subscription versions until reaches the original
        # subscription version.
        amendment_manager = AmendmentManager(self.zuora_config)
        subscription_id = subscription_response.get('id')
        has_valid_amendment = True
        while has_valid_amendment:
            subscription_response = self.get_subscriptions_by_key(subscription_id)

            # Do not process unsuccessful responses
            if not subscription_response.get('success', False):
                raise Exception('Could not find a subscription for id: {}'.format(subscription_id))

            # Append the subscription to the list of of subs + amendments
            subscription_response.update({'obj_type': 'subscription'})
            subscription_and_amendment_list.append(subscription_response)

            # Get the amendment prior to this version of the subscription
            amendment_response = amendment_manager.get_amendment_by_subscription_id(subscription_id)

            # If one does not exist, then we have reached the original subscription
            # should return the list of subscription versionss
            if not amendment_response.get('success', False):
                has_valid_amendment = False

            # Append the amdment to the list of subs + amendments
            amendment_response.update({'obj_type': 'amendment'})
            subscription_and_amendment_list.append(amendment_response)

            # Update the subscription_id (to fetch the next most recent version of the subscription)
            subscription_id = amendment_response.get('baseSubscriptionId')

        # Reverse the list of amendments + subs and return
        subscription_and_amendment_list.reverse()
        return subscription_and_amendment_list
