from src.Error.NotExpectedType import NotExpectedType
from src.Error.NegativeNumber import NegativeNumber

class URLSearchBuilder:
    def build_url(
        self,
        initial_url,
        search_location,
        encoded_query,
        search_config,
        params_for_builder,
        page=1
    ):
        url = str(initial_url)
        on_path = []
        on_query = []

        # Handle search query
        search_param = search_config.get('param')
        if search_location == "path":
            on_path.append((encoded_query, '/'))

        elif search_location == "query" and search_param:
            order = int(search_config['order'])

            if order == 0:
                on_query.append((f'{search_param}={encoded_query}', '?'))
            elif order > 0:
                on_query.append((f'{search_param}={encoded_query}', '&'))
            else:
                raise NegativeNumber('order', order)

        # Handle other parameters (sorted by order)
        for param_info in params_for_builder:
            location = param_info["location"]
            format_str = param_info["format"]
            param_key = param_info["param_key"]
            default_value = param_info["default_value"]
            before_key_union = param_info.get("before_key_union", "")
            order = param_info.get("order", None)

            # Calculate the value based on page number
            pagination_type = param_info["type"]
            if pagination_type == "page":
                value = page
            elif pagination_type == "offset":
                value = default_value * page
            else:
                raise NotExpectedType("offset or page", pagination_type)

            # Format the parameter using the format string
            formatted_param = format_str.format(key=param_key, value=value)

            if location == "path":
                on_path.append((formatted_param, before_key_union))

            elif location == "query":
                if order == 0 and not on_query:
                    on_query.append((formatted_param, '?'))
                else:
                    on_query.append((formatted_param, '&'))

        # Build final URL
        parts = on_path + on_query
        for part, union in parts:
            url += union + part

        return url