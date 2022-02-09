def clean_extension(extension: str) -> str:
    result = []
    for character in extension:
        if character.isalnum():
            result.append(character)

    return "".join(result)
