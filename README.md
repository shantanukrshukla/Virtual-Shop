# Virtual-Shop
Creates a virtual shop

## Build and Deploy
- For Deployment, create a wheel package that deploys in the site-packages directory.
- So, first need to run setup.py
- It will generate a wheel package in dist dir.
- And we can install the wheel package locall by using the following command
    $pip install dist/virutalshop-0.0.1-py3-none-any.whl

## Steps to run the wheel package
- Before running the wheel package execute the following command
    $python -c "from virtualshop.configuration.resource_encryption import ResourceEncrypt; instance = ResourceEncrypt(); instance.resourceEncrypt()"
- After running the above command execute the following command
    $python -m virtualshop.app
