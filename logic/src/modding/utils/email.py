def generate_message_email_html_template(email: str, message: str) -> str:
    return f"""
        <h3>User {email} is sending you a message:</h3>
        <p>{message}</p>
        <br/>
        <h5>Start a student, become an expert</h5>
        <h4>ModdingCode</h4>
    """
