
class Serializer:

    @staticmethod
    def serialize_event(self, event: dict) -> dict:
        """
        Safely serialize event data for JSON encoding.
        Handles ResultIntegrator and other complex objects.
        """
        serialized = {}
        
        for key, value in event.items():
            if key == "data" and hasattr(value, 'retrieve_dict'):
                # Handle ResultIntegrator
                serialized[key] = value.retrieve_dict()
            elif isinstance(value, (str, int, float, bool, type(None))):
                serialized[key] = value
            elif isinstance(value, dict):
                serialized[key] = value  # Assume dict is already serializable
            elif isinstance(value, list):
                serialized[key] = value  # Assume list is already serializable
            else:
                # Convert other objects to string
                serialized[key] = str(value)
        
        return serialized