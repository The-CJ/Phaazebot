from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from main import Phaazebot

def emergencyTwitchClientCredentialTokenRefresh(cls:"Phaazebot") -> None:
	# this will run the protocol to refresh the twitch credentials
	# this should be automated by external scripts, but lets be safe
	from Utils.Protocols.generatetwitchapptoken import GenerateTwitchCredentials
	Protocol:GenerateTwitchCredentials = GenerateTwitchCredentials()
	Protocol.log_func = cls.Logger.warning
	Protocol.force = True
	new_token:str = Protocol.main()
	cls.Access.twitch_client_credential_token = new_token
