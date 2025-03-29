from fastapi import Request

def get_client_ip(request: Request) -> str:
    """
    Extract the client's IP address from the HTTP request.

    Args:
        request (Request): The FastAPI Request object.

    Returns:
        str: The client's IP address.
    """
    # Extract the IP address from the request
    return request.client.host
