from google.cloud import storage
import os


def download_blob( source_blob_name, destination_file_name, bucket_name="data_for_fin"):
    """Downloads a blob from the bucket."""

    print("down")
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"

    # The ID of your GCS object
    # source_blob_name = "storage-object-name"

    # The path to which the file should be downloaded
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(source_blob_name)
    print("down2")
    blob.download_to_filename(destination_file_name)

    print(
        "Downloaded storage object {} from bucket {} to local file {}.".format(
            source_blob_name, bucket_name, destination_file_name
        )
    )

def file_exists( source_blob_name, bucket_name="data_for_fin"):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    try:
        blob.download_as_string()
        print("true")
        return True
    except:
        print("false")
        return False



def upload_blob(source_file_name, destination_blob_name, bucket_name="data_for_fin"):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Optional: set a generation-match precondition to avoid potential race conditions
    # and data corruptions. The request to upload is aborted if the object's
    # generation number does not match your precondition. For a destination
    # object that does not yet exist, set the if_generation_match precondition to 0.
    # If the destination object already exists in your bucket, set instead a
    # generation-match precondition using its generation number.
    generation_match_precondition = 0

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )


def download_folder(folder_prefix, destination_folder, bucket_name="data_for_fin"):
    """Downloads all objects from a folder prefix in a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    # List all blobs with a certain prefix (folder)
    blobs = bucket.list_blobs(prefix=folder_prefix)

    # print(blobs)

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    for blob in blobs:
        # Destination file path
        print(blob.name)
        destination_file_path = f"{destination_folder}/{blob.name.split(f'{folder_prefix}'+'/')[-1]}"
        if not os.path.exists("/".join(destination_file_path.split('/')[:-1])):
          os.makedirs("/".join(destination_file_path.split('/')[:-1]))
        print(destination_file_path)
        # Download each blob to the destination folder
        blob.download_to_filename(destination_file_path)
        print(f"Blob {blob.name} downloaded to {destination_file_path}.")


def upload_folder(folder_path, destination_prefix='', bucket_name="data_for_fin"):
    """Uploads all files from a local folder to a GCS bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for root, dirs, files in os.walk(folder_path):
        for file_name in files:
            local_file_path = os.path.join(root, file_name)
            blob_name = os.path.join(destination_prefix, os.path.relpath(local_file_path, folder_path))
            blob_name = blob_name.replace("\\", "/")

            # Upload file to the bucket
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(local_file_path)
            print(f"File {local_file_path} uploaded to {blob_name}.")