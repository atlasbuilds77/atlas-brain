# =====================================================
# KRONOS TERRAFORM VARIABLES
# =====================================================

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name (staging, production)"
  type        = string
  default     = "production"
  
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be 'staging' or 'production'."
  }
}

variable "domain_name" {
  description = "Primary domain name"
  type        = string
  default     = "kronos.app"
}

variable "client_domains" {
  description = "Map of client subdomains"
  type        = map(string)
  default = {
    laura = "laura.kronos.app"
  }
}

# ---------------------
# Database Configuration
# ---------------------
variable "db_instance_class" {
  description = "RDS instance type"
  type        = string
  default     = "db.t3.medium"
}

variable "db_allocated_storage" {
  description = "Initial database storage (GB)"
  type        = number
  default     = 20
}

variable "db_max_allocated_storage" {
  description = "Maximum database storage for autoscaling (GB)"
  type        = number
  default     = 100
}

variable "db_backup_retention_period" {
  description = "Days to retain backups"
  type        = number
  default     = 7
}

# ---------------------
# Redis Configuration
# ---------------------
variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t3.micro"
}

# ---------------------
# ECS Configuration
# ---------------------
variable "ecs_task_cpu" {
  description = "CPU units for ECS tasks"
  type        = number
  default     = 512
}

variable "ecs_task_memory" {
  description = "Memory (MiB) for ECS tasks"
  type        = number
  default     = 1024
}

variable "backend_desired_count" {
  description = "Desired number of backend containers"
  type        = number
  default     = 2
}

variable "frontend_desired_count" {
  description = "Desired number of frontend containers"
  type        = number
  default     = 2
}

variable "worker_desired_count" {
  description = "Desired number of worker containers"
  type        = number
  default     = 1
}

# ---------------------
# Autoscaling
# ---------------------
variable "autoscaling_min_capacity" {
  description = "Minimum container count"
  type        = number
  default     = 1
}

variable "autoscaling_max_capacity" {
  description = "Maximum container count"
  type        = number
  default     = 10
}

variable "autoscaling_cpu_target" {
  description = "Target CPU utilization for autoscaling"
  type        = number
  default     = 70
}

# ---------------------
# Monitoring
# ---------------------
variable "enable_container_insights" {
  description = "Enable CloudWatch Container Insights"
  type        = bool
  default     = true
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}

# ---------------------
# Tags
# ---------------------
variable "additional_tags" {
  description = "Additional tags for all resources"
  type        = map(string)
  default     = {}
}
