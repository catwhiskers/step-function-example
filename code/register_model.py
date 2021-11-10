import json
import time
import os
# from sagemaker import get_execution_role, session
import boto3

region = boto3.Session().region_name

runtime_region = os.environ['AWS_REGION']

sm_client = boto3.client('sagemaker', region_name=runtime_region)


def register_model_version(model_package_group_name, image_uri, content_type, response_mimetype, model_url ):
    modelpackage_inference_specification =  {
        "InferenceSpecification": {
            "Containers": [
                {
                    "Image": image_uri,
                }
            ],
            "SupportedContentTypes": [ content_type ],
            "SupportedResponseMIMETypes": [ response_mimetype ],
        }
    }
    

    # Specify the model data
    modelpackage_inference_specification["InferenceSpecification"]["Containers"][0]["ModelDataUrl"]=model_url

    create_model_package_input_dict = {
        "ModelPackageGroupName" : model_package_group_name,
        "ModelPackageDescription" : "Model to detect 3 different types of irises (Setosa, Versicolour, and Virginica)",
        "ModelApprovalStatus" : "Approved"
    }
    create_model_package_input_dict.update(modelpackage_inference_specification)
    create_mode_package_response = sm_client.create_model_package(**create_model_package_input_dict)
    model_package_arn = create_mode_package_response["ModelPackageArn"]
    print('ModelPackage Version ARN : {}'.format(model_package_arn))
    return model_package_arn



def lambda_handler(event, context):
    print("event:", event)
    model_package_group_name = event['model_package_group_name']
    image_uri = event['image_uri']
    model_url = event['model_url']
    content_type = event['content_type']
    response_mimetype = event['response_mimetype']
    #create model group if it does not exist 
    try:
        sm_client.describe_model_package_group(ModelPackageGroupName=model_package_group_name)
    except:      
        # model_package_group_name = "scikit-iris-detector-" + str(round(time.time()))
        model_package_group_input_dict = {
            "ModelPackageGroupName" : model_package_group_name,
            "ModelPackageGroupDescription" : "Sample model package group"
        }

        create_model_pacakge_group_response = sm_client.create_model_package_group(**model_package_group_input_dict)
        print('ModelPackageGroup Arn : {}'.format(create_model_pacakge_group_response['ModelPackageGroupArn']))
        
    
    
    model_package_arn = register_model_version(model_package_group_name, image_uri, content_type, response_mimetype, model_url )
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps(model_package_arn)
    }
