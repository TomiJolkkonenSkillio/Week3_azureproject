from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, Kind
from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueServiceClient
import os

# Define constants for Azure resources
SUBSCRIPTION_ID = "23b183d5-a30f-46b8-b418-ad060fb67787"
RESOURCE_GROUP_NAME = "tomijolkkonenresourcegroup2"
STORAGE_ACCOUNT_NAME = "tjuniquestorageacct"  # Must be globally unique
LOCATION = "eastus"  # Choose an Azure region
CONTAINER_NAME = "data"
QUEUE_NAME = "myqueue"
FILE_TO_UPLOAD = "example.txt"  # File to upload
DOWNLOADED_FILE = "downloaded_example.txt"  # File to save the downloaded blob

# Authenticate using DefaultAzureCredential
credential = DefaultAzureCredential()

# Step 1: Create a Storage Account
print("Creating Storage Account...")
storage_client = StorageManagementClient(credential, SUBSCRIPTION_ID)
params = StorageAccountCreateParameters(
    sku=Sku(name="Standard_LRS"),
    kind=Kind.STORAGE_V2,
    location=LOCATION,
    enable_https_traffic_only=True
)

async_create = storage_client.storage_accounts.begin_create(
    RESOURCE_GROUP_NAME,
    STORAGE_ACCOUNT_NAME,
    params
)
storage_account = async_create.result()
print(f"Storage Account '{storage_account.name}' created successfully!\n")

# Step 2: Get Storage Account Keys
print("Retrieving Storage Account keys...")
keys = storage_client.storage_accounts.list_keys(RESOURCE_GROUP_NAME, STORAGE_ACCOUNT_NAME)
storage_account_key = keys.keys[0].value

# Step 3: Connect to Blob Service
blob_service_client = BlobServiceClient(
    f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
    credential=storage_account_key
)

# Step 4: Create a Blob Container
print("Creating Blob Container...")
try:
    blob_service_client.create_container(CONTAINER_NAME)
    print(f"Blob Container '{CONTAINER_NAME}' created successfully!\n")
except Exception as e:
    print(f"Blob Container '{CONTAINER_NAME}' already exists.\n")

# Step 5: Upload a File to the Blob Container
print("Uploading file to Blob Container...")
blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=FILE_TO_UPLOAD)
with open(FILE_TO_UPLOAD, "w") as file:
    file.write("This is a sample file to upload to Azure Blob Storage.")
with open(FILE_TO_UPLOAD, "rb") as data:
    blob_client.upload_blob(data, overwrite=True)
print(f"File '{FILE_TO_UPLOAD}' uploaded successfully!\n")

# Step 6: Download the File from the Blob Container
print("Downloading file from Blob Container...")
with open(DOWNLOADED_FILE, "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())
print(f"File downloaded successfully as '{DOWNLOADED_FILE}'!\n")

# Step 7: Create a Queue
print("Creating Queue...")
queue_service_client = QueueServiceClient(
    f"https://{STORAGE_ACCOUNT_NAME}.queue.core.windows.net",
    credential=storage_account_key
)
try:
    queue_client = queue_service_client.create_queue(QUEUE_NAME)
    print(f"Queue '{QUEUE_NAME}' created successfully!\n")
except Exception as e:
    print(f"Queue '{QUEUE_NAME}' already exists.\n")
    queue_client = queue_service_client.get_queue_client(QUEUE_NAME)

# Step 8: Send a Message to the Queue
print("Sending message to Queue...")
message_content = "Hello, Azure Queue!"
queue_client.send_message(message_content)
print(f"Message sent to queue: {message_content}\n")

# Step 9: Receive a Message from the Queue
print("Receiving message from Queue...")
received_message = queue_client.receive_message()
if received_message:
    print(f"Received message: {received_message.content}\n")
    # Delete the message after processing
    queue_client.delete_message(received_message)
    print("Message deleted from the queue.\n")
else:
    print("No messages found in the queue.\n")

# Cleanup: Remove the temporary files
os.remove(FILE_TO_UPLOAD)
os.remove(DOWNLOADED_FILE)

print("Script completed successfully!")