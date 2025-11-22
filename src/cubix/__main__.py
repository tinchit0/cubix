
try:
    from .playground import run_app
    run_app()
except ImportError:
    print("It seems some packages are missing. Did you install the `gui` extras? pip install cubix[gui]")
