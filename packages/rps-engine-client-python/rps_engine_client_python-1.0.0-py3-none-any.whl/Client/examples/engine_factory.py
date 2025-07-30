"""Get the RPS Engine class after all configuration."""
from Client.auth.credentials_token_provider import ClientCredentialsTokenProvider
from Client.engine.rps_engine import RPSEngine
from Client.engine.rps_engine_converter import RPSEngineConverter
from Client.engine_client_options import EngineClientOptions
from Client.engine_context.rps_engine_context_json_file_provider import RPSEngineContextJsonFileProvider
from Client.engine_context.rps_engine_context_resolver import RPSEngineContextResolver
from Client.engine_context.rps_engine_context_settings_provider import RPSEngineContextSettingsProvider
from Client.json.engine_json_rest_api_client import EngineJsonRestApiClient
from Client.settings import Settings

class EngineFactory:
    """Provide the RPS Engine instance, after configuration

    Method:
        get_engine(): Configure options, create provider and context resolver and return RPS Engine instance.
    """
    @classmethod
    def get_engine(cls):
        """Configure options, create provider and context resolver and return RPS Engine instance.

        Returns:
            RPSEngine: Configured RPS Engine instance.
        """
        settings = Settings()
        engine_client_options = EngineClientOptions(settings=settings)

        engine_provider = EngineJsonRestApiClient(engine_client_options,
            ClientCredentialsTokenProvider(client_options=engine_client_options))

        rps_engine_context_resolver = RPSEngineContextResolver(RPSEngineContextJsonFileProvider(
            settings.external_source_files.rightsContextsFilePath,
            settings.external_source_files.processingContextsFilePath))

        # Uncomment the following lines if you want to use
        # settings-based context provider instead of JSON files as context source.
        
        # rps_engine_context_resolver = RPSEngineContextResolver(RPSEngineContextSettingsProvider(
        #     settings.rights_contexts, settings.processing_contexts))

        return RPSEngine(engine_provider, RPSEngineConverter(), rps_engine_context_resolver)
