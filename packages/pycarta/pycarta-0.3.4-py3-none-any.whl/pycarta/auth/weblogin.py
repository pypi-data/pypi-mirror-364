import threading
import time
import uvicorn
from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware


# Where the server will be hosted.
HOST = "http://localhost"
PORT = 3000


class CognitoLoginServer:
    def __init__(self, client_id, region, user_pool, *, log_level="error"):
        self.process = None
        self.token = None
        self.client_id = client_id
        self.region = region
        self.user_pool = user_pool
        self._thread = None
        self._server = None
        self._log_level = log_level
        
    def run(self):
        self_ = self  # capture self to use in routes.

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key="pycarta-weblogin-secret-key")

        # Setup OAuth
        oauth = OAuth()
        # Cognito Config
        oauth.register(
            name='oidc',
            authority=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool}",
            client_id=self.client_id,
            server_metadata_url=f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool}/.well-known/openid-configuration",
            client_kwargs={'scope': 'aws.cognito.signin.user.admin email openid profile'}
        )

        @app.get("/", response_class=HTMLResponse)
        async def index(request: Request):
            self_.token = await oauth.oidc.authorize_access_token(request)
            userinfo = self_.token["userinfo"]
            given, family = userinfo["given_name"], userinfo["family_name"]
            return f"Welcome, {given} {family}! You have been logged in. You may close this window."

        @app.get("/login")
        async def login(request: Request):
            return await oauth.oidc.authorize_redirect(request, f"{HOST}:{PORT}")
        
        config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level=self._log_level)
        self._server = uvicorn.Server(config=config)
        self._server.run()
        # uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="error")

    def __enter__(self):
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()
        # Wait for server to start
        while self._server is None or not self._server.started:
            time.sleep(0.1)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._server:
            self._server.should_exit = True
            # self._server.force_exit = True
            self._server = None
        if self._thread:
            self._thread.join(timeout=3)
            self._thread = None
        return exc_val is None
    
    def is_finished(self) -> bool:
        return self.token is not None
