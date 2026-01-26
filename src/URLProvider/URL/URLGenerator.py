from src.Navigator.NavigatorOrchestator import NavigatorOrchestrator
from src.Navigator.DataStructure.AbstractNavigator import AbstractNavigator
from src.URLProvider.Encoder.QueryEncoder import QueryEncoder
from src.URLProvider.Builder.URLSearchBuilder import URLSearchBuilder
from src.URLProvider.URLType.URLType import URLType
from src.Setters.Query.Query import Query

class URLGenerator:
    def __init__(self, sources_metadata, query: Query, navigation_strategy):
        self.sources_metadata = sources_metadata
        self.query = query
        self.navigation_strategy = navigation_strategy
        self.url_search_builder = URLSearchBuilder()
        self.query_encoder = QueryEncoder()

    def run(self) -> AbstractNavigator:
        navigator = NavigatorOrchestrator.get_navigator(self.navigation_strategy.type)
        sources = self.sources_metadata.keys()
        print(f"URLGenerator - Processing sources: {list(sources)}")

        for source in sources:
            try:
                for nav_rule in self.sources_metadata[source]["NavRules"]:

                    query_param_mapping = nav_rule.get("QueryParamMapping", {})

                    if nav_rule["NavType"].lower().strip() == URLType.SEARCH.value:

                        if nav_rule["PaginationType"].lower() == "page":
                            for i in range(1, nav_rule["MaxPages"] + 1):

                                url = self.generate_search_url(
                                    nav_rule, query_param_mapping, page=i
                                )
                                navigator.add(source, url, 0, URLType.SEARCH.value)

                        else:
                            continue  # Otros tipos de paginación pueden ser manejados aquí

            except Exception as e:
                print(f"Error processing source {source}: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()
                continue
            
        return navigator

    def generate_search_url(self, nav_rule, query_param_mapping, page=None) -> str:
        initial_url = nav_rule["UrlTemplate"]

        search_config = query_param_mapping.get("search", {})
        search_location = search_config.get("location")
        encoding_type = search_config.get("transform")
        search_param = search_config.get("param", None)

        encoded_query = self.query_encoder.encode(self.query.query, encoding_type)

        other_params = query_param_mapping.get("other_params", {})
        sorted_params = sorted(
            other_params.items(),
            key=lambda x: x[1].get("order", float('inf'))
        ) #Tengo mis dudas si este sort funciona

        params_for_builder = []
        for param_name, param_config in sorted_params:
            param_info = {
                "name": param_name,
                "location": param_config.get("location"),
                "param_key": param_config.get("param", {}).get("key"),
                "format": param_config.get("format"),
                "default_value": param_config.get("param", {}).get("defaultValue"),
                "order": param_config.get("order")
            }
            params_for_builder.append(param_info)

        search_url_built = self.url_search_builder.build_url(
            initial_url,
            search_location,
            encoded_query,
            search_param,
            params_for_builder,
            page
        )

        return search_url_built