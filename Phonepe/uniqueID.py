import uuid


# Generate unique IDs for Phonepe Autopay
def generate_unique_id(model, field_name):
    """
    Generates a unique ID for a specific field in a Django model.
    """
    while True:
        unique_id = str(uuid.uuid4())  # Generate a random UUID
        if not model.objects.filter(**{field_name: unique_id}).exists():
            return unique_id