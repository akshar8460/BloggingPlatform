from __future__ import annotations

from datetime import timedelta, datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from starlette import status

from config import SECRET_KEY
from log_config import logger

ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
        Creates an access token using the given data and expiration time.
        Args:
            data (dict): The data to encode in the access token.
            expires_delta (timedelta | None, optional): The expiration time for the token.
                If None, a default expiration time of 15 minutes will be used.
                Defaults to None.
        Returns:
            str: The encoded access token.
        """
    to_encode = data.copy()
    if expires_delta:
        # Calculate expiration time if expires_delta is provided
        expire = datetime.utcnow() + expires_delta
    else:
        # Use default expiration time of 15 minutes
        expire = datetime.utcnow() + timedelta(minutes=15)

    # Add expiration time to the data to be encoded
    to_encode.update({"exp": expire})

    # Encode the data into a JWT using the secret key and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def verify_access_token(token: Annotated[str, Depends(oauth2_scheme)]):
    """
        Verifies the provided access token.
        Args:
            token (str): The access token to verify.
        Returns:
            bool: True if the token is valid, otherwise raises an HTTPException.
        """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token using the secret key and algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract the subject claim from the payload
        sub: str = payload.get("sub")

        # If subject is None, raise credentials_exception
        if sub is None:
            raise credentials_exception
    except JWTError as exc:
        logger.warning(f"Token verification failed with following exception: {exc}")
        raise credentials_exception
    return True
