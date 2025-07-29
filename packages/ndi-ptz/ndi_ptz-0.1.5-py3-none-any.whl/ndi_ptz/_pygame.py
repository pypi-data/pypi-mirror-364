def silent_import_pygame():
    import contextlib

    with contextlib.redirect_stdout(None):
        import pygame

        return pygame
