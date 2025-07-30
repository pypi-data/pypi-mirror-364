import contextvars

# Context variable for storing request-scoped data
data_context = contextvars.ContextVar("request_context", default={})


def set_context(data: dict):
    data_context.set(data)


def get(key: str, default=None):
    return data_context.get({}).get(key, default)


def set(key: str, value):
    ctx = data_context.get({}).copy()
    ctx[key] = value
    data_context.set(ctx)


def clear():
    data_context.set({})
