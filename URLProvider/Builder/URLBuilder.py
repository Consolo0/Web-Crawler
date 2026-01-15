class URLBuilder:
    def build_url(
        self,
        initial_url,
        search_location,
        encoded_query,
        search_param,
        pagination_param__location,
        pagination_params_name_and_initial_value,
        page=1
    ):
        url = initial_url

        on_path = []
        on_query = []

        if search_location == "path":
            on_path.append(encoded_query)
        elif search_location == "query" and search_param:
            on_query.append(f'{search_param}={encoded_query}')

        for param_name, initial_value in pagination_params_name_and_initial_value:

            if pagination_param__location == "query":
                on_query.append(f'{param_name}={initial_value*page}')

            elif pagination_param__location == "path":
                on_path.append(param_name)
                on_path.append(initial_value*page)
        
        return url+'/'+'/'.join(on_path)+'?'+'&'.join(on_query)