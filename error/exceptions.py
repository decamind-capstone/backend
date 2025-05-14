from fastapi import HTTPException, status

class MissingFieldData(HTTPException):
    def __init__(self, fields: list):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Missing required fields: {', '.join(fields)}"
        )

class ConversationNotFound(HTTPException):
    def __init__(self):
        super().__init__(status_code=404, detail="Conversation not found")

class DuplicateConversationTitle(HTTPException):
    def __init__(self):
        super().__init__(status_code=409, detail="Conversation title already exists")
