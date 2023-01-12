from django import dispatch

# Arguments passed to receiver functions are documented at
# https://djangocas.dev/docs/latest/signals.html

cas_proxy_user_authenticated = dispatch.Signal()

cas_proxy_user_logout = dispatch.Signal()
