from ...services.auth_service import AuthenticationService
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from django.views import View
import json

@method_decorator(csrf_exempt, name="dispatch")
class LoginAPIView(View):
    """
    API endpoint for user authentication.

    Methods:
        POST: Authenticate user
            Params:
                username (str): Username
                password (str): Password
            Returns:
                200: Login successful
                400: Invalid credentials
                403: Email not verified
    """

    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request, "data"):
                data = request.data
            else:
                data = json.loads(request.body)
                
            # Clean residual session data
            request.session.flush()

            # Verify if there is an active session
            if request.session.session_key:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Ya hay una sesión activa. Por favor, cierra la sesión antes de iniciar una nueva.",
                        "code": "active_session",
                    },
                    status=403,
                )

            redirect_to = AuthenticationService.login_user(
                request,
                data.get("username"),
                data.get("password"),
                data.get("remember", False),
            )

            if redirect_to == "verify_2fa":
                return JsonResponse(
                    {"status": "pending_2fa", "message": "Código 2FA enviado"}
                )

            # Generate JWT tokens for API authentication
            from ...services.token_service import TokenService
            
            # Get the authenticated user
            user = request.user
            if user.is_authenticated:
                token_data = TokenService.generate_tokens(user)
                
                return JsonResponse({
                    "status": "success", 
                    "message": "Login successful",
                    "redirect_url": f"/{redirect_to}/",
                    "tokens": token_data
                })
            else:
                return JsonResponse(
                    {"status": "success", "redirect_url": f"/{redirect_to}/"}
                )

        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        except PermissionDenied as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=403)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, status=400
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class LogoutAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"status": "error", "message": "No hay ningún usuario conectado"},
                    status=401,
                )

            AuthenticationService.logout_user(request)
            return JsonResponse(
                {
                    "status": "success",
                    "message": AuthenticationService.MESSAGES["logout_success"],
                }
            )
        except ValidationError as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)
        except PermissionDenied as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=403)
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, status=400
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class RegisterAPIView(View):
    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request, "data"):
                data = request.data
            else:
                data = json.loads(request.body)

            try:
                result = AuthenticationService.handle_registration(data)

                if isinstance(result, dict):
                    # If the service returns a dictionary with data
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": AuthenticationService.MESSAGES[
                                "email_verification"
                            ],
                            "data": result,
                        },
                        status=201,
                    )
                elif result:
                    # If the service returns True
                    return JsonResponse(
                        {
                            "status": "success",
                            "message": AuthenticationService.MESSAGES[
                                "email_verification"
                            ],
                        },
                        status=201,
                    )
                else:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": AuthenticationService.MESSAGES[
                                "form_validation"
                            ],
                        },
                        status=400,
                    )

            except ValidationError as service_error:
                return JsonResponse(
                    {"status": "error", "message": str(service_error)}, status=400
                )
            except PermissionDenied as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=403)

        except json.JSONDecodeError as json_error:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, status=400
            )
        except Exception as e:
            return JsonResponse(
                {
                    "status": "error",
                    "message": AuthenticationService.MESSAGES.get(
                        "unexpected_error", "Error inesperado en el servidor"
                    ),
                },
                status=500,
            )


@method_decorator(csrf_exempt, name="dispatch")
class RefreshTokenAPIView(View):
    """
    API endpoint for refreshing access tokens using refresh tokens.
    
    Methods:
        POST: Refresh access token
            Params:
                refresh_token (str): Valid refresh token
            Returns:
                200: New tokens generated
                400: Invalid/expired refresh token
                401: Unauthorized
    """
    
    def post(self, request, *args, **kwargs):
        try:
            if hasattr(request, "data"):
                data = request.data
            else:
                data = json.loads(request.body)
            
            refresh_token = data.get("refresh_token")
            if not refresh_token:
                return JsonResponse(
                    {"status": "error", "message": "Refresh token requerido"},
                    status=400
                )
            
            from ...services.token_service import TokenService
            
            # Generate new tokens
            token_data = TokenService.refresh_access_token(refresh_token)
            
            return JsonResponse({
                "status": "success",
                "message": "Token refreshed successfully",
                "data": token_data
            })
            
        except ValidationError as e:
            return JsonResponse(
                {"status": "error", "message": str(e)}, 
                status=401
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, 
                status=400
            )
        except Exception as e:
            return JsonResponse(
                {"status": "error", "message": "Error interno del servidor"}, 
                status=500
            )
