variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "project" {
  type    = string
  default = "ops-brief-agent"
}

variable "notify_email" {
  type        = string
  description = "SES-verified sender/recipient"
}

variable "bedrock_inference_profile_id" {
  type    = string
  default = "us.amazon.nova-2-lite-v1:0"
}
