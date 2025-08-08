from fastapi import Request

JTI_EXPIRY = 3600

async def add_jti_to_blocklist(jti: str, request: Request) -> None:
    token_blocklist = request.app.state.redis
    await token_blocklist.set(name=jti, value="", ex=JTI_EXPIRY)

async def token_in_blocklist(jti: str, request: Request) -> bool:
    token_blocklist = request.app.state.redis
    exists = await token_blocklist.exists(jti)
    return exists == 1

