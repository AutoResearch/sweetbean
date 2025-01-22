from jinja2 import Template


def demographic(age, gender):
    """
    Creates a personalized message using age and gender.

    Parameters:
        age (int): The age of the individual.
        gender (str): The gender of the individual (e.g., 'man', 'woman').

    Returns:
        str: A formatted message based on the given demographics.

    Example:
        >>> demographic(52, 'woman')
        'You are a 52-year-old woman.'

    """

    # Template for generating the message
    template = "You are a {{ age }}-year-old {{ gender }}."

    # Render the template with local variables
    return Template(template).render(age=age, gender=gender)
