"""Core API client for handling HTTP requests to the Finatic API."""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, TypeVar, Generic, List
import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..types import (
    DeviceInfo,
    SessionResponse,
    OtpRequestResponse,
    OtpVerifyResponse,
    SessionAuthenticateResponse,
    PortalUrlResponse,
    SessionValidationResponse,
    UserToken,
    Holding,
    Order,
    Portfolio,
    BrokerInfo,
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    BrokerConnection,
    BrokerDataOptions,
    OrdersFilter,
    PositionsFilter,
    AccountsFilter,
    OrderResponse,
    BrokerOrderParams,
    BrokerExtras,
    CryptoOrderOptions,
    OptionsOrderOptions,
    TradingContext,
    ApiPaginationInfo,
    PaginatedResult,
)
from ..utils.errors import (
    ApiError,
    AuthenticationError,
    ValidationError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    AuthorizationError,
)

T = TypeVar('T')


class ApiClient:
    """Handles all HTTP requests to the Finatic API with proper authentication and error handling."""
    
    def __init__(
        self,
        base_url: str,
        device_info: Optional[DeviceInfo] = None,
        timeout: int = 30
    ):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            device_info: Device information for requests
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        if not self.base_url.endswith('/api/v1'):
            self.base_url = f"{self.base_url}/api/v1"
        
        self.device_info = device_info
        self.timeout = ClientTimeout(total=timeout)
        
        # Session state
        self.current_session_id: Optional[str] = None
        self.current_session_state: Optional[str] = None
        self.company_id: Optional[str] = None
        self.csrf_token: Optional[str] = None
        
        # Token management
        self.token_info: Optional[Dict[str, Any]] = None
        self.refresh_promise: Optional[asyncio.Future] = None
        self.refresh_buffer_minutes = 5
        
        # Trading context
        self.trading_context: TradingContext = TradingContext()
        
        # HTTP session
        self._session: Optional[ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._session = ClientSession(timeout=self.timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    def _get_session(self) -> ClientSession:
        """Get the HTTP session, creating one if needed."""
        if self._session is None:
            raise RuntimeError("Client not initialized. Use async context manager or call _ensure_session()")
        return self._session
    
    async def _ensure_session(self):
        """Ensure HTTP session is available."""
        if self._session is None:
            self._session = ClientSession(timeout=self.timeout)
    
    def _build_headers(self, access_token: Optional[str] = None, additional_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """Build comprehensive headers for API requests.
        
        Args:
            access_token: Access token for authentication
            additional_headers: Additional headers to include
            
        Returns:
            Dictionary of headers
        """
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add device info if available
        if self.device_info:
            headers['X-Device-Info'] = json.dumps({
                'ip_address': self.device_info.ip_address,
                'user_agent': self.device_info.user_agent,
                'fingerprint': self.device_info.fingerprint,
            })
        
        # Add session headers if available
        if self.current_session_id:
            headers['X-Session-ID'] = self.current_session_id
            headers['Session-ID'] = self.current_session_id
        
        if self.company_id:
            headers['X-Company-ID'] = self.company_id
        
        if self.csrf_token:
            headers['X-CSRF-Token'] = self.csrf_token
        
        # Add authorization header
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        
        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    async def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None,
        access_token: Optional[str] = None,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method
            path: API path
            data: Request body data
            params: Query parameters
            access_token: Access token for authentication
            additional_headers: Additional headers
            
        Returns:
            Response data
            
        Raises:
            ApiError: For API errors
            NetworkError: For network errors
            TimeoutError: For timeout errors
        """
        await self._ensure_session()
        session = self._get_session()
        
        # Build URL
        url = f"{self.base_url}{path}"
        
        # Build headers
        headers = self._build_headers(access_token, additional_headers)
        
        # Prepare request
        kwargs = {
            'headers': headers,
        }
        
        if data is not None:
            kwargs['json'] = data
        
        if params is not None:
            kwargs['params'] = params
        
        try:
            async with session.request(method, url, **kwargs) as response:
                response_text = await response.text()
                
                if not response.ok:
                    await self._handle_error_response(response.status, response_text)
                
                # Parse response
                try:
                    response_data = json.loads(response_text) if response_text else {}
                except json.JSONDecodeError:
                    raise ApiError(f"Invalid JSON response: {response_text}", response.status)
                
                # Check for API-level errors
                if isinstance(response_data, dict):
                    if response_data.get('success') is False:
                        raise ApiError(
                            response_data.get('message', 'API request failed'),
                            response_data.get('status_code', response.status),
                            response_data
                        )
                    
                    if response_data.get('status_code', 200) >= 400:
                        raise ApiError(
                            response_data.get('message', 'API request failed'),
                            response_data.get('status_code', response.status),
                            response_data
                        )
                
                return response_data
                
        except asyncio.TimeoutError:
            raise TimeoutError("Request timed out")
        except aiohttp.ClientError as e:
            raise NetworkError(f"Network error: {str(e)}")
    
    async def _handle_error_response(self, status: int, response_text: str):
        """Handle error responses from the API."""
        try:
            error_data = json.loads(response_text) if response_text else {}
        except json.JSONDecodeError:
            error_data = {"message": response_text or "Unknown error"}

        message = error_data.get("message", "Unknown error")
        
        # Provide more user-friendly error messages
        if status == 500:
            message = f"Server error: {message}. Please try again later or contact support."
        elif status == 401:
            message = f"Authentication failed: {message}. Please check your API key."
        elif status == 403:
            message = f"Access denied: {message}. Please check your permissions."
        elif status == 404:
            message = f"Resource not found: {message}. Please check the endpoint URL."
        elif status == 429:
            message = f"Rate limit exceeded: {message}. Please wait before retrying."
        elif status >= 500:
            message = f"Server error ({status}): {message}. Please try again later."
        elif status >= 400:
            message = f"Client error ({status}): {message}"

        if status == 401:
            raise AuthenticationError(message, status, error_data)
        elif status == 403:
            raise AuthorizationError(message, status, error_data)
        elif status == 422:
            raise ValidationError(message, status, error_data)
        elif status == 429:
            raise RateLimitError(message, status, error_data)
        elif status >= 500:
            raise NetworkError(message, status, error_data)
        else:
            raise ApiError(message, status, error_data)
    
    # Session management methods
    def set_session_context(self, session_id: str, company_id: str, csrf_token: Optional[str] = None):
        """Set session context for subsequent requests."""
        self.current_session_id = session_id
        self.company_id = company_id
        self.csrf_token = csrf_token
    
    def get_current_session_id(self) -> Optional[str]:
        """Get the current session ID."""
        return self.current_session_id
    
    def get_current_company_id(self) -> Optional[str]:
        """Get the current company ID."""
        return self.company_id
    
    def get_current_csrf_token(self) -> Optional[str]:
        """Get the current CSRF token."""
        return self.csrf_token
    
    # Token management methods
    def set_tokens(self, access_token: str, refresh_token: str, expires_at: str, user_id: Optional[str] = None):
        """Set authentication tokens."""
        self.token_info = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at,
            'user_id': user_id,
        }
    
    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """Get current token info."""
        return self.token_info
    
    async def get_valid_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if not self.token_info:
            raise AuthenticationError("No tokens available. Please authenticate first.")
        
        # Check if token is expired or about to expire
        if self._is_token_expired():
            await self._refresh_tokens()
        
        return self.token_info['access_token']
    
    def _is_token_expired(self) -> bool:
        """Check if the current token is expired or about to expire."""
        if not self.token_info:
            return True
        
        expires_at = datetime.fromisoformat(self.token_info['expires_at'].replace('Z', '+00:00'))
        current_time = datetime.now(expires_at.tzinfo)
        buffer_time = timedelta(minutes=self.refresh_buffer_minutes)
        
        return current_time >= expires_at - buffer_time
    
    async def _refresh_tokens(self):
        """Refresh authentication tokens."""
        if not self.token_info:
            raise AuthenticationError("No refresh token available.")
        
        # If a refresh is already in progress, wait for it
        if self.refresh_promise:
            await self.refresh_promise
            return
        
        # Start a new refresh
        self.refresh_promise = self._perform_token_refresh()
        
        try:
            await self.refresh_promise
        finally:
            self.refresh_promise = None
    
    async def _perform_token_refresh(self):
        """Perform the actual token refresh request."""
        if not self.token_info:
            raise AuthenticationError("No refresh token available.")
        
        try:
            response = await self._request(
                method='POST',
                path='/company/auth/refresh',
                data={
                    'refresh_token': self.token_info['refresh_token']
                }
            )
            
            # Update stored tokens
            self.token_info = {
                'access_token': response['response_data']['access_token'],
                'refresh_token': response['response_data']['refresh_token'],
                'expires_at': response['response_data']['expires_at'],
                'user_id': self.token_info.get('user_id')
            }
            
            return self.token_info
            
        except Exception as e:
            # Clear tokens on refresh failure
            self.token_info = None
            raise AuthenticationError(f"Token refresh failed. Please re-authenticate: {str(e)}")
    
    def clear_tokens(self):
        """Clear stored tokens."""
        self.token_info = None
        self.refresh_promise = None
    
    def get_current_session_state(self) -> Optional[str]:
        """Get current session state."""
        return self.current_session_state
    
    # Simple methods that automatically use stored tokens
    async def get_holdings_auto(self) -> List[Holding]:
        """Get holdings using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/portfolio/holdings',
            access_token=access_token
        )
        return [Holding(**holding) for holding in response.get('data', [])]
    
    async def get_orders_auto(self) -> List[Order]:
        """Get orders using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/data/orders',
            access_token=access_token
        )
        return [Order(**order) for order in response.get('data', [])]
    
    async def get_portfolio_auto(self) -> Portfolio:
        """Get portfolio using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/portfolio/',
            access_token=access_token
        )
        return Portfolio(**response.get('data', {}))
    
    async def get_broker_list_auto(self) -> List[BrokerInfo]:
        """Get broker list using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/brokers/',
            access_token=access_token
        )
        return [BrokerInfo(**broker) for broker in response.get('response_data', [])]
    
    async def get_broker_accounts(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> PaginatedResult:
        """Get broker accounts with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_type:
                params['account_type'] = filters.account_type
            if filters.status:
                params['status'] = filters.status
            if filters.currency:
                params['currency'] = filters.currency
        
        response = await self._request(
            method='GET',
            path='/brokers/data/accounts',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_type:
                    new_params['account_type'] = filters.account_type
                if filters.status:
                    new_params['status'] = filters.status
                if filters.currency:
                    new_params['currency'] = filters.currency
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/accounts',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerAccount(**account) for account in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerAccount(**account) for account in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    async def get_broker_orders(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> PaginatedResult:
        """Get broker orders with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
            if options.symbol:
                params['symbol'] = options.symbol
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_id:
                params['account_id'] = filters.account_id
            if filters.symbol:
                params['symbol'] = filters.symbol
            if filters.status:
                params['status'] = filters.status
            if filters.side:
                params['side'] = filters.side
            if filters.asset_type:
                params['asset_type'] = filters.asset_type
            if filters.created_after:
                params['created_after'] = filters.created_after
            if filters.created_before:
                params['created_before'] = filters.created_before
        
        response = await self._request(
            method='GET',
            path='/brokers/data/orders',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
                if options.symbol:
                    new_params['symbol'] = options.symbol
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_id:
                    new_params['account_id'] = filters.account_id
                if filters.symbol:
                    new_params['symbol'] = filters.symbol
                if filters.status:
                    new_params['status'] = filters.status
                if filters.side:
                    new_params['side'] = filters.side
                if filters.asset_type:
                    new_params['asset_type'] = filters.asset_type
                if filters.created_after:
                    new_params['created_after'] = filters.created_after
                if filters.created_before:
                    new_params['created_before'] = filters.created_before
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/orders',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerOrder(**order) for order in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerOrder(**order) for order in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    async def get_broker_positions(self, page: int = 1, per_page: int = 100, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> PaginatedResult:
        """Get broker positions with pagination support."""
        access_token = await self.get_valid_access_token()
        offset = (page - 1) * per_page
        
        # Build query parameters
        params = {
            'limit': str(per_page),
            'offset': str(offset),
        }
        
        if options:
            if options.broker_name:
                params['broker_name'] = options.broker_name
            if options.account_id:
                params['account_id'] = options.account_id
            if options.symbol:
                params['symbol'] = options.symbol
        
        if filters:
            if filters.broker_id:
                params['broker_id'] = filters.broker_id
            if filters.connection_id:
                params['connection_id'] = filters.connection_id
            if filters.account_id:
                params['account_id'] = filters.account_id
            if filters.symbol:
                params['symbol'] = filters.symbol
            if filters.side:
                params['side'] = filters.side
            if filters.asset_type:
                params['asset_type'] = filters.asset_type
            if filters.position_status:
                params['position_status'] = filters.position_status
            if filters.updated_after:
                params['updated_after'] = filters.updated_after
            if filters.updated_before:
                params['updated_before'] = filters.updated_before
        
        response = await self._request(
            method='GET',
            path='/brokers/data/positions',
            access_token=access_token,
            params=params
        )
        
        # Create navigation callback for pagination
        async def navigation_callback(new_offset: int, new_limit: int) -> PaginatedResult:
            new_params = {
                'limit': str(new_limit),
                'offset': str(new_offset),
            }
            
            if options:
                if options.broker_name:
                    new_params['broker_name'] = options.broker_name
                if options.account_id:
                    new_params['account_id'] = options.account_id
                if options.symbol:
                    new_params['symbol'] = options.symbol
            
            if filters:
                if filters.broker_id:
                    new_params['broker_id'] = filters.broker_id
                if filters.connection_id:
                    new_params['connection_id'] = filters.connection_id
                if filters.account_id:
                    new_params['account_id'] = filters.account_id
                if filters.symbol:
                    new_params['symbol'] = filters.symbol
                if filters.side:
                    new_params['side'] = filters.side
                if filters.asset_type:
                    new_params['asset_type'] = filters.asset_type
                if filters.position_status:
                    new_params['position_status'] = filters.position_status
                if filters.updated_after:
                    new_params['updated_after'] = filters.updated_after
                if filters.updated_before:
                    new_params['updated_before'] = filters.updated_before
            
            new_response = await self._request(
                method='GET',
                path='/brokers/data/positions',
                access_token=access_token,
                params=new_params
            )
            
            pagination_info = ApiPaginationInfo(
                has_more=new_response.get('pagination', {}).get('has_more', False),
                next_offset=new_response.get('pagination', {}).get('next_offset', new_offset),
                current_offset=new_response.get('pagination', {}).get('current_offset', new_offset),
                limit=new_response.get('pagination', {}).get('limit', new_limit),
            )
            
            return PaginatedResult(
                [BrokerPosition(**position) for position in new_response.get('response_data', [])],
                pagination_info,
                navigation_callback
            )
        
        pagination_info = ApiPaginationInfo(
            has_more=response.get('pagination', {}).get('has_more', False),
            next_offset=response.get('pagination', {}).get('next_offset', offset),
            current_offset=response.get('pagination', {}).get('current_offset', offset),
            limit=response.get('pagination', {}).get('limit', per_page),
        )
        
        return PaginatedResult(
            [BrokerPosition(**position) for position in response.get('response_data', [])],
            pagination_info,
            navigation_callback
        )
    
    # Helper methods to get all data across pages
    async def get_all_broker_accounts(self, options: Optional[BrokerDataOptions] = None, filters: Optional[AccountsFilter] = None) -> List[BrokerAccount]:
        """Get all broker accounts across all pages."""
        all_accounts = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_accounts(page, per_page, options, filters)
            if not result.data:
                break
            all_accounts.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_accounts
    
    async def get_all_broker_orders(self, options: Optional[BrokerDataOptions] = None, filters: Optional[OrdersFilter] = None) -> List[BrokerOrder]:
        """Get all broker orders across all pages."""
        all_orders = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_orders(page, per_page, options, filters)
            if not result.data:
                break
            all_orders.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_orders
    
    async def get_all_broker_positions(self, options: Optional[BrokerDataOptions] = None, filters: Optional[PositionsFilter] = None) -> List[BrokerPosition]:
        """Get all broker positions across all pages."""
        all_positions = []
        page = 1
        per_page = 100
        
        while True:
            result = await self.get_broker_positions(page, per_page, options, filters)
            if not result.data:
                break
            all_positions.extend(result.data)
            if not result.has_next:
                break
            page += 1
        
        return all_positions
    
    async def get_broker_connections_auto(self) -> List[BrokerConnection]:
        """Get broker connections using stored access token."""
        access_token = await self.get_valid_access_token()
        response = await self._request(
            method='GET',
            path='/brokers/connections',
            access_token=access_token
        )
        return [BrokerConnection(**connection) for connection in response.get('response_data', [])]
    
    # Trading context methods
    def set_broker(self, broker: str):
        """Set the current broker."""
        self.trading_context.broker = broker
    
    def set_account(self, account_number: str, account_id: Optional[str] = None):
        """Set the current account."""
        self.trading_context.account_number = account_number
        self.trading_context.account_id = account_id
    
    def get_trading_context(self) -> TradingContext:
        """Get the current trading context."""
        return self.trading_context
    
    def clear_trading_context(self):
        """Clear the trading context."""
        self.trading_context = TradingContext()
    
    def is_mock_client(self) -> bool:
        """Check if this is a mock client."""
        return False 

    async def get_portal_url(self, session_id: str) -> PortalUrlResponse:
        """Get portal URL for session."""
        response = await self._request(
            method='GET',
            path=f'/auth/session/portal',
            additional_headers={
                'X-Session-ID': session_id,
            }
        )
        return PortalUrlResponse(**response)

    async def get_session_user(self, session_id: str, company_id: str):
        """Get user and tokens for completed session.
        
        Args:
            session_id: Session ID to use as Bearer token
            company_id: Company ID for session validation
            
        Returns:
            SessionUserResponse with user info and tokens
        """
        response = await self._request(
            method='GET',
            path=f'/auth/session/{session_id}/user',
            additional_headers={
                'Authorization': f'Bearer {session_id}',
                'Company-ID': company_id,
            }
        )
        
        # Import here to avoid circular imports
        from ..types.auth import SessionUserResponse
        return SessionUserResponse(**response) 