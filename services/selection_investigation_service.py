from abc import ABCMeta, abstractmethod
import logging

class SelectionInvestigationService(object):
    __metaclass__ = ABCMeta

    def __init__(self, selected_mcnp_card):
        """
        Initialize the selection investigation service.

        Args:
            selected_mcnp_card (MCNPCard): The selected MCNP card object.
        """
        self.selected_mcnp_card = selected_mcnp_card
        self.logger = logging.getLogger(self.__class__.__name__)

    def investigate_selection(self):
        result = self.perform_investigation()
        if result.get("success"):
            self.logger.info("Investigation Successful")
        else:
            self.logger.error("Investigation Failed")
        return result
