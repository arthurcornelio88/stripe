# ☁️ README – Push to GCP (Production Setup)

This guide explains how to configure Google Cloud Platform (GCP) manually so that Terraform can provision infrastructure resources (such as a Cloud Storage bucket) in your **production environment**.

---

## ✅ 1. Create a GCP Project

Go to:
➡️ [https://console.cloud.google.com/projectcreate](https://console.cloud.google.com/projectcreate)

Create a project with the following parameters:

* **Project ID**: `stripe-b2-gcp`
* **Region**: `europe-west1`

---

## 🔐 2. Create a Service Account

1. Navigate to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)

2. Click **"Create Service Account"**

3. Give it a name like `terraform`

4. Grant the following role:

   * `Storage Admin`

5. After creation, go to **"Keys" > "Add Key" > "JSON"**

6. Download the key file

---

## 📁 3. Store the Credentials Locally

1. Rename and move the downloaded file to your repo:

   ```bash
   mv ~/Downloads/your-key.json infra/gcp/gcp_service_account.json
   ```

2. Your project structure should look like:

   ```
   infra/
   └── gcp/
       ├── main.tf
       ├── gcp_service_account.json ✅
       └── ...
   ```

---

## 🛠 4. Install Terraform (if needed)

> 📦 If Terraform is not installed, follow the official guide:
> 👉 [Install Terraform CLI](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)

Then verify the version:

```bash
terraform -v
# Terraform v1.12.x or later
```

---

## 🚀 5. Deploy with Make

Use the following command to deploy infrastructure:

```bash
make tf_bucket
```

This script will:

* Check whether the GCS bucket `stripe-oltp-bucket-prod` already exists,
* If it does **not**, it initializes and applies the Terraform configuration in `infra/gcp`.

> 🔄 **Note:** This command is also integrated into the `make all ENV=PROD` workflow.
> You don’t need to run `make tf_bucket` manually unless you're testing or working in isolation.

---

## ✅ Final Result

You should see the provisioned bucket here:
👉 [https://console.cloud.google.com/storage/browser](https://console.cloud.google.com/storage/browser)

---