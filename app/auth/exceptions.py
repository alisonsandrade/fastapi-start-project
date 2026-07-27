class AuthError(Exception):
    """Exceção base para erros de autenticação e autorização."""
    pass

class InvalidCredentialsError(AuthError):
    """Exceção para credenciais inválidas (usuário ou senha incorretos)."""
    pass

class InactiveUserError(AuthError):
    """Exceção para usuário inativo."""
    pass

class InvalidRefreshTokenError(AuthError):
    """Exceção para refresh token inválido."""
    pass

class InvalidSessionError(AuthError):
    """Exceção para sessão inválida ou expirada."""
    pass

class LogoutError(AuthError):
    pass

class PasswordResetTokenError(AuthError):
    """Invalid or expired password reset token."""
    pass
