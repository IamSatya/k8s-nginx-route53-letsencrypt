import kopf

if __name__ == "__main__":
    # Start Kopf operator
    kopf.run(
        standalone=True,
        verbose=True,
        module='operator.handler'  # Points to operator/handler.py
    )