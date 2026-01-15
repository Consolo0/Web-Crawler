from Navigator.NavigatorOrchestator import NavigatorOrchestator
from urllib.parse import quote_plus
from URLProvider.Encoder.QueryEncoder import QueryEncoder

class URLGenerator:
    def __init__(self, sources_metadata, query, navigation_strategy):
        self.sources_metadata = sources_metadata
        self.query = query
        self.navigation_strategy = navigation_strategy
        self.url_builder = URLBuilder()
        self.query_encoder = QueryEncoder()

    def run(self):
        navigator = NavigatorOrchestator.get_navigator(self.navigation_strategy.type)
        
        #Por ahora solo haremos una busqueda por search
        for source in self.sources_metadata:
            for nav_rule in self.sources_metadata[source]["NavRules"]:
                
                query_param_mapping = nav_rule.get("QueryParamMapping", {})
                if nav_rule["Type"].lower() == "search":

                    if nav_rule["PaginationType"].lower() == "page":
                        for i in range(1, nav_rule["MaxPages"] + 1):
                            url = self.generate_search_url(
                                query_param_mapping, page=i
                            )
                            navigator.add_url(source, url)
                    else:
                        continue  # Otros tipos de paginación pueden ser manejados aquí

    def generate_search_url(self, nav_rule, query_param_mapping, page=None) -> str:
        initial_url = nav_rule["UrlTemplate"]

        search_location = query_param_mapping["search"]["location"] #path o query
        encoding_type = query_param_mapping["search"]["transform"]
        search_param = query_param_mapping["search"].get("param", None)

        encoded_query = self.query_encoder.encode(self.query, encoding_type) 

        pagination_param__location = query_param_mapping["page"]["location"]
        pagination_params_name_and_initial_value = [
            (variable, query_param_mapping["page"]["param"][variable]["defaultValue"])
            for variable in query_param_mapping["page"]["param"]
        ]

        url_builder = self.url_builder.build_url(
            initial_url,
            search_location,
            encoded_query,
            search_param,
            pagination_param__location,
            pagination_params_name_and_initial_value,
            page
        )

        return url_builder.build()