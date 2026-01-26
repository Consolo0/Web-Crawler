class URLSearchBuilder:
    def build_url(
        self,
        initial_url,
        search_location,
        encoded_query,
        search_param,
        params_for_builder,
        page=1
    ):
        url = initial_url
        on_path = []
        on_query = []

        # Handle search query
        if search_location == "path":
            on_path.append(encoded_query)
        elif search_location == "query" and search_param:
            on_query.append(f'{search_param}={encoded_query}')

        # Handle other parameters (sorted by order)
        for param_info in params_for_builder:
            location = param_info["location"]
            format_str = param_info["format"]
            param_key = param_info["param_key"]
            default_value = param_info["default_value"]

            # Calculate the value based on page number
            if param_info["name"] == "page":
                value = page
            else:
                value = default_value * page

            # Format the parameter using the format string
            formatted_param = format_str.format(key=param_key, value=value)

            if location == "path":
                on_path.append(formatted_param)
            elif location == "query":
                on_query.append(formatted_param)

        # Build final URL
        path_part = '/'.join(on_path) if on_path else ''
        query_part = '&'.join(on_query) if on_query else ''

        result_url = url
        if path_part:
            result_url += '/' + path_part
        if query_part:
            result_url += '?' + query_part

        return result_url