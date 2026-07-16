variable "aws_region" {
  default = "us-east-1"
}

variable "app_name" {
  default = "skycast"
}

variable "container_image" {
  default = "209822908944.dkr.ecr.us-east-1.amazonaws.com/skycast:latest"
}

variable "openweather_api_key" {
  description = "OpenWeatherMap API key"
  sensitive   = true
}