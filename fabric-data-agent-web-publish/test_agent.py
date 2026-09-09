import time

from azure.identity import InteractiveBrowserCredential


PUBLISHED_URL = "BLANK"

FABRIC_SCOPE = "BLANK"


credential = InteractiveBrowserCredential()


print("Getting Microsoft Entra ID token...")

start_time = time.perf_counter()

try:
    token = credential.get_token(FABRIC_SCOPE)

    elapsed = time.perf_counter() - start_time

    print("\nAuthentication successful.")
    print(f"Token acquired in {elapsed:.2f} seconds")

    print("\nPublished Fabric Data Agent URL:")
    print(PUBLISHED_URL)

    print("\nReady for direct Published URL test.")

except Exception as error:
    print("\nAuthentication failed:")
    print(error)