import os
import sys
import socket
import requests
import boto3
from huggingface_hub import snapshot_download
from tqdm import tqdm
from base64 import b64encode
from botocore.exceptions import ClientError, EndpointConnectionError
from typing import List


class CephS3Manager:
    def __init__(self, endpoint_url, access_key, secret_key, bucket_name):
        self.s3 = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
        self.bucket_name = bucket_name

    def ensure_bucket_exists(self):
        try:
            buckets = self.s3.list_buckets()
            names = [b['Name'] for b in buckets.get('Buckets', [])]
            if self.bucket_name not in names:
                try:
                    self.s3.create_bucket(Bucket=self.bucket_name)
                    print(f"[OK] Ceph S3 Bucket Created: {self.bucket_name}")
                except ClientError as e:
                    if e.response['Error']['Code'] == "TooManyBuckets":
                        print(f"[WARN] Bucket limit reached. Please ensure bucket '{self.bucket_name}' exists.")
                    else:
                        raise e
            else:
                print(f"[OK] Ceph S3 Bucket Exists: {self.bucket_name}")
        except Exception as e:
            print(f"[FAIL] Ensure Bucket Error: {e}")

    def check_connection(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Connection")
            return True
        except EndpointConnectionError:
            print("[FAIL] Ceph S3 Connection")
            return False
        except ClientError as e:
            print(f"[FAIL] Ceph S3 ClientError: {e.response['Error']['Code']}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Unknown")
            return False

    def check_auth(self):
        try:
            self.s3.list_buckets()
            print("[OK] Ceph S3 Auth")
            return True
        except ClientError as e:
            code = e.response['Error']['Code']
            if code in ["InvalidAccessKeyId", "SignatureDoesNotMatch"]:
                print("[FAIL] Ceph S3 Auth Invalid")
            else:
                print(f"[FAIL] Ceph S3 Auth: {code}")
            return False
        except Exception:
            print("[FAIL] Ceph S3 Auth Unknown")
            return False

    def check_if_exists(self, key):
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=key)
        return resp.get("Contents", []) if "Contents" in resp else None

    def is_folder(self, key):
        contents = self.check_if_exists(key)
        return bool(contents) and any(obj['Key'] != key for obj in contents)

    def _download_file_with_progress_bar(self, remote_path, local_path):
        try:
            meta_data = self.s3.head_object(Bucket=self.bucket_name, Key=remote_path)
            total_length = int(meta_data.get('ContentLength', 0))
        except Exception as e:
            print(f"[ERROR] Failed to fetch metadata for '{remote_path}': {e}")
            total_length = None

        with tqdm(
            total=total_length,
            desc=os.path.basename(remote_path),
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            leave=False,            
            dynamic_ncols=True,
            ncols=100,               
            file=sys.stdout,        
            ascii=True               
        ) as pbar:
            with open(local_path, 'wb') as f:
                self.s3.download_fileobj(self.bucket_name, remote_path, f, Callback=pbar.update)

        print(f"Done downloading: {os.path.basename(remote_path)}")



    def download_file(self, remote_path, local_path):
        if os.path.isdir(local_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        try:
            self._download_file_with_progress_bar(remote_path, local_path)
            print(f"Downloaded '{remote_path}' to '{local_path}'")
        except Exception as e:
            print(f"Error downloading file '{remote_path}': {e}")

    def download_folder(self, remote_folder, local_folder, keep_folder=False, exclude=[], overwrite=False):
        if not remote_folder.endswith("/"):
            remote_folder += "/"
        resp = self.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=remote_folder)
        if "Contents" not in resp:
            print(f"[FAIL] Folder {remote_folder} not found")
            return
        print(f"Downloading folder '{remote_folder}' to '{local_folder}'...")
        if keep_folder:
            local_folder = os.path.join(local_folder, remote_folder.split('/')[-2])
        os.makedirs(local_folder, exist_ok=True)
        with tqdm(total=len(resp["Contents"]), desc="Downloading") as pbar:
            for obj in resp["Contents"]:
                file_key = obj["Key"]
                relative_path = file_key[len(remote_folder):]
                if any(x in relative_path for x in exclude):
                    print(f"Skipped file {file_key}. File matches excluded pattern.")
                    continue
                local_file_path = os.path.join(local_folder, relative_path)
                if not overwrite and os.path.exists(local_file_path):
                    print(f"Skipped file {file_key}. File already exists.")
                else:
                    self.download_file(file_key, local_file_path)
                pbar.update(1)

    def download(self, remote_path, local_path, keep_folder=False, exclude=[], overwrite=False):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot download folder to file path")
        if os.path.isdir(local_path) and not self.is_folder(remote_path):
            local_path = os.path.join(local_path, os.path.basename(remote_path))
        if self.is_folder(remote_path):
            self.download_folder(remote_path, local_path, keep_folder=keep_folder, exclude=exclude, overwrite=overwrite)
        else:
            self.download_file(remote_path, local_path)

    def upload_file(self, local_file_path, remote_path):
        self.s3.upload_file(local_file_path, self.bucket_name, remote_path)
        print(f"[Upload] {local_file_path} -> s3://{self.bucket_name}/{remote_path}")

    def upload(self, local_path, remote_path):
        if os.path.isfile(local_path) and self.is_folder(remote_path):
            raise ValueError("Cannot upload file to folder path")
        if os.path.isdir(local_path):
            if self.check_if_exists(remote_path) and not self.is_folder(remote_path):
                raise ValueError("Cannot upload folder to file path")
        if os.path.isdir(local_path):
            for root, _, files in os.walk(local_path):
                for file in files:
                    local_file = os.path.join(root, file)
                    s3_key = os.path.join(remote_path, os.path.relpath(local_file, local_path)).replace("\\", "/")
                    self.upload_file(local_file, s3_key)
        else:
            self.upload_file(local_path, remote_path)

    def delete_folder(self, prefix):
        objects = self.check_if_exists(prefix)
        if objects:
            for obj in objects:
                self.s3.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
            print(f"[Delete] s3://{self.bucket_name}/{prefix}")

class HealthChecker:
    @staticmethod
    def check_internet():
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=5)
            print("[OK] Internet")
            return True
        except OSError:
            print("[FAIL] Internet")
            return False

    @staticmethod
    def check_clearml_service(url):
        try:
            r = requests.get(url + "/auth.login", timeout=5)
            if r.status_code in [200, 401]:
                print("[OK] ClearML Service")
                return True
            print(f"[FAIL] ClearML Service {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Service")
            return False

    @staticmethod
    def check_clearml_auth(url, access_key, secret_key):
        try:
            creds = f"{access_key}:{secret_key}"
            auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
            r = requests.post(url + "/auth.login",
                              headers={"Authorization": f"Basic {auth_header}"},
                              timeout=5)
            if r.status_code == 200:
                print("[OK] ClearML Auth")
                return True
            print(f"[FAIL] ClearML Auth {r.status_code}")
            return False
        except Exception:
            print("[FAIL] ClearML Auth")
            return False

class ProjectsAPI:
    def __init__(self, post):
        self._post = post

    def create(self, name, description=""):
        return self._post("/projects.create", {"name": name, "description": description})

    def get_all(self):
        return self._post("/projects.get_all")['projects']

class ModelsAPI:
    def __init__(self, post):
        self._post = post

    def create(self, name, project_id):
        return self._post("/models.create", {
            "name": name,
            "project": project_id,
            "uri": "s3://dummy/uri"
        })

    def get_all(self, project_id):
        return self._post("/models.get_all", {"project": project_id})['models']

    def get_by_id(self, model_id):
        return self._post("/models.get_by_id", {"model": model_id})

    def update(self, model_id, uri):
        return self._post("/models.update", {"model": model_id, "uri": uri})

    def delete(self, model_id):
        return self._post("/models.delete", {"model": model_id})

class MLOpsManager:
    def __init__(self, clearml_url, clearml_access_key, clearml_secret_key):
        self.clearml_url = clearml_url
        self.clearml_access_key = clearml_access_key
        self.clearml_secret_key = clearml_secret_key

        self.ceph_url = "http://s3.cloud-ai.ir"
        self.ceph_access_key = "OAF0MC26UA7DV9WS11X5"
        self.ceph_secret_key = "6SY2dTxhcIVEsjbfpjRUBhe3k7mMJIjZpccwvw3d"
        self.user_name = "mohammad"
        self.ceph_bucket = "mlops"

        if not HealthChecker.check_internet(): sys.exit(1)
        ceph_mgr = CephS3Manager(self.ceph_url, self.ceph_access_key, self.ceph_secret_key, self.ceph_bucket)
        ceph_mgr.ensure_bucket_exists()
        if not ceph_mgr.check_connection(): sys.exit(1)
        if not ceph_mgr.check_auth(): sys.exit(1)
        if not HealthChecker.check_clearml_service(self.clearml_url): sys.exit(1)
        if not HealthChecker.check_clearml_auth(self.clearml_url, self.clearml_access_key, self.clearml_secret_key): sys.exit(1)

        self.ceph = ceph_mgr

        creds = f"{self.clearml_access_key}:{self.clearml_secret_key}"
        auth_header = b64encode(creds.encode("utf-8")).decode("utf-8")
        res = requests.post(f"{self.clearml_url}/auth.login",
                            headers={"Authorization": f"Basic {auth_header}"})
        self.token = res.json()['data']['token']

        self.projects = ProjectsAPI(self._post)
        self.models = ModelsAPI(self._post)

        projects = self.projects.get_all()
        self.project_name = f"project_{self.user_name}"
        exists = [p for p in projects if p['name'] == self.project_name]
        self.project_id = exists[0]['id'] if exists else self.projects.create(self.project_name)['id']

    def _post(self, path, params=None):
        headers = {"Authorization": f"Bearer {self.token}"}
        res = requests.post(f"{self.clearml_url}{path}", headers=headers, json=params)
        return res.json()['data']

    def get_model_id_by_name(self, name):
        models = self.models.get_all(self.project_id)
        for m in models:
            if m['name'] == name:
                return m['id']
        return None

    def get_model_name_by_id(self, model_id):
        model = self.models.get_by_id(model_id)
        return model.get("name") if model else None

    def add_model(self, source_type, model_code_path=None, **kwargs):

        model_name = kwargs.get("model_name")

        # Check if a model with the same name already exists
        if self.get_model_id_by_name(model_name):
            print(f"[WARN] Model with name '{model_name}' already exists.")
            print("[INFO] Listing existing models:")
            self.list_models(verbose=True)
            return None

        # Validate model_code_path extension if provided
        if model_code_path:
            if not model_code_path.endswith(".py"):
                raise ValueError(f"Invalid model_code_path: {model_code_path}. Only .py files are accepted.")

        # Create model entry in ClearML
        model = self.models.create(name=model_name, project_id=self.project_id)
        print("[DEBUG] Model Create Response:", model)
        model_id = model['id']
        dest_prefix = f"models/{model_id}/"

        # Determine model folder name based on source type
        if source_type == "local":
            source_path = kwargs.get("source_path")
            model_folder_name = os.path.basename(os.path.normpath(source_path))
        elif source_type == "hf":
            hf_source = kwargs.get("hf_source")
            model_folder_name = hf_source.split("/")[-1]
        elif source_type == "s3":
            source_path = kwargs.get("source_path")
            model_folder_name = os.path.basename(os.path.normpath(source_path))
        else:
            model_folder_name = "unknown"

        try:
            # Upload the model based on the specified source type
            if source_type == "local":
                self.ceph.upload(kwargs.get("source_path"), dest_prefix)
            elif source_type == "hf":
                local_path = snapshot_download(repo_id=kwargs.get("hf_source"))
                self.ceph.upload(local_path, dest_prefix)
            elif source_type == "s3":
                src_ceph = CephS3Manager(
                    kwargs.get("endpoint_url"),
                    kwargs.get("access_key"),
                    kwargs.get("secret_key"),
                    kwargs.get("bucket_name")
                )
                tmp = f"./tmp_{model_name}"
                src_ceph.download(
                    kwargs.get("source_path"),
                    tmp,
                    keep_folder=True,
                    exclude=[".git", ".DS_Store"],
                    overwrite=True
                )
                self.ceph.upload(tmp, dest_prefix)
            else:
                raise ValueError("Unknown source_type")

            # Check and upload model.py if provided
            have_model_py = False
            if model_code_path and os.path.isfile(model_code_path):
                remote_code_path = os.path.join(dest_prefix, "model.py").replace("\\", "/")
                self.ceph.upload_file(model_code_path, remote_code_path)
                print(f"[INFO] Uploaded model code: {remote_code_path}")
                have_model_py = True
            elif model_code_path:
                print(f"[WARN] model_code_path provided but file not found: {model_code_path}")
                have_model_py = False
            else:
                have_model_py = False

        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            print("[INFO] Cleaning up partially uploaded model...")
            self.models.delete(model_id)
            self.ceph.delete_folder(dest_prefix)
            return None

        # Update model URI in ClearML
        uri = f"s3://{self.ceph_bucket}/{dest_prefix}"
        self.models.update(model_id, uri)

        # Set metadata: modelFolderName and haveModelPy
        self._post("/models.set_metadata", {
            "model": model_id,
            "metadata": {
                "modelFolderName": model_folder_name,
                "haveModelPy": have_model_py
            }
        })

        print(f"[AddModel] {model_id} {model_name}")
        return model_id




    def get_model(self, model_name, local_dest):
        model_id = self.get_model_id_by_name(model_name)
        if not model_id:
            print("[FAIL] Model not found")
            return
        model_data = self.models.get_by_id(model_id)
        model = model_data.get("model") or model_data
        uri = model['uri']
        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.download(remote_path, local_dest,
                           keep_folder=True,
                           exclude=[".git", ".DS_Store"],
                           overwrite=False)
        print("[Info] Downloaded:", model)
        return model

    def list_models(self, verbose=True):
        models = self.models.get_all(self.project_id)
        if verbose:
            grouped = {}
            for m in models:
                grouped.setdefault(m["name"], []).append(m["id"])
            for name, ids in grouped.items():
                print(f"[Model] Name: {name}, Count: {len(ids)}")
        return [(m['name'], m['id']) for m in models]

    def delete_model(self, model_id=None, model_name=None):
        if model_name:
            model_id = self.get_model_id_by_name(model_name)
            if not model_id:
                print(f"[WARN] No model found with name '{model_name}'")
                return

        model_data = self.models.get_by_id(model_id)
        if not model_data:
            print(f"[WARN] Model with ID '{model_id}' not found.")
            return

        model = model_data.get("model") or model_data
        uri = model.get("uri")
        if not uri:
            print(f"[WARN] Model '{model_id}' has no 'uri'.")
            return

        _, remote_path = uri.replace("s3://", "").split("/", 1)
        self.ceph.delete_folder(remote_path)
        self.models.delete(model_id)
        print(f"[Deleted] {model_id}")



if __name__ == "__main__":
    manager = MLOpsManager(
        clearml_url="https://213.233.184.112:30008",
        clearml_access_key="9P39WXSAJAIKA51GE807PZFUAN5JCK",
        clearml_secret_key="EW-1JIIPgALdcPmjP2YG0F2KtzljMatXqH_p5BFdC9ygyJHkVZezvUoCjk2oFj-LMjU"
    )

    # Add local model with model.py
    # local_model_id = manager.add_model(
    #     source_type="local",
    #     source_path=r"D:\university\Master-Terms\DML\Projects\MLOPS\Test\Qwen2.5-14B-Instruct",
    #     model_name="local_model",
    #     # model_code_path=r"D:\university\Master-Terms\DML\Projects\MLOPS\Test\Qwen2.5-14B-Instruct\model.py"
    # )

    # Add huggingface model without model.py
    # hf_model_id = manager.add_model(
    #     source_type="hf",
    #     hf_source="facebook/wav2vec2-base-960h",
    #     model_name="hf_model"
    # )

    # Add model from S3 with optional model.py
    # s3_model_id = manager.add_model(
    #     source_type="s3",
    #     endpoint_url="http://s3.cloud-ai.ir",
    #     access_key="OAF0MC26UA7DV9WS11X5",
    #     secret_key="6SY2dTxhcIVEsjbfpjRUBhe3k7mMJIjZpccwvw3d",
    #     bucket_name="mlops",
    #     source_path="models/llm-small/1.0/Qwen2.5-0.5B-Instruct/",
    #     model_name="s3_test_model",
    #     # model_code_path=r"D:\optional\model.py"
    # )

    # Download model by name
    print("\n[Download hf_model]")
    manager.get_model(model_name="hf_model", local_dest="./downloads")

    # Retrieve and display metadata
    # print("\n[Metadata]")
    # if local_model_id:
    #     meta = manager._post("/models.get_by_id", {"model": local_model_id}).get("metadata", {})
    #     print("Local Model → modelFolderName:", meta.get("modelFolderName"))
    #     print("Local Model → haveModelPy:", meta.get("haveModelPy"))

    # if s3_model_id:
    #     meta = manager._post("/models.get_by_id", {"model": s3_model_id}).get("metadata", {})
    #     print("S3 Model → modelFolderName:", meta.get("modelFolderName"))
    #     print("S3 Model → haveModelPy:", meta.get("haveModelPy"))

    # List all models
    print("\n[Model List]")
    models = manager.list_models(verbose=False)
    for name, mid in models:
        print(f"Model Name: {name}, Model ID: {mid}")

    # Delete model by name (optional)
    manager.delete_model(model_name="local_model")
